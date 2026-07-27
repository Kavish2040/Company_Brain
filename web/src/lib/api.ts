/**
 * API client.
 *
 * The principal travels in the X-Principal header, never in a request body —
 * a demo stand-in for a session cookie, but the same shape: identity is
 * out-of-band. The UI never filters by permission (CLAUDE.md invariant 17);
 * everything here is already ACL-projected by the server.
 */

export type Principal = {
  id: string;
  display: string;
  visible_sources: number;
};

export type Citation = { node_id: string; title: string; snippet: string };

export type AskResult = {
  question: string;
  text: string;
  citations: Citation[];
  asserted: string[];
  inferred: string[];
  insufficient_evidence: boolean;
  seed_count: number;
  expanded_count: number;
  withheld_by_acl: number;
  /** Invariant 11: set when the citation validator refused the answer.
   *  A designed error state, not prose. */
  refused: string | null;
};

export type NodeSummary = { id: string; type: string; title: string };

/** One ACL ref this principal holds, with the tier it reaches on that ref. */
export type OverviewSource = { ref: string; ceiling: string; nodes: number };

export type OverviewNode = {
  id: string;
  type: string;
  title: string;
  sensitivity: string;
  /** Edges with both endpoints visible — not the stored degree. */
  degree: number;
  modified: string | null;
};

/**
 * What the graph holds, seen from one principal. Already projected: the
 * `withheld_*` counts describe nodes and sources this principal cannot open,
 * and the server deliberately reports their number and never their names.
 */
export type Overview = {
  nodes: number;
  edges: number;
  by_type: Record<string, number>;
  sources: OverviewSource[];
  withheld_nodes: number;
  withheld_sources: number;
  connected: OverviewNode[];
  recent: OverviewNode[];
};

export type Relation = {
  predicate: string;
  object: string;
  object_title: string;
  confidence: number;
  provenance: string;
  status: string;
};

export type NodeDetail = {
  id: string;
  type: string;
  title: string;
  body: string;
  sensitivity: string;
  relations: Relation[];
};

/** One edge as a line in a diff, rather than as a settled fact. */
export type RelationDiff = {
  predicate: string;
  subject: string | null;
  subject_title: string | null;
  object: string;
  object_title: string | null;
  confidence: number;
  provenance: string;
  quote: string;
};

export type DiffLine = {
  kind: "context" | "added" | "removed" | "gap";
  text: string;
};

/**
 * One queue item. Extraction-proposed edges and agent proposals arrive in the
 * same shape because to a reviewer they are the same job — an extraction edge
 * is simply a diff with one added relation and nothing removed.
 */
export type Pending = {
  key: string;
  /** "edge" — the §11 gates held it back; "proposal" — an agent wrote it;
   *  "outreach" — a message drafted for a real person, which carries a body
   *  rather than a relation diff. */
  kind: "edge" | "proposal" | "outreach";
  node_id: string;
  node_title: string;
  predicate: string | null;
  subject: string | null;
  subject_title: string | null;
  object: string | null;
  confidence: number | null;
  quote: string;
  summary: string;
  /** Agent proposals only. A suggestion nobody can attribute is a suggestion
   *  nobody should accept. */
  proposed_by: string | null;
  delegated_by: string | null;
  /** The target moved after the proposal was made; accepting would revert it. */
  stale: boolean;
  body_diff: DiffLine[];
  added_relations: RelationDiff[];
  removed_relations: RelationDiff[];
  /** Set only when kind is "outreach". */
  outreach: Outreach | null;
};

export type ReviewStats = {
  pending: number;
  pending_proposals: number;
  pending_outreach: number;
  by_predicate: Record<string, number>;
  /** predicate -> [accepted, decided]. 100% means the gate is theatre. */
  accept_rate: Record<string, [number, number]>;
  proposal_accept_rate: Record<string, [number, number]>;
  outreach_accept_rate: Record<string, [number, number]>;
};

/**
 * The contact Apollo resolved. `source` is "apollo" when a live lookup found
 * them and "offline" when it did not run — an offline lead carries a name and
 * no contact details, never a fabricated address.
 */
export type Lead = {
  name: string;
  email: string | null;
  title: string | null;
  organization: string | null;
  linkedin_url: string | null;
  source: string;
};

export type OutreachState = "pending" | "approved" | "rejected" | "sent";

/**
 * A drafted message. Never sent by drafting it, and never sent by approving
 * it either — dispatch is a third, separate act against /outreach/send.
 */
export type Outreach = {
  draft_id: string;
  node_id: string;
  node_title: string;
  sensitivity: string;
  drafted_by: string;
  created_at: string;
  subject: string;
  body: string;
  /** The graph statements the body was built from — the reviewer's evidence. */
  facts: string[];
  lead: Lead | null;
  lead_source: string;
  state: OutreachState;
  decided_by: string | null;
  sent_by: string | null;
  sent_at: string | null;
};

