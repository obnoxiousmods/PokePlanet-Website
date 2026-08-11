export type Platform = "windows" | "linux" | "macos" | "android";

export interface ReleaseAsset {
  name: string;
  platform: Platform;
  architecture: string;
  format: string;
  size: number;
  sha256: string | null;
  download_url: string;
}

export interface ReleasesResponse {
  version: string | null;
  published_at: string | null;
  prerelease: boolean;
  release_url: string;
  notes: string;
  assets: ReleaseAsset[];
  platforms: Record<Platform, "available" | "coming_soon">;
}

export interface StatusResponse {
  state: "online" | "degraded" | "offline";
  online_players: number;
  game_version: string | null;
  checked_at: string;
}

export interface TrainerProfile {
  name: string;
  graphics_id: number;
  play_time_seconds: number;
  money: number;
  badges: number;
  pokedex_caught: number;
  pokedex_seen: number;
  location: string;
  party: Array<{ species: number; name: string; level: number }>;
}

export interface MeResponse {
  authenticated: boolean;
  user: null | { id: string; username: string; display_name: string; avatar_url: string };
  character: TrainerProfile | null;
}

