"""Configuration management for pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Configuration
    llm_provider: str = Field(
        default="openai",
        description="LLM provider (openai, anthropic)"
    )

    llm_api_key: str = Field(
        ...,
        description="API key for the LLM provider"
    )

    llm_model: str = Field(
        default="gpt-4o-mini",
        description="Model to use for generation"
    )

    llm_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL for the LLM API"
    )

    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Temperature for generation",
    )

    # Embedding Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )

    embedding_dimension: int = Field(
        default=1536,
        description="Embedding vector dimension",
    )

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL"
    )

    db_pool_min_size: int = Field(
        default=5,
        description="Minimum database connection pool size",
    )

    db_pool_max_size: int = Field(
        default=20,
        description="Maximum database connection pool size",
    )

    # Workflow Configuration
    max_revisions: int = Field(
        default=3,
        description="Maximum revision iterations",
    )

    default_search_limit: int = Field(
        default=10,
        description="Default number of search results",
    )

    # WebUI Configuration
    webui_host: str = Field(
        default="0.0.0.0",
        description="WebUI host address",
    )

    webui_port: int = Field(
        default=7860,
        description="WebUI port",
    )

    webui_share: bool = Field(
        default=False,
        description="Create public share link",
    )

    # Chunking Configuration
    chunk_size: int = Field(
        default=512,
        description="Document chunk size in characters",
    )

    chunk_overlap: int = Field(
        default=50,
        description="Chunk overlap in characters",
    )

    # Search Configuration
    default_text_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for text matching in hybrid search",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # LLM tokens
    llm_max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for LLM response",
    )


def get_settings() -> Settings:
    """Get settings instance.

    Returns:
        Settings: Application settings.
    """
    return Settings()


def load_settings() -> Settings:
    """Load settings with proper error handling.

    Returns:
        Settings: Application settings instance.

    Raises:
        ValueError: If required configuration is missing.
    """
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "llm_api_key" in str(e).lower():
            error_msg += "\nMake sure to set LLM_API_KEY in your .env file"
        if "database_url" in str(e).lower():
            error_msg += "\nMake sure to set DATABASE_URL in your .env file"
        raise ValueError(error_msg) from e
