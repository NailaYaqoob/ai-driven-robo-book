"""Application configuration using Pydantic settings."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")

    # API Configuration
    API_V1_PREFIX: str = Field(default="/api", description="API v1 prefix")
    PROJECT_NAME: str = Field(default="Physical AI & Humanoid Robotics Textbook API", description="Project name")
    VERSION: str = Field(default="1.0.0", description="API version")

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "https://ai-driven-robo-book.vercel.app",
        ],
        description="Comma-separated list of allowed origins for CORS",
    )

    # Database Configuration
    NEON_DATABASE_URL: str = Field(default="", description="Neon Postgres database URL")

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for embeddings and completions")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model for chat completions")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    OPENAI_EMBEDDING_DIMENSIONS: int = Field(default=1536, description="Embedding dimensions")

    # Qdrant Configuration
    QDRANT_URL: str = Field(default="", description="Qdrant cloud URL")
    QDRANT_API_KEY: str = Field(default="", description="Qdrant API key")
    QDRANT_COLLECTION_NAME: str = Field(default="humanoid_robotics_textbook", description="Qdrant collection name")

    # RAG Configuration
    RAG_CHUNK_SIZE: int = Field(default=512, description="Chunk size in tokens for content splitting")
    RAG_CHUNK_OVERLAP: int = Field(default=50, description="Overlap between chunks in tokens")
    RAG_TOP_K: int = Field(default=5, description="Number of chunks to retrieve for RAG")
    RAG_MAX_TOKENS: int = Field(default=1500, description="Max tokens for RAG response generation")

    # Better-Auth Configuration
    BETTER_AUTH_SECRET: str = Field(default="", description="Better-Auth secret key")
    BETTER_AUTH_CLIENT_ID: str = Field(default="", description="Better-Auth client ID")
    BETTER_AUTH_CLIENT_SECRET: str = Field(default="", description="Better-Auth client secret")

    # JWT Configuration
    JWT_SECRET_KEY: str = Field(default="", description="JWT secret key for token signing")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_DAYS: int = Field(default=7, description="JWT token expiration in days")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="API rate limit per minute per IP")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("NEON_DATABASE_URL", mode="before")
    @classmethod
    def convert_postgres_url_to_async(cls, v: str) -> str:
        """Convert to asyncpg driver and strip psycopg-only query params.

        asyncpg uses ``ssl=`` and rejects ``sslmode=`` — Neon's default URL ships with
        ``?sslmode=require``, which crashes SQLAlchemy at connect time. We drop those
        psycopg-only params here; SSL is enforced via ``connect_args`` in database.py.
        """
        if not v:
            return v

        from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

        parts = urlsplit(v)
        if parts.query:
            psycopg_only = {"sslmode", "channel_binding", "options", "application_name"}
            kept = [(k, val) for k, val in parse_qsl(parts.query) if k not in psycopg_only]
            v = urlunsplit(parts._replace(query=urlencode(kept)))
        return v

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for FastAPI to get settings."""
    return settings
