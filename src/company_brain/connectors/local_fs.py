"""Local-directory connector and the ingest pipeline.

Maps a directory of mixed files into canonical nodes. Deliberately does not read
file mtimes: they change on checkout, and a timestamp that changes on checkout
would make byte-identical re-ingestion impossible (invariant 4). Timestamps come
from inside the artifact, or are absent.

ACL assignment is path-based here because the synthetic corpus encodes tiers in
its layout. A real connector derives the ref from the source system's own
permission object — that is M2's whole problem (§6.1).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from company_brain.corpus.generate import CHANNELS, PEOPLE, PROCESSES, TOOLS
from company_brain.extract.base import CachedExtractor, ExtractionRequest
from company_brain.extract.rules import Roster, RosterEntry
from company_brain.normalize.base import Registry, content_sha256
from company_brain.schemas.acl import AclRef, Sensitivity
from company_brain.schemas.edges import Edge, EdgeStatus, Predicate, Provenance
from company_brain.schemas.ids import document_slug, make_id, slugify
from company_brain.schemas.nodes import (
    ExtractionRef,
    ExtractionStatus,
    Frontmatter,
    Node,
    NodeType,
    NormalizerRef,
    SourceRef,
    Timestamps,
)
from company_brain.store.repository import Repository


@dataclass(frozen=True, slots=True)
class Discovered:
    path: Path
    relative: str
    raw: bytes
    acl: AclRef


@dataclass(slots=True)
class IngestReport:
    documents: int = 0
    entities: int = 0
    skipped: list[tuple[str, str]] = None  # type: ignore[assignment]
    cache_hits: int = 0
    cache_misses: int = 0

    def __post_init__(self) -> None:
        if self.skipped is None:
            self.skipped = []


_CHANNEL_TIER = {name: Sensitivity(tier) for _, name, tier in CHANNELS}


def acl_for(relative: str) -> AclRef:
    """Derive an ACL from corpus layout.

    The `leadership-comp` channel is `restricted` and is the acceptance suite's
    leak canary — a non-CEO answer citing it is a test failure.
    """
    parts = relative.split("/")
    if parts[0] == "slack" and len(parts) > 1:
        channel = parts[1]
        tier = _CHANNEL_TIER.get(channel, Sensitivity.INTERNAL)
        cid = next((c for c, name, _ in CHANNELS if name == channel), channel)
        return AclRef(ref=f"slack:channel:{cid}", sensitivity=tier)
    if parts[0] == "email":
        return AclRef(ref="gmail:mailbox:meridian", sensitivity=Sensitivity.INTERNAL)
    return AclRef(ref="fs:corpus:docs", sensitivity=Sensitivity.INTERNAL)


def discover(root: Path, registry: Registry) -> Iterator[Discovered]:
    """Yield every ingestable file, in sorted order for reproducibility."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name.startswith("."):
            continue
        if registry.for_suffix(path.suffix) is None:
            continue
        relative = path.relative_to(root).as_posix()
        yield Discovered(path, relative, path.read_bytes(), acl_for(relative))


def build_roster() -> Roster:
    """The curated entity list the extractor matches against (§10.3).

    Surface forms are hand-written, including the ones that collide. "Sam K." is
    deliberately *absent*: it is ambiguous between two real people, so it stays
    unresolved rather than being guessed into one of them (§10.2).
    """
    people = tuple(
        RosterEntry(
            make_id("Person", p.slug),
            (p.name, p.email, p.name.split()[0] + " " + p.name.split()[-1]),
        )
        for p in PEOPLE
    )
    teams = tuple(
        RosterEntry(make_id("Team", slugify(t)), (t, t.lower()))
        for t in sorted({p.team for p in PEOPLE})
    )
    tools = tuple(RosterEntry(make_id("Tool", slug), (name,)) for slug, name, _ in TOOLS)
    processes = tuple(
        RosterEntry(make_id("Process", slug), (name, name.lower()))
        for slug, name, _, _ in PROCESSES
    )
    accounts = (
        RosterEntry(
            make_id("Account", "support-inbox"),
            ("support@meridian.example", "Meridian Support"),
        ),
    )
    return Roster(
        people=people, teams=teams, tools=tools, processes=processes, accounts=accounts
    )


