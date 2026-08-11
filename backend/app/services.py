import asyncio
import re
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any

import httpx

from .settings import Settings

PLATFORMS = ("windows", "linux", "macos", "android")


def classify_asset(name: str) -> tuple[str | None, str, str]:
    lower = name.lower()
    platform = next((item for item in PLATFORMS if item in lower), None)
    if platform is None:
        if lower.endswith((".exe", ".msi")):
            platform = "windows"
        elif lower.endswith((".dmg", ".pkg")):
            platform = "macos"
        elif lower.endswith((".apk", ".aab")):
            platform = "android"
        elif "appimage" in lower or lower.endswith((".tar.gz", ".tar.xz", ".tar.zst")):
            platform = "linux"
    architecture = "universal"
    for marker, label in (
        ("arm64", "arm64"),
        ("aarch64", "arm64"),
        ("x86_64", "x86-64"),
        ("x64", "x86-64"),
        ("i686", "x86"),
    ):
        if marker in lower:
            architecture = label
            break
    if architecture == "universal" and re.search(r"(?:^|[-_.])x86(?:[-_.]|$)", lower):
        architecture = "x86"
    suffixes = (".tar.zst", ".tar.xz", ".tar.gz", ".appimage", ".7z", ".zip", ".dmg", ".exe", ".apk", ".aab")
    fmt = next((suffix.lstrip(".").upper() for suffix in suffixes if lower.endswith(suffix)), "FILE")
    return platform, architecture, fmt


class GitHubReleases:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client
        self.cached: tuple[float, dict[str, Any]] | None = None

    async def latest(self) -> dict[str, Any]:
        if self.cached and self.cached[0] > time.monotonic():
            return self.cached[1]
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.settings.github_token:
            headers["Authorization"] = f"Bearer {self.settings.github_token}"
        url = f"https://api.github.com/repos/{self.settings.github_repository}/releases?per_page=10"
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            releases = response.json()
            release = releases[0] if releases else None
        except (httpx.HTTPError, ValueError):
            release = None
        result: dict[str, Any] = {
            "version": None,
            "published_at": None,
            "prerelease": True,
            "release_url": f"https://github.com/{self.settings.github_repository}/releases",
            "notes": "The first coordinated alpha is being verified.",
            "assets": [],
            "platforms": {platform: "coming_soon" for platform in PLATFORMS},
        }
        if release:
            result.update(
                version=release.get("tag_name"),
                published_at=release.get("published_at"),
                prerelease=bool(release.get("prerelease")),
                release_url=release.get("html_url", result["release_url"]),
                notes=(release.get("body") or "")[:8000],
            )
            checksums = await self._checksums(release.get("assets", []))
            for item in release.get("assets", []):
                platform, architecture, fmt = classify_asset(item.get("name", ""))
                if not platform or item.get("name") == "release-manifest.json":
                    continue
                result["assets"].append(
                    {
                        "name": item["name"],
                        "platform": platform,
                        "architecture": architecture,
                        "format": fmt,
                        "size": item.get("size", 0),
                        "sha256": checksums.get(item["name"]),
                        "download_url": item["browser_download_url"],
                    }
                )
                result["platforms"][platform] = "available"
        self.cached = (time.monotonic() + 300, result)
        return result

    async def _checksums(self, assets: list[dict[str, Any]]) -> dict[str, str]:
        asset = next((item for item in assets if item.get("name") == "SHA256SUMS"), None)
        if not asset:
            return {}
        try:
            response = await self.client.get(asset["browser_download_url"])
            response.raise_for_status()
        except httpx.HTTPError:
            return {}
        return {
            name: digest
            for digest, name in re.findall(r"^([a-fA-F0-9]{64})\s+\*?(.+)$", response.text, re.MULTILINE)
        }


class RateLimiter:
    def __init__(self, limit: int = 5, window_seconds: int = 3600) -> None:
        self.limit = limit
        self.window = window_seconds
        self.hits: defaultdict[str, deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def allow(self, key: str) -> bool:
        now = time.monotonic()
        async with self.lock:
            values = self.hits[key]
            while values and values[0] < now - self.window:
                values.popleft()
            if len(values) >= self.limit:
                return False
            values.append(now)
            return True


async def public_status(settings: Settings, client: httpx.AsyncClient) -> dict[str, Any]:
    try:
        response = await client.get(settings.game_status_url, timeout=2.5)
        response.raise_for_status()
        match = re.search(r"(\d+) online", response.text)
        count = int(match.group(1)) if match else 0
        state = "online"
    except httpx.HTTPError:
        count, state = 0, "offline"
    return {
        "state": state,
        "online_players": count,
        "game_version": settings.game_version,
        "checked_at": datetime.now(UTC).isoformat(),
    }
