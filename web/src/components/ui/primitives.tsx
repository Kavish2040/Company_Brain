/**
 * Design-system primitives — docs/DESIGN_SYSTEM.md.
 *
 * The signature traits, all in one place so they can't drift:
 *   border-border/50 · bg-black/5 dark:bg-white/5 for hover and fill
 *   lucide at strokeWidth 1.5 · 13px body, 11px uppercase headings
 *   shadow-sm / shadow-xl / shadow-2xl only · nothing animates past 300ms
 *
 * §6 extensions live here too — citation chips, confidence, provenance,
 * proposed-vs-accepted, sensitivity. Deliberately not colour-only: the palette
 * has no semantic red/amber/green, and colour alone fails accessibility.
 */

import type { ReactNode } from "react";
import { ChevronRight, Lock, ShieldAlert } from "lucide-react";

export function cx(...parts: (string | false | null | undefined)[]) {
  return parts.filter(Boolean).join(" ");
}

/* ---- surfaces ---------------------------------------------------------- */

export function Card({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cx(
        "rounded-xl border border-border/50 bg-card shadow-sm",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function SectionHeading({ children }: { children: ReactNode }) {
  return (
    <span className="px-2.5 mb-1 text-[11px] font-semibold tracking-wider text-muted-foreground/50 uppercase">
      {children}
    </span>
  );
}

export function Empty({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-2">
      <div className="text-muted-foreground/30">{icon}</div>
      <p className="text-[13px] text-muted-foreground font-medium">{children}</p>
    </div>
  );
}

/* ---- §6 extensions ------------------------------------------------------ */

export function CitationChip({
  nodeId,
  title,
  onOpen,
}: {
  nodeId: string;
  title?: string;
  onOpen?: (id: string) => void;
}) {
  const label = nodeId.split("/").pop() ?? nodeId;
  return (
    <button
      type="button"
      title={title ?? nodeId}
      onClick={() => onOpen?.(nodeId)}
      className="inline-flex items-center h-5 px-1.5 mx-0.5 align-baseline text-[10px] font-medium font-mono
                 text-muted-foreground/80 bg-black/5 dark:bg-white/5
                 border border-border/50 rounded-[4px] transition-colors
                 hover:text-foreground hover:bg-black/10 dark:hover:bg-white/10"
    >
      {label}
    </button>
  );
}

/**
 * Confidence. A three-step bar plus the numeral — never colour alone, and never
 * a traffic light: the palette has no semantic red/amber/green (§6).
 */
export function Confidence({ value }: { value: number }) {
  const steps = value >= 0.85 ? 3 : value >= 0.6 ? 2 : 1;
  return (
    <span className="inline-flex items-center gap-1" title={`confidence ${value.toFixed(2)}`}>
      <span className="flex gap-px" aria-hidden>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className={cx(
              "block w-1 h-3 rounded-[1px]",
              i < steps ? "bg-primary/70" : "bg-black/10 dark:bg-white/10",
            )}
          />
        ))}
      </span>
      <span className="text-[10px] font-mono text-muted-foreground/70">
        {value.toFixed(2)}
      </span>
    </span>
  );
}

/** structural | llm | human — where a fact came from matters to the reader. */
export function ProvenanceBadge({ value }: { value: string }) {
  return (
    <span
      className="inline-flex items-center h-5 px-1.5 text-[10px] font-medium rounded-full
                 bg-primary/10 text-primary"
    >
      {value}
    </span>
  );
}

/** Proposed edges are never rendered as settled fact (§6). */
export function StatusMark({ status }: { status: string }) {
  if (status === "accepted") return null;
  return (
    <span
      className="inline-flex items-center h-5 px-1.5 text-[10px] font-medium rounded-full
                 border border-dashed border-border/50 text-muted-foreground/70"
    >
      {status}
    </span>
  );
}

export function Sensitivity({ tier }: { tier: string }) {
  if (tier === "public") return null;
  const Icon = tier === "restricted" ? ShieldAlert : Lock;
  return (
    <span
      className="inline-flex items-center gap-1 text-[10px] text-muted-foreground/70"
      title={`sensitivity: ${tier}`}
    >
      <Icon className="w-3 h-3" strokeWidth={1.5} />
      {tier}
    </span>
  );
}

/* ---- live collaboration ------------------------------------------------- */

/**
 * Presence colour.
 *
 * The one place this system uses palette colours rather than semantic tokens.
 * "Which of six people is this caret" has no semantic token to express it, and
 * the alternative — colour-free carets — makes two editors indistinguishable,
 * which defeats the feature. Bounded and explicit: six named entries, written
 * out in full so Tailwind's scanner can see them (a `bg-${name}-500` template
 * would be purged from the build).
 *
 * The server sends the *name*; the mapping to a class lives here, so no hex
 * ever crosses the wire.
 */
