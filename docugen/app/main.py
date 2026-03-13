"""FastAPI 主应用入口。

集成 FastAPI、LangGraph 和 Gradio。
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.config import get_settings
from app.api import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。

    启动时初始化资源，关闭时清理资源。
    """
    from app.utils.db import init_db, close_db_pool

    logger.info("正在启动 DocuGen 应用...")

    # 初始化数据库
    await init_db()
    logger.info("数据库初始化完成")

    yield

    # 清理资源
    logger.info("正在关闭 DocuGen 应用...")
    await close_db_pool()
    logger.info("应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="DocuGen",
    description="多智能体文档生成系统",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router)


@app.get("/")
async def root():
    """根路径健康检查。"""
    return {
        "status": "healthy",
        "service": "DocuGen API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """健康检查端点。"""
    return {"status": "ok"}


def mount_gradio():
    """挂载 Gradio WebUI。"""
    import gradio as gr
    from app.webui import create_interface

    interface = create_interface()
    gr.mount_gradio_app(app, interface, path="/webui")
    logger.info("Gradio WebUI 已挂载到 /webui")


def main():
    """主入口函数。"""
    settings = get_settings()

    # 挂载 Gradio
    mount_gradio()

    # 运行服务器
    uvicorn.run(
        "app.main:app",
        host=settings.webui_host,
        port=settings.webui_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
