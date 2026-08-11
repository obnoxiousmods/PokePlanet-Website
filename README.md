# PokePlanet Website

The official website, download hub, documentation, and Discord-linked trainer portal for
[PokePlanet](https://github.com/obnoxiousmods/PokePlanet), a server-authoritative Pokémon
Emerald MMORPG.

## Stack

- React, TypeScript, and Vite for the responsive frontend
- Starlette, asyncpg, and httpx for the API and production static host
- Discord OAuth2 with opaque, hashed server-side sessions
- GitHub Releases as the canonical download feed
- PostgreSQL views that expose only the signed-in trainer's public summary

## Local development

```sh
npm install
uv sync --project backend --group dev
cp .env.example .env

# Terminal 1: frontend with /api proxied to Starlette
npm run dev

# Terminal 2
cd backend
uv run uvicorn app.main:app --reload --port 8791
```

Without Discord or PostgreSQL settings, the public site remains fully usable; sign-in and
contact delivery report that they are not configured. Development sessions use an in-memory
store. Production refuses to boot without required secrets.

## Verification

```sh
npm run check
npm run build
npm run test:e2e
cd backend
uv run pytest
uv run ruff check app tests
```

## Production

1. Build the frontend with the public Turnstile site key set as
   `VITE_TURNSTILE_SITE_KEY`.
2. Run `backend/sql/001_web.sql` as the PokePlanet database owner after replacing the generated
   role password. Use that restricted role in the website's `DATABASE_URL`.
3. Install the systemd and nginx templates from `deploy/`, then place production settings in
   `/etc/pokeplanet-website.env` with mode `0600`.
4. Keep the existing Rust game's exact `/login`, `/auth/callback`, and `/health` nginx routes.
   The website uses `/api/auth/discord/*`, so the two Discord flows do not collide.

`pokeplanet.obby.ca` must remain DNS-only at Cloudflare because the native game reaches QUIC on
port 4433 directly. `pp.obby.ca`, `pokemon.obby.ca`, and `pokeplanet.obnoxious.lol` are redirect
aliases.

## Privacy boundary

The website cannot read raw saves, story state, inventory, game session tokens, login tickets,
account moderation fields, or exact position. Discord access tokens are used once to fetch the
identity and then discarded. Contact messages are relayed to a private Discord webhook and are
not stored by the application.

## Project notice

PokePlanet is an unofficial fan project and is not affiliated with Nintendo, Creatures Inc.,
GAME FREAK, or The Pokémon Company. Pokémon and related marks belong to their respective owners.

