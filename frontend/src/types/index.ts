export interface User {
  id: string;
  username: string;
  email: string;
  role: 'ADMIN' | 'MARKETING' | 'CUSTOMER_SUPPORT' | 'AUDITOR';
}

export interface DiscoveryField {
  field_name: string;
  data_type: string;
  classification: string;
  confidence: number;
  recommended_protection: string;
  sample_masked?: string;
}

export interface PolicyItem {
  field_name: string;
  classification: string;
  protection_method: 'KEEP' | 'TOKENIZE' | 'FPE' | 'ENCRYPT' | 'MASK';
  enabled: boolean;
  deterministic: boolean;
  version: number;
}

export interface BatchRun {
  batch_id: string;
  source: string;
  start_time: string;
  end_time?: string;
  status: string;
  batch_size: number;
  processed_rows: number;
  success_count: number;
  error_count: number;
  error_summary?: string;
}

export interface ProtectedCustomer {
  customer_id: string;
  name?: string;
  email?: string;
  mobile?: string;
  city?: string;
  segment?: string;
  protection_version: number;
  created_at?: string;
}

export interface AuditEvent {
  id: string;
  actor: string;
  protected_subject: string;
  action: string;
  field?: string;
  purpose?: string;
  reference?: string;
  result: string;
  timestamp: string;
  error_code?: string;
}

export interface DashboardStats {
  total_source_records: number;
  protected_records: number;
  latest_batch?: BatchRun;
  processed_rows: number;
  successful_rows: number;
  failed_rows: number;
  discovered_pii_fields: number;
  audit_events: number;
  email_operations: number;
  bounce_events: number;
  denied_reveals: number;
  allowed_reveals: number;
}
