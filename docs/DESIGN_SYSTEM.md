# company_brain — Design System

**Source of truth for all UI.** Extracted from the reference component in
[docs/UI.md](UI.md). Every UI surface in this project must match this language.

Status: recorded, not implemented. No frontend code exists yet.

The reference is a shadcn-style app shell: collapsible 260px sidebar, 56px topbar with
breadcrumb, scrollable content, ⌘K command palette. Its *visual language* is what we
adopt — quiet surfaces, small type, half-opacity borders, restrained motion. Its
*information architecture* (Projects / Customers / Finance) is generic SaaS filler and
does not transfer; see [§7](#7-mapping-to-company_brain-surfaces).

---

## 1. Stack

| Concern | Choice |
|---|---|
| Framework | React + TypeScript (strict) |
| Styling | Tailwind CSS |
| Components | shadcn/ui, installed into `components/ui/` |
| Icons | `lucide-react` — the only icon source |
| Theming | CSS variables + `dark:` variants |

`components/ui/` is not optional. The shadcn CLI writes there by default, and every
generated component's relative imports assume it. Moving it means patching every
`npx shadcn add` afterwards.

---

## 2. Color

Use **semantic tokens**, never raw hex. The full token set in play:

`background` · `foreground` · `card` · `card-foreground` · `primary` ·
`primary-foreground` · `muted-foreground` · `border` · `ring`

Three idioms that define the look and must be followed:

1. **Borders are half-opacity.** `border-border/50` everywhere, not `border-border`.
   Full-strength borders read as heavy and immediately break the language.
2. **Hover and fill are theme-inverted alpha, not tokens:**
   `bg-black/5 dark:bg-white/5`. Pressed/active goes to `dark:bg-white/10`.
   Skeletons and inert placeholder blocks use the same pair.
3. **Muted text is layered by opacity.** `text-muted-foreground` for secondary,
   `/70` for tertiary (inactive icons), `/50` for quaternary (section headings,
   placeholders, decorative chevrons).

Primary is used sparingly and almost always at low alpha: `bg-primary/10 text-primary`
for badges and selected rows, solid `bg-primary` only for the workspace avatar tile.

**Every surface must be specified in both light and dark.** There is no light-only
component. Dark is not an afterthought filter over light.

---

## 3. Typography

Small, tight, and deliberately below default web sizes.

| Role | Spec |
|---|---|
| Nav item / menu row / body | `text-[13px]`, `tracking-wide` on nav labels |
| Section heading | `text-[11px] font-semibold tracking-wider uppercase text-muted-foreground/50` |
| Badge / `kbd` | `text-[10px] font-medium`, `font-mono` for keys |
| Search input | `text-[14px]` |
| Breadcrumb | `text-sm` |
| Sub-label (e.g. "Pro Plan") | `text-[11px] text-muted-foreground` |

Active nav items get `font-medium` plus full-strength `text-foreground`; inactive stay
`text-muted-foreground` at normal weight. **Weight and color carry state — never a
size change.** Rows must not reflow on selection.

---

## 4. Geometry, elevation, motion

**Radii** ladder by element size: `rounded-[4px]` kbd · `rounded-[6px]` nav items,
avatar tile, buttons · `rounded-lg` (8px) dropdowns, menu rows, list rows ·
`rounded-xl` (12px) cards, panels, modals, app shell · `rounded-full` badges, avatars.

**Icons** are `lucide-react` at `strokeWidth={1.5}` — this is the single most
recognizable trait of the language. Exception: small chevrons use `strokeWidth={2}` to
stay legible. Sizes: `w-[16px]` in nav, `w-[18px]` in chrome (topbar, search),
`w-3.5` for disclosure chevrons.

**Elevation is restrained.** `shadow-sm` on cards and the app shell · `shadow-xl` on
dropdowns · `shadow-2xl` on the command palette · `ring-1 ring-black/5
dark:ring-white/5` on the outermost shell. Nothing else casts a shadow.

**Spacing:** sidebar `w-[260px] p-3` · topbar `h-14 px-4` · content `p-6 md:p-8` ·
nav item `px-2.5 py-[7px]` · `gap-0.5` within a nav group, `gap-4` between groups ·
`gap-6` between cards.

**Motion** is short and functional:

- color/state: `transition-colors`, or `transition-all duration-200`
- disclosure: grid trick — `grid-rows-[0fr]` → `grid-rows-[1fr]` with
  `transition-[grid-template-rows,opacity] duration-300 ease-in-out` and an
  `overflow-hidden min-h-0` child. No max-height hacks, no measured heights.
- sidebar collapse: width + opacity, `duration-300 ease-in-out`
- overlays: `animate-in fade-in zoom-in-95`, `duration-100` menus / `duration-200` modals
- palette backdrop: `bg-background/40 backdrop-blur-sm`

Nothing animates longer than 300ms. Nothing bounces.

---

## 5. Component idioms to reuse

- **Hidden scrollbars** on every scroll container:
  `[&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]`
- **Reveal-on-hover affordances** via `group` / `hidden group-hover:inline-flex` —
  keyboard shortcuts appear on row hover, they don't sit there permanently.
- **Nested list indent guide**: an absolutely positioned `border-l` at
  `left: level * 12 + 17.5px`, with row padding `level * 12 + 10px`.
- **Dropdown dismissal**: a `fixed inset-0 z-40` transparent click-catcher behind the
  `z-50` panel. Same pattern for modals with an inner `absolute inset-0` catcher.
- **Command palette**: `pt-[15vh]`, `max-w-xl`, blurred backdrop, an inline `ESC` kbd
  that is itself clickable, plus an `X` button. Both dismiss.
- **Empty states** are centered icon (`w-6 h-6 text-muted-foreground/30`) over
  `text-[13px] text-muted-foreground font-medium`. Quiet, never illustrated.
- **Truncation over wrapping** in all chrome: `truncate` + `min-w-0` / `shrink-0` on
  siblings. Long node titles and person names must not reflow the shell.

**Controlled/uncontrolled dual API.** Every stateful component accepts an optional
value + handler and falls back to internal state:

```tsx
const current = selected ?? internalSelected;
const handleSelect = onSelect ?? setInternalSelected;
```

Keep this — it's what makes the components usable in isolation (Storybook, tests)
without a provider.

**Props, not module-scope mocks.** The reference hardcodes `mockNavGroups` at module
scope and `demo.tsx` is a near-verbatim duplicate of `dashboard-sidebar.tsx`. When we
build, nav data and all content come in as props from one source. Do not copy the
duplication forward.

---

## 6. Extensions this project needs

The reference has no vocabulary for the things company_brain is actually about. These
are additions to the system, built in the same language:

- **Citation chip** — inline, monospace-ish node ID, `rounded-[4px]`, hover reveals
  title + source; click opens the node. Uses the `kbd` treatment as its base.
- **Confidence indicator** — for edges and claims. Must be legible without color alone
  (accessibility, and the palette has no semantic red/amber/green). Proposal: a small
  numeric or 3-step bar, never a traffic light.
- **Provenance badge** — `structural` / `llm` / `human`, at badge scale
  (`text-[10px]`, `bg-primary/10`-family). Users need to know whether a fact came from
  metadata, a model, or a person.
- **Proposed vs. accepted state** — proposed edges and nodes are visually distinct
  (dashed `border-border/50`, reduced opacity) and never rendered as settled fact.
- **Diff view** for the review queue — the review UI is fundamentally a diff reviewer.
  Additions/removals in the alpha-fill idiom, not GitHub green/red.
- **Sensitivity marker** — a node's tier must be visible when its content is on screen.
  Quiet, but always present.

Two hard rules from the architecture that bind the UI:

1. The UI renders the **ACL-projected** node from the API, never stored bytes. It never
   receives content the principal can't see, so there is no client-side filtering to
   get wrong. A node with no visible edges is a 404, and the UI shows a genuine
   not-found — not an empty page that confirms the node exists.
2. **An answer without citations is an error state**, not a plain answer. The UI must
   have a designed error state for it and must never render an uncited claim as normal
   output.

---

## 7. Mapping to company_brain surfaces

Same shell, our IA:

- **Sidebar** — Ask (⌘K), Inbox/Review Queue (badge = pending proposal count), Browse
  (grouped: People, Teams, Tools, Processes, Decisions, Documents — the nested
  disclosure pattern fits exactly), Connectors, Settings.
- **Workspace switcher** → **tenant + principal switcher.** Critical: the demo's
  "view as" capability is how we show permission filtering, so this control is
  load-bearing, not decoration.
- **Topbar breadcrumb** → `workspace / node type / node title`.
- **⌘K palette** → the primary Ask entry point. This is the product's main interaction,
  so it graduates from an overlay to a full surface with results and citations.
- **Content cards** → answer + citations, node detail, review diff, graph view.

---

## 8. Roadmap impact

ROADMAP.md currently has no UI until M3 (the review queue) and treats CLI + editor as
the interface through M2. This design system doesn't change that sequencing by itself,
but it does mean two things:

- When the UI lands, it lands in **this** language — the M3 review UI is not a throwaway
  admin panel, it's the first piece of the real product surface.
- **Open question:** does a web UI now belong in M1's demo? A ⌘K ask-with-citations
  surface would be a far better demo than a CLI, at the cost of a frontend stack, an
  API contract, and auth in M1 instead of M3. My recommendation is still CLI-first for
  M1 — the risky parts are determinism and ACL correctness, and a UI proves neither —
  but this is your call, and the existence of this doc suggests you may want it sooner.
