/**
 * The node vocabulary, in one place.
 *
 * Not a design-system primitive — this is company_brain's own taxonomy, and it
 * lives here so the sidebar and the Ask overview name and draw a Process the
 * same way. `NodeType` in schemas/nodes.py is the source of truth; this is its
 * presentation layer.
 */

import {
  Bot,
  Boxes,
  FileText,
  User,
  Users,
  Workflow,
  Wrench,
  type LucideIcon,
} from "lucide-react";

export type NodeTypeMeta = { type: string; label: string; icon: LucideIcon };

/** Browse order: entities first, documents last — they are the bulk. */
export const NODE_TYPES: NodeTypeMeta[] = [
  { type: "Person", label: "People", icon: User },
  { type: "Team", label: "Teams", icon: Users },
  { type: "Process", label: "Processes", icon: Workflow },
  { type: "Tool", label: "Tools", icon: Wrench },
  { type: "Decision", label: "Decisions", icon: Boxes },
  { type: "Document", label: "Documents", icon: FileText },
];

// Account exists in the schema but has no Browse entry yet (M3). It still needs
// a label and an icon, because the API already returns nodes of that type and a
// surface that only knows the six Browse rows would quietly drop them — which
// on a breakdown means the parts stop summing to the whole.
const META: Record<string, { label: string; icon: LucideIcon }> = {
  ...Object.fromEntries(NODE_TYPES.map((t) => [t.type, { label: t.label, icon: t.icon }])),
  Account: { label: "Accounts", icon: Bot },
};

export function iconFor(type: string): LucideIcon {
  return META[type]?.icon ?? FileText;
}

export function labelFor(type: string): string {
  return META[type]?.label ?? `${type}s`;
}

/** Browse order, with anything the taxonomy has not caught up with at the end. */
export function orderTypes(types: string[]): string[] {
  const rank = new Map(NODE_TYPES.map((t, i) => [t.type, i]));
  return [...types].sort(
    (a, b) =>
      (rank.get(a) ?? NODE_TYPES.length) - (rank.get(b) ?? NODE_TYPES.length) ||
      a.localeCompare(b),
  );
}
