"""测试服务层。"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import json

from app.services.task_service import TaskService


class TestTaskService:
    """测试任务服务。"""

    @pytest.fixture
    def mock_db_pool(self):
        """模拟数据库连接池。"""
        pool = MagicMock()

        # 模拟连接上下文管理器
        mock_conn = AsyncMock()
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_cm.__aexit__ = AsyncMock()

        pool.acquire = MagicMock(return_value=mock_cm)

        return pool, mock_conn

    @pytest.mark.asyncio
    async def test_create_task(self, mock_db_pool):
        """应该创建任务。"""
        pool, mock_conn = mock_db_pool

        # 模拟数据库返回
        mock_row = {
            "id": "task-123",
            "user_id": "user-456",
            "requirements": "测试需求",
            "template_id": None,
            "knowledge_ids": [],
            "status": "pending",
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_row)

        service = TaskService(pool)
        result = await service.create_task(
            user_id="user-456",
            requirements="测试需求",
        )

        assert result is not None
        assert result["id"] == "task-123"

    @pytest.mark.asyncio
    async def test_get_task(self, mock_db_pool):
        """应该获取任务。"""
        pool, mock_conn = mock_db_pool

        mock_row = {
            "id": "task-123",
            "user_id": "user-456",
            "requirements": "测试需求",
            "status": "completed",
        }
        mock_conn.fetchrow = AsyncMock(return_value=mock_row)

        service = TaskService(pool)
        result = await service.get_task("task-123")

        assert result is not None
        assert result["id"] == "task-123"

    @pytest.mark.asyncio
    async def test_update_task_status(self, mock_db_pool):
        """应该更新任务状态。"""
        pool, mock_conn = mock_db_pool

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_conn.execute = AsyncMock(return_value=mock_result)

        service = TaskService(pool)
        result = await service.update_task_status(
            task_id="task-123",
            status="completed",
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_save_workflow_state(self, mock_db_pool):
        """应该保存工作流状态。"""
        pool, mock_conn = mock_db_pool

        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_conn.execute = AsyncMock(return_value=mock_result)

        service = TaskService(pool)
        result = await service.save_workflow_state(
            task_id="task-123",
            workflow_state={"status": "processing"},
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_list_tasks(self, mock_db_pool):
        """应该列出任务。"""
        pool, mock_conn = mock_db_pool

        mock_rows = [
            {"id": "task-1", "status": "pending"},
            {"id": "task-2", "status": "completed"},
        ]
        mock_conn.fetch = AsyncMock(return_value=mock_rows)

        service = TaskService(pool)
        results = await service.list_tasks(user_id="user-456")

        assert len(results) == 2
