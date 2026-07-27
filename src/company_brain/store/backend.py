"""Storage backends for the canonical markdown tree.

The store is the database (invariant 1), so a backend has exactly two hard
obligations:

* **Atomicity.** A partially written file is never observable (invariant 14).
  Readers either see the previous bytes or the new bytes, never a prefix.
* **Path confinement.** Node IDs are derived from connector output, which is
  ultimately attacker-influenced content. A path that escapes the store root is
  a write primitive, so it is rejected here rather than trusted upstream.

All three implementations are checked by the same conformance suite in
``tests/unit/test_backend.py``, so behaviour can't drift between dev and prod.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator, Mapping
from pathlib import Path, PurePosixPath
from typing import Protocol, runtime_checkable

from company_brain.schemas.acl import Sensitivity


class StorePathError(ValueError):
    """A path was absolute, escaped the root, or was otherwise unusable."""


def tier_root(tier: Sensitivity) -> str:
    """Leading path segment for a sensitivity tier.

    The tier's own name, so the tree is self-describing to anyone who opens it
    in an editor — which is half the reason the store is markdown at all.
    """
    return tier.value


_TIER_ROOTS: dict[str, Sensitivity] = {tier_root(t): t for t in Sensitivity}


def safe_relpath(path: str) -> PurePosixPath:
    """Validate a store-relative path and return it normalized.

    Rejects absolute paths, parent traversal, and empty segments. Backslashes
    are rejected outright rather than normalized: on POSIX a backslash is a legal
    filename character, so silently converting it would let ``a\\..\\b`` mean two
    different things on two platforms.
    """
    if not path or path in (".", "/"):
        raise StorePathError(f"empty store path: {path!r}")
    if "\\" in path:
        raise StorePathError(f"backslash in store path: {path!r}")
    if "\x00" in path:
        raise StorePathError(f"null byte in store path: {path!r}")

    pure = PurePosixPath(path)
    if pure.is_absolute():
        raise StorePathError(f"store paths must be relative: {path!r}")
    parts = [p for p in pure.parts if p != "."]
    if any(p == ".." for p in parts):
        raise StorePathError(f"store path escapes the root: {path!r}")
    if not parts:
        raise StorePathError(f"empty store path: {path!r}")
    return PurePosixPath(*parts)


@runtime_checkable
class StoreBackend(Protocol):
    """Byte-level storage. Knows nothing about markdown or nodes."""

    def read_text(self, path: str) -> str | None:
        """Return file contents, or None if absent. Never raises on absence."""
        ...

    def write_text(self, path: str, text: str) -> None:
        """Write atomically, creating parent directories as needed."""
        ...

    def delete(self, path: str) -> bool:
        """Remove the file. Returns False if it wasn't there."""
        ...

    def exists(self, path: str) -> bool: ...

    def walk(self, prefix: str = "") -> Iterator[str]:
        """Yield every path under ``prefix``, in sorted order.

        Sorted because callers diff and hash the results, and an
        enumeration-order difference between backends would show up as spurious
        drift in `cb doctor`.
        """
        ...


class MemoryBackend:
    """In-process backend. The default test double — no temp dirs, no cleanup."""

    def __init__(self) -> None:
        self._files: dict[str, str] = {}

    def read_text(self, path: str) -> str | None:
        return self._files.get(str(safe_relpath(path)))

    def write_text(self, path: str, text: str) -> None:
        self._files[str(safe_relpath(path))] = text

    def delete(self, path: str) -> bool:
        return self._files.pop(str(safe_relpath(path)), None) is not None

    def exists(self, path: str) -> bool:
        return str(safe_relpath(path)) in self._files

    def walk(self, prefix: str = "") -> Iterator[str]:
        normalized = str(safe_relpath(prefix)) + "/" if prefix else ""
        yield from sorted(p for p in self._files if p.startswith(normalized))


