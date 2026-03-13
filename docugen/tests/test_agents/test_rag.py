"""测试 RAG Agent。"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.rag.agent import rag_node, rag_node_with_db
from app.agents.rag.tools import semantic_search, hybrid_search


class TestRAGNode:
    """测试 RAG 节点。"""

    @pytest.mark.asyncio
    async def test_rag_node_without_knowledge(self, sample_document_state):
        """没有知识库时应该跳过检索。"""
        state = sample_document_state
        state["knowledge_ids"] = []

        result = await rag_node(state)

        assert "retrieved_context" in result
        assert result["retrieved_context"] == []
        assert result["status"] == "generating"

    @pytest.mark.asyncio
    async def test_rag_node_with_knowledge(
        self, sample_document_state, mock_db_pool, mock_openai_client
    ):
        """有知识库时应该执行检索。"""
        state = sample_document_state
        state["knowledge_ids"] = ["kb-001"]

        with patch("app.agents.rag.agent.get_db_pool", return_value=mock_db_pool), \
             patch("app.agents.rag.agent.openai.AsyncOpenAI", return_value=mock_openai_client):

            result = await rag_node_with_db(state, mock_db_pool)

            assert "retrieved_context" in result
            assert "status" in result


class TestSemanticSearch:
    """测试语义搜索。"""

    @pytest.mark.asyncio
    async def test_semantic_search_returns_results(self, mock_db_pool):
        """语义搜索应该返回结果。"""
        embedding = [0.1] * 1536

        # 模拟数据库返回
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "content": "测试内容",
                "chunk_index": 0,
                "document_title": "测试文档",
                "document_source": "test.txt",
                "similarity": 0.9,
            }
        ])
        mock_db_pool.acquire = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_conn), __aexit__=AsyncMock()))

        results = await semantic_search(
            embedding=embedding,
            match_count=10,
            db_pool=mock_db_pool,
            user_id="test-user",
        )

        assert len(results) == 1
        assert results[0]["content"] == "测试内容"


class TestHybridSearch:
    """测试混合搜索。"""

    @pytest.mark.asyncio
    async def test_hybrid_search_combines_scores(self, mock_db_pool):
        """混合搜索应该组合分数。"""
        embedding = [0.1] * 1536

        # 模拟数据库返回
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "chunk_id": "chunk-1",
                "document_id": "doc-1",
                "content": "测试内容",
                "chunk_index": 0,
                "document_title": "测试文档",
                "document_source": "test.txt",
                "combined_score": 0.85,
                "vector_similarity": 0.9,
                "text_similarity": 0.8,
            }
        ])
        mock_db_pool.acquire = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_conn), __aexit__=AsyncMock()))

        results = await hybrid_search(
            embedding=embedding,
            query="测试查询",
            match_count=10,
            text_weight=0.3,
            db_pool=mock_db_pool,
            user_id="test-user",
        )

        assert len(results) == 1
        assert "combined_score" in results[0]
