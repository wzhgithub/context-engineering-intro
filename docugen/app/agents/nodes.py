"""LangGraph 工作流节点函数。

包装各个智能体实现为图节点。
"""

import logging
from typing import Any

from .state import DocumentState

logger = logging.getLogger(__name__)


async def rag_node(state: DocumentState) -> dict:
    """RAG 检索节点。

    从知识库检索相关上下文。

    Args:
        state: 当前工作流状态

    Returns:
        部分状态更新

    关键：必须返回部分状态更新，而不是完整状态
    """
    from .rag import rag_node_with_db
    from app.utils.db import get_db_pool

    try:
        # 获取数据库连接池
        db_pool = await get_db_pool()

        # 调用 RAG agent
        result = await rag_node_with_db(state, db_pool)
        return result

    except Exception as e:
        logger.error(f"RAG 节点失败: {e}")
        # 如果 RAG 失败，继续生成（无上下文）
        return {
            "retrieved_context": [],
            "retrieval_score": 0.0,
            "status": "generating",
        }


async def generator_node(state: DocumentState) -> dict:
    """文档生成节点。

    使用 LLM 生成文档内容。

    Args:
        state: 当前工作流状态

    Returns:
        部分状态更新
    """
    from .generator import generator_node_with_db
    from app.utils.db import get_db_pool

    try:
        # 获取数据库连接池（用于模板）
        db_pool = await get_db_pool()

        # 调用 Generator agent
        result = await generator_node_with_db(state, db_pool)
        return result

    except Exception as e:
        logger.error(f"生成节点失败: {e}")
        return {
            "status": "failed",
            "error": f"文档生成失败: {e}",
        }


async def reviewer_node(state: DocumentState) -> dict:
    """文档审查节点。

    评估文档质量并提供反馈。

    Args:
        state: 当前工作流状态

    Returns:
        部分状态更新
    """
    from .reviewer import reviewer_node as _reviewer_node

    try:
        # 调用 Reviewer agent
        result = await _reviewer_node(state)
        return result

    except Exception as e:
        logger.error(f"审查节点失败: {e}")
        return {
            "status": "failed",
            "error": f"文档审查失败: {e}",
        }
