"""API 模块。"""

from fastapi import APIRouter
from .routes import documents, templates, knowledge, tasks

api_router = APIRouter(prefix="/api")

# 注册路由
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

__all__ = ["api_router"]
