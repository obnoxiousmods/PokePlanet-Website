import { CheckCircle2, MessageCircle, Send } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";
import { api } from "../lib/api";
import { DISCORD_URL } from "../lib/content";

export function ContactPage() {
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [message, setMessage] = useState("");
  const [turnstileToken, setTurnstileToken] = useState("");
  const challenge = useRef<HTMLDivElement>(null);
  const siteKey = import.meta.env.VITE_TURNSTILE_SITE_KEY;
  useEffect(() => {
    if (!siteKey || !challenge.current) return;
    const script = document.createElement("script");
    script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
    script.async = true;
    script.onload = () => {
      const turnstile = (window as typeof window & { turnstile?: { render: (element: HTMLElement, options: Record<string, unknown>) => void } }).turnstile;
      turnstile?.render(challenge.current!, { sitekey: siteKey, theme: "dark", callback: setTurnstileToken, "expired-callback": () => setTurnstileToken("") });
    };
    document.head.append(script);
    return () => script.remove();
  }, [siteKey]);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setState("sending"); setMessage("");
    const form = new FormData(event.currentTarget);
    try { await api.contact({ ...(Object.fromEntries(form.entries()) as Record<string, string>), turnstile_token: turnstileToken }); setState("sent"); event.currentTarget.reset(); }
    catch (error) { setState("error"); setMessage(error instanceof Error ? error.message : "Could not send your message."); }
  }
  return <div className="page section contact-page"><div><span className="eyebrow">Contact the team</span><h1>Send a signal.</h1><p>For launch trouble, account questions, collaboration, or a quiet security heads-up.</p><a href={DISCORD_URL} className="discord-card"><MessageCircle /><span><b>Want a faster answer?</b><small>Join the Modding Cartel on Discord</small></span></a></div><form onSubmit={submit}><label>Your name<input name="name" maxLength={80} autoComplete="name" /></label><label>Reply email or Discord handle<input name="reply_to" maxLength={160} required /></label><label>What is this about?<select name="category"><option>Game support</option><option>Account help</option><option>Bug report</option><option>Security</option><option>Press or collaboration</option><option>Something else</option></select></label><label>Message<textarea name="message" minLength={20} maxLength={2000} required rows={7} /></label><input name="website" tabIndex={-1} autoComplete="off" className="honeypot" aria-hidden="true" /><div ref={challenge} />{siteKey && !turnstileToken && <small>Complete the anti-abuse check to send.</small>}<button className="button" disabled={state === "sending" || Boolean(siteKey && !turnstileToken)}>{state === "sent" ? <><CheckCircle2 />Sent</> : <><Send size={17} />{state === "sending" ? "Sending…" : "Send message"}</>}</button>{state === "error" && <p className="form-error">{message}</p>}<small>Protected by rate limits and abuse checks. Messages are delivered privately and are not stored by this website.</small></form></div>;
}
