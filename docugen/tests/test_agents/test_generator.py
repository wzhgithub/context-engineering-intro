"""测试 Generator Agent。"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.generator.agent import generator_node, _format_feedback


class TestGeneratorNode:
    """测试 Generator 节点。"""

    @pytest.mark.asyncio
    async def test_generator_creates_document(
        self, sample_document_state, mock_openai_client
    ):
        """生成器应该创建文档。"""
        state = sample_document_state
        state["retrieved_context"] = [
            {"document_source": "test.txt", "content": "测试上下文"}
        ]

        with patch("app.agents.generator.agent.get_settings") as mock_settings, \
             patch("app.agents.generator.agent.openai.AsyncOpenAI", return_value=mock_openai_client):

            from pydantic import BaseModel

            class MockSettings(BaseModel):
                llm_api_key: str = "test-key"
                llm_base_url: str = "https://api.openai.com/v1"
                llm_model: str = "gpt-4o-mini"
                llm_temperature: float = 0.7
                llm_max_tokens: int = 4096

            mock_settings.return_value = MockSettings()

            result = await generator_node(state)

            assert "generated_content" in result
            assert result["generated_content"] == "生成的测试文档内容"
            assert result["status"] == "reviewing"
            assert result["revision_count"] == 1

    @pytest.mark.asyncio
    async def test_generator_handles_revision(
        self, sample_document_state, mock_openai_client
    ):
        """生成器应该处理修订。"""
        state = sample_document_state
        state["revision_count"] = 1
        state["review_feedback"] = {
            "completeness": {"score": 0.8, "issues": ["需要更多细节"]}
        }

        with patch("app.agents.generator.agent.get_settings") as mock_settings, \
             patch("app.agents.generator.agent.openai.AsyncOpenAI", return_value=mock_openai_client):

            from pydantic import BaseModel

            class MockSettings(BaseModel):
                llm_api_key: str = "test-key"
                llm_base_url: str = "https://api.openai.com/v1"
                llm_model: str = "gpt-4o-mini"
                llm_temperature: float = 0.7
                llm_max_tokens: int = 4096

            mock_settings.return_value = MockSettings()

            result = await generator_node(state)

            assert result["revision_count"] == 2


class TestFormatFeedback:
    """测试反馈格式化。"""

    def test_formats_feedback_correctly(self):
        """应该正确格式化反馈。"""
        feedback = {
            "completeness": {"score": 0.8, "issues": ["缺少细节"]},
            "accuracy": {"score": 0.9, "issues": []},
        }

        result = _format_feedback(feedback)

        assert "COMPLETENESS" in result
        assert "ACCURACY" in result
        assert "缺少细节" in result
        assert "0.8" in result