const PRESENCE: Record<string, { fill: string; ring: string }> = {
  amber: { fill: "bg-amber-500", ring: "ring-amber-500/40" },
  cyan: { fill: "bg-cyan-500", ring: "ring-cyan-500/40" },
  emerald: { fill: "bg-emerald-500", ring: "ring-emerald-500/40" },
  fuchsia: { fill: "bg-fuchsia-500", ring: "ring-fuchsia-500/40" },
  rose: { fill: "bg-rose-500", ring: "ring-rose-500/40" },
  violet: { fill: "bg-violet-500", ring: "ring-violet-500/40" },
};

const FALLBACK = { fill: "bg-primary", ring: "ring-primary/40" };

export type Presence = {
  connection: string;
  display: string;
  color: string;
  anchor?: number;
  head?: number;
};

function initials(display: string): string {
  return display
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase() ?? "")
    .join("");
}

/** Who else is in this document right now. Overlapped avatars, quiet. */
export function PresenceStack({ participants }: { participants: Presence[] }) {
  if (participants.length === 0) return null;
  return (
    <div className="flex items-center -space-x-1.5">
      {participants.map((p) => {
        const tone = PRESENCE[p.color] ?? FALLBACK;
        return (
          <span
            key={p.connection}
            title={p.display}
            className={cx(
              "inline-flex items-center justify-center w-5 h-5 rounded-full",
              "text-[9px] font-medium text-white ring-2 ring-card",
              tone.fill,
            )}
          >
            {initials(p.display)}
          </span>
        );
      })}
    </div>
  );
}

/**
 * Remote carets, drawn over a textarea.
 *
 * One absolutely-positioned mirror per participant: an invisible copy of the
 * text up to their offset, then a visible caret. The mirror inherits the
 * textarea's exact typography via `textClass`, so the caret lands where the
 * character does without measuring anything.
 *
 * `pointer-events-none` throughout — this is decoration over a live input.
 */
export function RemoteCarets({
  body,
  participants,
  textClass,
}: {
  body: string;
  participants: Presence[];
  textClass: string;
}) {
  return (
    <>
      {participants.map((p) => {
        const tone = PRESENCE[p.color] ?? FALLBACK;
        const offset = Math.max(0, Math.min(p.head ?? 0, body.length));
        return (
          <div
            key={p.connection}
            aria-hidden
            className={cx(
              "absolute inset-0 pointer-events-none select-none overflow-hidden",
              textClass,
            )}
          >
            <span className="invisible">{body.slice(0, offset)}</span>
            <span className="relative inline-block align-baseline">
              <span
                className={cx("absolute left-0 top-0 w-[2px] h-[1.35em] rounded-full", tone.fill)}
              />
              <span
                className={cx(
                  "absolute left-0 -top-4 px-1 h-4 rounded-[3px] whitespace-nowrap",
                  "text-[9px] font-medium text-white",
                  tone.fill,
                )}
              >
                {p.display}
              </span>
            </span>
          </div>
        );
      })}
    </>
  );
}

/* ---- controls ----------------------------------------------------------- */

export function Row({
  active,
  onClick,
  icon,
  children,
  trailing,
  indent = 0,
}: {
  active?: boolean;
  onClick?: () => void;
  icon?: ReactNode;
  children: ReactNode;
  trailing?: ReactNode;
  indent?: number;
}) {
  return (
    <div
      onClick={onClick}
      style={{ paddingLeft: `${indent * 12 + 10}px` }}
      className={cx(
        "group flex items-center justify-between px-2.5 py-[7px] rounded-[6px]",
        "cursor-pointer select-none transition-all duration-200",
        // Weight and colour carry state, never size — rows must not reflow.
        active
          ? "bg-black/5 dark:bg-white/10 text-foreground font-medium"
          : "text-muted-foreground hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground/90",
      )}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        {icon}
        <span className="text-[13px] tracking-wide truncate">{children}</span>
      </div>
      {trailing ? <div className="flex items-center gap-2 shrink-0">{trailing}</div> : null}
    </div>
  );
}

export function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="flex items-center justify-center min-w-[20px] h-5 px-1.5 text-[10px] font-medium rounded-full bg-primary/10 text-primary">
      {children}
    </span>
  );
}

export function Kbd({ children }: { children: ReactNode }) {
  return (
    <kbd className="inline-flex items-center justify-center h-5 px-1.5 text-[10px] font-medium font-mono text-muted-foreground/60 bg-background/50 border border-border/50 rounded-[4px]">
      {children}
    </kbd>
  );
}

export function Disclosure({ open, children }: { open: boolean; children: ReactNode }) {
  // The grid-rows 0fr -> 1fr trick: no measured heights, no max-height hacks.
  return (
    <div
      className={cx(
        "grid transition-[grid-template-rows,opacity] duration-300 ease-in-out",
        open ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0",
      )}
    >
      <div className="overflow-hidden min-h-0 flex flex-col gap-0.5 mt-0.5">
        {children}
      </div>
    </div>
  );
}

export function Chevron({ open }: { open: boolean }) {
  return (
    <ChevronRight
      className={cx(
        "w-3.5 h-3.5 text-muted-foreground/50 transition-transform duration-200",
        open && "rotate-90",
      )}
      strokeWidth={2}
    />
  );
}
