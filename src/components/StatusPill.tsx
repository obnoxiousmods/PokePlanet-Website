import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { StatusResponse } from "../lib/types";

export function StatusPill() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  useEffect(() => { api.status().then(setStatus).catch(() => setStatus({ state: "offline", online_players: 0, game_version: null, checked_at: new Date().toISOString() })); }, []);
  return <div className={`status-pill ${status?.state ?? "loading"}`}><i />{status ? status.state === "online" ? `${status.online_players} trainer${status.online_players === 1 ? "" : "s"} online` : "Server status unavailable" : "Checking the world…"}</div>;
}

