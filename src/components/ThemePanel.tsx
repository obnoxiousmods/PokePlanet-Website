import { Check, Palette, X } from "lucide-react";
import { useEffect, useState } from "react";

const themes = [
  ["deadman", "Deadman", "#ff3b3b"],
  ["emerald", "Emerald", "#61f3a5"],
  ["sapphire", "Sapphire", "#58b9ff"],
  ["ruby", "Ruby", "#ff667d"],
  ["aqua", "Aqua", "#48e5e0"],
  ["magma", "Magma", "#ff9a5c"],
] as const;

export function ThemePanel() {
  const [open, setOpen] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem("pp-theme") || "deadman");
  const [compact, setCompact] = useState(() => localStorage.getItem("pp-compact") === "true");
  const [motion, setMotion] = useState(() => localStorage.getItem("pp-motion") !== "false");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.compact = String(compact);
    document.documentElement.dataset.motion = String(motion);
    localStorage.setItem("pp-theme", theme);
    localStorage.setItem("pp-compact", String(compact));
    localStorage.setItem("pp-motion", String(motion));
  }, [theme, compact, motion]);

  return (
    <>
      <button className="theme-trigger" onClick={() => setOpen(true)} aria-label="Customize appearance"><Palette size={18} /></button>
      {open && <div className="scrim" onClick={() => setOpen(false)} />}
      <aside className={`theme-panel ${open ? "is-open" : ""}`} aria-hidden={!open} aria-label="Customize PokePlanet">
        <div className="panel-head"><div><span className="eyebrow">Make it yours</span><h2>Trainer style</h2></div><button className="icon-button" onClick={() => setOpen(false)} aria-label="Close"><X /></button></div>
        <p className="muted">Choose a region-inspired signal colour. Your preference stays on this device.</p>
        <div className="theme-grid">
          {themes.map(([id, label, color]) => <button key={id} className={theme === id ? "selected" : ""} onClick={() => setTheme(id)}><i style={{ background: color }} />{label}{theme === id && <Check size={15} />}</button>)}
        </div>
        <label className="toggle-row"><span><b>Compact interface</b><small>Fit more on every screen</small></span><input type="checkbox" checked={compact} onChange={(event) => setCompact(event.target.checked)} /></label>
        <label className="toggle-row"><span><b>Interface motion</b><small>Turn off animated transitions</small></span><input type="checkbox" checked={motion} onChange={(event) => setMotion(event.target.checked)} /></label>
      </aside>
    </>
  );
}

