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

import { useState, type FormEvent } from "react";
import { AlertTriangle, CornerDownLeft, Loader2, Search, ShieldOff } from "lucide-react";

import { api, ApiError, type AskResult } from "../lib/api";
import { Card, CitationChip, Empty, cx } from "../components/ui/primitives";

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
