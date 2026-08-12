import hashlib
import json
import secrets
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any

import asyncpg


def new_token() -> str:
    return secrets.token_urlsafe(40)


def _combat_level(max_level: int, avg_level: float, badges: int) -> int:
    """The OSRS-style combat level (3..126), mirroring the game server's deadman::combat_level_from.

    A character with no living party (fresh or wiped) is the floor, 3.
    """
    if max_level <= 0:
        return 3
    raw = round(max_level * 0.9 + avg_level * 0.4 + badges * 4.0)
    return max(3, min(126, raw))


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def decode_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return {}
    return dict(value) if isinstance(value, Mapping) else {}


class SessionStore:
    def __init__(self, database_url: str | None, ttl_days: int = 30) -> None:
        self.database_url = database_url
        self.ttl = timedelta(days=ttl_days)
        self.pool: asyncpg.Pool | None = None
        self.memory: dict[str, tuple[datetime, dict[str, Any]]] = {}

    async def connect(self) -> None:
        if self.database_url:
            self.pool = await asyncpg.create_pool(self.database_url, min_size=1, max_size=6)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()

    async def load(self, token: str | None) -> dict[str, Any]:
        if not token:
            return {}
        digest = token_hash(token)
        if self.pool:
            row = await self.pool.fetchrow(
                "SELECT payload FROM pokeplanet_web.sessions WHERE token_hash = $1 AND expires_at > now()",
                digest,
            )
            return decode_payload(row["payload"]) if row else {}
        item = self.memory.get(digest)
        if not item or item[0] <= datetime.now(UTC):
            self.memory.pop(digest, None)
            return {}
        return dict(item[1])

    async def save(self, token: str, payload: dict[str, Any]) -> None:
        digest = token_hash(token)
        expires = datetime.now(UTC) + self.ttl
        if self.pool:
            await self.pool.execute(
                "INSERT INTO pokeplanet_web.sessions (token_hash, payload, expires_at) "
                "VALUES ($1, $2::jsonb, $3) ON CONFLICT (token_hash) DO UPDATE "
                "SET payload = EXCLUDED.payload, expires_at = EXCLUDED.expires_at, updated_at = now()",
                digest,
                json.dumps(payload),
                expires,
            )
        else:
            self.memory[digest] = (expires, dict(payload))

    async def delete(self, token: str | None) -> None:
        if not token:
            return
        digest = token_hash(token)
        if self.pool:
            await self.pool.execute("DELETE FROM pokeplanet_web.sessions WHERE token_hash = $1", digest)
        self.memory.pop(digest, None)

    async def leaderboard(self, mode: str, limit: int = 100) -> list[dict[str, Any]]:
        """The top characters in a world, ranked by badges, then Pokedex, then time played.

        Combat level is derived here from the party's max/average level and badge count, matching
        the game server's own formula so the site and the game agree.
        """
        if not self.pool:
            return []
        rows = await self.pool.fetch(
            "SELECT name, badges, pokedex_caught, play_time_s, graveyard_count, "
            "party_max_level, party_avg_level "
            "FROM pokeplanet_web.leaderboard WHERE mode = $1 "
            "ORDER BY badges DESC, pokedex_caught DESC, play_time_s DESC LIMIT $2",
            mode,
            limit,
        )
        return [
            {
                "rank": index + 1,
                "name": row["name"],
                "badges": row["badges"],
                "combat_level": _combat_level(
                    row["party_max_level"], row["party_avg_level"], row["badges"]
                ),
                "pokedex_caught": row["pokedex_caught"],
                "graveyard": row["graveyard_count"],
                "play_hours": max(0, row["play_time_s"]) // 3600,
            }
            for index, row in enumerate(rows)
        ]

    async def recent_deaths(self, mode: str, limit: int = 20) -> list[dict[str, Any]]:
        """The most recent deaths in a world, newest first, for the death feed."""
        if not self.pool:
            return []
        rows = await self.pool.fetch(
            "SELECT name, species, died_at FROM pokeplanet_web.recent_deaths "
            "WHERE mode = $1 ORDER BY died_at DESC LIMIT $2",
            mode,
            limit,
        )
        return [
            {
                "name": row["name"],
                "species": row["species"],
                "died_on": row["died_at"].date().isoformat(),
            }
            for row in rows
        ]

    async def profile_for_discord(self, discord_id: str) -> dict[str, Any] | None:
        if not self.pool:
            return None
        row = await self.pool.fetchrow(
            "SELECT * FROM pokeplanet_web.player_profiles WHERE discord_id = $1", discord_id
        )
        if not row:
            return None
        party_rows = await self.pool.fetch(
            "SELECT species, species_name, level FROM pokeplanet_web.player_party "
            "WHERE character_id = $1 ORDER BY slot LIMIT 6",
            row["character_id"],
        )
        return {
            "name": row["name"],
            "graphics_id": row["graphics_id"],
            "play_time_seconds": max(0, row["play_time_s"]),
            "money": max(0, row["money"]),
            "badges": row["badges"],
            "pokedex_caught": row["pokedex_caught"],
            "pokedex_seen": row["pokedex_seen"],
            "location": row["location"],
            "party": [
                {"species": item["species"], "name": item["species_name"], "level": item["level"]}
                for item in party_rows
            ],
        }
