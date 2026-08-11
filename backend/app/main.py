import base64
import hashlib
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
from starlette.applications import Starlette
from starlette.datastructures import URL
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Route

from .services import GitHubReleases, RateLimiter, public_status
from .sessions import SessionStore, new_token
from .settings import Settings, get_settings


class WebsiteState:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.http = httpx.AsyncClient(
            timeout=10, follow_redirects=True, headers={"User-Agent": "PokePlanet-Website/0.1"}
        )
        self.sessions = SessionStore(settings.database_url, settings.session_days)
        self.releases = GitHubReleases(settings, self.http)
        self.contact_limiter = RateLimiter(limit=5, window_seconds=3600)

    async def start(self) -> None:
        await self.sessions.connect()

    async def close(self) -> None:
        await self.sessions.close()
        await self.http.aclose()


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        state: WebsiteState = request.app.state.services
        token = request.cookies.get(state.settings.session_cookie)
        request.state.session_token = token
        request.state.session = await state.sessions.load(token)
        request.state.session_dirty = False
        request.state.session_delete = False
        response = await call_next(request)
        if request.state.session_delete:
            await state.sessions.delete(token)
            response.delete_cookie(state.settings.session_cookie, path="/")
        elif request.state.session_dirty:
            token = token or new_token()
            await state.sessions.save(token, request.state.session)
            response.set_cookie(
                state.settings.session_cookie,
                token,
                max_age=state.settings.session_days * 86400,
                httponly=True,
                secure=state.settings.production,
                samesite="lax",
                path="/",
            )
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self' https://challenges.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://cdn.discordapp.com; "
            "media-src 'self' https://ss.obby.ca; connect-src 'self' https://challenges.cloudflare.com; "
            "frame-src https://challenges.cloudflare.com; frame-ancestors 'none'; "
            "base-uri 'self'; form-action 'self'",
        )
        return response


def services(request: Request) -> WebsiteState:
    return request.app.state.services


def fail(detail: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"detail": detail}, status_code=status)


def valid_origin(request: Request) -> bool:
    origin = request.headers.get("origin")
    if not origin:
        return not services(request).settings.production
    expected = URL(services(request).settings.base_url)
    supplied = URL(origin)
    return (supplied.scheme, supplied.netloc) == (expected.scheme, expected.netloc)


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"ok": True, "service": "pokeplanet-web", "version": "0.1.0"})


async def status(request: Request) -> JSONResponse:
    state = services(request)
    return JSONResponse(await public_status(state.settings, state.http))


async def releases(request: Request) -> JSONResponse:
    return JSONResponse(await services(request).releases.latest())


async def oauth_start(request: Request) -> RedirectResponse | JSONResponse:
    cfg = services(request).settings
    if not cfg.discord_client_id or not cfg.discord_client_secret:
        return fail("Discord sign-in is not configured yet.", 503)
    state_token = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    request.state.session.update(oauth_state=state_token, pkce_verifier=verifier)
    request.state.session_dirty = True
    query = urlencode(
        {
            "client_id": cfg.discord_client_id,
            "redirect_uri": cfg.oauth_callback_url,
            "response_type": "code",
            "scope": "identify",
            "state": state_token,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "prompt": "none",
        }
    )
    return RedirectResponse(f"https://discord.com/oauth2/authorize?{query}", status_code=302)


async def oauth_callback(request: Request) -> RedirectResponse | JSONResponse:
    cfg = services(request).settings
    query = request.query_params
    supplied_state = query.get("state", "")
    expected_state = request.state.session.pop("oauth_state", "")
    verifier = request.state.session.pop("pkce_verifier", "")
    request.state.session_dirty = True
    if query.get("error"):
        return RedirectResponse("/account?error=cancelled", status_code=303)
    if (
        not query.get("code")
        or not expected_state
        or not secrets.compare_digest(supplied_state, expected_state)
    ):
        return fail("That Discord sign-in was invalid or expired.", 400)
    try:
        token_response = await services(request).http.post(
            "https://discord.com/api/v10/oauth2/token",
            data={
                "client_id": cfg.discord_client_id,
                "client_secret": cfg.discord_client_secret,
                "grant_type": "authorization_code",
                "code": query["code"],
                "redirect_uri": cfg.oauth_callback_url,
                "code_verifier": verifier,
            },
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]
        user_response = await services(request).http.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_response.raise_for_status()
        discord = user_response.json()
    except (httpx.HTTPError, KeyError, ValueError):
        return fail("Discord could not verify that sign-in.", 502)
    avatar = (
        f"https://cdn.discordapp.com/avatars/{discord['id']}/{discord['avatar']}.png?size=128"
        if discord.get("avatar")
        else ""
    )
    request.state.session["user"] = {
        "id": str(discord["id"]),
        "username": discord["username"],
        "display_name": discord.get("global_name") or discord["username"],
        "avatar_url": avatar,
    }
    return RedirectResponse("/account", status_code=303)


