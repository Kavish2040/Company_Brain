/**
 * Ask — the primary surface.
 *
 * Two rules from CLAUDE.md bind this view:
 *   17. it never filters by permission; the server returns projected data
 *   11. an uncited answer is an ERROR with its own designed state, never
 *       rendered as ordinary prose
 *
 * Claims are split into asserted (a document says this) and inferred (reached
 * by traversal), because the §11 gates make that distinction load-bearing —
 * flattening the two is exactly the mention-to-ownership drift they exist to
 * prevent.
 */

import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import {
  AlertTriangle,
  Clock,
  CornerDownLeft,
  Eye,
  EyeOff,
  Loader2,
  Network,
  Search,
  ShieldOff,
  type LucideIcon,
} from "lucide-react";

import { api, ApiError, type AskResult, type Overview, type OverviewNode } from "../lib/api";
import { iconFor, labelFor, orderTypes } from "../lib/nodeTypes";
import {
  Card,
  CitationChip,
  Empty,
  Row,
  Sensitivity,
  cx,
} from "../components/ui/primitives";

const SUGGESTIONS = [
  "who owns vendor renewals?",
  "where do Support and Engineering hand off?",
  "what is Project Snowflake?",
  "who is responsible for incident response?",
];

export function AskView({
  principal,
  onOpenNode,
}: {
  principal: string;
  onOpenNode: (id: string) => void;
}) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AskResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function run(q: string) {
    if (!q.trim() || busy) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.ask(principal, q));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void run(question);
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      <form onSubmit={onSubmit}>
        <Card className="flex items-center px-4">
          <Search
            className="w-[18px] h-[18px] text-muted-foreground/70 mr-3 shrink-0"
            strokeWidth={1.5}
          />
          <input
            autoFocus
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about people, processes, ownership, handoffs…"
            className="flex-1 bg-transparent py-4 outline-none text-[14px] text-foreground placeholder:text-muted-foreground/50"
          />
          <button
            type="submit"
            disabled={busy || !question.trim()}
            className="ml-2 p-1.5 rounded-md text-muted-foreground/70 hover:bg-black/5 dark:hover:bg-white/10 hover:text-foreground transition-colors disabled:opacity-40"
            aria-label="Ask"
          >
            {busy ? (
              <Loader2 className="w-[18px] h-[18px] animate-spin" strokeWidth={1.5} />
            ) : (
              <CornerDownLeft className="w-[18px] h-[18px]" strokeWidth={1.5} />
            )}
          </button>
        </Card>
      </form>

      {!result && !error && !busy && (
        <>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => {
                  setQuestion(s);
                  void run(s);
                }}
                className="px-3 py-1.5 text-[13px] rounded-lg border border-border/50 text-muted-foreground
                           hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
          <Landing principal={principal} onOpenNode={onOpenNode} />
        </>
      )}

      {error && (
        <Card className="p-4 flex items-start gap-3">
          <ShieldOff className="w-[18px] h-[18px] text-muted-foreground/70 mt-0.5 shrink-0" strokeWidth={1.5} />
          <div>
            <p className="text-[13px] font-medium">Request refused</p>
            <p className="text-[13px] text-muted-foreground mt-1">{error}</p>
          </div>
        </Card>
      )}

      {result?.refused && (
        /* Invariant 11: not a degraded answer — a designed error state. */
        <Card className="p-4 flex items-start gap-3 border-dashed">
          <AlertTriangle className="w-[18px] h-[18px] text-muted-foreground/70 mt-0.5 shrink-0" strokeWidth={1.5} />
          <div>
            <p className="text-[13px] font-medium">Answer withheld — failed citation check</p>
            <p className="text-[13px] text-muted-foreground mt-1">{result.refused}</p>
            <p className="text-[11px] text-muted-foreground/70 mt-2">
              An uncited claim is a bug, not a lower-quality answer, so nothing is shown.
            </p>
          </div>
        </Card>
      )}

      {result?.insufficient_evidence && (
        <Empty icon={<Search className="w-6 h-6" strokeWidth={1.5} />}>
          {result.text}
        </Empty>
      )}

      {result && !result.refused && !result.insufficient_evidence && (
        <>
          <Card className="p-6 flex flex-col gap-4">
            <ClaimList title="Asserted" claims={result.asserted} onOpenNode={onOpenNode} />
            <ClaimList
              title="Inferred"
              claims={result.inferred}
              onOpenNode={onOpenNode}
              muted
            />
          </Card>

          {result.citations.length > 0 && (
            <Card className="p-6">
              <p className="text-[11px] font-semibold tracking-wider text-muted-foreground/50 uppercase mb-3">
                Sources
              </p>
              <div className="flex flex-col gap-3">
                {result.citations.map((c) => (
                  <button
                    key={c.node_id}
                    onClick={() => onOpenNode(c.node_id)}
                    className="text-left rounded-lg p-3 -m-1 hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
                  >
                    <p className="text-[13px] font-medium truncate">{c.title}</p>
                    <p className="text-[11px] font-mono text-muted-foreground/60 truncate">
                      {c.node_id}
                    </p>
                  </button>
                ))}
              </div>
            </Card>
          )}

          <p className="text-[11px] text-muted-foreground/60 text-center">
            {result.seed_count} matched · {result.expanded_count} reached by traversal
            {result.withheld_by_acl > 0 && (
              <> · {result.withheld_by_acl} withheld by permissions</>
            )}
          </p>
        </>
      )}
    </div>
  );
}

