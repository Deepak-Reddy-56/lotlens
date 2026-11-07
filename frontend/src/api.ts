export type CaseRecord = {
  id: string;
  case_code: string;
  supplier: { code: string; name: string };
  component: { code: string; name: string };
  lot: { code: string };
  symptoms: string;
  description: string;
  severity: string;
  status: string;
  root_cause_status: string;
  root_cause: string | null;
  created_at: string;
};

export type HistoricalCase = {
  case_code: string;
  supplier_code: string;
  supplier_name: string;
  component_code: string;
  component_name: string;
  lot_code: string;
  symptoms: string;
  root_cause_status: string;
  root_cause: string | null;
  status: string;
  actions: { id: string; description: string; outcome: string }[];
};

export type Investigation = {
  id: string;
  case_id: string;
  query: string;
  result_text: string;
  memory_hit_count: number;
  evidence_cases: HistoricalCase[];
  unlinked_case_codes: string[];
  citation_warnings: string[];
  created_at: string;
};

export type ActionRecord = {
  id: string;
  case_id: string;
  description: string;
  outcome: string;
  created_at: string;
};

export type Verification = {
  id: string;
  case_id: string;
  action_id: string;
  action_outcome: string;
  root_cause_status: string;
  confirmed_root_cause: string | null;
  verified_by: string;
  memory_sync_status: string;
  memory_sync_error: string | null;
  created_at: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; hindsight_configured: boolean; bank_id: string }>("/health"),
  listCases: () => request<CaseRecord[]>("/api/v1/cases"),
  seedDemo: () => request<{ created: number; total_seed_cases: number; note: string }>("/api/v1/demo/seed", { method: "POST" }),
  createCase: (payload: Record<string, unknown>) =>
    request<CaseRecord>("/api/v1/cases", { method: "POST", body: JSON.stringify(payload) }),
  investigate: (id: string) =>
    request<Investigation>(`/api/v1/cases/${id}/investigate`, { method: "POST" }),
  createAction: (id: string, description: string) =>
    request<ActionRecord>(`/api/v1/cases/${id}/actions`, { method: "POST", body: JSON.stringify({ description }) }),
  verify: (id: string, payload: Record<string, unknown>) =>
    request<Verification>(`/api/v1/cases/${id}/verify`, { method: "POST", body: JSON.stringify(payload) }),
};