class LocalIngest:
    """Runs discover -> normalize -> extract -> write."""

    def __init__(
        self,
        repo: Repository,
        registry: Registry,
        extractor: CachedExtractor,
        *,
        workers: int = 8,
    ) -> None:
        self.repo = repo
        self.registry = registry
        self.extractor = extractor
        self.roster = build_roster()
        self.workers = max(1, workers)
        self._report_lock = Lock()

    def run(
        self, root: Path, *, progress: Callable[[int, int], None] | None = None
    ) -> IngestReport:
        """Ingest a directory.

        Documents are processed concurrently because extraction is entirely
        network-bound — sequentially, 201 documents against a live model takes
        roughly two hours. Concurrency is safe for determinism: each document
        writes its own file, so the resulting tree does not depend on
        completion order. Entity nodes are written afterwards, sequentially,
        because they are shared.
        """
        report = IngestReport()
        items = list(discover(root, self.registry))
        done = 0

        def one(item: Discovered) -> None:
            nonlocal done
            try:
                self._ingest_one(item, report)
            except Exception as exc:
                with self._report_lock:
                    report.skipped.append((item.relative, str(exc)))
            finally:
                with self._report_lock:
                    done += 1
                    if progress:
                        progress(done, len(items))

        if self.workers == 1:
            for item in items:
                one(item)
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                list(pool.map(one, items))

        self._write_entities(report)
        report.cache_hits = self.extractor.hits
        report.cache_misses = self.extractor.misses
        return report

    def _ingest_one(self, item: Discovered, report: IngestReport) -> None:
        normalizer = self.registry.for_suffix(item.path.suffix)
        assert normalizer is not None  # discover() already filtered
        result = normalizer.normalize(item.raw)

        uri = f"file://corpus/{item.relative}"
        slug = f"{Path(item.relative).parent.as_posix()}/{document_slug(result.title, uri)}"
        node_id = make_id("Document", slug.lstrip("./"))
        sha = content_sha256(item.raw)

        request = ExtractionRequest(
            node_id=node_id, title=result.title, body=result.body, content_sha256=sha
        )
        extracted = self.extractor.extract(request)

        authors = tuple(
            sorted(
                {
                    entry.node_id
                    for entry in self.roster.people + self.roster.accounts
                    for surface in entry.surfaces
                    if surface in result.author_hints
                }
            )
        )
        author_edges = tuple(
            Edge(
                predicate=Predicate.AUTHORED_BY,
                object=author,
                confidence=1.0,
                provenance=Provenance.STRUCTURAL,
                status=EdgeStatus.ACCEPTED,
            )
            for author in authors
        )
        relations = {(str(e.predicate), e.object): e for e in extracted.edges}
        for edge in author_edges:
            relations[(str(edge.predicate), edge.object)] = edge

        node = Node(
            frontmatter=Frontmatter(
                id=node_id,
                type=NodeType.DOCUMENT,
                title=result.title,
                acl=item.acl,
                source=SourceRef(
                    connector="local_fs",
                    uri=uri,
                    external_id=item.relative,
                    external_version=sha[:16],
                    content_sha256=sha,
                ),
                authors=authors,
                timestamps=Timestamps(created=result.created, modified=result.modified),
                normalizer=NormalizerRef(name=normalizer.name, version=normalizer.version),
                extraction=ExtractionRef(
                    model=self.extractor.model,
                    prompt_version=self.extractor.prompt_version,
                    cache_key=self.extractor.key_for(request),
                    status=ExtractionStatus.ACCEPTED,
                ),
                relations=tuple(relations.values()),
            ),
            body=result.body,
        )
        self.repo.put(node, input_tiers=(item.acl.sensitivity,))
        with self._report_lock:
            report.documents += 1

    def _write_entities(self, report: IngestReport) -> None:
        """Create the curated entity nodes the documents point at.

        Written only if absent: an entity page may carry human annotation, and
        re-ingesting must never clobber it (invariant 13). Regenerating the
        machine-owned summary regions is a separate pass.
        """
        specs: list[tuple[NodeType, RosterEntry, str]] = [
            *((NodeType.PERSON, e, e.surfaces[0]) for e in self.roster.people),
            *((NodeType.TEAM, e, e.surfaces[0]) for e in self.roster.teams),
            *((NodeType.TOOL, e, e.surfaces[0]) for e in self.roster.tools),
            *((NodeType.PROCESS, e, e.surfaces[0]) for e in self.roster.processes),
            *((NodeType.ACCOUNT, e, e.surfaces[1]) for e in self.roster.accounts),
        ]
        for node_type, entry, title in specs:
            if self.repo.exists(entry.node_id):
                continue
            self.repo.put(
                Node(
                    frontmatter=Frontmatter(
                        id=entry.node_id,
                        type=node_type,
                        title=title,
                        acl=AclRef(ref="fs:corpus:docs", sensitivity=Sensitivity.INTERNAL),
                        aliases=tuple(sorted(entry.surfaces)),
                    ),
                    body="",
                )
            )
            report.entities += 1
