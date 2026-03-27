const API = "/api";

async function request(path: string, init?: RequestInit) {
  const res = await fetch(`${API}${path}`, {
    credentials: "include",
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// Auth
export const getAuthStatus = () => request("/auth/status");

// Files
export const listFiles = (provider: string, params = "") =>
  request(`/files/${provider}${params ? "?" + params : ""}`);

export const uploadFile = (provider: string, formData: FormData) =>
  request(`/files/${provider}/upload`, { method: "POST", body: formData });

export const deleteFile = (provider: string, params: string) =>
  request(`/files/${provider}?${params}`, { method: "DELETE" });

export const renameFile = (provider: string, params: string) =>
  request(`/files/${provider}/rename?${params}`, { method: "PATCH" });

// Calendar
export const listEvents = (params = "") =>
  request(`/calendar/events${params ? "?" + params : ""}`);

export const createEvent = (body: object) =>
  request("/calendar/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

export const updateEvent = (eventId: string, body: object) =>
  request(`/calendar/events/${eventId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

export const deleteEvent = (eventId: string) =>
  request(`/calendar/events/${eventId}`, { method: "DELETE" });

// Documents
export const parseDocument = (formData: FormData) =>
  request("/documents/parse", { method: "POST", body: formData });
