import { Apple, CheckCircle2, Download, ExternalLink, Github, Monitor, Smartphone, Terminal } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api, formatBytes } from "../lib/api";
import type { Platform, ReleasesResponse } from "../lib/types";

const platformInfo: Record<Platform, { label: string; icon: typeof Monitor; requirement: string; formats: string }> = {
  windows: { label: "Windows", icon: Monitor, requirement: "Windows 10 or newer", formats: "Installer · ZIP · 7z" },
  linux: { label: "Linux", icon: Terminal, requirement: "Modern x86-64 distribution", formats: "AppImage · portable archive" },
  macos: { label: "macOS", icon: Apple, requirement: "macOS 12 or newer", formats: "Universal DMG · ZIP" },
  android: { label: "Android", icon: Smartphone, requirement: "Android 5.0 or newer", formats: "APK · AAB" },
};

function detectPlatform(): Platform {
  const value = navigator.userAgent.toLowerCase();
  if (value.includes("android")) return "android";
  if (value.includes("mac")) return "macos";
  if (value.includes("linux")) return "linux";
  return "windows";
}

export function DownloadPage() {
  const [data, setData] = useState<ReleasesResponse | null>(null);
  const [selected, setSelected] = useState<Platform>(detectPlatform);
  useEffect(() => { api.releases().then(setData).catch(() => undefined); }, []);
  const assets = useMemo(() => data?.assets.filter(asset => asset.platform === selected) ?? [], [data, selected]);
  const current = platformInfo[selected];
  const CurrentIcon = current.icon;
  return <div className="page section"><div className="page-heading"><span className="eyebrow">Choose your platform</span><h1>Start your adventure.</h1><p>Standalone builds—no emulator, patching, or separate ROM required.</p></div><div className="platform-tabs" role="tablist">{(Object.keys(platformInfo) as Platform[]).map(platform => { const Info = platformInfo[platform]; const Icon = Info.icon; return <button role="tab" aria-selected={selected === platform} className={selected === platform ? "active" : ""} onClick={() => setSelected(platform)} key={platform}><Icon size={20} />{Info.label}<span className={`availability ${data?.platforms[platform] ?? "coming_soon"}`} /></button>; })}</div>
    <section className="download-panel"><div className="download-title"><CurrentIcon size={38} /><div><span className="eyebrow">{data?.version ?? "First alpha in progress"}</span><h2>PokePlanet for {current.label}</h2><p>{current.requirement} · {current.formats}</p></div></div>{assets.length ? <div className="asset-list">{assets.map(asset => <a href={asset.download_url} key={asset.name}><span><b>{asset.name}</b><small>{asset.architecture} · {asset.format} · {formatBytes(asset.size)}</small></span><Download /></a>)}</div> : <div className="coming-soon"><span>Release candidate building</span><p>This platform is part of the coordinated alpha. Downloads appear here only after the build launches, connects, and passes verification.</p><a href="https://github.com/obnoxiousmods/PokePlanet/releases" className="button button-ghost"><Github size={17} />Watch GitHub Releases</a></div>}
      <div className="checksum-note"><CheckCircle2 size={18} /><span><b>Verified downloads</b>Every release includes SHA-256 checksums and a machine-readable manifest.</span></div></section>
    <section className="install-steps"><div className="section-heading left"><span className="eyebrow">Quick start</span><h2>From download to Littleroot.</h2></div><ol><li><span>01</span><div><b>Get the build</b><p>Choose the installer or portable package for your system.</p></div></li><li><span>02</span><div><b>Launch PokePlanet</b><p>Keep the included network component beside the game.</p></div></li><li><span>03</span><div><b>Sign in with Discord</b><p>Your browser verifies who you are, then returns control to the game.</p></div></li></ol><a href="/guides/getting-started" className="text-link">Read the complete installation guide <ExternalLink size={15} /></a></section>
  </div>;
}
