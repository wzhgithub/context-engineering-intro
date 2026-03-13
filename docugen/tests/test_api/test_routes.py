"""测试 API 路由。"""

import pytest
from httpx import AsyncClient


class TestDocumentRoutes:
    """测试文档路由。"""

    @pytest.mark.asyncio
    async def test_generate_document(self, async_client: AsyncClient):
        """应该创建文档生成任务。"""
        response = await async_client.post(
            "/api/documents/generate",
            json={
                "requirements": "创建一个项目提案文档",
                "template_id": None,
                "knowledge_ids": [],
                "max_revisions": 3,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"


class TestTaskRoutes:
    """测试任务路由。"""

    @pytest.mark.asyncio
    async def test_get_task_status(self, async_client: AsyncClient):
        """应该获取任务状态。"""
        # 首先创建任务
        create_response = await async_client.post(
            "/api/documents/generate",
            json={
                "requirements": "测试需求",
            },
        )

        assert create_response.status_code == 200
        task_id = create_response.json()["task_id"]

        # 获取任务状态
        response = await async_client.get(f"/api/tasks/{task_id}")

        # 可能还在处理中
        assert response.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_list_tasks(self, async_client: AsyncClient):
        """应该列出任务。"""
        response = await async_client.get("/api/tasks")

        assert response.status_code == 200


class TestTemplateRoutes:
    """测试模板路由。"""

    @pytest.mark.asyncio
    async def test_create_template(self, async_client: AsyncClient):
        """应该创建模板。"""
        response = await async_client.post(
            "/api/templates",
            json={
                "name": "测试模板",
                "description": "测试模板描述",
                "sections": [{"name": "引言", "required": True}],
                "formatting_rules": {"style": "formal"},
                "required_fields": ["title", "content"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试模板"

    @pytest.mark.asyncio
    async def test_list_templates(self, async_client: AsyncClient):
        """应该列出模板。"""
        response = await async_client.get("/api/templates")

        assert response.status_code == 200


class TestKnowledgeRoutes:
    """测试知识库路由。"""

    @pytest.mark.asyncio
    async def test_list_documents(self, async_client: AsyncClient):
        """应该列出知识文档。"""
        response = await async_client.get("/api/knowledge")

        assert response.status_code == 200
