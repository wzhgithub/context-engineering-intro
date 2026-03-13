"""测试 Reviewer Agent。"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from app.agents.reviewer.agent import reviewer_node, parse_review_response


class TestReviewerNode:
    """测试 Reviewer 节点。"""

    @pytest.mark.asyncio
    async def test_reviewer_returns_score(self, sample_document_state):
        """审查者应该返回分数。"""
        state = sample_document_state
        state["generated_content"] = "这是一个测试文档。"

        # 模拟 LLM 返回 JSON 响应
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content=json.dumps({
                "score": 0.88,
                "feedback": {
                    "completeness": {"score": 0.9, "issues": []},
                    "accuracy": {"score": 0.85, "issues": []},
                    "quality": {"score": 0.9, "issues": []},
                    "compliance": {"score": 0.85, "issues": []}
                },
                "revision_suggestions": []
            })))
        ]

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        mock_settings = MagicMock()
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_base_url = "https://api.openai.com/v1"
        mock_settings.llm_model = "gpt-4o-mini"
        mock_settings.llm_temperature = 0.3
        mock_settings.llm_max_tokens = 1024

        with patch("app.agents.reviewer.agent.get_settings", return_value=mock_settings), \
             patch("app.agents.reviewer.agent.openai.AsyncOpenAI", return_value=mock_client):

            result = await reviewer_node(state)

            assert "review_score" in result
            assert 0 <= result["review_score"] <= 1
            assert result["status"] in ("completed", "reviewing")

    @pytest.mark.asyncio
    async def test_reviewer_approves_high_score(self, sample_document_state):
        """高分数应该完成状态。"""
        state = sample_document_state
        state["generated_content"] = "这是一个优秀的测试文档。"

        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(message=AsyncMock(content=json.dumps({
                "score": 0.95,
                "feedback": {},
                "revision_suggestions": []
            })))
        ]

        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        mock_settings = MagicMock()
        mock_settings.llm_api_key = "test-key"
        mock_settings.llm_base_url = "https://api.openai.com/v1"
        mock_settings.llm_model = "gpt-4o-mini"

        with patch("app.agents.reviewer.agent.get_settings", return_value=mock_settings), \
             patch("app.agents.reviewer.agent.openai.AsyncOpenAI", return_value=mock_client):

            result = await reviewer_node(state)

            assert result["status"] == "completed"


class TestParseReviewResponse:
    """测试解析审查响应。"""

    def test_parse_valid_json(self):
        """应该解析有效 JSON。"""
        response_text = '{"score": 0.85, "feedback": {}, "revision_suggestions": []}'

        result = parse_review_response(response_text)

        assert result["score"] == 0.85

    def test_parse_embedded_json(self):
        """应该解析嵌入的 JSON。"""
        response_text = '一些文本 {"score": 0.9} 更多文本'

        result = parse_review_response(response_text)

        assert result["score"] == 0.9

    def test_parse_invalid_returns_defaults(self):
        """无效输入应该返回默认值。"""
        result = parse_review_response("无效文本")

        assert result["score"] == 0.0
        assert result["feedback"] == {}
