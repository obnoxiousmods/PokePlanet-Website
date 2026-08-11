import { Check, Github } from "lucide-react";
import { roadmap } from "../lib/content";

export function RoadmapPage() {
  return <div className="page section"><div className="page-heading"><span className="eyebrow">Living roadmap</span><h1>Built in the open.</h1><p>What works today, what is being polished, and where the planet goes next.</p></div><div className="roadmap-grid">{roadmap.map(group => <article key={group.title}><span className={`roadmap-state ${group.state.toLowerCase()}`}>{group.state}</span><h2>{group.title}</h2><ul>{group.items.map(item => <li key={item}><Check size={15} />{item}</li>)}</ul></article>)}</div><div className="callout roadmap-source"><Github /><div><b>The repository is the source of truth</b><p>Technical detail, blockers, current work, and every implementation decision live in the synchronized README and roadmap.</p></div><a href="https://github.com/obnoxiousmods/PokePlanet/blob/master/ROADMAP.md">Full roadmap</a></div></div>;
}

