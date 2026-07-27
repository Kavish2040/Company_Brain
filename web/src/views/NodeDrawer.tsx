/**
 * Node detail.
 *
 * Renders the ACL-projected node the server returned — never stored bytes
 * (§6.3). A node the principal cannot see 404s, and this shows a genuine
 * not-found rather than an empty page, because an empty page confirms the node
 * exists.
 */

import { useEffect, useState } from "react";
import { FileQuestion, Loader2, X } from "lucide-react";

import { api, ApiError, type NodeDetail } from "../lib/api";
import {
  Confidence,
  Empty,
  ProvenanceBadge,
  SectionHeading,
  Sensitivity,
  StatusMark,
} from "../components/ui/primitives";

export function NodeDrawer({
  principal,
  nodeId,
  onClose,
  onOpenNode,
}: {
  principal: string;
  nodeId: string;
  onClose: () => void;
  onOpenNode: (id: string) => void;
}) {
  const [node, setNode] = useState<NodeDetail | null>(null);
  const [missing, setMissing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setMissing(false);
    setNode(null);
    api
      .node(principal, nodeId)
      .then(setNode)
      .catch((e) => setMissing(e instanceof ApiError && e.status === 404))
      .finally(() => setLoading(false));
  }, [principal, nodeId]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-background/40 backdrop-blur-sm fade-in" onClick={onClose} />
      <aside className="relative w-full max-w-xl h-full bg-card border-l border-border/50 shadow-2xl overflow-y-auto no-scrollbar animate-in">
        <header className="sticky top-0 h-14 px-4 flex items-center justify-between bg-card border-b border-border/50">
          <span className="text-[11px] font-mono text-muted-foreground/60 truncate">{nodeId}</span>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-muted-foreground/70 hover:bg-black/5 dark:hover:bg-white/10 hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X className="w-[18px] h-[18px]" strokeWidth={1.5} />
          </button>
        </header>

        {loading && (
          <Empty icon={<Loader2 className="w-6 h-6 animate-spin" strokeWidth={1.5} />}>
            Loading…
          </Empty>
        )}

        {missing && (
          <Empty icon={<FileQuestion className="w-6 h-6" strokeWidth={1.5} />}>
            Not found, or not visible to you.
          </Empty>
        )}

        {node && (
          <div className="p-6 flex flex-col gap-6">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[10px] font-medium rounded-full bg-primary/10 text-primary px-1.5 h-5 inline-flex items-center">
                  {node.type}
                </span>
                <Sensitivity tier={node.sensitivity} />
              </div>
              <h2 className="text-[17px] font-medium">{node.title}</h2>
            </div>

            {node.relations.length > 0 && (
              <div>
                <SectionHeading>Relations</SectionHeading>
                <div className="flex flex-col gap-2 mt-2">
                  {node.relations.map((r) => (
                    <div
                      key={`${r.predicate}:${r.object}`}
                      className="flex items-center gap-2 flex-wrap text-[13px]"
                    >
                      <span className="font-mono text-[11px] text-muted-foreground w-28 shrink-0">
                        {r.predicate}
                      </span>
                      <button
                        onClick={() => onOpenNode(r.object)}
                        className="text-primary hover:underline truncate"
                      >
                        {r.object_title}
                      </button>
                      <ProvenanceBadge value={r.provenance} />
                      <StatusMark status={r.status} />
                      <Confidence value={r.confidence} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {node.body && (
              <div>
                <SectionHeading>Content</SectionHeading>
                <pre className="mt-2 text-[13px] leading-relaxed whitespace-pre-wrap font-sans text-muted-foreground">
                  {node.body}
                </pre>
              </div>
            )}
          </div>
        )}
      </aside>
    </div>
  );
}
