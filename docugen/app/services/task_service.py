"""任务服务。

管理文档生成任务的生命周期。
"""

import logging
from datetime import datetime
from typing import Optional, Any
import json

from ..models import Task, GeneratedDocument

logger = logging.getLogger(__name__)


class TaskService:
    """任务管理服务。"""

    def __init__(self, db_pool: Any):
        """初始化任务服务。

        Args:
            db_pool: 数据库连接池
        """
        self.db_pool = db_pool

    async def create_task(
        self,
        user_id: str,
        requirements: str,
        template_id: Optional[str] = None,
        knowledge_ids: Optional[list[str]] = None,
        max_revisions: int = 3,
    ) -> Task:
        """创建新任务。

        Args:
            user_id: 用户 ID
            requirements: 用户需求
            template_id: 可选的模板 ID
            knowledge_ids: 知识库 ID 列表
            max_revisions: 最大修订次数

        Returns:
            创建的任务对象
        """
        async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    INSERT INTO tasks (user_id, requirements, template_id, knowledge_ids, max_revisions)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                    """,
                    user_id,
                    requirements,
                    template_id,
                    json.dumps(knowledge_ids or []),
                    max_revisions,
                )

        return Task(**row) if row else None

    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务。

        Args:
            task_id: 任务 ID

        Returns:
            任务对象或 None
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM tasks WHERE id = $1
                """,
                task_id,
            )

        return Task(**row) if row else None

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        current_stage: Optional[str] = None,
        error: Optional[str] = None,
    ) -> bool:
        """更新任务状态。

        Args:
            task_id: 任务 ID
            status: 新状态
            current_stage: 当前阶段
            error: 错误信息

        Returns:
            是否更新成功
        """
        updates = ["status = $2", "updated_at = NOW()"]
        params = [task_id, status]

        if current_stage:
            updates.append(f"current_stage = ${len(params) + 1}")
            params.append(current_stage)

        if error:
            updates.append(f"error = ${len(params) + 1}")
            params.append(error)

        if status == "completed":
            updates.append("completed_at = NOW()")

        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                f"""
                UPDATE tasks SET {', '.join(updates)} WHERE id = $1
                """,
                *params,
            )

        return result.rowcount > 0

    async def save_workflow_state(
        self,
        task_id: str,
        workflow_state: dict,
    ) -> bool:
        """保存工作流状态。

        Args:
            task_id: 任务 ID
            workflow_state: 工作流状态字典

        Returns:
            是否保存成功
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE tasks
                SET workflow_state = $2, updated_at = NOW()
                WHERE id = $1
                """,
                task_id,
                json.dumps(workflow_state),
            )

        return result.rowcount > 0

    async def save_generated_document(
        self,
        task_id: str,
        user_id: str,
        content: str,
        review_score: float,
        review_feedback: dict,
        template_id: Optional[str] = None,
    ) -> GeneratedDocument:
        """保存生成的文档。

        Args:
            task_id: 任务 ID
            user_id: 用户 ID
            content: 文档内容
            review_score: 审查分数
            review_feedback: 审查反馈
            template_id: 模板 ID

        Returns:
            生成的文档对象
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO generated_documents
                (task_id, user_id, content, template_id, review_score, review_feedback)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                task_id,
                user_id,
                content,
                template_id,
                review_score,
                json.dumps(review_feedback),
            )

        return GeneratedDocument(**row) if row else None

    async def list_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Task]:
        """列出用户的任务。

        Args:
            user_id: 用户 ID
            status: 可选的状态过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            任务列表
        """
        async with self.db_pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    """
                    SELECT * FROM tasks
                    WHERE user_id = $1 AND status = $2
                    ORDER BY created_at DESC
                    LIMIT $3 OFFSET $4
                    """,
                    user_id,
                    status,
                    limit,
                    offset,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM tasks
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2 OFFSET $3
                    """,
                    user_id,
                    limit,
                    offset,
                )

        return [Task(**row) for row in rows]
