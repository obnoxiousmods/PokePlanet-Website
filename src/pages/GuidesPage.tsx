import { ArrowLeft, ArrowRight, BookOpen, Clock } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { guides } from "../lib/content";

export function GuidesPage() {
  const { slug } = useParams();
  const guide = guides.find(item => item.slug === slug);
  if (slug && guide) return <article className="article section"><Link className="back-link" to="/guides"><ArrowLeft size={16} />All guides</Link><span className="eyebrow">{guide.eyebrow}</span><h1>{guide.title}</h1><p className="article-lead">{guide.summary}</p><div className="article-meta"><Clock size={15} />{guide.time}</div><ol className="guide-steps">{guide.steps.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, "0")}</span><p>{step}</p></li>)}</ol><div className="callout"><b>Need a human?</b><p>The Modding Cartel community can help with releases, sign-in, controls, and bug reports.</p><a href="https://discord.gg/moddingcartel">Ask on Discord <ArrowRight size={15} /></a></div></article>;
  return <div className="page section"><div className="page-heading"><BookOpen /><span className="eyebrow">Trainer handbook</span><h1>Everything you need.<br />Nothing you do not.</h1><p>Short, tested guides for installing, playing, and understanding PokePlanet.</p></div><div className="guide-grid">{guides.map((item, index) => <Link to={`/guides/${item.slug}`} key={item.slug}><span className="guide-index">0{index + 1}</span><span className="eyebrow">{item.eyebrow}</span><h2>{item.title}</h2><p>{item.summary}</p><small><Clock size={14} />{item.time}<ArrowRight size={16} /></small></Link>)}</div></div>;
}

