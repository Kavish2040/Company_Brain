"""`company_brain` / `cb` command line."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from company_brain.app import CORPUS_ROOT, PRINCIPALS, STORE_ROOT, build_app, cached_extractor
from company_brain.cli.auth import auth_app
from company_brain.retrieve.hybrid import HybridRetriever
from company_brain.synthesize.answer import (
    CitationLeakError,
    UncitedAnswerError,
    validate,
)

if TYPE_CHECKING:  # `eval` pulls the corpus tables in; keep it out of `cb --help`
    from company_brain.eval.harness import Metrics

app = typer.Typer(add_completion=False, help="company_brain — a company knowledge graph.")
app.add_typer(auth_app, name="auth")
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


@app.command("eval")
def eval_cmd(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    k: Annotated[int, typer.Option(help="Rank cutoff for recall@k.")] = 10,
    json_out: Annotated[Path | None, typer.Option("--json", help="Write the report.")] = None,
    update_baseline: Annotated[
        bool, typer.Option(help="Record this run as the new baseline.")
    ] = False,
    detail: Annotated[bool, typer.Option(help="List every question that missed.")] = False,
) -> None:
    """Score the golden question set. Exit 1 on regression, 2 on any leak.

    Deliberately mirrors `cb ask`'s exit codes: a leak outranks a quality
    regression, and neither is ever a printed warning.

    `--update-baseline` writes what this store scores, so run `cb doctor` first:
    a half-ingested store scores badly and would record that as the new bar.
    """
    from company_brain.eval.baseline import compare, load_baseline, write_baseline
    from company_brain.eval.harness import run_eval

    instance = build_app(store)
    instance.load_index()
    report = run_eval(instance, k=k)

    echo(f"{len(report.results)} question/principal pairs, synthesizer={report.synthesizer}\n")
    header = f"{'':<16}{'graded':>7}{'recall@k':>10}{'hit@k':>8}{'refusals':>10}{'leaks':>7}"

    def row(label: str, m: Metrics) -> None:
        # A rate over an empty denominator is not zero, it is absent — printing
        # 0.000 for a principal who legitimately sees nothing reads as a bug.
        recall = f"{m.recall_at_k:.3f}" if m.graded else "—"
        hit = f"{m.hit_rate:.3f}" if m.graded else "—"
        refusal = f"{m.refusal_rate:.3f}/{m.refusal_expected}" if m.refusal_expected else "—"
        echo(f"{label:<16}{m.graded:>7}{recall:>10}{hit:>8}{refusal:>10}{m.leaks:>7}")

    echo("By question class" + "\n" + header)
    for name, metrics in report.by_class.items():
        row(name, metrics)
    echo("\nBy principal" + "\n" + header)
    for name, metrics in report.by_principal.items():
        row(name, metrics)
    echo("\n" + header)
    row("overall", report.overall)
    row("M1 goldens", report.seeded)

    if detail:
        echo("\nMisses:")
        for result in report.results:
            if result.graded_for_recall and result.recall < 1.0:
                missing = [e for e in result.expected if e not in result.matched]
                echo(f"  [{result.principal}] {result.question_id}: missing {missing}")

    if json_out is not None:
        json_out.write_text(json.dumps(report.to_json(), indent=2, sort_keys=True) + "\n")
        echo(f"\nWrote {json_out}")

    if update_baseline:
        write_baseline(report)
        echo("\nBaseline updated. Commit the diff — this is a deliberate act.")
        return

    if report.leaks:
        for leak in report.leaks[:10]:
            echo(f"  LEAK [{leak.principal}] {leak.question_id}: {list(leak.leaked)[:3]}")
        echo(f"\n{len(report.leaks)} leaking question(s)")
        raise typer.Exit(2)

    regressions = compare(report, load_baseline())
    if regressions:
        echo("\nREGRESSION against the committed baseline:")
        for regression in regressions:
            echo(f"  {regression}")
        raise typer.Exit(1)
    echo("\nNo regression against the baseline.")


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
    connector: Annotated[str, typer.Option(help="Connector name: 'simulated-slack' or 'gdrive'.")] = "simulated-slack",
    folder: Annotated[
        str | None, typer.Option(help="Drive folder ID (overrides GOOGLE_DRIVE_SCOPE_ID env var).")
    ] = None,
    deletes: Annotated[
        bool, typer.Option(help="Enumerate the source to detect deletions (expensive).")
    ] = True,
    edit: Annotated[
        str | None, typer.Option(help="CHANNEL — rewrite its newest message (simulated-slack only).")
    ] = None,
    delete: Annotated[
        str | None, typer.Option(help="CHANNEL — delete its latest day upstream (simulated-slack only).")
    ] = None,
    trash: Annotated[
        str | None, typer.Option(help="CHANNEL — move its latest day to trash (simulated-slack only).")
    ] = None,
    unshare: Annotated[
        str | None,
        typer.Option(help="CHANNEL — WE lose access (simulated-slack only)."),
    ] = None,
    leave: Annotated[
        str | None, typer.Option(help="PRINCIPAL@CHANNEL — a member leaves (simulated-slack only).")
    ] = None,
    join: Annotated[
        str | None, typer.Option(help="PRINCIPAL@CHANNEL — a member joins (simulated-slack only).")
    ] = None,
    reset: Annotated[
        bool, typer.Option(help="Reseed the workspace from the corpus and clear the cursor (simulated-slack only).")
    ] = False,
) -> None:
    """Incrementally sync a source: content, deletions, and grants.

    For `--connector simulated-slack`: the scenario flags (`--edit`, `--delete`,
    etc.) mutate the simulated workspace *before* syncing, so one command shows
    cause and effect. The workspace persists in `store/_sim/`, composing across
    invocations.

    For `--connector gdrive`: requires `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
    (from `.env`), and a stored refresh token (from `cb auth drive`). The
    `--folder` ID is required (or set `GOOGLE_DRIVE_SCOPE_ID`). Direct children
    only (non-recursive).

    `--unshare` and `--leave` are deliberately different. `--unshare` is *we*
    lost visibility, routing through `Disappearance.ACCESS_LOST` and leaving the
    document alone; `--leave` is a principal losing a grant, narrowing what
    `cb ask` returns for them. An enumeration diff cannot tell those apart,
    which is the whole reason `classify_departure` exists.
    """
    if connector == "simulated-slack":
        _sync_simulated_slack(
            store,
            deletes=deletes,
            edit=edit,
            delete=delete,
            trash=trash,
            unshare=unshare,
            leave=leave,
            join=join,
            reset=reset,
        )
    elif connector == "gdrive":
        _sync_gdrive(store, folder=folder, detect_deletes=deletes)
    else:
        echo(f"unknown connector {connector!r}; try 'simulated-slack' or 'gdrive'")
        raise typer.Exit(64)


def _sync_simulated_slack(
    store: Path,
    *,
    deletes: bool,
    edit: str | None,
    delete: str | None,
    trash: str | None,
    unshare: str | None,
    leave: str | None,
    join: str | None,
    reset: bool,
) -> None:
    """Sync the simulated Slack workspace (scenario-mutable for testing)."""
    from company_brain.connectors.simulated import load_or_seed, seed_from_corpus
    from company_brain.connectors.sync import SyncEngine

    instance = build_app(store)
    backend = instance.repo.backend

    if reset:
        source = seed_from_corpus()
        source.save(backend)
        backend.delete("_sync/slack.json")
        echo(f"reset: reseeded {len(source.channels)} channels from the corpus, cursor cleared")
    else:
        source = load_or_seed(backend)

    def split(value: str) -> tuple[str, str]:
        principal, _, channel = value.partition("@")
        if not principal or not channel:
            echo(f"expected PRINCIPAL@CHANNEL, got {value!r}")
            raise typer.Exit(64)
        return principal, channel

    try:
        if edit:
            when = source.edit_latest(edit, "EDITED UPSTREAM: this message was rewritten.")
            echo(f"upstream: edited #{edit} {when}")
        if delete:
            echo(f"upstream: deleted #{delete} {source.mark_gone(delete, 'deleted')}")
        if trash:
            echo(f"upstream: trashed #{trash} {source.mark_gone(trash, 'trashed')}")
        if unshare:
            echo(f"upstream: lost access to #{unshare} {source.mark_gone(unshare, 'unshared')}")
        if leave:
            who, channel = split(leave)
            source.leave(channel, who)
            echo(f"upstream: {who} left #{channel}")
        if join:
            who, channel = split(join)
            source.join(channel, who)
            echo(f"upstream: {who} joined #{channel}")
    except KeyError as exc:
        echo(str(exc))
        raise typer.Exit(64) from exc

    source.save(backend)

    engine = SyncEngine(
        instance.repo,
        instance.registry,
        cached_extractor(instance, store, frozen=False),
        instance.grants,
    )
    report = engine.sync(source, detect_deletes=deletes)
    _print_sync_report(report)


def _sync_gdrive(
    store: Path,
    *,
    folder: str | None,
    detect_deletes: bool,
) -> None:
    """Sync Google Drive (requires OAuth credentials)."""
    import os

    from company_brain.connectors.drive import DriveConnector
    from company_brain.connectors.gdrive_transport import GoogleDriveTransport
    from company_brain.connectors.google_auth import GoogleOAuthCredentials, OAuthError
    from company_brain.connectors.sync import SyncEngine

    # Resolve folder scope.
    scope_id = folder or os.environ.get("GOOGLE_DRIVE_SCOPE_ID", "").strip()
    if not scope_id:
        echo("No Drive folder ID provided. Pass --folder <id> or set GOOGLE_DRIVE_SCOPE_ID.")
        echo("  To find a folder's ID: open it in Drive; it's the last path segment after /folders/")
        raise typer.Exit(64)

    # Load credentials.
    try:
        credentials = GoogleOAuthCredentials.load("gdrive")
    except OAuthError as exc:
        echo(f"OAuth error: {exc}")
        raise typer.Exit(64) from exc

    # Build the connector and sync.
    instance = build_app(store)
    engine = SyncEngine(
        instance.repo,
        instance.registry,
        cached_extractor(instance, store, frozen=False),
        instance.grants,
    )
    connector = DriveConnector(
        transport=GoogleDriveTransport(
            credentials=credentials,
            scope_folder_id=scope_id,
        )
    )
    report = engine.sync(connector, detect_deletes=detect_deletes)
    _print_sync_report(report)


def _print_sync_report(report) -> None:
    """Print a sync report summary."""
    echo(report.summary())
    if report.quiet:
        echo("  no changes since the last sync")
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
    read_only: Annotated[
        bool, typer.Option(help="Expose the read tools only; no proposals.")
    ] = False,
) -> None:
    """Describe, or run, the MCP server.

    `--as` binds the session's identity at startup — for reads *and* for the
    write path. No tool accepts a principal argument, so a connected model
    cannot claim a different one (invariant 8), and a proposal it creates
    carries both identities into the review queue.

    `--read-only` drops the two write tools from the manifest entirely rather
    than refusing them at call time: a tool a model cannot see is a tool it
    cannot spend a turn discovering it may not use.
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
    run_stdio(store, agent_id=agent_id, delegated_by=as_user, read_only=read_only)


review_app = typer.Typer(help="The human review queue for proposed edges.")
app.add_typer(review_app, name="review")


@review_app.command("list")
def review_list(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    predicate: Annotated[str | None, typer.Option(help="Filter by predicate.")] = None,
    limit: Annotated[int, typer.Option()] = 20,
) -> None:
    """Show everything awaiting a decision: agent proposals, then edges."""
    from company_brain.review.queue import ReviewQueue

    instance = build_app(store)
    queue = ReviewQueue(instance.repo)

    # Agent proposals lead: they are unreviewed input from outside the system,
    # where a proposed edge is the system reporting its own uncertainty about a
    # document a human already trusted.
    proposals = queue.pending_proposals(predicate)
    for diff in proposals[:limit]:
        record = diff.record
        echo(f"\n{record.proposal_id}   [agent]")
        echo(f"  {record.summary}")
        echo(
            f"  by {record.proposed_by} for {record.delegated_by}"
            + ("  STALE" if diff.stale else "")
        )
        echo(f"  `cb review show {record.proposal_id}` for the diff")

    pending = queue.pending_edges(predicate)
    for item in pending[: max(0, limit - len(proposals))]:
        echo(f"\n{item.key}")
        echo(f"  {item.node_title}  (confidence {item.edge.confidence:.2f})")
        if item.quote():
            echo(f"  evidence: {item.quote()[:120]!r}")

    total = len(pending) + len(proposals)
    if not total:
        echo("Nothing pending.")
        return
    echo(
        f"\n{total} pending ({len(proposals)} from agents)"
        + (f", showing {limit}" if total > limit else "")
    )


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


@review_app.command("show")
def review_show(
    proposal_id: Annotated[str, typer.Argument(help="A proposal id from `review list`.")],
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
) -> None:
    """Show one agent proposal as a diff.

    The terminal version of the review UI's diff view. `+`/`-` here rather than
    colour for the same reason the web version uses fill and not green/red: a
    diff that is only legible in colour is not legible.
    """
    from company_brain.review.proposals import ProposalError, ProposalStore

    instance = build_app(store)
    try:
        diff = ProposalStore(instance.repo).diff(proposal_id)
    except ProposalError as exc:
        echo(str(exc))
        raise typer.Exit(1) from exc

    record = diff.record
    echo(f"{record.proposal_id}  [{record.state}]")
    echo(f"  target     {record.target}  ({diff.target_title})")
    echo(f"  proposed   {record.proposed_by} acting for {record.delegated_by}")
    echo(f"  at         {record.created_at.isoformat()}  via {record.surface}")
    echo(f"  inherits   {record.sensitivity}")
    if diff.stale:
        echo("  STALE — the target changed since this was proposed; re-propose it")

    for edge in diff.added_relations:
        echo(f"\n  + {edge.subject or record.target} -{edge.predicate}-> {edge.object}")
        for evidence in edge.evidence:
            if evidence.quote:
                echo(f'      evidence: "{evidence.quote[:160]}"')
    for edge in diff.removed_relations:
        echo(f"\n  - {edge.subject or record.target} -{edge.predicate}-> {edge.object}")

    if diff.body:
        echo("")
        for change in diff.body:
            marker = {"added": "+", "removed": "-", "gap": " ", "context": " "}[change.kind]
            echo(f"  {marker} {change.text}")
    if diff.is_empty:
        echo("\n  (no change — this proposal is a no-op)")


@review_app.command("accept")
def review_accept(
    keys: Annotated[list[str], typer.Argument(help="Edge keys or proposal ids.")],
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    reviewer: Annotated[
        str, typer.Option(help=f"Who is deciding: {', '.join(PRINCIPALS)}")
    ] = "ceo",
) -> None:
    """Accept one or more proposals into the graph."""
    _decide(keys, store, reviewer, accept=True)


@review_app.command("reject")
def review_reject(
    keys: Annotated[list[str], typer.Argument(help="Edge keys or proposal ids.")],
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    reviewer: Annotated[
        str, typer.Option(help=f"Who is deciding: {', '.join(PRINCIPALS)}")
    ] = "ceo",
) -> None:
    """Reject proposals. Retained, not deleted — they're the tuning signal."""
    _decide(keys, store, reviewer, accept=False)


@review_app.command("bulk")
def review_bulk(
    predicate: Annotated[str, typer.Argument(help="Decide every pending edge of this type.")],
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    reject: Annotated[bool, typer.Option(help="Reject instead of accept.")] = False,
    reviewer: Annotated[str, typer.Option()] = "ceo",
    limit: Annotated[int, typer.Option(help="Cap the batch.")] = 100,
) -> None:
    """Decide a whole predicate at once.

    The bet the review queue makes is that a reviewer recognises *patterns* —
    "every `mentions` edge on this corpus is right" — faster than they evaluate
    items. If that bet is wrong for a predicate, its accept rate will say so.
    """
    from company_brain.review.queue import ReviewQueue

    instance = build_app(store)
    queue = ReviewQueue(instance.repo)
    keys = [item.key for item in queue.pending_edges(predicate)][:limit]
    if not keys:
        echo(f"Nothing pending for {predicate!r}.")
        return
    _decide(keys, store, reviewer, accept=not reject)


def _decide(keys: list[str], store: Path, reviewer: str, *, accept: bool) -> None:
    from company_brain.audit.log import Surface
    from company_brain.review.proposals import ProposalError
    from company_brain.review.queue import Decision, ReviewQueue

    app_instance = build_app(store)
    who = app_instance.principal(reviewer)
    queue = ReviewQueue(app_instance.repo, audit=app_instance.audit(Surface.CLI))
    decision = Decision.ACCEPTED if accept else Decision.REJECTED

    # One pass, same as the API. Consecutive edges accumulate and flush
    # together so `decide_many` still pays one store write per node; the kind
    # comes from `kind_of`, which asks the queue rather than reading the shape
    # of the string a human typed.
    run: list[str] = []
    try:
        for key in keys:
            if queue.kind_of(key) == "edge":
                run.append(key)
                continue
            if run:
                queue.decide_many(run, decision, reviewer=who)
                run = []
            queue.decide_proposal(key, decision, reviewer=who)
        if run:
            queue.decide_many(run, decision, reviewer=who)
    except (KeyError, ValueError, ProposalError) as exc:
        echo(f"Could not decide: {exc}")
        raise typer.Exit(1) from exc
    echo(f"{'Accepted' if accept else 'Rejected'} {len(keys)} item(s) as {who.display}")


@app.command("audit")
def audit_cmd(
    store: Annotated[Path, typer.Option()] = STORE_ROOT,
    actor: Annotated[str | None, typer.Option(help="Filter by principal or agent id.")] = None,
    node: Annotated[str | None, typer.Option(help="Filter by node id.")] = None,
    limit: Annotated[int, typer.Option()] = 25,
    stats: Annotated[
        bool, typer.Option(help="Volume per action instead of a listing.")
    ] = False,
) -> None:
    """Who saw what, when.

    Node IDs only — never content (invariant 15). Reading this tells you the
    shape of activity against the graph, never the material in it.
    """
    from company_brain.audit.log import Surface, summarize

    instance = build_app(store)
    log = instance.audit(Surface.CLI)

    if stats:
        tally = summarize(log.scan())
        if not tally:
            echo("No audit records yet.")
            return
        for key, count in tally.items():
            echo(f"  {key:34} {count}")
        return

    records = log.read(limit=limit, actor=actor, node_id=node)
    if not records:
        echo("No matching audit records.")
        return
    for entry in records:
        acting = f" for {entry.delegated_by}" if entry.delegated_by else ""
        ids = ", ".join(entry.node_ids[:3]) + ("…" if len(entry.node_ids) > 3 else "")
        echo(f"{entry.at.isoformat()}  {entry.actor}{acting}")
        echo(f"  {entry.action} -> {entry.outcome}  [{entry.surface}]")
        if ids:
            echo(f"  nodes: {ids}")
        if entry.proposal_id:
            echo(f"  proposal: {entry.proposal_id}")
        if entry.detail:
            echo(f"  {entry.detail}")


if __name__ == "__main__":
    app()
