"""Incremental sync: the world moving underneath the graph.

M1 ingested a directory once. M2's problem is different — documents get edited,
deleted, and re-shared, and permissions change. Four things have to hold:

* An **edit** rewrites the node in place, same ID, and re-extracts. The diff
  must be minimal and reviewable, not a whole-file churn.
* An edit can **orphan evidence**. A span that pointed at text which no longer
  exists is demoted to `stale` and re-proposed — not silently kept, and not
  silently dropped. A citation pointing at text that is gone is worse than no
  citation, and dropping it hides that the graph was ever wrong.
* A **delete** produces a tombstone, never a file removal. Inbound edges
  survive, so a citation issued before the delete resolves to "this source was
  deleted on <date>" rather than a dangling ID (§9.3).
* A **revoked grant** takes effect on the next sync. The window between the
  source change and the sync is a real leak window; it is bounded and reported,
  not eliminated.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime

from company_brain.acl.grants import GrantTable
from company_brain.connectors.base import (
    Connector,
    Disappearance,
    Page,
    SourceRecord,
    SyncState,
)
from company_brain.extract.base import CachedExtractor, ExtractionRequest
from company_brain.normalize.base import Registry, content_sha256
from company_brain.schemas.edges import Edge, EdgeStatus
from company_brain.schemas.ids import document_slug, make_id
from company_brain.schemas.nodes import (
    ExtractionRef,
    ExtractionStatus,
    Frontmatter,
    Node,
    NodeStatus,
    NodeType,
    NormalizerRef,
    SourceRef,
    Timestamps,
)
from company_brain.store.repository import Repository

GRANTS_PREFIX = "_sync/grants"


@dataclass(slots=True)
class SyncReport:
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    trashed: int = 0
    access_lost: int = 0
    stale_edges: int = 0
    grants_added: int = 0
    grants_revoked: int = 0
    skipped: list[tuple[str, str]] = field(default_factory=list)

    @property
    def changed(self) -> int:
        return self.added + self.updated + self.deleted + self.trashed

    @property
    def quiet(self) -> bool:
        """Nothing moved. Distinct from "nothing was there", which is why
        `unchanged` is counted rather than left at zero."""
        return (
            self.changed == 0
            and self.access_lost == 0
            and self.grants_added == 0
            and self.grants_revoked == 0
        )

    def summary(self) -> str:
        return (
            f"+{self.added} added  ~{self.updated} updated  "
            f"-{self.deleted} deleted  ={self.unchanged} unchanged"
            + (f"  {self.trashed} trashed" if self.trashed else "")
            + (f"  {self.access_lost} hidden (NOT deleted)" if self.access_lost else "")
            + (f"  {self.stale_edges} edges stale" if self.stale_edges else "")
            + f"  ·  grants +{self.grants_added}/-{self.grants_revoked}"
        )


class SyncEngine:
    def __init__(
        self,
        repo: Repository,
        registry: Registry,
        extractor: CachedExtractor,
        grants: GrantTable,
    ) -> None:
        self.repo = repo
        self.registry = registry
        self.extractor = extractor
        self.grants = grants

    def sync(
        self, connector: Connector, *, now: datetime | None = None, detect_deletes: bool = True
    ) -> SyncReport:
        report = SyncReport()
        moment = now or datetime.now(UTC)
        state = SyncState.load(self.repo.backend, connector.name)

        # 1. content -------------------------------------------------------
        cursor = state.cursor
        page = Page(records=(), cursor=cursor)
        while True:
            page = connector.fetch(cursor)
            report.unchanged += page.cursor_skipped
            for record in page.records:
                try:
                    self._apply(record, connector.name, report)
                except Exception as exc:
                    report.skipped.append((record.external_id, str(exc)))
            cursor = page.cursor
            if not page.has_more:
                break

        # 2. deletions and pre-existing files ---------------------------------
        # Enumeration is the only reliable signal; most sources do not push
        # delete events. Skippable because it is the expensive half of a sync.
        if detect_deletes:
            live = connector.enumerate_ids()

            # For connectors like Drive where changes.startPageToken() returns "now"
            # and pre-existing files won't appear in the changes feed, fetch them
            # explicitly. This handles the "cold start" case where files exist in
            # the source folder before we start tracking changes.
            fetched_ids = {r.external_id for r in page.records}
            for pre_existing_id in sorted(live - state.seen):
                if pre_existing_id not in fetched_ids:
                    try:
                        # Try to fetch the file if the connector supports it.
                        if hasattr(connector, "fetch_file_by_id"):
                            record = connector.fetch_file_by_id(pre_existing_id)
                            if record is not None:
                                self._apply(record, connector.name, report)
                    except Exception as exc:
                        report.skipped.append((pre_existing_id, str(exc)))

            for gone in sorted(state.seen - live):
                node_id = self._node_id_for(connector.name, gone)
                if not node_id or not self.repo.exists(node_id):
                    continue
                self._depart(connector, gone, node_id, moment, report)
            state.seen = live
        else:
            state.seen |= {r.external_id for r in page.records}

        # 3. permissions ---------------------------------------------------
        self._sync_grants(connector, report)
        self._persist_grants(connector)

        state.cursor = cursor
        state.save(self.repo.backend, now=moment)
        return report

    def _depart(
        self,
        connector: Connector,
        external_id: str,
        node_id: str,
        moment: datetime,
        report: SyncReport,
    ) -> None:
        """Act on *why* something vanished, not merely that it did.

        An enumeration diff cannot tell a deletion from an unshare — Drive's
        changes feed says as much in its own documentation. Treating both as
        deletion tombstones every file someone stops sharing, and under the
        §14 Q3 default that purges a body which was never deleted.

        The asymmetry decides the default: a late delete is a bounded
        freshness-SLA problem; a false delete with a purged body cannot be
        undone. So anything the connector cannot classify is left alone.
        """
        reason = connector.classify_departure(external_id)

        if reason is Disappearance.DELETED:
            self.repo.tombstone(node_id, deleted_at=moment, retain_content=False)
            report.deleted += 1
        elif reason is Disappearance.TRASHED:
            # Recoverable upstream for a window. Tombstone so it leaves
            # retrieval immediately, but keep the body — it may come back, and
            # re-extraction is neither free nor deterministic.
            self.repo.tombstone(
                node_id, deleted_at=moment, retain_content=True, reason="moved to trash"
            )
            report.trashed += 1
        else:
            # ACCESS_LOST or UNKNOWN. The artifact still exists; we simply
            # cannot see it. That is a grant change, and the grant sync below
            # handles it. Destroying a live document here would be the one
            # unrecoverable mistake in this whole path.
            report.access_lost += 1

    # ---- content ---------------------------------------------------------

    def _apply(self, record: SourceRecord, connector: str, report: SyncReport) -> None:
        normalizer = self.registry.for_suffix(record.suffix)
        if normalizer is None:
            raise ValueError(f"no normalizer for {record.suffix!r}")

        sha = content_sha256(record.raw)
        normalized = normalizer.normalize(record.raw)
        node_id = self._node_id_for(connector, record.external_id, record, normalized.title)

        existing = self.repo.find(node_id)
        if (
            existing is not None
            and existing.frontmatter.source is not None
            and existing.frontmatter.source.content_sha256 == sha
            and existing.frontmatter.status is NodeStatus.ACTIVE
        ):
            # The cursor handed it to us, but the bytes are the ones we already
            # have — a re-fetch, not a change. Counted, because an uncounted
            # no-op prints "=0", which reads as an empty source.
            report.unchanged += 1
            return

        request = ExtractionRequest(node_id, normalized.title, normalized.body, sha)
        extracted = self.extractor.extract(request)

        relations = list(extracted.edges)
        if existing is not None:
            relations = self._reconcile(existing, relations, normalized.body, report)

        node = Node(
            frontmatter=Frontmatter(
                id=node_id,
                type=NodeType.DOCUMENT,
                title=normalized.title,
                acl=record.acl,
                source=SourceRef(
                    connector=connector,
                    uri=record.uri,
                    external_id=record.external_id,
                    external_version=record.external_version,
                    content_sha256=sha,
                ),
                timestamps=Timestamps(
                    created=record.created or normalized.created,
                    modified=record.modified or normalized.modified,
                ),
                normalizer=NormalizerRef(name=normalizer.name, version=normalizer.version),
                extraction=ExtractionRef(
                    model=self.extractor.model,
                    prompt_version=self.extractor.prompt_version,
                    cache_key=self.extractor.key_for(request),
                    status=ExtractionStatus.ACCEPTED,
                ),
                relations=tuple(relations),
            ),
            body=normalized.body,
        )
        self.repo.put(node, input_tiers=(record.acl.sensitivity,))
        if existing is None:
            report.added += 1
        else:
            report.updated += 1

    def _reconcile(
        self, existing: Node, fresh: list[Edge], body: str, report: SyncReport
    ) -> list[Edge]:
        """Carry forward human decisions, and mark orphaned evidence stale.

        Two things must survive a re-extraction:

        * A human's accept or reject. Re-extracting must not silently undo a
          review decision — that would make the queue Sisyphean.
        * Knowledge that an edge's evidence no longer exists. The span is
          re-checked against the *new* body; if it no longer resolves, the edge
          becomes `stale` rather than being kept (a citation into deleted text)
          or dropped (hiding that the graph was wrong).
        """
        decided = {
            (str(e.predicate), e.object): e
            for e in existing.frontmatter.relations
            if e.status in (EdgeStatus.ACCEPTED, EdgeStatus.REJECTED)
            and str(e.provenance) != "structural"
        }

        out: list[Edge] = []
        for edge in fresh:
            key = (str(edge.predicate), edge.object)
            prior = decided.pop(key, None)
            if prior is not None:
                # Keep the human's verdict, take the fresh evidence.
                out.append(edge.model_copy(update={"status": prior.status}))
            else:
                out.append(edge)

        # Anything previously decided that this extraction no longer supports.
        for edge in decided.values():
            if _evidence_resolves(edge, body):
                out.append(edge)
            else:
                out.append(edge.model_copy(update={"status": EdgeStatus.STALE}))
                report.stale_edges += 1
        return out

    def _node_id_for(
        self,
        connector: str,
        external_id: str,
        record: SourceRecord | None = None,
        title: str | None = None,
    ) -> str:
        """Stable node ID for a source artifact.

        Derived from the *URI*, so a retitled document keeps its ID and its
        inbound citations (invariant 12). Without a record we can only look the
        ID up, which is what delete detection needs.
        """
        if record is not None and title is not None:
            # `record.path` lets a connector place its nodes where another
            # connector already put them. The simulated Slack serves the
            # corpus's own channel-days, so it must land on the corpus's node
            # ids or every sync writes a second copy of the whole workspace.
            slug = f"{record.path or connector}/{document_slug(title, record.uri)}"
            return make_id("Document", slug)
        for node_id in self.repo.walk_ids("Document"):
            node = self.repo.find(node_id)
            if (
                node
                and node.frontmatter.source
                and node.frontmatter.source.connector == connector
                and node.frontmatter.source.external_id == external_id
            ):
                return node_id
        return ""

    # ---- permissions -----------------------------------------------------

    def _persist_grants(self, connector: Connector) -> None:
        """Mirror this connector's grants to disk.

        `build_grants()` reconstructs from CHANNEL_MEMBERS on every process, so
        without this a revocation dies the moment the CLI exits — `cb sync
        --leave` would report a revocation and `cb ask` in the next process
        would still see the channel. Invariant 2 already names `acl_grants` as
        state that is *not* derivable from markdown; this is that state.
        """
        prefix = f"{connector.name}:"
        mirrored = {
            principal: sorted(r for r in refs if r.startswith(prefix))
            for principal, refs in self.grants.snapshot().items()
        }
        self.repo.backend.write_text(
            f"{GRANTS_PREFIX}/{connector.name}.json",
            json.dumps(
                {
                    "connector": connector.name,
                    "grants": {p: r for p, r in sorted(mirrored.items()) if r},
                    "tiers": {g.acl_ref: str(g.sensitivity) for g in connector.grants()},
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    def _sync_grants(self, connector: Connector, report: SyncReport) -> None:
        """Mirror source membership into the grant table.

        Revocation is the case that matters. A principal who left a channel must
        lose access, and must lose it for delegated agents too — the agent's cap
        is the human's set, so shrinking the human shrinks the agent (§8.2).
        """
        prefix = f"{connector.name}:"
        fresh = {(g.principal_id, g.acl_ref): g for g in connector.grants()}

        current: set[tuple[str, str]] = {
            (principal, ref)
            for principal, refs in self.grants.snapshot().items()
            for ref in refs
            if ref.startswith(prefix)
        }

        for key, grant in fresh.items():
            if key not in current:
                self.grants.grant(grant.principal_id, grant.acl_ref, grant.sensitivity)
                report.grants_added += 1

        for principal, ref in current - set(fresh):
            self.grants.revoke(principal, ref)
            report.grants_revoked += 1


def _evidence_resolves(edge: Edge, body: str) -> bool:
    """Does this edge's evidence still point at real text?"""
    for evidence in edge.evidence:
        if evidence.span is None:
            continue
        start, end = evidence.span
        if end > len(body):
            return False
        if evidence.quote and body[start:end].strip() != evidence.quote.strip():
            return False
    return True
