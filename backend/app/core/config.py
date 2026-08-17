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
    environment: str = "development"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = [".xml", ".pdf"]

    # Official KoSIT EN 16931 / XRechnung validator (Java CLI).
    # Required when environment is production, or when kosit_required is true.
    kosit_java_bin: str = "java"
    kosit_validator_jar: Optional[str] = None
    kosit_scenarios_xml: Optional[str] = None
    kosit_timeout_seconds: int = 60
    kosit_required: bool = False

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


settings: Settings = Settings()
