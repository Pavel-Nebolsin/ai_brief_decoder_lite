import type { DecodeBriefResponse } from './types';

const BACKEND_URL = 'http://localhost:8000';

/**
 * Decode a brief via the backend. Never throws — every failure mode (transport
 * error, non-2xx response, network unreachable) is converted into a normal
 * DecodeBriefResponse with `status: "failed"`. This mirrors the backend's own
 * approach of treating errors as regular data, not exceptions, so callers never
 * need a try/catch around this call. The `network_error` code is a client-only
 * addition to SafeError.code — the backend never produces it — since the backend
 * itself has no way to observe "the client couldn't reach me at all".
 */
export async function decodeBrief(text: string): Promise<DecodeBriefResponse> {
  try {
    const res = await fetch(`${BACKEND_URL}/v1/briefs/decode`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      // 422/5xx — transport-level failure, not a domain error (see backend-spec section 9)
      return networkErrorResponse(`Backend returned ${res.status}`);
    }

    return await res.json(); // shape: DecodeBriefResponse
  } catch {
    // fetch throws on actual network failure (backend down, no connection)
    return networkErrorResponse('Could not reach the backend. Is it running?');
  }
}

function networkErrorResponse(message: string): DecodeBriefResponse {
  return {
    run_id: crypto.randomUUID(),
    status: 'failed',
    result: null,
    error: { code: 'network_error', message },
    created_at: new Date().toISOString(),
  };
}
