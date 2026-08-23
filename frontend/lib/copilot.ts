const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface CopilotMessage {
  role: "user" | "assistant";
  content: string;
}

export interface CopilotChatRequest {
  message: string;
  context_type?: string;
  context_id?: number;
  conversation_history?: CopilotMessage[];
}

export interface CopilotResponse {
  response: string;
  tools_used?: string[];
  context_type?: string;
  context_id?: number;
  model?: string;
  tokens_used?: number;
  error?: boolean;
}

export async function copilotChat(request: CopilotChatRequest): Promise<CopilotResponse> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE}/api/copilot/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(request),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    return { response: err.detail || "Failed to reach AI Copilot", error: true };
  }
  return res.json();
}

export async function copilotInvestigateAlert(alertId: number): Promise<CopilotResponse> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE}/api/copilot/investigate/alert/${alertId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    return { response: err.detail || "Investigation failed", error: true };
  }
  return res.json();
}

export async function copilotInvestigateIncident(incidentId: number): Promise<CopilotResponse> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE}/api/copilot/investigate/incident/${incidentId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    return { response: err.detail || "Investigation failed", error: true };
  }
  return res.json();
}

export async function copilotHealthCheck(): Promise<{ status: string; model?: string }> {
  const res = await fetch(`${API_BASE}/api/copilot/health`);
  if (!res.ok) return { status: "offline" };
  return res.json();
}

export async function copilotClearConversation(): Promise<void> {
  const token = localStorage.getItem("token");
  await fetch(`${API_BASE}/api/copilot/clear`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
}
