/**
 * Review queue — the first piece of the real product surface (ROADMAP M3,
 * DESIGN_SYSTEM §8), not an admin panel.
 *
 * It is fundamentally a **diff reviewer** (§6). Every item shows what accepting
 * it would do to the node *as it stands now*, with the verbatim evidence
 * attached, because a gate whose evidence a reviewer cannot check is not a gate.
 * Additions and removals are drawn in the alpha-fill idiom with a gutter marker
 * — never GitHub green/red — so the diff is legible without colour and in both
 * themes.
 *
 * The acceptance criterion is fifty proposals in fifteen minutes without a
 * terminal: eighteen seconds each. That budget is what shapes the interaction,
 * and it rules out three things this view therefore does not do —
 *
 *   - a round trip before the next item appears (decisions are optimistic, and
 *     the list advances immediately),
 *   - re-confirming a recognised pattern item by item (bulk decides a whole
 *     predicate at once),
 *   - reaching for the mouse (j/k/a/r/u are the primary controls, and the
 *     shortcuts are visible rather than folklore).
 *
 * The accept-rate panel is the calibration signal ARCHITECTURE §11 asks for:
 * near 100% means the gate is theatre; near 10% means the extractor is wasting
 * a reviewer's time. It is surfaced here rather than buried in a metric because
 * whether this queue is sustainable decides whether the product is operable.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  Check,
  CheckCheck,
  Inbox,
  Loader2,
  Mail,
  Send,
  TriangleAlert,
  Undo2,
  X,
} from "lucide-react";

import {
  api,
  ApiError,
  type Decision,
  type DiffLine,
  type Outreach,
  type Pending,
  type RelationDiff,
  type ReviewStats,
} from "../lib/api";
import {
  Card,
  Confidence,
  Empty,
  Kbd,
  SectionHeading,
  cx,
} from "../components/ui/primitives";

/** One reversible step. Undo re-sends the same items as `pending`. */
type LastAction = { items: Pending[]; decision: Decision };

