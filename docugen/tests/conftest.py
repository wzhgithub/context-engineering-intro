"""Pytest 配置文件。

提供测试 fixtures 和共享配置。
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环。"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """模拟设置。"""
    from pydantic import BaseModel

    class MockSettings(BaseModel):
        llm_provider: str = "openai"
        llm_api_key: str = "test-key"
        llm_model: str = "gpt-4o-mini"
        llm_base_url: str = "https://api.openai.com/v1"
        llm_temperature: float = 0.7
        llm_max_tokens: int = 4096
        embedding_model: str = "text-embedding-3-small"
        embedding_dimensions: int = 1536
        database_url: str = "postgresql://test:test@localhost:5432/test"
        db_pool_min_size: int = 2
        db_pool_max_size: int = 5
        default_search_limit: int = 10
        max_search_limit: int = 50
        default_text_weight: float = 0.3
        max_revisions: int = 3
        review_threshold: float = 0.85
        webui_host: str = "0.0.0.0"
        webui_port: int = 7860
        webui_share: bool = False
        chunk_size: int = 512
        chunk_overlap: int = 50
        log_level: str = "INFO"

    return MockSettings()


@pytest.fixture
def mock_db_pool():
    """模拟数据库连接池。"""
    pool = AsyncMock()

    async def mock_acquire():
        conn = AsyncMock()
        conn.fetch = AsyncMock(return_value=[])
        conn.fetchrow = AsyncMock(return_value=None)
        conn.execute = AsyncMock(return_value=MagicMock(rowcount=1))
        yield conn

    pool.acquire = mock_acquire
    return pool


@pytest.fixture
def mock_openai_client():
    """模拟 OpenAI 客户端。"""
    client = AsyncMock()

    # 模拟聊天完成
    mock_response = AsyncMock()
    mock_response.choices = [AsyncMock(message=AsyncMock(content="生成的测试文档内容"))]
    mock_response.usage = AsyncMock(total_tokens=100)
    client.chat.completions.create = AsyncMock(return_value=mock_response)

    # 模拟嵌入
    mock_embedding_response = AsyncMock()
    mock_embedding_response.data = [AsyncMock(embedding=[0.1] * 1536)]
    client.embeddings.create = AsyncMock(return_value=mock_embedding_response)

    return client


@pytest.fixture
def sample_document_state():
    """示例文档状态。"""
    from app.agents.state import DocumentState

    return DocumentState(
        task_id="test-task-123",
        user_id="test-user",
        thread_id="test-thread-123",
        user_requirements="创建一个项目提案",
        template_id=None,
        knowledge_ids=[],
        knowledge_query="项目提案",
        retrieved_context=[],
        retrieval_score=0.0,
        generated_content="",
        generation_metadata={},
        review_score=0.0,
        review_feedback={},
        revision_suggestions=[],
        revision_count=0,
        max_revisions=3,
        status="pending",
        error=None,
    )
