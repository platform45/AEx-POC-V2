const API_BASE = `${process.env.NEXT_PUBLIC_API_URL ?? ""}/api/v1`;

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export interface HealthResponse {
  status: string;
}

export interface DiagnosticResponse {
  device_id: string;
  status: string;
  result: Record<string, unknown>;
}

export interface CaseResponse {
  id: string;
  title: string;
  description: string;
  raw_context: Record<string, unknown>;
}

export function getHealth(): Promise<HealthResponse> {
  return fetchAPI<HealthResponse>("/health");
}

export function getDiagnostics(deviceId: string): Promise<DiagnosticResponse> {
  return fetchAPI<DiagnosticResponse>(`/diagnostics/${deviceId}`);
}

export function getCases(): Promise<{ cases: CaseResponse[] }> {
  return fetchAPI<{ cases: CaseResponse[] }>("/cases/");
}
