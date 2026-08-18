from pathlib import Path
from typing import ClassVar, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_name: str = "eInvoice API"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    # json = one JSON object per line (production default). text = key=value lines.
    log_format: str = "json"
    environment: str = "development"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    cors_allow_credentials: bool = True
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = [".xml", ".pdf"]
    # 0 disables the in-app limiter (nginx limit_req remains the edge control).
    rate_limit_per_minute: int = 30
    request_timeout_seconds: int = 90
    kosit_java_max_heap_mb: int = 512

    # Official KoSIT EN 16931 / XRechnung validator (Java CLI).
    # Required when environment is production, or when kosit_required is true.
    kosit_java_bin: str = "java"
    kosit_validator_jar: Optional[str] = None
    kosit_scenarios_xml: Optional[str] = None
    kosit_timeout_seconds: int = 60
    kosit_required: bool = False

    # Alert watchdog (localhost scrape). Optional webhook receives no invoice data.
    alert_base_url: str = "http://127.0.0.1:8000"
    alert_webhook_url: Optional[str] = None
    alert_state_path: str = "alert_state.json"
    alert_scrape_timeout_seconds: int = 5

    # Text-only feedback. Optional webhook; never accepts invoice files.
    feedback_webhook_url: Optional[str] = None
    feedback_max_chars: int = 2000

    # Account foundation (Stage 1). Guest parse works without this.
    # Production with accounts must use postgresql:// — SQLite is for tests/dev only.
    database_url: Optional[str] = None
    auth_secret_key: str = "dev-only-change-me"
    auth_cookie_name: str = "einv_session"
    auth_session_days: int = 14
    auth_token_hours: int = 24
    admin_api_token: Optional[str] = None
    public_app_url: str = "http://localhost:5173"
    email_backend: str = "log"

    @property
    def effective_cors_origins(self) -> List[str]:
        """Production must not keep the local Vite origins unless explicitly set."""
        origins: List[str] = list(self.cors_origins)
        if not self.is_production:
            return origins
        local_only: set[str] = {
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }
        public_origins: List[str] = [item for item in origins if item not in local_only]
        return public_origins if public_origins else origins

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() in {"production", "prod"}

    @property
    def require_kosit(self) -> bool:
        return self.kosit_required or self.is_production

    @property
    def kosit_ready(self) -> bool:
        jar: Optional[str] = self.kosit_validator_jar
        scenarios: Optional[str] = self.kosit_scenarios_xml
        if not jar or not scenarios:
            return False
        return Path(jar).is_file() and Path(scenarios).is_file()

    @property
    def auth_enabled(self) -> bool:
        url: Optional[str] = self.database_url
        return bool(url and url.strip())

    @property
    def uses_postgres(self) -> bool:
        url: str = (self.database_url or "").strip().lower()
        return url.startswith("postgresql") or url.startswith("postgres")


settings: Settings = Settings()
