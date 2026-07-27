"""`company_brain` / `cb` command line."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Annotated

import typer

from company_brain.app import CORPUS_ROOT, PRINCIPALS, STORE_ROOT, build_app, cached_extractor
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.synthesize.answer import (
    CitationLeakError,
    UncitedAnswerError,
    validate,
)

app = typer.Typer(add_completion=False, help="company_brain — a company knowledge graph.")
echo = typer.echo


@app.command()
def corpus(
    out: Annotated[Path, typer.Option(help="Where to write the corpus.")] = CORPUS_ROOT,
    force: Annotated[bool, typer.Option(help="Delete and regenerate.")] = False,
) -> None:
    """Generate the synthetic company corpus."""
    from company_brain.corpus.generate import generate

    if out.exists() and not force:
        echo(f"{out} already exists; pass --force to regenerate.")
        raise typer.Exit(0)
    shutil.rmtree(out, ignore_errors=True)
    files = generate(out)
    echo(f"Wrote {len(files)} files to {out}")


@app.command()
def ingest(
    source: Annotated[Path, typer.Argument()] = CORPUS_ROOT,
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    frozen: Annotated[
        bool, typer.Option(help="Fail on an extraction cache miss (CI mode).")
    ] = False,
    workers: Annotated[
        int, typer.Option(help="Concurrent extractions. Extraction is network-bound.")
    ] = 8,
) -> None:
    """Normalize a directory into the markdown store."""
    from company_brain.connectors.local_fs import LocalIngest

    if not source.exists():
        echo(f"No corpus at {source}. Run `cb corpus` first.")
        raise typer.Exit(1)

    instance = build_app(store)
    echo(f"Providers: {instance.providers.reason}")
    extractor = cached_extractor(instance, store, frozen=frozen)
    ingest_run = LocalIngest(instance.repo, instance.registry, extractor, workers=workers)

    def progress(done: int, total: int) -> None:
        if done % 10 == 0 or done == total:
            typer.echo(f"  {done}/{total}", err=True)

    report = ingest_run.run(source, progress=progress)

    echo(
        f"Ingested {report.documents} documents, {report.entities} new entities "
        f"(cache {report.cache_hits} hit / {report.cache_misses} miss)"
    )
    for path, error in report.skipped[:10]:
        echo(f"  skipped {path}: {error}")
    if report.skipped:
        echo(f"  {len(report.skipped)} skipped in total")


@app.command("index")
def index_cmd(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    rebuild: Annotated[bool, typer.Option(help="Rebuild from scratch.")] = True,
) -> None:
    """Rebuild the derived index from the markdown store."""
    instance = build_app(store)
    chunks = instance.load_index()
    stats = instance.index.stats()
    echo(
        f"Indexed {stats['nodes']} nodes, {chunks} chunks, "
        f"{stats['edges']} accepted edges, {stats['terms']} terms"
    )


@app.command()
def doctor(store: Annotated[Path, typer.Option()] = STORE_ROOT) -> None:
    """Check the store parses and the index agrees with it."""
    instance = build_app(store)
    problems: list[str] = []
    ids: set[str] = set()

    for node_id in instance.repo.walk_ids():
        node = instance.repo.find(node_id)
        if node is None:
            problems.append(f"{node_id}: unreadable")
            continue
        ids.add(node_id)

    for node_id in sorted(ids):
        node = instance.repo.get(node_id)
        for edge in node.frontmatter.relations:
            if edge.object not in ids:
                problems.append(f"{node_id}: edge {edge.predicate} -> missing {edge.object}")

    instance.load_index()
    indexed = instance.index.stats()["nodes"]
    if indexed != len(ids):
        problems.append(f"index has {indexed} nodes, store has {len(ids)}")

    echo(f"Store: {len(ids)} nodes. Index: {indexed} nodes.")
    if problems:
        for problem in problems[:20]:
            echo(f"  DRIFT {problem}")
        echo(f"{len(problems)} problem(s)")
        raise typer.Exit(1)
    echo("Clean.")


@app.command()
def ask(
    question: Annotated[str, typer.Argument()],
    principal: Annotated[str, typer.Option(help=f"One of {', '.join(PRINCIPALS)}")] = "ceo",
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    limit: Annotated[int, typer.Option()] = 6,
) -> None:
    """Answer a question with citations, as a specific principal."""
    instance = build_app(store)
    instance.load_index()
    who = instance.principal(principal)
    access = instance.access(who)

    retrieval = HybridRetriever(instance.index, access).retrieve(question, limit=limit)
    answer = instance.providers.synthesizer().synthesize(question, retrieval, instance.index)

    try:
        validate(answer, retrieval, access, instance.index)
    except CitationLeakError as exc:
        echo(f"LEAK BLOCKED: {exc}")
        raise typer.Exit(2) from exc
    except UncitedAnswerError as exc:
        # Invariant 11: this is an error path, not a degraded answer.
        echo(f"REFUSED (uncited): {exc}")
        raise typer.Exit(3) from exc

    echo(f"\nQ: {question}")
    echo(f"   (as {who.display} — {len(access.refs)} visible sources)\n")
    if answer.insufficient_evidence:
        echo(answer.text)
    else:
        echo(answer.text)
        echo("\nCitations:")
        for citation in answer.citations:
            echo(f"  [{citation.node_id}] {citation.title}")
    echo(
        f"\n({retrieval.seed_count} seed, {retrieval.expanded_count} expanded, "
        f"{retrieval.filtered_out} withheld by ACL)"
    )


@app.command()
def sync(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    connector: Annotated[str, typer.Option(help="Connector name.")] = "simulated-slack",
    deletes: Annotated[
        bool, typer.Option(help="Enumerate the source to detect deletions (expensive).")
    ] = True,
) -> None:
    """Incrementally sync a source: content, deletions, and grants.

    Only `simulated-slack` exists today — a working connector over mutable
    in-memory state, used to exercise edits, deletions, stale evidence and grant
    revocation without credentials. Real Slack and Drive replace three methods
    and keep the rest (see connectors/base.py).
    """
    from company_brain.connectors.simulated import SimulatedSlack
    from company_brain.connectors.sync import SyncEngine

    if connector != "simulated-slack":
        echo(f"unknown connector {connector!r}; only 'simulated-slack' exists so far")
        raise typer.Exit(64)

    instance = build_app(store)
    source = SimulatedSlack()
    engine = SyncEngine(
        instance.repo,
        instance.registry,
        cached_extractor(instance, store, frozen=False),
        instance.grants,
    )
    report = engine.sync(source, detect_deletes=deletes)
    echo(report.summary())
    for external_id, error in report.skipped[:10]:
        echo(f"  skipped {external_id}: {error}")


@app.command()
def principals(store: Annotated[Path, typer.Option()] = STORE_ROOT) -> None:
    """Show what each synthetic principal can see."""
    instance = build_app(store)
    for name in sorted(PRINCIPALS):
        access = instance.access(instance.principal(name))
        echo(f"{name:14} {len(access.refs)} refs  {sorted(access.refs)}")


@app.command("mcp")
def mcp_cmd(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    serve: Annotated[bool, typer.Option(help="Run the stdio server.")] = False,
    agent_id: Annotated[str, typer.Option(help="This agent's own identity.")] = "agent-local",
    as_user: Annotated[
        str, typer.Option("--as", help=f"Human to act for: {', '.join(PRINCIPALS)}")
    ] = "ceo",
) -> None:
    """Describe, or run, the MCP server.

    `--as` binds the session's identity at startup. No tool accepts a principal
    argument, so a connected model cannot claim a different one (invariant 8).
    """
    if not serve:
        from company_brain.mcp.server import describe

        echo(json.dumps(describe(), indent=2))
        return

    from company_brain.mcp.stdio import serve as run_stdio

    if as_user not in PRINCIPALS:
        echo(f"unknown principal {as_user!r}; try {', '.join(sorted(PRINCIPALS))}")
        raise typer.Exit(64)
    # stdout is the MCP transport — anything printed there corrupts the protocol.
    run_stdio(store, agent_id=agent_id, delegated_by=as_user)


review_app = typer.Typer(help="The human review queue for proposed edges.")
app.add_typer(review_app, name="review")


@review_app.command("list")
def review_list(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    predicate: Annotated[str | None, typer.Option(help="Filter by predicate.")] = None,
    limit: Annotated[int, typer.Option()] = 20,
) -> None:
    """Show proposed edges awaiting a decision."""
    from company_brain.review.queue import ReviewQueue

    instance = build_app(store)
    pending = ReviewQueue(instance.repo).pending_edges(predicate)
    if not pending:
        echo("Nothing pending.")
        return
    for item in pending[:limit]:
        echo(f"\n{item.key}")
        echo(f"  {item.node_title}  (confidence {item.edge.confidence:.2f})")
        if item.quote():
            echo(f"  evidence: {item.quote()[:120]!r}")
    echo(f"\n{len(pending)} pending" + (f", showing {limit}" if len(pending) > limit else ""))


@review_app.command("stats")
def review_stats(store: Annotated[Path, typer.Option()] = STORE_ROOT) -> None:
    """Queue volume and per-predicate accept rate.

    Accept rate is the calibration signal: near 100% means the gate is theatre,
    near 10% means the extractor is wasting reviewer time (ARCHITECTURE §11).
    """
    from company_brain.review.queue import ReviewQueue

    instance = build_app(store)
    queue = ReviewQueue(instance.repo)
    stats = queue.stats()

    echo(f"Pending: {stats.total} ({stats.with_evidence} carry evidence)")
    for name, count in sorted(stats.by_predicate.items(), key=lambda kv: -kv[1]):
        echo(f"  {name:22} {count}")

    rates = queue.accept_rate()
    echo("\nAccept rate (llm-provenance edges that have been decided):")
    if not rates:
        echo("  nothing decided yet — no calibration signal")
        return
    for name, (accepted, decided) in rates.items():
        echo(f"  {name:22} {accepted}/{decided} ({100 * accepted / decided:.0f}%)")


@review_app.command("accept")
def review_accept(
    key: Annotated[str, typer.Argument(help="node_id|predicate|object")],
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
) -> None:
    """Accept a proposed edge into the graph."""
    _decide(key, store, accept=True)


@review_app.command("reject")
def review_reject(
    key: Annotated[str, typer.Argument(help="node_id|predicate|object")],
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
) -> None:
    """Reject a proposed edge. Retained, not deleted — it's the tuning signal."""
    _decide(key, store, accept=False)


def _decide(key: str, store: Path, *, accept: bool) -> None:
    from company_brain.review.queue import Decision, ReviewQueue

    instance = build_app(store)
    try:
        ReviewQueue(instance.repo).decide(
            key, Decision.ACCEPTED if accept else Decision.REJECTED
        )
    except (KeyError, ValueError) as exc:
        echo(f"Could not decide {key!r}: {exc}")
        raise typer.Exit(1) from exc
    echo(f"{'Accepted' if accept else 'Rejected'} {key}")


if __name__ == "__main__":
    app()
