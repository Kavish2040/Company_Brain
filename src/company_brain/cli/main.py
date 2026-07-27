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
    ExtractiveSynthesizer,
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
) -> None:
    """Normalize a directory into the markdown store."""
    from company_brain.connectors.local_fs import LocalIngest

    if not source.exists():
        echo(f"No corpus at {source}. Run `cb corpus` first.")
        raise typer.Exit(1)

    instance = build_app(store)
    echo(f"Providers: {instance.providers.reason}")
    extractor = cached_extractor(instance, store, frozen=frozen)
    report = LocalIngest(instance.repo, instance.registry, extractor).run(source)

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
    answer = ExtractiveSynthesizer().synthesize(question, retrieval, instance.index)

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
def principals(store: Annotated[Path, typer.Option()] = STORE_ROOT) -> None:
    """Show what each synthetic principal can see."""
    instance = build_app(store)
    for name in sorted(PRINCIPALS):
        access = instance.access(instance.principal(name))
        echo(f"{name:14} {len(access.refs)} refs  {sorted(access.refs)}")


@app.command("mcp")
def mcp_cmd(store: Annotated[Path, typer.Option()] = STORE_ROOT) -> None:
    """Describe the MCP tool surface (stdio server entry point)."""
    from company_brain.mcp.server import describe

    echo(json.dumps(describe(), indent=2))


if __name__ == "__main__":
    app()