async def me(request: Request) -> JSONResponse:
    user = request.state.session.get("user")
    if not user:
        return JSONResponse({"authenticated": False, "user": None, "character": None})
    character = await services(request).sessions.profile_for_discord(user["id"])
    return JSONResponse({"authenticated": True, "user": user, "character": character})


async def logout(request: Request) -> JSONResponse:
    if not valid_origin(request):
        return fail("Invalid request origin.", 403)
    request.state.session_delete = True
    return JSONResponse({"ok": True})


async def verify_turnstile(state: WebsiteState, token: str, remote_ip: str) -> bool:
    if not state.settings.turnstile_secret:
        # Turnstile is an optional second layer. The honeypot plus application and
        # nginx rate limits remain active when a site has not provisioned keys yet.
        return True
    try:
        response = await state.http.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": state.settings.turnstile_secret, "response": token, "remoteip": remote_ip},
        )
        response.raise_for_status()
        return bool(response.json().get("success"))
    except (httpx.HTTPError, ValueError):
        return False


def client_ip(request: Request) -> str:
    direct = request.client.host if request.client else "unknown"
    if direct in {"127.0.0.1", "::1"}:
        return request.headers.get("x-forwarded-for", direct).split(",")[0].strip()
    return direct


async def contact(request: Request) -> JSONResponse:
    state = services(request)
    if not valid_origin(request):
        return fail("Invalid request origin.", 403)
    try:
        payload: dict[str, Any] = await request.json()
    except ValueError:
        return fail("Invalid message.")
    if payload.get("website"):
        return JSONResponse({"ok": True})
    remote_ip = client_ip(request)
    if not await state.contact_limiter.allow(remote_ip):
        return fail("Too many messages. Please try again later.", 429)
    message = str(payload.get("message", "")).strip()
    reply_to = str(payload.get("reply_to", "")).strip()
    name = str(payload.get("name", "Anonymous")).strip() or "Anonymous"
    category = str(payload.get("category", "Something else")).strip()
    if not (20 <= len(message) <= 2000) or not (1 <= len(reply_to) <= 160) or len(name) > 80:
        return fail("Please check the message fields and try again.")
    if not await verify_turnstile(state, str(payload.get("turnstile_token", "")), remote_ip):
        return fail("Abuse check failed. Please refresh and try again.", 403)
    if not state.settings.contact_webhook_url:
        return fail("Contact delivery is not configured yet.", 503)
    safe_message = message.replace("@", "＠")
    body = {
        "username": "PokePlanet Contact",
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "title": category[:200],
                "description": safe_message,
                "color": 6422437,
                "fields": [
                    {"name": "From", "value": name[:80], "inline": True},
                    {"name": "Reply to", "value": reply_to.replace("@", "＠")[:160], "inline": True},
                ],
            }
        ],
    }
    try:
        response = await state.http.post(state.settings.contact_webhook_url, json=body)
        response.raise_for_status()
    except httpx.HTTPError:
        return fail("The message could not be delivered. Please use Discord instead.", 502)
    return JSONResponse({"ok": True})


async def frontend(request: Request) -> Response:
    state = services(request)
    dist = Path(state.settings.frontend_dist).expanduser().resolve()
    requested = dist / request.path_params.get("path", "")
    if requested.is_file() and requested.resolve().is_relative_to(dist):
        response = FileResponse(requested)
        if "/assets/" in request.url.path:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response
    index = dist / "index.html"
    if index.is_file():
        return FileResponse(index, headers={"Cache-Control": "no-cache"})
    return fail("Frontend build not found. Run npm run build.", 503)


def create_app(settings: Settings | None = None) -> Starlette:
    cfg = settings or get_settings()
    state = WebsiteState(cfg)

    @asynccontextmanager
    async def lifespan(app: Starlette):
        app.state.services = state
        await state.start()
        yield
        await state.close()

    app = Starlette(
        debug=not cfg.production,
        lifespan=lifespan,
        routes=[
            Route("/api/health", health),
            Route("/api/status", status),
            Route("/api/releases", releases),
            Route("/api/auth/discord/start", oauth_start),
            Route("/api/auth/discord/callback", oauth_callback),
            Route("/api/auth/logout", logout, methods=["POST"]),
            Route("/api/me", me),
            Route("/api/contact", contact, methods=["POST"]),
            Route("/{path:path}", frontend),
        ],
    )
    app.state.services = state
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(SessionMiddleware)
    return app


app = create_app()