/* ---- the empty state --------------------------------------------------- *
 *
 * A search box over nothing asks the reader to guess what is in there. This
 * shows them instead: the entities the graph is densest around, what changed
 * most recently, and the edges of their own permissions — the last one because
 * a contractor looking at eleven visible nodes has no way to tell a small
 * company from a narrow grant, and the honest answer is to say which it is.
 *
 * Nothing here filters (invariant 17); `/api/overview` returns one principal's
 * projection and this renders it.
 */

function Landing({
  principal,
  onOpenNode,
}: {
  principal: string;
  onOpenNode: (id: string) => void;
}) {
  const [data, setData] = useState<Overview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let live = true;
    setLoading(true);
    api
      .overview(principal)
      .then((d) => live && setData(d))
      .catch(() => live && setData(null))
      .finally(() => live && setLoading(false));
    return () => {
      live = false;
    };
  }, [principal]);

  if (loading) return <LandingSkeleton />;
  // The box still works without this; a failed overview should not stand in
  // front of it with an error.
  if (!data) return null;

  return (
    <div className="flex flex-col gap-6">
      <p className="text-[11px] text-muted-foreground/60 px-1">
        {data.nodes} nodes · {data.edges} edges · {data.sources.length}{" "}
        {data.sources.length === 1 ? "source" : "sources"} visible to you
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        <Panel title="Most connected" icon={Network}>
          {data.connected.length === 0 ? (
            <Quiet>No entities are visible to you yet.</Quiet>
          ) : (
            data.connected.map((n) => (
              <NodeRow
                key={n.id}
                node={n}
                onOpenNode={onOpenNode}
                trailing={
                  <span
                    className="text-[10px] font-mono text-muted-foreground/50"
                    title={`${n.degree} visible edges`}
                  >
                    {n.degree}
                  </span>
                }
              />
            ))
          )}
        </Panel>

        <Panel title="Recently changed" icon={Clock}>
          {data.recent.length === 0 ? (
            <Quiet>Nothing here carries a source date.</Quiet>
          ) : (
            data.recent.map((n) => (
              <NodeRow
                key={n.id}
                node={n}
                onOpenNode={onOpenNode}
                trailing={
                  <span className="text-[10px] font-mono text-muted-foreground/50">
                    {/* The source artifact's own date — never ingest time
                        (invariant 4). Sliced rather than localised so it reads
                        the same in every locale the demo lands in. */}
                    {(n.modified ?? "").slice(0, 10)}
                  </span>
                }
              />
            ))
          )}
        </Panel>
      </div>

      <Panel title="What you can see" icon={Eye}>
        {/* Driven by the response, not by the sidebar's six rows: a type the
            Browse nav has not caught up with still has to be counted, or the
            breakdown stops summing to the total above it. */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-4">
          {orderTypes(Object.keys(data.by_type)).map((type) => {
            const TypeIcon = iconFor(type);
            return (
              <div key={type} className="flex items-center gap-2.5 px-2.5 py-[7px] min-w-0">
                <TypeIcon
                  className="w-[16px] h-[16px] text-muted-foreground/70 shrink-0"
                  strokeWidth={1.5}
                />
                <span className="text-[13px] text-muted-foreground truncate">
                  {labelFor(type)}
                </span>
                <span className="ml-auto text-[10px] font-mono text-muted-foreground/50 shrink-0">
                  {data.by_type[type]}
                </span>
              </div>
            );
          })}
        </div>

        <div className="border-t border-border/50 my-2" />

        {data.sources.map((s) => (
          <div key={s.ref} className="flex items-center gap-2.5 px-2.5 py-[7px] min-w-0">
            <span className="text-[11px] font-mono text-muted-foreground truncate">
              {s.ref}
            </span>
            <span className="ml-auto flex items-center gap-2 shrink-0">
              {s.ceiling ? <Sensitivity tier={s.ceiling} /> : null}
              <span className="text-[10px] font-mono text-muted-foreground/50">
                {s.nodes}
              </span>
            </span>
          </div>
        ))}

        {/* Dashed and dimmed — the §6 "not settled fact" idiom, reused for
            "not yours to read". */}
        {data.withheld_sources > 0 || data.withheld_nodes > 0 ? (
          <div className="flex items-center gap-2.5 mt-2 px-2.5 py-2 rounded-lg border border-dashed border-border/50">
            <EyeOff
              className="w-[16px] h-[16px] text-muted-foreground/50 shrink-0"
              strokeWidth={1.5}
            />
            <span className="text-[13px] text-muted-foreground/70">
              {data.withheld_sources}{" "}
              {data.withheld_sources === 1 ? "source" : "sources"} and{" "}
              {data.withheld_nodes} nodes sit outside your grants.
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2.5 mt-2 px-2.5 py-2">
            <span className="text-[13px] text-muted-foreground/70">
              Nothing in this store is hidden from you.
            </span>
          </div>
        )}
      </Panel>
    </div>
  );
}

