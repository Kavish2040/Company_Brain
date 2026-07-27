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
// an icon, because a node of that type can already be returned by the API.
const ICONS: Record<string, LucideIcon> = {
  ...Object.fromEntries(NODE_TYPES.map((t) => [t.type, t.icon])),
  Account: Bot,
};

export function iconFor(type: string): LucideIcon {
  return ICONS[type] ?? FileText;
}
