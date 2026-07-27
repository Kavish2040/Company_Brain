/**
 * Browse — one node type at a time.
 *
 * The list is whatever the server returned; the client applies no permission
 * logic (invariant 17). Switching principal genuinely changes what appears
 * here, which is the point.
 */

import { useEffect, useMemo, useState } from "react";
import { Loader2, Search, SearchX } from "lucide-react";

import { api, type NodeSummary } from "../lib/api";
import { Card, Empty, Row } from "../components/ui/primitives";

export function BrowseView({
  principal,
  type,
  onOpenNode,
}: {
  principal: string;
  type: string;
  onOpenNode: (id: string) => void;
}) {
  const [nodes, setNodes] = useState<NodeSummary[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .nodes(principal, type)
      .then(setNodes)
      .catch(() => setNodes([]))
      .finally(() => setLoading(false));
  }, [principal, type]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? nodes.filter((n) => n.title.toLowerCase().includes(q)) : nodes;
  }, [nodes, query]);

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-4">
      <Card className="flex items-center px-4">
        <Search className="w-[18px] h-[18px] text-muted-foreground/70 mr-3 shrink-0" strokeWidth={1.5} />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Filter ${type.toLowerCase()}…`}
          className="flex-1 bg-transparent py-3 outline-none text-[13px] placeholder:text-muted-foreground/50"
        />
        <span className="text-[11px] font-mono text-muted-foreground/60">
          {filtered.length}
        </span>
      </Card>

      {loading ? (
        <Empty icon={<Loader2 className="w-6 h-6 animate-spin" strokeWidth={1.5} />}>
          Loading…
        </Empty>
      ) : filtered.length === 0 ? (
        <Empty icon={<SearchX className="w-6 h-6" strokeWidth={1.5} />}>
          Nothing visible here.
        </Empty>
      ) : (
        <Card className="p-2 flex flex-col gap-0.5">
          {filtered.map((node) => (
            <Row
              key={node.id}
              onClick={() => onOpenNode(node.id)}
              trailing={
                <span className="text-[10px] font-mono text-muted-foreground/50 truncate max-w-[220px]">
                  {node.id}
                </span>
              }
            >
              {node.title}
            </Row>
          ))}
        </Card>
      )}
    </div>
  );
}
