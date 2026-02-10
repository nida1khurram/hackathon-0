from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root: 2 parents up from this file (backend/app/config.py -> backend -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / "backend" / ".env",
        env_file_encoding="utf-8",
    )

    VAULT_PATH: str = "../vault"
    OWNER: str = "AI Employee"
    BUSINESS: str = "My Business"

    # Gmail watcher
    GMAIL_CREDENTIALS_PATH: str = "credentials.json"
    GMAIL_TOKEN_PATH: str = "token.json"
    GMAIL_POLL_INTERVAL: int = 120
    GMAIL_QUERY: str = "is:unread is:important"
    DRY_RUN: bool = True

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    @property
    def vault_dir(self) -> Path:
        """Resolve VAULT_PATH to an absolute path relative to project root."""
        p = Path(self.VAULT_PATH)
        if p.is_absolute():
            return p
        return (PROJECT_ROOT / p).resolve()

    @property
    def credentials_path(self) -> Path:
        p = Path(self.GMAIL_CREDENTIALS_PATH)
        if p.is_absolute():
            return p
        return (PROJECT_ROOT / p).resolve()

    @property
    def token_path(self) -> Path:
        p = Path(self.GMAIL_TOKEN_PATH)
        if p.is_absolute():
            return p
        return (PROJECT_ROOT / p).resolve()


settings = Settings()
