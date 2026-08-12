-- Deadman ladder + death feed views for the public website.
--
-- Run as the PokePlanet database owner (the same role that ran 001_web.sql), so the views are
-- owned by it and read the game's own tables with its privileges; the website's restricted
-- pokeplanet_web role only ever gets SELECT on the views, never on the underlying tables.
--
-- Idempotent: CREATE OR REPLACE + GRANT, safe to re-run on every deploy.

-- The per-mode ladder. Combat level is derived in the app from the party max/avg level and badges
-- (the same formula the game server uses), so the raw inputs are exposed here rather than a
-- pre-rounded number. Banned accounts are excluded.
CREATE OR REPLACE VIEW pokeplanet_web.leaderboard AS
SELECT
    c.id            AS character_id,
    c.mode,
    c.name,
    c.badges,
    c.pokedex_caught,
    c.play_time_s,
    c.graveyard_count,
    COALESCE(pt.max_level, 0)::int    AS party_max_level,
    COALESCE(pt.avg_level, 0)::float8 AS party_avg_level
FROM public.characters c
JOIN public.accounts a ON a.id = c.account_id
LEFT JOIN (
    SELECT character_id, MAX(level) AS max_level, AVG(level) AS avg_level
      FROM public.pokemon
     WHERE box_id = 0 AND NOT is_egg
     GROUP BY character_id
) pt ON pt.character_id = c.id
WHERE NOT a.banned;

-- The roll of the dead: one row per Pokemon a Deadman character has lost, newest first when the app
-- orders it. Species is the game's internal number; the site names it generically for now.
CREATE OR REPLACE VIEW pokeplanet_web.recent_deaths AS
SELECT
    c.name,
    c.mode,
    d.species,
    d.died_at
FROM public.deaths d
JOIN public.characters c ON c.id = d.character_id
JOIN public.accounts a ON a.id = c.account_id
WHERE NOT a.banned;

GRANT SELECT ON pokeplanet_web.leaderboard, pokeplanet_web.recent_deaths TO pokeplanet_web;
