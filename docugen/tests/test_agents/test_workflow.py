"""测试工作流逻辑。"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.agents.state import DocumentState, create_initial_state
from app.agents.graph import should_revise, build_workflow


class TestShouldRevise:
    """测试 should_revise 条件边函数。"""

    def test_high_score_completes(self):
        """高分应该完成。"""
        state = DocumentState(
            task_id="test",
            user_id="test",
            thread_id="test",
            user_requirements="test",
            template_id=None,
            knowledge_ids=[],
            knowledge_query="",
            retrieved_context=[],
            retrieval_score=0.0,
            generated_content="",
            generation_metadata={},
            review_score=0.90,
            review_feedback={},
            revision_suggestions=[],
            revision_count=0,
            max_revisions=3,
            status="reviewing",
            error=None,
        )

        result = should_revise(state)
        assert result == "complete"

    def test_low_score_triggers_revision(self):
        """低分应该触发修订。"""
        state = DocumentState(
            task_id="test",
            user_id="test",
            thread_id="test",
            user_requirements="test",
            template_id=None,
            knowledge_ids=[],
            knowledge_query="",
            retrieved_context=[],
            retrieval_score=0.0,
            generated_content="",
            generation_metadata={},
            review_score=0.70,
            review_feedback={},
            revision_suggestions=[],
            revision_count=1,
            max_revisions=3,
            status="reviewing",
            error=None,
        )

        result = should_revise(state)
        assert result == "revise"

    def test_max_revisions_completes(self):
        """达到最大修订次数应该完成。"""
        state = DocumentState(
            task_id="test",
            user_id="test",
            thread_id="test",
            user_requirements="test",
            template_id=None,
            knowledge_ids=[],
            knowledge_query="",
            retrieved_context=[],
            retrieval_score=0.0,
            generated_content="",
            generation_metadata={},
            review_score=0.60,
            review_feedback={},
            revision_suggestions=[],
            revision_count=3,
            max_revisions=3,
            status="reviewing",
            error=None,
        )

        result = should_revise(state)
        assert result == "complete"

    def test_error_completes(self):
        """有错误应该完成。"""
        state = DocumentState(
            task_id="test",
            user_id="test",
            thread_id="test",
            user_requirements="test",
            template_id=None,
            knowledge_ids=[],
            knowledge_query="",
            retrieved_context=[],
            retrieval_score=0.0,
            generated_content="",
            generation_metadata={},
            review_score=0.0,
            review_feedback={},
            revision_suggestions=[],
            revision_count=0,
            max_revisions=3,
            status="failed",
            error="测试错误",
        )

        result = should_revise(state)
        assert result == "complete"


class TestCreateInitialState:
    """测试创建初始状态。"""

    def test_creates_valid_state(self):
        """应该创建有效状态。"""
        state = create_initial_state(
            task_id="task-123",
            user_id="user-456",
            thread_id="thread-789",
            requirements="创建项目提案",
            template_id="template-001",
            knowledge_ids=["kb-001", "kb-002"],
            max_revisions=3,
        )

        assert state["task_id"] == "task-123"
        assert state["user_id"] == "user-456"
        assert state["thread_id"] == "thread-789"
        assert state["user_requirements"] == "创建项目提案"
        assert state["template_id"] == "template-001"
        assert state["knowledge_ids"] == ["kb-001", "kb-002"]
        assert state["status"] == "pending"
        assert state["revision_count"] == 0
        assert state["max_revisions"] == 3

    def test_defaults_are_applied(self):
        """应该应用默认值。"""
        state = create_initial_state(
            task_id="task-123",
            user_id="user-456",
            thread_id="thread-789",
            requirements="测试需求",
        )

        assert state["template_id"] is None
        assert state["knowledge_ids"] == []
        assert state["max_revisions"] == 3
        assert state["status"] == "pending"


class TestBuildWorkflow:
    """测试构建工作流。"""

    @pytest.mark.asyncio
    async def test_workflow_builds_successfully(self):
        """工作流应该成功构建。"""
        workflow = await build_workflow()

        assert workflow is not None
        # 验证节点存在
        assert "rag_retrieval" in workflow.nodes
        assert "generate" in workflow.nodes
        assert "review" in workflow.nodes
