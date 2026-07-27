/**
 * Node detail.
 *
 * Renders the ACL-projected node the server returned — never stored bytes
 * (§6.3). A node the principal cannot see 404s, and this shows a genuine
 * not-found rather than an empty page, because an empty page confirms the node
 * exists.
 */

import { useEffect, useRef, useState } from "react";
import {
  Eye,
  FileQuestion,
  Loader2,
  Mail,
  PenLine,
  ShieldAlert,
  X,
} from "lucide-react";

import { api, ApiError, type NodeDetail, type Outreach } from "../lib/api";
import { useCollab } from "../lib/collab";
import {
  Confidence,
  Empty,
  PresenceStack,
  ProvenanceBadge,
  RemoteCarets,
  SectionHeading,
  Sensitivity,
  StatusMark,
  cx,
} from "../components/ui/primitives";

/**
 * Shared by the textarea and the caret mirrors. They must agree exactly — the
 * mirror positions carets by laying out the same text in the same box, so any
 * divergence in font, size, padding, or wrapping puts the caret in the wrong
 * place.
 */
const EDITOR_TEXT =
  "text-[13px] leading-relaxed font-sans whitespace-pre-wrap break-words p-3";

/** Connection state, stated rather than implied — an editor that has silently
 *  stopped syncing is the worst version of this feature. */
function LiveBadge({ status }: { status: string }) {
  const label =
    status === "live" ? "Live" : status === "connecting" ? "Connecting…" : "Reconnecting…";
  return (
    <span className="inline-flex items-center gap-1.5 text-[10px] text-muted-foreground/70">
      <span
        className={cx(
          "w-1.5 h-1.5 rounded-full",
          status === "live" ? "bg-primary" : "bg-black/20 dark:bg-white/20",
        )}
      />
      {label}
    </span>
  );
}

/**
 * Draft outreach from this node.
 *
 * The button says "Draft outreach", not "Send" — because that is what it does.
 * Drafting queues a message for review; approving it in the Review view still
 * does not send it; dispatch is a third act. Labelling the first step "send"
 * would be the interface lying about which of those three has happened, on the
 * one surface in this app that can result in contacting a real person.
 */
