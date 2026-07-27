/**
 * App shell — docs/DESIGN_SYSTEM.md §7.
 *
 * 260px sidebar, 56px topbar with breadcrumb, scrollable content. The
 * reference's Projects/Customers/Finance nav is generic SaaS filler; the IA
 * here is Ask / Review / Browse.
 *
 * The workspace switcher becomes a **principal switcher**, and it is
 * load-bearing rather than decoration: "view as contractor" is how the
 * permission model gets demonstrated at all.
 */

import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  Building2,
  ChevronDown,
  Inbox,
  Mail,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Send,
  Sun,
} from "lucide-react";

import { api, type Health, type Principal } from "./lib/api";
import { NODE_TYPES } from "./lib/nodeTypes";
import {
  Badge,
  Chevron,
  Disclosure,
  Row,
  SectionHeading,
  cx,
} from "./components/ui/primitives";
import { AskView } from "./views/AskView";
import { ReviewView } from "./views/ReviewView";
import { BrowseView } from "./views/BrowseView";
import { GmailView } from "./views/GmailView";
import { GraphView } from "./views/GraphView";
import { OutreachView } from "./views/OutreachView";
import { NodeDrawer } from "./views/NodeDrawer";

type View =
  | { kind: "ask" }
  | { kind: "review" }
  | { kind: "browse"; type: string }
  | { kind: "gmail" }
  | { kind: "graph" }
  | { kind: "outreach" };

