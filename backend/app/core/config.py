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
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    max_upload_size_mb: int = 10
    allowed_extensions: List[str] = [".xml", ".pdf"]

    # Optional official KoSIT EN 16931 / XRechnung validator (Java CLI)
    kosit_java_bin: str = "java"
    kosit_validator_jar: Optional[str] = None
    kosit_scenarios_xml: Optional[str] = None
    kosit_timeout_seconds: int = 60


settings: Settings = Settings()
