/**
 * Outreach — the Apollo console.
 *
 * The one surface in this app whose output is addressed to a person outside
 * it, which is what shapes every decision here:
 *
 *   - **Three states are shown, not two.** Drafting, approving, and dispatching
 *     are separate acts against separate endpoints, and the console names all
 *     three rather than collapsing them into "sent". A reviewer who cannot see
 *     which of the three has happened cannot tell a queued message from a
 *     delivered one.
 *   - **Dispatch is never optimistic.** Every other action in this app moves
 *     the list before the server agrees, because every other action is
 *     reversible. A send is not, so the row holds until the server confirms.
 *   - **The lead's provenance is on the row.** "Apollo matched this address"
 *     and "we have a name and nothing else" are different claims, and
 *     approving outreach to an address nobody verified is the mistake the
 *     review step exists to catch.
 *
 * Permission filtering is the server's (invariant 17). `/api/outreach` returns
 * only drafts whose subject this principal can open, and the people list is
 * whatever `/api/nodes` projected — switching principal genuinely changes both.
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Check,
  Loader2,
  Mail,
  MailPlus,
  Send,
  ShieldAlert,
  TriangleAlert,
  Undo2,
  X,
} from "lucide-react";

import {
  api,
  ApiError,
  type NodeSummary,
  type Outreach,
  type OutreachState,
} from "../lib/api";
import {
  Card,
  Empty,
  Row,
  SectionHeading,
  Sensitivity,
  cx,
} from "../components/ui/primitives";
import { iconFor } from "../lib/nodeTypes";

/** Pipeline order, left to right — the order a draft moves through. */
const STATES: OutreachState[] = ["pending", "approved", "rejected", "sent"];

const STATE_HINT: Record<OutreachState, string> = {
  pending: "awaiting a decision",
  approved: "cleared review, not yet dispatched",
  rejected: "declined — reopen to reconsider",
  sent: "dispatched and audited",
};

