import httpx
import pytest

from app.main import create_app
from app.services import classify_asset
from app.settings import Settings


@pytest.fixture
def app():
    return create_app(Settings())


@pytest.mark.asyncio
async def test_health(app):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["service"] == "pokeplanet-web"
    assert response.headers["x-frame-options"] == "DENY"


@pytest.mark.asyncio
async def test_me_is_anonymous_without_session(app):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/me")
    assert response.json() == {"authenticated": False, "user": None, "character": None}


@pytest.mark.asyncio
async def test_contact_rejects_short_message(app):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/contact", json={"reply_to": "Ash", "message": "short"})
    assert response.status_code == 400


def test_asset_classification():
    assert classify_asset("PokePlanet-windows-x86.zip") == ("windows", "x86", "ZIP")
    assert classify_asset("PokePlanet-macos-arm64.dmg") == ("macos", "arm64", "DMG")
    assert classify_asset("PokePlanet-linux-x86_64.AppImage") == ("linux", "x86-64", "APPIMAGE")


def test_production_allows_optional_contact_protection():
    settings = Settings(
        environment="production",
        session_secret="a" * 32,
        database_url="postgresql://website@example.invalid/pokeplanet",
        discord_client_id="client",
        discord_client_secret="secret",
    )
    settings.validate_production()
