"""
config.py
=========
Central configuration for ResearchCompass.

All environment-driven configuration is loaded here exactly once and
exposed as a single `settings` object so the rest of the codebase never
touches `os.environ` directly. This keeps configuration testable and
makes it trivial to see, at a glance, every external dependency the
system has.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env as early as possible, before any other module reads env vars.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    val = os.getenv(name)
    try:
        return int(val) if val is not None else default
    except ValueError:
        return default


@dataclass
class Settings:
    # --- Paths -----------------------------------------------------------
    base_dir: Path = BASE_DIR
    data_dir: Path = BASE_DIR / "data"
    faculty_dir: Path = BASE_DIR / "data" / "faculty"
    trends_cache_dir: Path = BASE_DIR / "data" / "trends_cache"
    logs_dir: Path = BASE_DIR / "data" / "logs"
    chroma_dir: Path = BASE_DIR / "chroma_db"
    sqlite_path: Path = BASE_DIR / "data" / "logs" / "research_compass.db"

    # --- LLM ---------------------------------------------------------------
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    llm_temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.3")))

    # --- Embeddings ----------------------------------------------------------
    embedding_provider: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
    )
    embedding_model: str = field(
        default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    )

    # --- External APIs -------------------------------------------------------
    tavily_api_key: str = field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    semantic_scholar_api_key: str = field(
        default_factory=lambda: os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
    )

    # --- SMTP / email --------------------------------------------------------
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", ""))
    smtp_port: int = field(default_factory=lambda: _get_int("SMTP_PORT", 587))
    smtp_user: str = field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    smtp_use_tls: bool = field(default_factory=lambda: _get_bool("SMTP_USE_TLS", True))
    email_from: str = field(default_factory=lambda: os.getenv("EMAIL_FROM", ""))

    # --- Behaviour flags -----------------------------------------------------
    require_confirmation: bool = field(
        default_factory=lambda: _get_bool("REQUIRE_CONFIRMATION", True)
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # --- Retrieval -------------------------------------------------------------
    chroma_collection_name: str = "faculty_profiles"
    top_k_faculty: int = field(default_factory=lambda: _get_int("TOP_K_FACULTY", 5))

    def __post_init__(self) -> None:
        for p in (self.data_dir, self.faculty_dir, self.trends_cache_dir, self.logs_dir, self.chroma_dir):
            p.mkdir(parents=True, exist_ok=True)

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key)

    @property
    def has_smtp(self) -> bool:
        return bool(self.smtp_host and self.smtp_user and self.smtp_password)


settings = Settings()