export function OutreachView({
  principal,
  onChanged,
  onOpenNode,
}: {
  principal: string;
  onChanged: () => void;
  onOpenNode: (id: string) => void;
}) {
  const [drafts, setDrafts] = useState<Outreach[]>([]);
  const [people, setPeople] = useState<NodeSummary[]>([]);
  const [filter, setFilter] = useState<OutreachState | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    const [all, persons, accounts] = await Promise.all([
      api.outreachList(principal).catch(() => [] as Outreach[]),
      api.nodes(principal, "Person").catch(() => [] as NodeSummary[]),
      api.nodes(principal, "Account").catch(() => [] as NodeSummary[]),
    ]);
    setDrafts(all);
    setPeople([...persons, ...accounts]);
    setLoading(false);
  }, [principal]);

  useEffect(() => {
    void load();
  }, [load]);

  const counts = useMemo(() => {
    const tally: Record<string, number> = {};
    for (const draft of drafts) tally[draft.state] = (tally[draft.state] ?? 0) + 1;
    return tally;
  }, [drafts]);

  /**
   * Everyone visible with no draft at all — including rejected ones.
   *
   * A rejected draft looks like it should free the person up to be drafted
   * again, but it does not: draft ids are content-addressed on the message, so
   * re-drafting an unchanged message lands on the rejected draft and the store
   * refuses to reset it to pending. Offering a button that can only conflict
   * would be worse than not offering it. Reopening the rejected draft is the
   * action that actually works, and it lives on that draft's own card.
   */
  const undrafted = useMemo(() => {
    const spoken = new Set(drafts.map((d) => d.node_id));
    return people.filter((p) => !spoken.has(p.id));
  }, [drafts, people]);

  const shown = filter ? drafts.filter((d) => d.state === filter) : drafts;

  async function run(key: string, action: () => Promise<unknown>) {
    if (busy) return;
    setBusy(key);
    setError(null);
    try {
      await action();
      await load();
      onChanged();
    } catch (exc) {
      setError(exc instanceof ApiError ? exc.message : "that did not land");
    } finally {
      setBusy(null);
    }
  }

  const decide = (draft: Outreach, decision: "accepted" | "rejected" | "pending") =>
    run(draft.draft_id, () =>
      api.decide(principal, [{ key: draft.draft_id, kind: "outreach" }], decision),
    );

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <Card className="p-6">
        <div className="flex items-baseline justify-between gap-4 mb-4">
          <p className="text-[13px] font-medium">
            {drafts.length} draft{drafts.length === 1 ? "" : "s"}
            <span className="text-muted-foreground font-normal">
              {" "}
              · {counts.pending ?? 0} awaiting review
            </span>
          </p>
          <div className="flex gap-1 flex-wrap justify-end">
            <Pill active={!filter} onClick={() => setFilter(null)}>
              all
            </Pill>
            {STATES.map((state) => (
              <Pill
                key={state}
                active={filter === state}
                title={STATE_HINT[state]}
                onClick={() => setFilter(state)}
              >
                {state} {counts[state] ?? 0}
              </Pill>
            ))}
          </div>
        </div>

        <p className="pt-4 border-t border-border/50 text-[11px] text-muted-foreground/70">
          Apollo is wired for lead lookup only. Drafting queues a message,
          approving clears it for dispatch, and dispatch records and audits the
          send — no message leaves this system yet.
        </p>
      </Card>

      {error && (
        <Card className="p-3 border-dashed">
          <p className="text-[12px] text-muted-foreground flex items-center gap-2">
            <TriangleAlert className="w-4 h-4 shrink-0" strokeWidth={1.5} />
            {error}
          </p>
        </Card>
      )}

      {loading ? (
        <Empty icon={<Loader2 className="w-6 h-6 animate-spin" strokeWidth={1.5} />}>
          Loading outreach…
        </Empty>
      ) : (
        <>
          {shown.length === 0 ? (
            <Empty icon={<Mail className="w-6 h-6" strokeWidth={1.5} />}>
              {filter ? `Nothing ${filter}.` : "No drafts yet."}
            </Empty>
          ) : (
            <div className="flex flex-col gap-3">
              {shown.map((draft) => (
                <DraftCard
                  key={draft.draft_id}
                  draft={draft}
                  busy={busy === draft.draft_id}
                  disabled={busy !== null}
                  onOpenNode={onOpenNode}
                  onDecide={(decision) => void decide(draft, decision)}
                  onDispatch={() =>
                    void run(draft.draft_id, () =>
                      api.outreachSend(principal, draft.draft_id),
                    )
                  }
                />
              ))}
            </div>
          )}

          {undrafted.length > 0 && (
            <Card className="p-4">
              <div className="flex items-center gap-2 mb-1">
                <MailPlus
                  className="w-3.5 h-3.5 text-muted-foreground/50"
                  strokeWidth={1.5}
                />
                <SectionHeading>No draft yet</SectionHeading>
              </div>
              <div className="flex flex-col gap-0.5">
                {undrafted.map((person) => {
                  const TypeIcon = iconFor(person.type);
                  return (
                    <Row
                      key={person.id}
                      onClick={() => onOpenNode(person.id)}
                      icon={
                        <TypeIcon
                          className="w-[16px] h-[16px] text-muted-foreground/70 shrink-0"
                          strokeWidth={1.5}
                        />
                      }
                      trailing={
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            void run(person.id, () =>
                              api.outreachDraft(principal, person.id),
                            );
                          }}
                          disabled={busy !== null}
                          className="inline-flex items-center gap-1.5 h-6 px-2 rounded-[6px]
                                     text-[11px] font-medium text-muted-foreground
                                     hover:bg-black/5 dark:hover:bg-white/10 hover:text-foreground
                                     transition-colors disabled:opacity-40"
                        >
                          {busy === person.id ? (
                            <Loader2 className="w-3 h-3 animate-spin" strokeWidth={1.5} />
                          ) : (
                            <MailPlus className="w-3 h-3" strokeWidth={1.5} />
                          )}
                          Draft
                        </button>
                      }
                    >
                      {person.title}
                    </Row>
                  );
                })}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ---- one draft ---------------------------------------------------------- */

function DraftCard({
  draft,
  busy,
  disabled,
  onOpenNode,
  onDecide,
  onDispatch,
}: {
  draft: Outreach;
  busy: boolean;
  disabled: boolean;
  onOpenNode: (id: string) => void;
  onDecide: (decision: "accepted" | "rejected" | "pending") => void;
  onDispatch: () => void;
}) {
  const [open, setOpen] = useState(false);
  const settled = draft.state === "sent";

  return (
    <Card
      className={cx(
        "p-4 transition-all duration-200",
        // A draft is not settled fact until it has actually gone out (§6).
        settled ? "border-solid" : "border-dashed",
        draft.state === "rejected" && "opacity-60",
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <button
          onClick={() => setOpen((v) => !v)}
          className="min-w-0 flex-1 text-left"
        >
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[13px] font-medium truncate">{draft.subject}</span>
            <StateBadge state={draft.state} />
            <Sensitivity tier={draft.sensitivity} />
          </div>
          <p className="mt-1 text-[11px] text-muted-foreground/70 truncate">
            to {draft.node_title} · drafted by {draft.drafted_by}
            {draft.decided_by && ` · decided by ${draft.decided_by}`}
            {draft.sent_by && ` · dispatched by ${draft.sent_by}`}
          </p>
        </button>

        <div className="flex items-center gap-1 shrink-0">
          {busy && (
            <Loader2
              className="w-4 h-4 animate-spin text-muted-foreground/70"
              strokeWidth={1.5}
            />
          )}
          {draft.state === "pending" && (
            <>
              <Action label="Reject" disabled={disabled} onClick={() => onDecide("rejected")}>
                <X className="w-4 h-4" strokeWidth={1.5} />
              </Action>
              <Action
                label="Approve"
                primary
                disabled={disabled}
                onClick={() => onDecide("accepted")}
              >
                <Check className="w-4 h-4" strokeWidth={1.5} />
              </Action>
            </>
          )}
          {draft.state === "approved" && (
            <button
              onClick={onDispatch}
              disabled={disabled}
              className="inline-flex items-center gap-1.5 h-7 px-2.5 rounded-[6px]
                         text-[11px] font-medium text-primary hover:bg-primary/10
                         transition-colors disabled:opacity-40"
            >
              <Send className="w-3.5 h-3.5" strokeWidth={1.5} />
              Dispatch
            </button>
          )}
          {draft.state === "rejected" && (
            <Action label="Reopen" disabled={disabled} onClick={() => onDecide("pending")}>
              <Undo2 className="w-4 h-4" strokeWidth={1.5} />
            </Action>
          )}
        </div>
      </div>

      <LeadLine draft={draft} />

      {open && (
        <div className="mt-3 pt-3 border-t border-border/50 flex flex-col gap-3">
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

          <button
            onClick={() => onOpenNode(draft.node_id)}
            className="self-start text-[11px] font-mono text-muted-foreground/60 hover:text-foreground transition-colors"
          >
            {draft.node_id}
          </button>
        </div>
      )}
    </Card>
  );
}

/**
 * Where the address came from, always shown.
 *
 * An offline lookup returns a name and no contact details rather than a
 * fabricated address, so "no address" here means the message has nowhere to go
 * — which a reviewer should see *before* approving it, not after.
 */
function LeadLine({ draft }: { draft: Outreach }) {
  const email = draft.lead?.email;
  return (
    <p className="mt-2 text-[11px] text-muted-foreground/70 flex items-center gap-2 flex-wrap">
      {email ? (
        <>
          <Mail className="w-3 h-3 shrink-0" strokeWidth={1.5} />
          <span className="font-mono">{email}</span>
          <span>· resolved by {draft.lead_source}</span>
        </>
      ) : (
        <>
          <ShieldAlert className="w-3 h-3 shrink-0" strokeWidth={1.5} />
          <span>
            No address — the {draft.lead_source} lookup returned no contact details.
          </span>
        </>
      )}
      {draft.lead?.title && <span>· {draft.lead.title}</span>}
      {draft.lead?.organization && <span>· {draft.lead.organization}</span>}
      <span>· {draft.facts.length} fact{draft.facts.length === 1 ? "" : "s"}</span>
    </p>
  );
}

/* ---- controls ----------------------------------------------------------- */

function StateBadge({ state }: { state: OutreachState }) {
  // `sent` is the only terminal, irreversible state, so it is the only one
  // drawn as settled. The rest stay in the dashed/muted register.
  return (
    <span
      title={STATE_HINT[state]}
      className={cx(
        "inline-flex items-center h-5 px-1.5 text-[10px] font-medium rounded-full",
        state === "sent"
          ? "bg-primary/10 text-primary"
          : "border border-dashed border-border/50 text-muted-foreground/70",
      )}
    >
      {state}
    </span>
  );
}

function Pill({
  active,
  onClick,
  title,
  children,
}: {
  active?: boolean;
  onClick: () => void;
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={title}
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
  primary,
  disabled,
  onClick,
  children,
}: {
  label: string;
  primary?: boolean;
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      title={label}
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
