import { Skull, Trophy } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { DeathEntry, LadderEntry } from "../lib/types";

type Mode = "deadman" | "normal";

export function LadderPage() {
  const [mode, setMode] = useState<Mode>("deadman");
  const [entries, setEntries] = useState<LadderEntry[] | null>(null);
  const [deaths, setDeaths] = useState<DeathEntry[]>([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    let live = true;
    setEntries(null);
    setError(false);
    api
      .ladder(mode)
      .then((r) => live && setEntries(r.entries))
      .catch(() => live && setError(true));
    api
      .deaths(mode)
      .then((r) => live && setDeaths(r.deaths))
      .catch(() => live && setDeaths([]));
    return () => {
      live = false;
    };
  }, [mode]);

  const deadman = mode === "deadman";

  return (
    <div className="page section">
      <div className="page-heading">
        <span className="eyebrow">{deadman ? "Survival ladder" : "Standard ladder"}</span>
        <h1>{deadman ? "The still-living." : "The open world."}</h1>
        <p>
          {deadman
            ? "Every name here is a run still going — ranked by how far it has been pushed. Progress is capped to the next gym, and a single death can end it."
            : "Trainers of the classic world, ranked by badges, Pokédex, and time played."}
        </p>
      </div>

      <div className="ladder-tabs">
        <button className={deadman ? "active" : ""} onClick={() => setMode("deadman")}>
          <Skull size={15} /> Deadman
        </button>
        <button className={!deadman ? "active" : ""} onClick={() => setMode("normal")}>
          <Trophy size={15} /> Standard
        </button>
      </div>

      <div className="ladder-layout">
        <div className="ladder-main">
          {error ? (
            <p className="ladder-empty">The ladder is unavailable right now. Try again shortly.</p>
          ) : entries === null ? (
            <p className="ladder-empty">Loading the ladder…</p>
          ) : entries.length === 0 ? (
            <p className="ladder-empty">No one has set out in this world yet. Be the first.</p>
          ) : (
            <table className="ladder-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Trainer</th>
                  <th>Combat</th>
                  <th>Badges</th>
                  <th>Pokédex</th>
                  {deadman && <th>Lost</th>}
                  <th>Hours</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e) => (
                  <tr key={e.rank}>
                    <td className="rank">{e.rank}</td>
                    <td className="trainer">{e.name}</td>
                    <td className="combat">{e.combat_level}</td>
                    <td>{e.badges}</td>
                    <td>{e.pokedex_caught}</td>
                    {deadman && <td className="lost">{e.graveyard}</td>}
                    <td>{e.play_hours}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {deadman && (
          <aside className="death-feed">
            <h2>
              <Skull size={16} /> The recently fallen
            </h2>
            {deaths.length === 0 ? (
              <p className="ladder-empty">No deaths recorded yet.</p>
            ) : (
              <ul>
                {deaths.map((d, i) => (
                  <li key={i}>
                    <span className="who">{d.name}</span> lost a Pokémon
                    <span className="when">{d.died_on}</span>
                  </li>
                ))}
              </ul>
            )}
          </aside>
        )}
      </div>
    </div>
  );
}
