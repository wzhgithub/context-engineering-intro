"""LLM client utilities."""

from typing import Optional
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI
from app.config import settings


_client: Optional[AsyncOpenAI] = None
_llm_model: Optional[ChatOpenAI] = None


def get_llm_client() -> AsyncOpenAI:
    """Get LLM client instance.

    Returns:
        AsyncOpenAI: Configured with settings.
    """
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
    return _client


def get_embedding_client() -> AsyncOpenAI:
    """Get embedding client instance.

    Returns:
        AsyncOpenAI: Configured with settings.
    """
    return get_llm_client()


def get_llm_model() -> ChatOpenAI:
    """Get the LLM model instance from settings.

    Returns:
        ChatOpenAI: Configured LangChain ChatOpenAI instance.
    """
    global _llm_model
    if _llm_model is None:
        _llm_model = ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            temperature=settings.llm_temperature,
        )
    return _llm_model


def get_embedding_model() -> str:
    """Get the embedding model name from settings."""
    return settings.embedding_model


def get_embedding_dimension() -> int:
    """Get the embedding dimension from settings."""
    return settings.embedding_dimension
