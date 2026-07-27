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
  /** "edge" — the §11 gates held it back; "proposal" — an agent wrote it. */
  kind: "edge" | "proposal";
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
};

export type ReviewStats = {
  pending: number;
  pending_proposals: number;
  by_predicate: Record<string, number>;
  /** predicate -> [accepted, decided]. 100% means the gate is theatre. */
  accept_rate: Record<string, [number, number]>;
  proposal_accept_rate: Record<string, [number, number]>;
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
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Principal": principal,
      ...(init?.headers ?? {}),
    },
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
  nodes: (p: string, type?: string, q?: string) => {
    const params = new URLSearchParams();
    if (type) params.set("type", type);
    if (q) params.set("q", q);
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
   * Decide one item or many, in the order the reviewer worked them. Each item
   * carries back the `kind` the queue gave it, so the server validates a tag
   * rather than inferring a code path from the shape of a key.
   */
  decide: (p: string, items: Pending[], decision: Decision) =>
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
};
