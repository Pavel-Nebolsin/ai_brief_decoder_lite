export interface RiskItem {
  risk: string;
  severity: 'low' | 'medium' | 'high';
  reason: string;
}

export interface BriefDecodeResult {
  summary: string;
  goals: string[];
  deliverables: string[];
  constraints: string[];
  risks: RiskItem[];
  clarifying_questions: string[];
  recommended_next_action: string;
}

/**
 * Mirrors the backend's SafeError, extended with 'network_error' — a client-only
 * code the backend never returns, used when the backend can't be reached at all.
 */
export interface SafeError {
  code: 'invalid_json' | 'missing_field' | 'invalid_severity' | 'provider_error' | 'timeout' | 'network_error';
  message: string;
}

export interface DecodeBriefResponse {
  run_id: string;
  status: 'pending' | 'succeeded' | 'failed';
  result: BriefDecodeResult | null;
  error: SafeError | null;
  created_at: string;
}
