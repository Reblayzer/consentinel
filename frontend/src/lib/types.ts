// TypeScript mirror of the backend's JSON contract (see backend/app/api/schemas.py).

export type Role = "admin" | "data_owner" | "data_steward" | "data_subject";

export interface Principal {
  actor: string;
  role: Role;
}

export type PIICategory =
  | "none"
  | "name"
  | "email"
  | "phone"
  | "national_id"
  | "address"
  | "date_of_birth"
  | "ip_address"
  | "credit_card";

export interface DataField {
  id: number;
  name: string;
  pii_category: PIICategory;
  confidence: number;
  rationale: string;
}

export interface Dataset {
  id: number;
  name: string;
  description: string;
  owner: string;
  source_system: string;
  created_at: string;
  contains_personal_data: boolean;
  fields: DataField[];
}

export interface FieldSample {
  name: string;
  sample_values: string[];
}

export interface DatasetCreate {
  name: string;
  description?: string;
  owner: string;
  source_system: string;
  fields: FieldSample[];
}

export type LegalBasis =
  | "consent"
  | "contract"
  | "legal_obligation"
  | "vital_interests"
  | "public_task"
  | "legitimate_interests";

export interface UsageAgreement {
  id: number;
  dataset_id: number;
  purpose: string;
  legal_basis: LegalBasis;
  retention_days: number;
  created_at: string;
}

export type RequestType = "access" | "erasure";
export type RequestStatus = "pending" | "approved" | "rejected" | "completed";

export interface ComplianceRequest {
  id: number;
  request_type: RequestType;
  subject_ref: string;
  dataset_id: number | null;
  reason: string;
  status: RequestStatus;
  requested_by: string;
  decided_by: string | null;
  decision_note: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface ComplianceRequestCreate {
  request_type: RequestType;
  subject_ref: string;
  dataset_id?: number | null;
  reason?: string;
}

export interface AuditEvent {
  id: number;
  actor: string;
  action: string;
  entity_type: string;
  entity_id: number | null;
  detail: string;
  created_at: string;
}
