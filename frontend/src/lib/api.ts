import type {
  AuditEvent,
  ComplianceRequest,
  ComplianceRequestCreate,
  Dataset,
  DatasetCreate,
  Principal,
  RequestStatus,
} from "./types";

// Requests go through the Next.js rewrite proxy (see next.config.ts).
const BASE = "/api";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  principal?: Principal;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, principal } = options;
  const headers: Record<string, string> = { "content-type": "application/json" };
  if (principal) {
    headers["X-Actor"] = principal.actor;
    headers["X-Role"] = principal.role;
  }

  const response = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      if (data?.detail) detail = String(data.detail);
    } catch {
      // non-JSON error body; keep the status text
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export const api = {
  listDatasets: () => request<Dataset[]>("/datasets"),

  getDataset: (id: number) => request<Dataset>(`/datasets/${id}`),

  registerDataset: (payload: DatasetCreate, principal: Principal) =>
    request<Dataset>("/datasets", { method: "POST", body: payload, principal }),

  listRequests: (status?: RequestStatus) =>
    request<ComplianceRequest[]>(`/requests${status ? `?status=${status}` : ""}`),

  fileRequest: (payload: ComplianceRequestCreate, principal: Principal) =>
    request<ComplianceRequest>("/requests", { method: "POST", body: payload, principal }),

  decideRequest: (
    id: number,
    action: "approve" | "reject" | "complete",
    principal: Principal,
    note?: string,
  ) =>
    request<ComplianceRequest>(`/requests/${id}/${action}`, {
      method: "POST",
      body: action === "complete" ? undefined : { note: note ?? "" },
      principal,
    }),

  listAudit: (principal: Principal) => request<AuditEvent[]>("/audit", { principal }),
};
