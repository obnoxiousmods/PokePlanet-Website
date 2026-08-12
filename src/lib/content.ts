import { Ban, Cloud, Gauge, MessagesSquare, ShieldCheck, Skull, Swords, Trophy } from "lucide-react";

export const DISCORD_URL = "https://discord.gg/moddingcartel";
export const GAME_SOURCE_URL = "https://github.com/obnoxiousmods/PokePlanet";
export const SITE_SOURCE_URL = "https://github.com/obnoxiousmods/PokePlanet-Website";
export const GAMEPLAY_VIDEO_URL = "https://ss.obby.ca/t_2026_08_10_02_01_24_DLA0eV.mp4";

// The pillars that make Deadman what it is -- the headline of the whole site.
export const deadmanPillars = [
  { icon: Skull, title: "Death is permanent", text: "Faint outside a Pokémon Center and that Pokémon is gone for good — laid to rest in a read-only graveyard it never leaves." },
  { icon: Ban, title: "Capped to your next gym", text: "Party levels and size are gated to the badge ahead of you. Every gym is a real wall; you cannot out-grind it." },
  { icon: Swords, title: "Everything on the line", text: "Lose a fight in the wild and you drop what you carry. Run out of Pokémon entirely and the run resets to nothing." },
  { icon: Trophy, title: "One life, ranked", text: "A combat level and a survival ladder track how far you have pushed a run that can end in a single careless step." },
];

export const features = [
  { icon: Skull, title: "Permadeath, server-enforced", text: "A death is final and validated on the server — there is no save-scum, no local file to edit, no way to undo it." },
  { icon: Swords, title: "High-stakes PvP", text: "Face another Deadman trainer near your badge count and the loser drops everything they were carrying to the floor." },
  { icon: Gauge, title: "A world that pushes back", text: "Slow experience, scarce money, and low catch rates mean every capture and purchase is a decision you plan for." },
  { icon: ShieldCheck, title: "Impossible to cheat", text: "Movement, saves, progression, deaths, and the economy are all authored server-side. The client only ever asks." },
  { icon: MessagesSquare, title: "Chat that belongs in-game", text: "Talk globally, locally, or privately without leaving the world — and read the room before you pick a fight." },
  { icon: Cloud, title: "Your run, everywhere", text: "Your Deadman character lives on the server and follows you between supported devices, life and all." },
];

export const guides = [
  { slug: "getting-started", eyebrow: "Start here", title: "Your first five minutes", summary: "Download, sign in with Discord, and step into Hoenn.", time: "3 min", steps: ["Choose your platform on the Download page.", "Extract the portable build or run the installer.", "Launch PokePlanet and select Sign in.", "Approve the Discord prompt in your browser.", "Return to the game—your trainer is ready automatically."] },
  { slug: "controls", eyebrow: "Play", title: "Controls and shortcuts", summary: "Movement, menus, chat, battles, and controllers.", time: "4 min", steps: ["Use the arrow keys or D-pad to move.", "Z / controller A confirms; X / controller B goes back.", "Enter opens the field menu.", "S opens chat; use /s for local chat and /w NAME for whispers.", "Controllers are detected through SDL2 and can be customized in Options."] },
  { slug: "multiplayer", eyebrow: "Together", title: "Battles, chat, and presence", summary: "Everything that changes when Hoenn becomes an MMO.", time: "5 min", steps: ["Players on your map appear as animated trainers.", "Use global, map, and private chat scopes.", "Face another trainer and send a battle invitation.", "Only one active session can control your trainer at a time.", "Progress is autosaved to your server-side character."] },
  { slug: "troubleshooting", eyebrow: "Support", title: "Fix common launch issues", summary: "Fast answers for sign-in, security prompts, and graphics.", time: "6 min", steps: ["Confirm you downloaded the artifact for your operating system and CPU.", "Keep the game and pokeplanet-net sidecar together.", "Allow the app through your firewall when prompted.", "On unsigned prereleases, follow the platform-specific security note on the Download page.", "If sign-in expires, return to the game and request a fresh browser link."] },
];

export const roadmap = [
  { state: "Live", title: "Connected world", items: ["Server-authoritative movement", "Animated nearby players", "Map-indexed presence", "Shared spawn and position"] },
  { state: "Live", title: "Persistent trainers", items: ["Discord sign-in", "Server-side characters and saves", "Automatic saving", "Portable identity across devices"] },
  { state: "Live", title: "Multiplayer", items: ["Global, local, and private chat", "Player-vs-player link battles", "Server-configured gameplay rates", "Single active session"] },
  { state: "Building", title: "Beyond Emerald", items: ["Per-player colour identity", "Expanded live configuration", "Replay-based validation", "Polished cross-platform clients"] },
];