function Panel({
  title,
  icon: Icon,
  children,
}: {
  title: string;
  icon: LucideIcon;
  children: ReactNode;
}) {
  return (
    <Card className="p-2 flex flex-col">
      <div className="flex items-center gap-2 px-2.5 pt-1.5 pb-2">
        <Icon className="w-3.5 h-3.5 text-muted-foreground/50 shrink-0" strokeWidth={1.5} />
        <span className="text-[11px] font-semibold tracking-wider text-muted-foreground/50 uppercase">
          {title}
        </span>
      </div>
      {children}
    </Card>
  );
}

function NodeRow({
  node,
  onOpenNode,
  trailing,
}: {
  node: OverviewNode;
  onOpenNode: (id: string) => void;
  trailing: ReactNode;
}) {
  const TypeIcon = iconFor(node.type);
  return (
    <Row
      onClick={() => onOpenNode(node.id)}
      icon={
        <TypeIcon
          className="w-[16px] h-[16px] text-muted-foreground/70 group-hover:text-foreground/70 transition-colors shrink-0"
          strokeWidth={1.5}
        />
      }
      trailing={
        <>
          {/* §6: a node's tier is visible wherever its content is. */}
          <Sensitivity tier={node.sensitivity} />
          {trailing}
        </>
      }
    >
      {node.title}
    </Row>
  );
}

function Quiet({ children }: { children: ReactNode }) {
  return (
    <p className="px-2.5 py-[7px] text-[13px] text-muted-foreground/50">{children}</p>
  );
}

/** Inert placeholder blocks in the fill idiom — no pulse, nothing moves. */
function LandingSkeleton() {
  return (
    <div className="flex flex-col gap-6" aria-hidden>
      <div className="h-3 w-52 mx-1 rounded-[4px] bg-black/5 dark:bg-white/5" />
      <div className="grid md:grid-cols-2 gap-6">
        {[0, 1].map((panel) => (
          <Card key={panel} className="p-2 flex flex-col gap-0.5">
            <div className="h-3 w-24 m-2.5 rounded-[4px] bg-black/5 dark:bg-white/5" />
            {[0, 1, 2, 3, 4, 5, 6, 7].map((row) => (
              <div key={row} className="h-[30px] mx-1 rounded-[6px] bg-black/5 dark:bg-white/5" />
            ))}
          </Card>
        ))}
      </div>
    </div>
  );
}

function ClaimList({
  title,
  claims,
  onOpenNode,
  muted,
}: {
  title: string;
  claims: string[];
  onOpenNode: (id: string) => void;
  muted?: boolean;
}) {
  if (claims.length === 0) return null;
  return (
    <div>
      <p className="text-[11px] font-semibold tracking-wider text-muted-foreground/50 uppercase mb-2">
        {title}
      </p>
      <div className="flex flex-col gap-2">
        {claims.map((claim, i) => (
          <p
            key={i}
            className={cx(
              "text-[13px] leading-relaxed",
              muted ? "text-muted-foreground" : "text-foreground",
            )}
          >
            <Claim text={claim} onOpenNode={onOpenNode} />
          </p>
        ))}
      </div>
    </div>
  );
}

/** Renders `[[node_id]]` markers as citation chips, leaving prose intact. */
function Claim({
  text,
  onOpenNode,
}: {
  text: string;
  onOpenNode: (id: string) => void;
}) {
  const parts = text.replace(/^[-*]\s*/, "").split(/(\[\[[^\]]+\]\])/g);
  return (
    <>
      {parts.map((part, i) => {
        const match = /^\[\[([^\]|]+)(?:\|[^\]]*)?\]\]$/.exec(part);
        if (!match) return <span key={i}>{part}</span>;
        return <CitationChip key={i} nodeId={match[1]} onOpen={onOpenNode} />;
      })}
    </>
  );
}
