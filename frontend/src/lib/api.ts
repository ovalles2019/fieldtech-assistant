const API_BASE = "/api";

let token: string | null = null;

export async function initAuth(): Promise<void> {
  const stored = localStorage.getItem("fieldtech_token");
  if (stored) {
    token = stored;
    return;
  }
  const res = await fetch(`${API_BASE}/auth/dev-token`, { method: "POST" });
  const data = await res.json();
  token = data.access_token;
  localStorage.setItem("fieldtech_token", token!);
}

function headers(): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function ask(
  question: string,
  equipmentId?: string
): Promise<import("../types").AskResponse> {
  const res = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      question,
      equipment_id: equipmentId ?? null,
      include_service_history: true,
    }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function resolveQR(payload: string): Promise<import("../types").QRResolveResponse> {
  const res = await fetch(`${API_BASE}/equipment/qr/resolve`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ payload }),
  });
  if (!res.ok) throw new Error("QR not recognized");
  return res.json();
}

export async function listEquipment(): Promise<import("../types").Equipment[]> {
  const res = await fetch(`${API_BASE}/equipment`, { headers: headers() });
  return res.json();
}

export async function createTicket(body: {
  equipment_id: string;
  title: string;
  description: string;
  priority: string;
  error_codes: string[];
}): Promise<import("../types").ServiceTicket> {
  const res = await fetch(`${API_BASE}/tickets`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function submitFeedback(body: {
  question: string;
  answer: string;
  rating: number;
  equipment_id?: string;
  comment?: string;
  citation_ids: string[];
}): Promise<void> {
  await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify(body),
  });
}
