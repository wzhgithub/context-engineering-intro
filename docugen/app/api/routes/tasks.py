"""任务状态 API 路由。"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


class TaskStatusResponse(BaseModel):
    """任务状态响应。"""

    id: str
    status: str
    current_stage: str
    revision_count: int
    max_revisions: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]


class TaskDetailResponse(TaskStatusResponse):
    """任务详情响应。"""

    requirements: str
    generated_document: Optional[str]
    review_score: Optional[float]


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task_status(task_id: str):
    """获取任务状态。

    Args:
        task_id: 任务 ID

    Returns:
        任务详情
    """
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    t.id, t.status, t.current_stage, t.revision_count,
                    t.max_revisions, t.created_at, t.updated_at, t.completed_at,
                    t.error, t.requirements,
                    gd.content as generated_document,
                    gd.review_score
                FROM tasks t
                LEFT JOIN generated_documents gd ON t.id = gd.task_id
                WHERE t.id = $1
                """,
                task_id,
            )

        if not row:
            raise HTTPException(status_code=404, detail="任务不存在")

        return TaskDetailResponse(
            id=str(row["id"]),
            status=row["status"],
            current_stage=row["current_stage"],
            revision_count=row["revision_count"],
            max_revisions=row["max_revisions"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
            error=row["error"],
            requirements=row["requirements"],
            generated_document=row["generated_document"],
            review_score=float(row["review_score"]) if row["review_score"] else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {e}")


@router.get("", response_model=list[TaskStatusResponse])
async def list_tasks(status: Optional[str] = None, limit: int = 20):
    """列出任务。

    Args:
        status: 可选的状态过滤
        limit: 返回数量限制

    Returns:
        任务列表
    """
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            if status:
                rows = await conn.fetch(
                    """
                    SELECT id, status, current_stage, revision_count,
                           max_revisions, created_at, updated_at, completed_at, error
                    FROM tasks
                    WHERE user_id = $1 AND status = $2
                    ORDER BY created_at DESC
                    LIMIT $3
                    """,
                    "default_user",
                    status,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT id, status, current_stage, revision_count,
                           max_revisions, created_at, updated_at, completed_at, error
                    FROM tasks
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    "default_user",
                    limit,
                )

        return [
            TaskStatusResponse(
                id=str(row["id"]),
                status=row["status"],
                current_stage=row["current_stage"],
                revision_count=row["revision_count"],
                max_revisions=row["max_revisions"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"],
                error=row["error"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {e}")
