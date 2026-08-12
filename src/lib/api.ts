import type { DeathsResponse, LadderResponse, MeResponse, ReleasesResponse, StatusResponse } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(payload.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  status: () => request<StatusResponse>("/api/status"),
  releases: () => request<ReleasesResponse>("/api/releases"),
  ladder: (mode: string) => request<LadderResponse>(`/api/ladder?mode=${encodeURIComponent(mode)}`),
  deaths: (mode: string) => request<DeathsResponse>(`/api/deaths?mode=${encodeURIComponent(mode)}`),
  me: () => request<MeResponse>("/api/me"),
  logout: () => request<{ ok: boolean }>("/api/auth/logout", { method: "POST", body: "{}" }),
  contact: (body: Record<string, string>) =>
    request<{ ok: boolean }>("/api/contact", { method: "POST", body: JSON.stringify(body) }),
};

export function formatBytes(bytes: number): string {
  if (!bytes) return "—";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / 1024 ** index).toFixed(index ? 1 : 0)} ${units[index]}`;
}

export function formatPlayTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${minutes}m`;
}