export function ReviewView({
  principal,
  onChanged,
  onOpenNode,
}: {
  principal: string;
  onChanged: () => void;
  onOpenNode: (id: string) => void;
}) {
  const [pending, setPending] = useState<Pending[]>([]);
  const [stats, setStats] = useState<ReviewStats | null>(null);
  const [filter, setFilter] = useState<string | undefined>();
  const [cursor, setCursor] = useState(0);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [last, setLast] = useState<LastAction | null>(null);
  const [approved, setApproved] = useState<Outreach[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    const [items, s, waiting] = await Promise.all([
      api.review(principal, filter),
      api.reviewStats(principal),
      // Approved outreach is not "pending" — it has cleared review and is
      // waiting on a separate, deliberate dispatch. It gets its own section
      // rather than sitting in a queue whose whole verb is "decide".
      api.outreachList(principal, "approved").catch(() => [] as Outreach[]),
    ]);
    setPending(items);
    setStats(s);
    setApproved(waiting);
    setCursor(0);
    setLoading(false);
  }, [principal, filter]);

  useEffect(() => {
    void load();
  }, [load]);

  const decide = useCallback(
    async (items: Pending[], decision: Decision) => {
      if (items.length === 0 || busy) return;
      const keys = new Set(items.map((i) => i.key));
      setBusy(true);
      setError(null);
      // Optimistic: the next item is on screen before the request returns.
      // Eighteen seconds an item does not survive a round trip per keystroke.
      setPending((current) => current.filter((p) => !keys.has(p.key)));
      try {
        await api.decide(principal, items, decision);
        setLast(decision === "pending" ? null : { items, decision });
        onChanged();
        void api.reviewStats(principal).then(setStats);
        // An approved outreach draft moves into the dispatch list, so that
        // section has to catch up with the decision that fed it.
        if (items.some((i) => i.kind === "outreach")) {
          void api
            .outreachList(principal, "approved")
            .then(setApproved)
            .catch(() => undefined);
        }
      } catch (exc) {
        // Put them back. A queue that silently drops a failed decision is a
        // queue that quietly loses work.
        setPending((current) =>
          [...items, ...current].sort((a, b) => a.key.localeCompare(b.key)),
        );
        setError(
          exc instanceof ApiError ? exc.message : "the decision did not land",
        );
      } finally {
        setBusy(false);
      }
    },
    [busy, onChanged, principal],
  );

  const current = pending[cursor];

  const dispatch = useCallback(
    async (draft: Outreach) => {
      setError(null);
      // Not optimistic. Every other decision here is reversible and can afford
      // to move the list before the server agrees; a dispatch is the one act
      // that is not, so the row stays until the server confirms it.
      try {
        await api.outreachSend(principal, draft.draft_id);
        setApproved((current) =>
          current.filter((d) => d.draft_id !== draft.draft_id),
        );
      } catch (exc) {
        setError(
          exc instanceof ApiError ? exc.message : "the dispatch did not land",
        );
      }
    },
    [principal],
  );

  const undo = useCallback(() => {
    if (!last) return;
    void decide(last.items, "pending");
    setLast(null);
  }, [decide, last]);

  const bulk = useCallback(
    (decision: Decision) => {
      if (!current?.predicate) return;
      void decide(
        pending.filter((p) => p.predicate === current.predicate),
        decision,
      );
    },
    [current, decide, pending],
  );

  // Keyboard first. The shortcuts are rendered on every row rather than hidden
  // in a help modal, because a shortcut nobody discovers saves nobody time.
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target && /^(INPUT|TEXTAREA)$/.test(target.tagName)) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;

      switch (event.key) {
        case "j":
          setCursor((c) => Math.min(c + 1, Math.max(pending.length - 1, 0)));
          break;
        case "k":
          setCursor((c) => Math.max(c - 1, 0));
          break;
        case "a":
          if (current) void decide([current], "accepted");
          break;
        case "r":
          if (current) void decide([current], "rejected");
          break;
        case "A":
          bulk("accepted");
          break;
        case "R":
          bulk("rejected");
          break;
        case "u":
          undo();
          break;
        default:
          return;
      }
      event.preventDefault();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [bulk, current, decide, pending.length, undo]);

  // Keep the cursor inside the list as items leave it.
  useEffect(() => {
    setCursor((c) => Math.min(c, Math.max(pending.length - 1, 0)));
  }, [pending.length]);

  const samePredicate = useMemo(
    () =>
      current?.predicate
        ? pending.filter((p) => p.predicate === current.predicate).length
        : 0,
    [current, pending],
  );

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      {stats && (
        <Card className="p-6">
          <div className="flex items-baseline justify-between gap-4 mb-4">
            <p className="text-[13px] font-medium">
              {stats.pending} awaiting review
              {stats.pending_proposals > 0 && (
                <span className="text-muted-foreground font-normal">
                  {" "}
                  · {stats.pending_proposals} from agents
                </span>
              )}
            </p>
            <div className="flex gap-1 flex-wrap justify-end">
              <Pill active={!filter} onClick={() => setFilter(undefined)}>
                all
              </Pill>
              {Object.entries(stats.by_predicate).map(([name, count]) => (
                <Pill
                  key={name}
                  active={filter === name}
                  onClick={() => setFilter(name)}
                >
                  {name} {count}
                </Pill>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-border/50">
            <SectionHeading>Gate calibration</SectionHeading>
            <div className="flex flex-col gap-1.5 mt-2">
              {Object.entries(stats.accept_rate).map(([name, [a, d]]) => (
                <RateBar key={name} name={name} accepted={a} decided={d} />
              ))}
              {Object.entries(stats.proposal_accept_rate).map(([name, [a, d]]) => (
                <RateBar
                  key={`agent:${name}`}
                  name={name}
                  accepted={a}
                  decided={d}
                  agent
                />
              ))}
              {Object.keys(stats.accept_rate).length === 0 &&
                Object.keys(stats.proposal_accept_rate).length === 0 && (
                  <p className="text-[11px] text-muted-foreground/60">
                    Nothing decided yet — no calibration signal.
                  </p>
                )}
            </div>
          </div>
        </Card>
      )}

      {error && (
        <Card className="p-3 border-dashed">
          <p className="text-[12px] text-muted-foreground flex items-center gap-2">
            <TriangleAlert className="w-4 h-4 shrink-0" strokeWidth={1.5} />
            {error}
          </p>
        </Card>
      )}

      {approved.length > 0 && (
        <Card className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Send className="w-3.5 h-3.5 text-muted-foreground/50" strokeWidth={1.5} />
            <SectionHeading>Approved — awaiting dispatch</SectionHeading>
          </div>
          <div className="flex flex-col gap-2">
            {approved.map((draft) => (
              <div
                key={draft.draft_id}
                className="flex items-center gap-3 px-3 py-2 rounded-lg bg-black/5 dark:bg-white/5"
              >
                <Mail
                  className="w-3.5 h-3.5 text-muted-foreground/70 shrink-0"
                  strokeWidth={1.5}
                />
                <div className="min-w-0 flex-1">
                  <button
                    onClick={() => onOpenNode(draft.node_id)}
                    className="text-[13px] truncate hover:underline block max-w-full text-left"
                  >
                    {draft.subject}
                  </button>
                  <p className="text-[11px] text-muted-foreground/70 truncate">
                    to {draft.node_title} · approved by {draft.decided_by}
                    {draft.lead?.email ? ` · ${draft.lead.email}` : " · no address"}
                  </p>
                </div>
                <button
                  onClick={() => void dispatch(draft)}
                  className="shrink-0 inline-flex items-center gap-1.5 h-7 px-2.5 rounded-[6px]
                             text-[11px] font-medium text-primary hover:bg-primary/10
                             transition-colors"
                >
                  <Send className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Dispatch
                </button>
              </div>
            ))}
          </div>
          <p className="mt-3 pt-3 border-t border-border/50 text-[11px] text-muted-foreground/70">
            Apollo is wired for lead lookup only. Dispatch records the send and
            audits it; no message leaves this system yet.
          </p>
        </Card>
      )}

      {loading ? (
        <Empty icon={<Loader2 className="w-6 h-6 animate-spin" strokeWidth={1.5} />}>
          Loading queue…
        </Empty>
      ) : pending.length === 0 ? (
        <Empty icon={<Inbox className="w-6 h-6" strokeWidth={1.5} />}>
          Nothing pending.
        </Empty>
      ) : (
        <>
          <div className="flex items-center justify-between text-[11px] text-muted-foreground/70">
            <span>
              {cursor + 1} of {pending.length}
            </span>
            <div className="flex items-center gap-3">
              {last && (
                <button
                  onClick={undo}
                  className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"
                >
                  <Undo2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                  undo {last.items.length} {last.decision}
                  <Kbd>u</Kbd>
                </button>
              )}
              <span className="flex items-center gap-1">
                <Kbd>j</Kbd>
                <Kbd>k</Kbd> move
              </span>
              <span className="flex items-center gap-1">
                <Kbd>a</Kbd>
                <Kbd>r</Kbd> decide
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-3">
            {pending.map((item, index) => (
              <ProposalCard
                key={item.key}
                item={item}
                selected={index === cursor}
                busy={busy}
                onSelect={() => setCursor(index)}
                onOpenNode={onOpenNode}
                onDecide={(decision) => void decide([item], decision)}
                onBulk={
                  index === cursor && samePredicate > 1
                    ? (decision) => bulk(decision)
                    : undefined
                }
                bulkCount={samePredicate}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

/* ---- one item ----------------------------------------------------------- */

function ProposalCard({
  item,
  selected,
  busy,
  onSelect,
  onOpenNode,
  onDecide,
  onBulk,
  bulkCount,
}: {
  item: Pending;
  selected: boolean;
  busy: boolean;
  onSelect: () => void;
  onOpenNode: (id: string) => void;
  onDecide: (decision: Decision) => void;
  onBulk?: (decision: Decision) => void;
  bulkCount: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (selected) ref.current?.scrollIntoView({ block: "nearest" });
  }, [selected]);

  return (
    <div ref={ref}>
      <Card
        className={cx(
          // Proposed items are never rendered as settled fact (§6).
          "p-4 border-dashed transition-all duration-200",
          selected && "border-solid ring-1 ring-black/5 dark:ring-white/5",
        )}
      >
        <div
          onClick={onSelect}
          className="flex items-start justify-between gap-4 cursor-pointer"
        >
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 flex-wrap">
              <button
                onClick={() => onOpenNode(item.node_id)}
                className="text-[13px] font-medium truncate hover:underline"
              >
                {item.node_title}
              </button>
              {item.kind === "proposal" && (
                <span
                  title={`proposed by ${item.proposed_by}, acting for ${item.delegated_by}`}
                  className="inline-flex items-center gap-1 h-5 px-1.5 text-[10px] font-medium rounded-full bg-primary/10 text-primary"
                >
                  <Bot className="w-3 h-3" strokeWidth={1.5} />
                  {item.proposed_by}
                </span>
              )}
              {item.kind === "outreach" && (
                <span
                  title={`drafted by ${item.proposed_by}`}
                  className="inline-flex items-center gap-1 h-5 px-1.5 text-[10px] font-medium rounded-full bg-primary/10 text-primary"
                >
                  <Mail className="w-3 h-3" strokeWidth={1.5} />
                  outreach
                </span>
              )}
              {item.stale && (
                <span className="inline-flex items-center gap-1 h-5 px-1.5 text-[10px] rounded-full border border-dashed border-border/50 text-muted-foreground/70">
                  <TriangleAlert className="w-3 h-3" strokeWidth={1.5} />
                  stale — re-propose
                </span>
              )}
            </div>

            {item.kind === "proposal" && item.delegated_by && (
              <p className="mt-1 text-[11px] text-muted-foreground/70">
                acting for {item.delegated_by}
              </p>
            )}
          </div>

          <div className="flex items-center gap-1 shrink-0">
            {item.confidence !== null && <Confidence value={item.confidence} />}
            <Action
              label="Reject"
              hint="r"
              busy={busy}
              onClick={() => onDecide("rejected")}
            >
              <X className="w-4 h-4" strokeWidth={1.5} />
            </Action>
            <Action
              label="Accept"
              hint="a"
              primary
              busy={busy}
              onClick={() => onDecide("accepted")}
            >
              <Check className="w-4 h-4" strokeWidth={1.5} />
            </Action>
          </div>
        </div>

        <Diff item={item} onOpenNode={onOpenNode} />

        {onBulk && (
          <div className="mt-3 pt-3 border-t border-border/50 flex items-center gap-3 text-[11px] text-muted-foreground">
            <CheckCheck className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
            <span>
              {bulkCount} pending {item.predicate} edges
            </span>
            <button
              onClick={() => onBulk("accepted")}
              disabled={busy}
              className="hover:text-foreground transition-colors disabled:opacity-40"
            >
              accept all <Kbd>⇧A</Kbd>
            </button>
            <button
              onClick={() => onBulk("rejected")}
              disabled={busy}
              className="hover:text-foreground transition-colors disabled:opacity-40"
            >
              reject all <Kbd>⇧R</Kbd>
            </button>
          </div>
        )}
      </Card>
    </div>
  );
}

/* ---- the diff ----------------------------------------------------------- */

/**
 * Additions and removals in the alpha-fill idiom, never green/red (§6). Each
 * line carries a gutter marker as well as its fill, so the diff survives
 * greyscale, colour-blindness, and a dark theme without a second palette.
 */
function Diff({
  item,
  onOpenNode,
}: {
  item: Pending;
  onOpenNode: (id: string) => void;
}) {
  // An outreach draft is not a change to the graph, so there is no diff to
  // show. What the reviewer has to check is the message itself and the graph
  // statements it was built from — the same "check the evidence, not the
  // prose" rule the edge gates apply, pointed at a different artifact.
  if (item.kind === "outreach") {
    return item.outreach ? <OutreachBody draft={item.outreach} /> : null;
  }

  const empty =
    item.added_relations.length === 0 &&
    item.removed_relations.length === 0 &&
    item.body_diff.length === 0;

  if (empty) {
    return (
      <p className="mt-3 text-[11px] text-muted-foreground/60 italic">
        No change — this proposal is already in the graph.
      </p>
    );
  }

  return (
    <div className="mt-3 flex flex-col gap-2">
      {item.removed_relations.map((edge) => (
        <RelationLine
          key={`-${edge.predicate}${edge.object}`}
          edge={edge}
          removed
          onOpenNode={onOpenNode}
          container={item.node_id}
        />
      ))}
      {item.added_relations.map((edge) => (
        <RelationLine
          key={`+${edge.predicate}${edge.object}`}
          edge={edge}
          onOpenNode={onOpenNode}
          container={item.node_id}
        />
      ))}

      {item.body_diff.length > 0 && (
        <div className="mt-1 rounded-lg border border-border/50 overflow-x-auto">
          {item.body_diff.map((line, index) => (
            <BodyLine key={index} line={line} />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * The message, then what it was built from.
 *
 * The lead line is not decoration. Approving outreach to a contact nobody
 * verified is the mistake this whole review step exists to catch, so where the
 * address came from — a live Apollo match, or nothing at all — is stated on
 * the row rather than left to be assumed.
 */
function OutreachBody({ draft }: { draft: Outreach }) {
  return (
    <div className="mt-3 flex flex-col gap-3">
      <div className="rounded-lg border border-border/50 bg-black/5 dark:bg-white/5 p-3">
        <pre className="text-[12px] leading-relaxed whitespace-pre-wrap font-sans text-muted-foreground">
          {draft.body}
        </pre>
      </div>

      {draft.facts.length > 0 && (
        <div>
          <p className="text-[11px] font-semibold tracking-wider text-muted-foreground/50 uppercase mb-1.5">
            Built from
          </p>
          <div className="flex flex-col gap-1">
            {draft.facts.map((fact) => (
              <p
                key={fact}
                className="text-[12px] text-muted-foreground border-l-2 border-border/50 pl-3"
              >
                {fact}
              </p>
            ))}
          </div>
        </div>
      )}

      <p className="text-[11px] text-muted-foreground/70 flex items-center gap-2 flex-wrap">
        <Mail className="w-3 h-3 shrink-0" strokeWidth={1.5} />
        {draft.lead?.email ? (
          <>
            <span className="font-mono">{draft.lead.email}</span>
            <span>· resolved by {draft.lead_source}</span>
          </>
        ) : (
          <span>
            No contact details — {draft.lead_source} lookup returned no address.
          </span>
        )}
        {draft.lead?.title && <span>· {draft.lead.title}</span>}
      </p>
    </div>
  );
}

function RelationLine({
  edge,
  removed,
  container,
  onOpenNode,
}: {
  edge: RelationDiff;
  removed?: boolean;
  container: string;
  onOpenNode: (id: string) => void;
}) {
  const subject = edge.subject ?? container;
  const subjectLabel = edge.subject_title ?? subject.split("/").pop();
  return (
    <div
      className={cx(
        "flex flex-col gap-1 pl-3 py-1.5 border-l-2 rounded-r-lg",
        removed
          ? "border-border/50 bg-black/[0.03] dark:bg-white/[0.03] opacity-60"
          : "border-foreground/25 bg-black/5 dark:bg-white/5",
      )}
    >
      <div className="flex items-center gap-2 text-[12px] flex-wrap">
        <span className="font-mono text-muted-foreground/70 select-none w-3 shrink-0">
          {removed ? "−" : "+"}
        </span>
        <button
          onClick={() => onOpenNode(subject)}
          className={cx("hover:underline truncate", removed && "line-through")}
        >
          {subjectLabel}
        </button>
        <span className="text-[11px] font-mono text-muted-foreground/70">
          {edge.predicate}
        </span>
        <button
          onClick={() => onOpenNode(edge.object)}
          className={cx(
            "text-[11px] font-mono text-primary hover:underline truncate",
            removed && "line-through",
          )}
        >
          {edge.object_title ?? edge.object}
        </button>
      </div>
      {edge.quote && (
        // A gate whose evidence the reviewer cannot check is not a gate.
        <p className="ml-5 text-[12px] text-muted-foreground border-l-2 border-border/50 pl-3 italic">
          “{edge.quote}”
        </p>
      )}
    </div>
  );
}

function BodyLine({ line }: { line: DiffLine }) {
  if (line.kind === "gap") {
    return (
      <div className="px-3 py-1 text-[11px] text-muted-foreground/50 bg-black/[0.02] dark:bg-white/[0.02] select-none">
        {line.text}
      </div>
    );
  }
  const marker = line.kind === "added" ? "+" : line.kind === "removed" ? "−" : " ";
  return (
    <div
      className={cx(
        "flex gap-2 px-3 py-0.5 text-[12px] font-mono whitespace-pre",
        line.kind === "added" && "bg-black/5 dark:bg-white/5 font-medium",
        line.kind === "removed" &&
          "bg-black/[0.03] dark:bg-white/[0.03] line-through opacity-60",
        line.kind === "context" && "text-muted-foreground/70",
      )}
    >
      <span className="text-muted-foreground/50 select-none shrink-0">{marker}</span>
      <span className="min-w-0">{line.text || " "}</span>
    </div>
  );
}

/* ---- telemetry ---------------------------------------------------------- */

/**
 * One predicate's accept rate. §11: near 100% means the gate never
 * discriminates and is costing reviewer time for nothing; near 10% means the
 * extractor is generating work rather than doing it. Both are called out,
 * because a bar on its own reads as a score rather than as a question.
 */
function RateBar({
  name,
  accepted,
  decided,
  agent,
}: {
  name: string;
  accepted: number;
  decided: number;
  agent?: boolean;
}) {
  const rate = decided ? accepted / decided : 0;
  const verdict =
    decided < 20 ? null : rate === 1 ? "never rejects" : rate < 0.15 ? "mostly noise" : null;

  return (
    <div className="flex items-center gap-3 text-[11px]">
      <span className="w-28 shrink-0 text-muted-foreground truncate flex items-center gap-1">
        {agent && <Bot className="w-3 h-3 shrink-0" strokeWidth={1.5} />}
        {name}
      </span>
      <span className="flex-1 h-1 rounded-full bg-black/5 dark:bg-white/10 overflow-hidden">
        <span
          className="block h-full bg-primary/60"
          style={{ width: `${rate * 100}%` }}
        />
      </span>
      <span className="font-mono text-muted-foreground/70 w-20 text-right">
        {accepted}/{decided}
      </span>
      <span className="w-24 text-[10px] text-muted-foreground/70 italic">
        {verdict}
      </span>
    </div>
  );
}

/* ---- controls ----------------------------------------------------------- */

function Pill({
  active,
  onClick,
  children,
}: {
  active?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cx(
        "px-2 py-1 text-[11px] rounded-md transition-colors",
        active
          ? "bg-primary/10 text-primary font-medium"
          : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/5",
      )}
    >
      {children}
    </button>
  );
}

function Action({
  label,
  hint,
  primary,
  busy,
  onClick,
  children,
}: {
  label: string;
  hint: string;
  primary?: boolean;
  busy?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={(event) => {
        event.stopPropagation();
        onClick();
      }}
      disabled={busy}
      aria-label={label}
      title={`${label} (${hint})`}
      className={cx(
        "p-1.5 rounded-md transition-colors disabled:opacity-40",
        primary
          ? "text-primary hover:bg-primary/10"
          : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground",
      )}
    >
      {children}
    </button>
  );
}
