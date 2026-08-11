import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import asyncpg


def new_token() -> str:
    return secrets.token_urlsafe(40)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


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
            return dict(row["payload"]) if row else {}
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