export type Decision = "accepted" | "rejected" | "pending";

export type Health = {
  ok: boolean;
  providers: string;
  offline: boolean;
  nodes: number;
  chunks: number;
  edges: number;
};

export type GmailMessage = {
  id: string;
  threadId: string;
  subject: string;
  from: string;
  snippet: string;
  receivedAt: string;
  bucket: "urgent" | "promotional" | "social" | "updates" | "normal";
  labels: string[];
};

export type GmailStatus = {
  linked: boolean;
  email: string | null;
  lastRefreshed: string | null;
};

export type GmailTriage = {
  email: string;
  lastRefreshed: string;
  buckets: Record<string, GmailMessage[]>;
};

export class ApiError extends Error {
  // A plain field rather than a parameter property: the template sets
  // erasableSyntaxOnly, which forbids constructor-parameter properties.
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  principal: string,
  // Narrowed from RequestInit: `HeadersInit` also admits `Headers` and
  // `string[][]`, neither of which survives the object spread below.
  init?: Omit<RequestInit, "headers"> & { headers?: Record<string, string> },
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init?.headers ?? {}),
  };
  if (principal) {
    headers["X-Principal"] = principal;
  }
  const response = await fetch(`/api${path}`, {
    ...init,
    credentials: "include",
    headers,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      detail = (await response.json()).detail ?? detail;
    } catch {
      /* non-JSON error body; the status text is all we have */
    }
    throw new ApiError(detail, response.status);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: (p: string) => request<Health>("/health", p),
  principals: (p: string) => request<Principal[]>("/principals", p),
  ask: (p: string, question: string, limit = 6) =>
    request<AskResult>("/ask", p, {
      method: "POST",
      body: JSON.stringify({ question, limit }),
    }),
  overview: (p: string) => request<Overview>("/overview", p),
  nodes: (p: string, type?: string, q?: string, limit: number = 200) => {
    const params = new URLSearchParams();
    if (type) params.set("type", type);
    if (q) params.set("q", q);
    params.set("limit", String(limit));
    return request<NodeSummary[]>(`/nodes?${params}`, p);
  },
  node: (p: string, id: string) => request<NodeDetail>(`/nodes/${id}`, p),
  review: (p: string, predicate?: string) =>
    request<Pending[]>(
      `/review${predicate ? `?predicate=${predicate}` : ""}`,
      p,
    ),
  reviewStats: (p: string) => request<ReviewStats>("/review/stats", p),
  /**
   * Draft outreach from a node. Composes from the graph and queues for review
   * — it does not send, and there is no parameter that would make it.
   */
  outreachDraft: (p: string, nodeId: string) =>
    request<Outreach>("/outreach/draft", p, {
      method: "POST",
      body: JSON.stringify({ node_id: nodeId }),
    }),
  /** Dispatch an approved draft. 409s on anything not yet approved. */
  outreachSend: (p: string, draftId: string) =>
    request<Outreach>("/outreach/send", p, {
      method: "POST",
      body: JSON.stringify({ draft_id: draftId }),
    }),
  outreachList: (p: string, state?: OutreachState) =>
    request<Outreach[]>(`/outreach${state ? `?state=${state}` : ""}`, p),
  /**
   * Decide one item or many, in the order the reviewer worked them. Each item
   * carries back the `kind` the queue gave it, so the server validates a tag
   * rather than inferring a code path from the shape of a key.
   *
   * Typed to the two fields it actually sends rather than to `Pending`, so a
   * caller holding an `Outreach` can decide it without fabricating a queue row
   * of nulls to satisfy a shape the request never uses. `Pending[]` still
   * satisfies it.
   */
  decide: (
    p: string,
    items: readonly { key: string; kind: Pending["kind"] }[],
    decision: Decision,
  ) =>
    request<{ decided: number; decision: string; by: string }>(
      "/review/decide",
      p,
      {
        method: "POST",
        body: JSON.stringify({
          items: items.map(({ key, kind }) => ({ key, kind })),
          decision,
        }),
      },
    ),
  gmailStatus: () => request<GmailStatus>("/gmail/status", ""),
  gmailTriage: (forceRefresh?: boolean) =>
    request<GmailTriage>(
      `/gmail/triage${forceRefresh ? "?force_refresh=true" : ""}`,
      "",
    ),
  gmailOauthStart: () => "http://localhost:9000/api/gmail/oauth/start",
  gmailLogout: () =>
    request<{ status: string }>("/gmail/oauth/logout", "", {
      method: "POST",
    }),
};