export default function App() {
  const [principal, setPrincipal] = useState("ceo");
  const [principals, setPrincipals] = useState<Principal[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [view, setView] = useState<View>({ kind: "ask" });
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [browseOpen, setBrowseOpen] = useState(true);
  const [switcherOpen, setSwitcherOpen] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [outreachCount, setOutreachCount] = useState(0);
  const [openNode, setOpenNode] = useState<string | null>(null);
  const [dark, setDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches,
  );

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  const refreshCounts = useCallback(() => {
    api
      .reviewStats(principal)
      .then((s) => {
        setPendingCount(s.pending);
        // Its own badge as well as its share of the review count: outreach is
        // the only queue item that ends up addressed to a person, so "three
        // things need you" should not hide which one is the message.
        setOutreachCount(s.pending_outreach);
      })
      .catch(() => {
        setPendingCount(0);
        setOutreachCount(0);
      });
  }, [principal]);

  useEffect(() => {
    api.principals(principal).then(setPrincipals).catch(() => setPrincipals([]));
    api.health(principal).then(setHealth).catch(() => setHealth(null));
    refreshCounts();
  }, [principal, refreshCounts]);

  const current = principals.find((p) => p.id === principal);
  const openNodeCb = useCallback((id: string) => setOpenNode(id), []);

  const TITLES: Record<string, string> = {
    ask: "Ask",
    review: "Review",
    gmail: "Gmail",
    graph: "Graph",
    outreach: "Outreach",
  };
  // Only `browse` carries its own label; everything else is named by its kind.
  const breadcrumb =
    view.kind === "browse" ? view.type : (TITLES[view.kind] ?? view.kind);

  return (
    <div className="flex h-full bg-background text-foreground">
      <aside
        className={cx(
          "h-full shrink-0 overflow-hidden bg-card/50 border-r border-border/50",
          "transition-all duration-300 ease-in-out",
          sidebarOpen ? "w-[260px] opacity-100" : "w-0 opacity-0 border-none",
        )}
      >
        <div className="flex flex-col w-[260px] h-full p-3">
          <div className="relative">
            <div
              onClick={() => setSwitcherOpen((v) => !v)}
              className="flex items-center justify-between px-2 py-2 mb-4 rounded-lg
                         hover:bg-black/5 dark:hover:bg-white/5 cursor-pointer
                         transition-colors select-none group"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-8 h-8 rounded-[6px] bg-primary text-primary-foreground flex items-center justify-center font-semibold text-[13px] shadow-sm shrink-0">
                  {(current?.display ?? "?").charAt(0)}
                </div>
                <div className="flex flex-col overflow-hidden">
                  <span className="text-[13px] font-medium leading-none mb-1 text-foreground truncate max-w-[130px]">
                    {current?.display ?? "…"}
                  </span>
                  <span className="text-[11px] text-muted-foreground leading-none">
                    {current ? `${current.visible_sources} sources visible` : "loading"}
                  </span>
                </div>
              </div>
              <ChevronDown
                className="w-4 h-4 text-muted-foreground/50 group-hover:text-foreground/70 transition-colors shrink-0"
                strokeWidth={1.5}
              />
            </div>

            {switcherOpen && (
              <>
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setSwitcherOpen(false)}
                />
                <div className="absolute top-[52px] left-0 w-full bg-card border border-border/50 rounded-lg shadow-xl z-50 py-1 flex flex-col gap-0.5 animate-in">
                  {principals.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => {
                        setPrincipal(p.id);
                        setSwitcherOpen(false);
                      }}
                      className={cx(
                        "px-3 py-2 mx-1 text-[13px] rounded-md cursor-pointer transition-colors flex items-center justify-between",
                        p.id === principal
                          ? "bg-primary/10 text-primary font-medium"
                          : "text-foreground/80 hover:bg-black/5 dark:hover:bg-white/5",
                      )}
                    >
                      <span className="truncate">{p.display}</span>
                      <span className="text-[10px] font-mono text-muted-foreground/70 shrink-0">
                        {p.visible_sources}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>

          <nav className="flex-1 overflow-y-auto no-scrollbar flex flex-col gap-4 mt-2">
            <div className="flex flex-col gap-0.5">
              <Row
                active={view.kind === "ask"}
                onClick={() => setView({ kind: "ask" })}
                icon={<Icon of={Search} active={view.kind === "ask"} />}
              >
                Ask
              </Row>
              <Row
                active={view.kind === "review"}
                onClick={() => setView({ kind: "review" })}
                icon={<Icon of={Inbox} active={view.kind === "review"} />}
                trailing={pendingCount > 0 ? <Badge>{pendingCount}</Badge> : undefined}
              >
                Review
              </Row>
              <Row
                active={view.kind === "outreach"}
                onClick={() => setView({ kind: "outreach" })}
                icon={<Icon of={Send} active={view.kind === "outreach"} />}
                trailing={outreachCount > 0 ? <Badge>{outreachCount}</Badge> : undefined}
              >
                Outreach
              </Row>
              <Row
                active={view.kind === "gmail"}
                onClick={() => setView({ kind: "gmail" })}
                icon={<Icon of={Mail} active={view.kind === "gmail"} />}
              >
                Gmail
              </Row>
            </div>

            <div className="flex flex-col gap-0.5">
              <SectionHeading>Browse</SectionHeading>
              <Row
                active={view.kind === "graph"}
                onClick={() => setView({ kind: "graph" })}
                icon={<Icon of={Building2} active={view.kind === "graph"} />}
              >
                Graph
              </Row>
              <Row
                onClick={() => setBrowseOpen((v) => !v)}
                icon={<Icon of={Building2} active={false} />}
                trailing={<Chevron open={browseOpen} />}
              >
                Nodes by Type
              </Row>
              <Disclosure open={browseOpen}>
                <div className="relative">
                  <div
                    className="absolute top-0 bottom-0 border-l border-black/5 dark:border-white/5"
                    style={{ left: "17.5px" }}
                  />
                  {NODE_TYPES.map(({ type, label, icon }) => (
                    <Row
                      key={type}
                      indent={1}
                      active={view.kind === "browse" && view.type === type}
                      onClick={() => setView({ kind: "browse", type })}
                      icon={
                        <Icon
                          of={icon}
                          active={view.kind === "browse" && view.type === type}
                        />
                      }
                    >
                      {label}
                    </Row>
                  ))}
                </div>
              </Disclosure>
            </div>
          </nav>

          <div className="mt-auto pt-4 border-t border-border/50 flex flex-col gap-0.5">
            <Row
              onClick={() => setDark((v) => !v)}
              icon={<Icon of={dark ? Sun : Moon} active={false} />}
            >
              {dark ? "Light mode" : "Dark mode"}
            </Row>
            <div className="px-2.5 pt-2 text-[10px] leading-relaxed text-muted-foreground/50">
              {health ? (
                <>
                  {health.nodes} nodes · {health.chunks} chunks
                  <br />
                  <span title={health.providers}>
                    {health.offline ? "offline providers" : "live providers"}
                  </span>
                </>
              ) : (
                "api unreachable"
              )}
            </div>
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0 bg-black/[0.02] dark:bg-white/[0.02]">
        <header className="h-14 shrink-0 border-b border-border/50 bg-card flex items-center px-4 justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="p-1.5 rounded-md text-muted-foreground hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground transition-colors"
              aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
            >
              {sidebarOpen ? (
                <PanelLeftClose className="w-[18px] h-[18px]" strokeWidth={1.5} />
              ) : (
                <PanelLeftOpen className="w-[18px] h-[18px]" strokeWidth={1.5} />
              )}
            </button>
            <div className="flex items-center gap-2 text-sm text-muted-foreground min-w-0">
              <span className="truncate">{current?.display ?? "company_brain"}</span>
              <span>/</span>
              <span className="font-medium text-foreground truncate">{breadcrumb}</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground/70">
            <Activity className="w-3.5 h-3.5" strokeWidth={1.5} />
            {health?.offline === false ? "live" : "offline"}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto no-scrollbar p-6 md:p-8">
          {view.kind === "ask" && (
            <AskView principal={principal} onOpenNode={openNodeCb} />
          )}
          {view.kind === "review" && (
            <ReviewView
              principal={principal}
              onChanged={refreshCounts}
              onOpenNode={openNodeCb}
            />
          )}
          {view.kind === "outreach" && (
            <OutreachView
              principal={principal}
              onChanged={refreshCounts}
              onOpenNode={openNodeCb}
            />
          )}
          {view.kind === "browse" && (
            <BrowseView principal={principal} type={view.type} onOpenNode={openNodeCb} />
          )}
          {view.kind === "graph" && current && (
            <GraphView principal={current} />
          )}
          {view.kind === "gmail" && <GmailView />}
        </main>
      </div>

      {openNode && (
        <NodeDrawer
          principal={principal}
          nodeId={openNode}
          onClose={() => setOpenNode(null)}
          onOpenNode={openNodeCb}
        />
      )}
    </div>
  );
}

function Icon({ of: Component, active }: { of: React.ElementType; active: boolean }) {
  return (
    <Component
      className={cx(
        "w-[16px] h-[16px] transition-colors shrink-0",
        active
          ? "text-foreground"
          : "text-muted-foreground/70 group-hover:text-foreground/70",
      )}
      strokeWidth={1.5}
    />
  );
}
