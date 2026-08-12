import { Github, Menu, X } from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { DISCORD_URL, GAME_SOURCE_URL } from "../lib/content";
import { ThemePanel } from "./ThemePanel";

const links = [["/ladder", "Ladder"], ["/download", "Download"], ["/guides", "Guides"], ["/about", "About"], ["/roadmap", "Roadmap"], ["/media", "Media"]];

export function Logo() {
  return <Link to="/" className="logo" aria-label="PokePlanet home"><span className="logo-orbit"><i /></span><span>Poke<span>Planet</span></span></Link>;
}

export function Layout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="site-shell">
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="site-header"><Logo /><nav className={open ? "is-open" : ""} aria-label="Primary navigation">{links.map(([path, label]) => <NavLink key={path} to={path} onClick={() => setOpen(false)}>{label}</NavLink>)}<a href={DISCORD_URL} target="_blank" rel="noreferrer">Community</a></nav><div className="header-actions"><ThemePanel /><a className="button button-small button-ghost desktop-only" href={GAME_SOURCE_URL} target="_blank" rel="noreferrer"><Github size={16} />Source</a><Link className="button button-small" to="/account">Sign in</Link><button className="menu-button" aria-label="Toggle menu" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button></div></header>
      <main id="main"><Outlet /></main>
      <footer><div className="footer-grid"><div><Logo /><p>Pokémon Emerald, imagined as a living online world.</p></div><div><b>Explore</b><Link to="/download">Download</Link><Link to="/guides">Guides</Link><Link to="/roadmap">Roadmap</Link></div><div><b>Connect</b><a href={DISCORD_URL}>Discord</a><Link to="/contact">Contact</Link><a href={GAME_SOURCE_URL}>GitHub</a></div><div><b>Project</b><Link to="/privacy">Privacy</Link><Link to="/terms">Terms</Link><a href="https://github.com/obnoxiousmods/PokePlanet/blob/master/LICENSE">License</a></div></div><div className="legal">PokePlanet is an unofficial fan project and is not affiliated with Nintendo, Creatures Inc., GAME FREAK, or The Pokémon Company. Pokémon and related marks belong to their respective owners.<span>Built openly, with no pay-to-win.</span></div></footer>
    </div>
  );
}

