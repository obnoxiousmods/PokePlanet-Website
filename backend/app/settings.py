from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    base_url: str = "http://localhost:5173"
    session_secret: str = "development-only-change-me"
    session_cookie: str = "pp_session"
    session_days: int = 30

    database_url: str | None = None
    game_status_url: str = "http://127.0.0.1:8790/health"
    game_version: str | None = None

    discord_client_id: str | None = None
    discord_client_secret: str | None = None
    discord_invite_url: str = "https://discord.gg/moddingcartel"
    contact_webhook_url: str | None = None
    turnstile_secret: str | None = None

    github_repository: str = "obnoxiousmods/PokePlanet"
    github_token: str | None = Field(default=None, repr=False)
    frontend_dist: str = str(Path(__file__).resolve().parents[2] / "dist")

    @property
    def production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def oauth_callback_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/auth/discord/callback"

    def validate_production(self) -> None:
        if not self.production:
            return
        missing = [
            name
            for name, value in {
                "SESSION_SECRET": self.session_secret
                if self.session_secret != "development-only-change-me"
                else None,
                "DATABASE_URL": self.database_url,
                "DISCORD_CLIENT_ID": self.discord_client_id,
                "DISCORD_CLIENT_SECRET": self.discord_client_secret,
                "CONTACT_WEBHOOK_URL": self.contact_webhook_url,
                "TURNSTILE_SECRET": self.turnstile_secret,
            }.items()
            if not value
        ]
        if missing:
            raise RuntimeError(f"Missing required production settings: {', '.join(missing)}")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production()
    return settings
