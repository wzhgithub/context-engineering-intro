"""文档生成 API 路由。"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()


class GenerateRequest(BaseModel):
    """文档生成请求。"""

    requirements: str = Field(..., min_length=10, max_length=10000)
    template_id: Optional[str] = Field(default=None)
    knowledge_ids: list[str] = Field(default_factory=list)
    max_revisions: int = Field(default=3, ge=1, le=5)


class GenerateResponse(BaseModel):
    """文档生成响应。"""

    task_id: str
    status: str
    message: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_document(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
):
    """生成文档。

    Args:
        request: 生成请求
        background_tasks: 后台任务

    Returns:
        任务 ID 和初始状态
    """
    from app.utils.db import get_db_pool
    from app.services import TaskService
    from app.agents import create_initial_state, compile_workflow

    try:
        db_pool = await get_db_pool()
        task_service = TaskService(db_pool)

        # 创建任务
        task = await task_service.create_task(
            user_id="default_user",  # TODO: 从认证获取
            requirements=request.requirements,
            template_id=request.template_id,
            knowledge_ids=request.knowledge_ids,
            max_revisions=request.max_revisions,
        )

        # 在后台运行工作流
        background_tasks.add_task(
            run_workflow,
            task.id,
            task.thread_id,
            request.requirements,
            request.template_id,
            request.knowledge_ids,
            request.max_revisions,
        )

        return GenerateResponse(
            task_id=task.id,
            status="pending",
            message="文档生成任务已创建，正在后台处理",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {e}")


async def run_workflow(
    task_id: str,
    thread_id: str,
    requirements: str,
    template_id: Optional[str],
    knowledge_ids: list[str],
    max_revisions: int,
):
    """在后台运行文档生成工作流。

    Args:
        task_id: 任务 ID
        thread_id: 线程 ID
        requirements: 用户需求
        template_id: 模板 ID
        knowledge_ids: 知识库 ID
        max_revisions: 最大修订次数
    """
    import logging

    logger = logging.getLogger(__name__)

    try:
        from app.utils.db import get_db_pool
        from app.services import TaskService
        from app.agents import create_initial_state, compile_workflow

        db_pool = await get_db_pool()
        task_service = TaskService(db_pool)

        # 更新状态
        await task_service.update_task_status(task_id, "processing", "rag")

        # 创建初始状态
        initial_state = create_initial_state(
            task_id=task_id,
            user_id="default_user",
            thread_id=thread_id,
            requirements=requirements,
            template_id=template_id,
            knowledge_ids=knowledge_ids,
            max_revisions=max_revisions,
        )

        # 编译并运行工作流
        app = await compile_workflow()
        config = {"configurable": {"thread_id": thread_id}}

        # 流式执行
        async for event in app.astream(initial_state, config=config):
            # 更新状态
            current_state = event.get("state", {})
            status = current_state.get("status", "processing")
            stage = current_state.get("status", "pending")

            await task_service.update_task_status(task_id, status, stage)
            await task_service.save_workflow_state(task_id, dict(current_state))

            # 如果完成或失败，退出
            if status in ("completed", "failed"):
                break

        # 获取最终状态
        final_state = await app.aget_state(config)

        # 保存生成的文档
        if final_state.get("generated_content"):
            await task_service.save_generated_document(
                task_id=task_id,
                user_id="default_user",
                content=final_state["generated_content"],
                review_score=final_state.get("review_score", 0.0),
                review_feedback=final_state.get("review_feedback", {}),
                template_id=template_id,
            )

        # 更新任务状态
        final_status = final_state.get("status", "completed")
        error = final_state.get("error")

        await task_service.update_task_status(
            task_id, final_status, None, error
        )

        logger.info(f"任务 {task_id} 完成，状态: {final_status}")

    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        from app.utils.db import get_db_pool
        from app.services import TaskService

        try:
            db_pool = await get_db_pool()
            task_service = TaskService(db_pool)
            await task_service.update_task_status(
                task_id, "failed", None, str(e)
            )
        except Exception as inner_e:
            logger.error(f"更新失败状态也失败: {inner_e}")
