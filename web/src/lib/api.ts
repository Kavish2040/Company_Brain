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

export type Pending = {
  key: string;
  node_id: string;
  node_title: string;
  predicate: string;
  object: string;
  confidence: number;
  quote: string;
};

export type ReviewStats = {
  pending: number;
  by_predicate: Record<string, number>;
  /** predicate -> [accepted, decided]. 100% means the gate is theatre. */
  accept_rate: Record<string, [number, number]>;
};

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
  decide: (p: string, key: string, decision: "accepted" | "rejected") =>
    request<{ key: string }>("/review/decide", p, {
      method: "POST",
      body: JSON.stringify({ key, decision }),
    }),
};