function OutreachActions({
  node,
  drafted,
  drafting,
  error,
  onDraft,
}: {
  node: NodeDetail;
  drafted: Outreach | null;
  drafting: boolean;
  error: string | null;
  onDraft: () => void;
}) {
  return (
    <div>
      <SectionHeading>Outreach</SectionHeading>
      <div className="mt-2 flex flex-col gap-2">
        {!drafted && (
          <button
            onClick={onDraft}
            disabled={drafting}
            className="inline-flex items-center justify-center gap-2 h-8 px-3 rounded-[6px]
                       text-[13px] font-medium border border-border/50 text-muted-foreground
                       hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground
                       transition-colors disabled:opacity-40"
          >
            {drafting ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" strokeWidth={1.5} />
            ) : (
              <Mail className="w-3.5 h-3.5" strokeWidth={1.5} />
            )}
            Draft outreach to {node.title}
          </button>
        )}

        {error && (
          <p
            className="px-3 py-2 rounded-lg text-[12px] text-muted-foreground
                       border border-dashed border-border/50 bg-black/5 dark:bg-white/5"
          >
            {error}
          </p>
        )}

        {drafted && (
          <div className="rounded-lg border border-dashed border-border/50 p-3 flex flex-col gap-2">
            <p className="text-[13px] font-medium">{drafted.subject}</p>
            <pre className="text-[12px] leading-relaxed whitespace-pre-wrap font-sans text-muted-foreground">
              {drafted.body}
            </pre>
            <p className="text-[11px] text-muted-foreground/70 pt-2 border-t border-border/50">
              Queued for review — nothing has been sent.
              {drafted.lead?.email
                ? ` Lead ${drafted.lead.email} via ${drafted.lead_source}.`
                : ` No contact details (lead source: ${drafted.lead_source}).`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

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
  const [editing, setEditing] = useState(false);
  const [drafted, setDrafted] = useState<Outreach | null>(null);
  const [drafting, setDrafting] = useState(false);
  const [draftError, setDraftError] = useState<string | null>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);

  const collab = useCollab(nodeId, principal, editing);
  const remote = collab.participants.filter((p) => p.connection !== collab.connection);

  useEffect(() => {
    setLoading(true);
    setMissing(false);
    setNode(null);
    setEditing(false); // a new node starts read-only
    setDrafted(null);
    setDraftError(null);
    api
      .node(principal, nodeId)
      .then(setNode)
      .catch((e) => setMissing(e instanceof ApiError && e.status === 404))
      .finally(() => setLoading(false));
  }, [principal, nodeId]);

  async function draftOutreach() {
    if (drafting) return;
    setDrafting(true);
    setDraftError(null);
    try {
      setDrafted(await api.outreachDraft(principal, nodeId));
    } catch (exc) {
      setDraftError(
        exc instanceof ApiError ? exc.message : "the draft did not land",
      );
    } finally {
      setDrafting(false);
    }
  }

  const reportCursor = () => {
    const element = textarea.current;
    if (element) collab.moveCursor(element.selectionStart, element.selectionEnd);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-background/40 backdrop-blur-sm fade-in" onClick={onClose} />
      <aside className="relative w-full max-w-xl h-full bg-card border-l border-border/50 shadow-2xl overflow-y-auto no-scrollbar animate-in">
        <header className="sticky top-0 z-10 h-14 px-4 flex items-center justify-between gap-3 bg-card border-b border-border/50">
          <span className="text-[11px] font-mono text-muted-foreground/60 truncate">{nodeId}</span>
          <div className="flex items-center gap-2 shrink-0">
            {editing && <PresenceStack participants={remote} />}
            {node && (
              <button
                onClick={() => setEditing((on) => !on)}
                className={cx(
                  "inline-flex items-center gap-1.5 h-7 px-2 rounded-[6px] text-[11px] font-medium",
                  "transition-colors",
                  editing
                    ? "bg-black/5 dark:bg-white/10 text-foreground"
                    : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground",
                )}
              >
                {editing ? (
                  <Eye className="w-3.5 h-3.5" strokeWidth={1.5} />
                ) : (
                  <PenLine className="w-3.5 h-3.5" strokeWidth={1.5} />
                )}
                {editing ? "Done" : "Edit"}
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 rounded-md text-muted-foreground/70 hover:bg-black/5 dark:hover:bg-white/10 hover:text-foreground transition-colors"
              aria-label="Close"
            >
              <X className="w-[18px] h-[18px]" strokeWidth={1.5} />
            </button>
          </div>
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

            {/* Outreach addresses a person, so the action only exists on one.
                Restricted nodes keep the button and are refused by the server
                — the UI never makes the access decision (invariant 17), and a
                hidden button would teach the reader the wrong rule. */}
            {(node.type === "Person" || node.type === "Account") && (
              <OutreachActions
                node={node}
                drafted={drafted}
                drafting={drafting}
                error={draftError}
                onDraft={draftOutreach}
              />
            )}

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

            {(node.body || editing) && (
              <div>
                <div className="flex items-center justify-between">
                  <SectionHeading>Content</SectionHeading>
                  {editing && <LiveBadge status={collab.status} />}
                </div>

                {!editing ? (
                  <pre className="mt-2 text-[13px] leading-relaxed whitespace-pre-wrap font-sans text-muted-foreground">
                    {node.body}
                  </pre>
                ) : collab.status === "denied" ? (
                  <Empty icon={<ShieldAlert className="w-6 h-6" strokeWidth={1.5} />}>
                    You can't edit this node.
                  </Empty>
                ) : (
                  <>
                    {collab.rejected && (
                      // Invariant 13, inverted: generated regions are the
                      // machine's. A refused edit is a designed state, not a toast.
                      <p
                        className="mt-2 px-3 py-2 rounded-lg text-[11px] text-muted-foreground
                                   border border-dashed border-border/50 bg-black/5 dark:bg-white/5"
                      >
                        {collab.rejected}
                      </p>
                    )}
                    <div className="relative mt-2 rounded-lg border border-border/50 bg-black/5 dark:bg-white/5">
                      <textarea
                        ref={textarea}
                        value={collab.body}
                        spellCheck={false}
                        onChange={(e) => {
                          collab.edit(e.target.value);
                          reportCursor();
                        }}
                        onSelect={reportCursor}
                        onKeyUp={reportCursor}
                        onClick={reportCursor}
                        className={cx(
                          EDITOR_TEXT,
                          "relative block w-full min-h-[240px] bg-transparent",
                          "text-foreground resize-y outline-none",
                        )}
                      />
                      <RemoteCarets
                        body={collab.body}
                        participants={remote}
                        textClass={cx(EDITOR_TEXT, "block w-full")}
                      />
                    </div>
                    <p className="mt-1.5 text-[11px] text-muted-foreground/50">
                      Saves itself. Generated regions are read-only.
                    </p>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </aside>
    </div>
  );
}
