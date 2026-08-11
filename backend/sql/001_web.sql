-- Run as the PokePlanet database owner. Replace the password before execution.
CREATE ROLE pokeplanet_web LOGIN PASSWORD 'REPLACE_WITH_A_RANDOM_PASSWORD';
CREATE SCHEMA IF NOT EXISTS pokeplanet_web AUTHORIZATION pokeplanet_web;

CREATE TABLE IF NOT EXISTS pokeplanet_web.sessions (
    token_hash TEXT PRIMARY KEY,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE pokeplanet_web.sessions OWNER TO pokeplanet_web;

-- Public website profile surface. Deliberately excludes saves, session tokens,
-- account flags, raw positions, story state, inventory, and private timestamps.
CREATE OR REPLACE VIEW pokeplanet_web.player_profiles AS
SELECT
    a.discord_id,
    c.id AS character_id,
    c.name,
    c.graphics_id,
    c.play_time_s,
    c.money,
    c.badges,
    c.pokedex_caught,
    c.pokedex_seen,
    CASE
      WHEN c.map_group = 0 AND c.map_num = 9 THEN 'Littleroot Town'
      ELSE 'Hoenn'
    END AS location
FROM public.accounts a
JOIN public.characters c ON c.account_id = a.id
WHERE NOT a.banned;

CREATE OR REPLACE VIEW pokeplanet_web.player_party AS
SELECT
    p.character_id,
    p.slot,
    p.species,
    'Pokémon #' || p.species::text AS species_name,
    p.level
FROM public.pokemon p
WHERE p.box_id = 0;

REVOKE ALL ON SCHEMA public FROM pokeplanet_web;
GRANT USAGE ON SCHEMA pokeplanet_web TO pokeplanet_web;
GRANT SELECT, INSERT, UPDATE, DELETE ON pokeplanet_web.sessions TO pokeplanet_web;
GRANT SELECT ON pokeplanet_web.player_profiles, pokeplanet_web.player_party TO pokeplanet_web;

