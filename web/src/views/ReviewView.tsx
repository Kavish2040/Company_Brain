/**
 * Review queue.
 *
 * Fundamentally a diff reviewer (§6). Every pending edge is shown with its
 * verbatim evidence quote, because a gate whose evidence a reviewer cannot
 * check is not a gate.
 *
 * The accept-rate panel is the calibration signal ARCHITECTURE §11 asks for:
 * near 100% means the gate is theatre; near 10% means the extractor is wasting
 * a reviewer's time. It is surfaced here rather than buried in a metric because
 * whether this queue is sustainable decides whether the product is operable.
 */

import { useCallback, useEffect, useState } from "react";
import { Check, Inbox, Loader2, X } from "lucide-react";

import { api, type Pending, type ReviewStats } from "../lib/api";
import {
  Card,
  Confidence,
  Empty,
  SectionHeading,
  cx,
} from "../components/ui/primitives";

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
  const [busy, setBusy] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const [items, s] = await Promise.all([
      api.review(principal, filter),
      api.reviewStats(principal),
    ]);
    setPending(items);
    setStats(s);
    setLoading(false);
  }, [principal, filter]);

  useEffect(() => {
    void load();
  }, [load]);

  async function decide(key: string, decision: "accepted" | "rejected") {
    setBusy(key);
    try {
      await api.decide(principal, key, decision);
      setPending((current) => current.filter((p) => p.key !== key));
      onChanged();
      void api.reviewStats(principal).then(setStats);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      {stats && (
        <Card className="p-6">
          <div className="flex items-baseline justify-between mb-4">
            <p className="text-[13px] font-medium">{stats.pending} awaiting review</p>
            <div className="flex gap-1">
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
              {Object.entries(stats.accept_rate).map(([name, [accepted, decided]]) => {
                const rate = decided ? accepted / decided : 0;
                // 100% accepted means the threshold never discriminates.
                const theatre = decided >= 20 && rate === 1;
                return (
                  <div key={name} className="flex items-center gap-3 text-[11px]">
                    <span className="w-28 shrink-0 text-muted-foreground">{name}</span>
                    <span className="flex-1 h-1 rounded-full bg-black/5 dark:bg-white/10 overflow-hidden">
                      <span
                        className="block h-full bg-primary/60"
                        style={{ width: `${rate * 100}%` }}
                      />
                    </span>
                    <span className="font-mono text-muted-foreground/70 w-20 text-right">
                      {accepted}/{decided}
                    </span>
                    {theatre && (
                      <span className="text-[10px] text-muted-foreground/70 italic">
                        never rejects
                      </span>
                    )}
                  </div>
                );
              })}
              {Object.keys(stats.accept_rate).length === 0 && (
                <p className="text-[11px] text-muted-foreground/60">
                  Nothing decided yet — no calibration signal.
                </p>
              )}
            </div>
          </div>
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
        <div className="flex flex-col gap-3">
          {pending.map((item) => (
            <Card key={item.key} className="p-4 border-dashed">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <button
                      onClick={() => onOpenNode(item.node_id)}
                      className="text-[13px] font-medium truncate hover:underline"
                    >
                      {item.node_title}
                    </button>
                    <span className="text-[11px] font-mono text-muted-foreground/70">
                      {item.predicate}
                    </span>
                    <button
                      onClick={() => onOpenNode(item.object)}
                      className="text-[11px] font-mono text-primary hover:underline truncate"
                    >
                      {item.object}
                    </button>
                  </div>
                  {item.quote && (
                    <p className="mt-2 text-[13px] text-muted-foreground border-l-2 border-border/50 pl-3 italic">
                      “{item.quote}”
                    </p>
                  )}
                  <div className="mt-2">
                    <Confidence value={item.confidence} />
                  </div>
                </div>

                <div className="flex items-center gap-1 shrink-0">
                  <Action
                    label="Reject"
                    busy={busy === item.key}
                    onClick={() => decide(item.key, "rejected")}
                  >
                    <X className="w-4 h-4" strokeWidth={1.5} />
                  </Action>
                  <Action
                    label="Accept"
                    primary
                    busy={busy === item.key}
                    onClick={() => decide(item.key, "accepted")}
                  >
                    <Check className="w-4 h-4" strokeWidth={1.5} />
                  </Action>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

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
  primary,
  busy,
  onClick,
  children,
}: {
  label: string;
  primary?: boolean;
  busy?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      disabled={busy}
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
