import os
import secrets
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "FLYYY.AI Privacy-Preserving CDP"
    VERSION: str = "1.0.0"

    # Separate Database URLs (supports PostgreSQL or SQLite)
    DATABASE_URL_SOURCE: str = "sqlite:///./source.db"
    DATABASE_URL_PROTECTED: str = "sqlite:///./protected.db"
    DATABASE_URL_VAULT: str = "sqlite:///./vault.db"
    DATABASE_URL_POLICY: str = "sqlite:///./policy.db"
    DATABASE_URL_AUDIT: str = "sqlite:///./audit.db"

    # Cryptographic keys (Hex format, 256-bit = 64 hex chars)
    # Generated securely if not provided in environment
    FPE_KEY_HEX: str = os.getenv("FPE_KEY_HEX", secrets.token_hex(32))
    VAULT_KEY_HEX: str = os.getenv("VAULT_KEY_HEX", secrets.token_hex(32))
    TOKEN_KEY_HEX: str = os.getenv("TOKEN_KEY_HEX", secrets.token_hex(32))

    # JWT Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", secrets.token_hex(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Local SMTP (Mailpit)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_FROM_EMAIL: str = "noreply@flyyy.ai"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:80",
        "http://127.0.0.1:80",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


settings = Settings()
