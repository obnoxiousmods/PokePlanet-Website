import httpx
import pytest

from app.main import create_app
from app.settings import Settings


@pytest.mark.asyncio
async def test_oauth_requires_configuration():
    app = create_app(Settings())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/auth/discord/start")
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_callback_rejects_missing_state():
    app = create_app(Settings(discord_client_id="client", discord_client_secret="secret"))
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/auth/discord/callback?code=bad&state=bad")
    assert response.status_code == 400