class LocalFsBackend:
    """Filesystem backend. The default for dev and CI, where git provides the
    revision log and `git diff --exit-code` provides the acceptance test."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    def _resolve(self, path: str) -> Path:
        target = (self.root / safe_relpath(path)).resolve()
        # Second check, after resolve(): safe_relpath rejects literal '..', but a
        # symlink inside the tree can still point outside it.
        if not target.is_relative_to(self.root):
            raise StorePathError(f"store path escapes the root via symlink: {path!r}")
        return target

    def read_text(self, path: str) -> str | None:
        target = self._resolve(path)
        try:
            return target.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except IsADirectoryError:
            raise StorePathError(f"store path is a directory: {path!r}") from None

    def write_text(self, path: str, text: str) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        # Temp file in the destination directory so os.replace stays within one
        # filesystem — across a mount boundary replace() is not atomic.
        fd, tmp_name = tempfile.mkstemp(
            dir=target.parent, prefix=f".{target.name}.", suffix=".tmp"
        )
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, target)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise

        # Persist the rename itself, so a crash can't leave the directory entry
        # pointing at nothing. Not all platforms permit opening a directory.
        try:
            dir_fd = os.open(target.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
        finally:
            os.close(dir_fd)

    def delete(self, path: str) -> bool:
        target = self._resolve(path)
        try:
            target.unlink()
        except FileNotFoundError:
            return False
        return True

    def exists(self, path: str) -> bool:
        return self._resolve(path).is_file()

    def walk(self, prefix: str = "") -> Iterator[str]:
        base = self._resolve(prefix) if prefix else self.root
        if not base.exists():
            return
        found = [
            p.relative_to(self.root).as_posix()
            for p in base.rglob("*")
            if p.is_file() and not p.name.startswith(".")
        ]
        yield from sorted(found)


class TieredBackend:
    """One logical store spread over a separate backend per sensitivity tier.

    §6.2 asks for tiers that are *physically* separated — distinct buckets with
    distinct IAM — and a directory inside one bucket is not that. This routes on
    the leading path segment, which :class:`Repository` guarantees is the tier
    root, so a credential scoped to the internal bucket cannot read a restricted
    node even if some future bug asks it to.

    Paths are passed through verbatim, tier segment and all. A per-tier bucket
    therefore holds exactly the keys of the matching dev subtree, which makes
    promotion a copy rather than a rewrite, and makes an ``internal/`` key
    inside the restricted bucket visible as misplacement rather than as an
    ordinary node.

    ``shared`` takes the workflow trees that are not tier-partitioned
    (``_proposals/``, ``_cache/``, ``_sync/``). Omitting it makes them an error
    rather than a silent write into an arbitrary tier.
    """

    def __init__(
        self,
        tiers: Mapping[Sensitivity, StoreBackend],
        *,
        shared: StoreBackend | None = None,
    ) -> None:
        missing = [t for t in Sensitivity if t not in tiers]
        if missing:
            raise ValueError(f"no backend for tier(s): {', '.join(missing)}")
        self._tiers = dict(tiers)
        self._shared = shared

    def _route(self, path: str) -> StoreBackend:
        head = safe_relpath(path).parts[0]
        tier = _TIER_ROOTS.get(head)
        if tier is not None:
            return self._tiers[tier]
        if self._shared is None:
            raise StorePathError(
                f"{path!r} is outside every tier root and no shared backend is configured"
            )
        return self._shared

    def read_text(self, path: str) -> str | None:
        return self._route(path).read_text(path)

    def write_text(self, path: str, text: str) -> None:
        self._route(path).write_text(path, text)

    def delete(self, path: str) -> bool:
        return self._route(path).delete(path)

    def exists(self, path: str) -> bool:
        return self._route(path).exists(path)

    def walk(self, prefix: str = "") -> Iterator[str]:
        if prefix:
            yield from self._route(prefix).walk(prefix)
            return
        # Merge rather than concatenate: callers hash and diff this, and the
        # order must not depend on which tier a node happens to live in.
        seen: list[str] = []
        for tier in Sensitivity:
            seen.extend(self._tiers[tier].walk(tier_root(tier)))
        if self._shared is not None:
            others = self._shared.walk()
            seen.extend(p for p in others if p.partition("/")[0] not in _TIER_ROOTS)
        yield from sorted(seen)


class SupabaseStorageBackend:
    """Supabase Storage (S3-compatible) backend for deployed environments.

    Atomicity comes from the object store: an upload is not visible until it
    completes, so there is no torn-read window and no temp-file dance.

    NOTE: exercised by the shared conformance suite, but that run is marked
    ``integration`` and only executes against a live stack (`supabase start`).
    Treat it as unverified until that job has run.
    """

    def __init__(self, client: object, bucket: str, prefix: str = "") -> None:
        # Typed as object because storage3's client type varies across versions
        # and this package is under `mypy --strict`; the calls are duck-typed.
        self._bucket = client.from_(bucket)  # type: ignore[attr-defined]
        self._prefix = prefix.strip("/")

    def _key(self, path: str) -> str:
        rel = safe_relpath(path)
        return f"{self._prefix}/{rel}" if self._prefix else str(rel)

    def read_text(self, path: str) -> str | None:
        try:
            blob = self._bucket.download(self._key(path))
        except Exception:
            # storage3 raises a generic StorageApiError for "not found" as well
            # as for transport failures; absence is not distinguishable without
            # inspecting the message, so an existence check disambiguates.
            if not self.exists(path):
                return None
            raise
        return bytes(blob).decode("utf-8")

    def write_text(self, path: str, text: str) -> None:
        self._bucket.upload(
            self._key(path),
            text.encode("utf-8"),
            {"content-type": "text/markdown; charset=utf-8", "upsert": "true"},
        )

    def delete(self, path: str) -> bool:
        if not self.exists(path):
            return False
        self._bucket.remove([self._key(path)])
        return True

    def exists(self, path: str) -> bool:
        key = self._key(path)
        parent, _, name = key.rpartition("/")
        entries = self._bucket.list(parent or None, {"search": name})
        return any(e.get("name") == name for e in entries)

    def walk(self, prefix: str = "") -> Iterator[str]:
        root = self._key(prefix) if prefix else self._prefix
        yield from sorted(self._walk_from(root))

    def _walk_from(self, folder: str) -> Iterator[str]:
        for entry in self._bucket.list(folder or None):
            name = entry.get("name")
            if not name or name.startswith("."):
                continue
            child = f"{folder}/{name}" if folder else name
            # Supabase Storage has no real directories; a listing entry with no
            # id is a synthetic folder marker.
            if entry.get("id") is None:
                yield from self._walk_from(child)
            else:
                yield child.removeprefix(f"{self._prefix}/") if self._prefix else child
