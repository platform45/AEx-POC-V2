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

export interface QueryResponse {
  answer: string;
  sql: string | null;
  data: Record<string, unknown>[] | null;
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

export function postQuery(question: string): Promise<QueryResponse> {
  return fetchAPI<QueryResponse>("/query/", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

// Returned by every issue session endpoint. done=true signals the conversation
// has ended; escalated=true means it ended without resolution.
export interface SessionResponse {
  session_id: string;
  message: string;
  done: boolean;
  escalated: boolean;
}

// Creates a new issue resolution session and returns the agent's first prompt
export function startIssueSession(): Promise<SessionResponse> {
  return fetchAPI<SessionResponse>("/issues/session", { method: "POST" });
}

// Sends a user reply to an active session and returns the agent's next message
export function respondToIssueSession(
  sessionId: string,
  input: string
): Promise<SessionResponse> {
  return fetchAPI<SessionResponse>(`/issues/session/${sessionId}/respond`, {
    method: "POST",
    body: JSON.stringify({ input }),
  });
}
