"""RAG Agent 实现。

从知识库检索相关上下文。
"""

import logging
from typing import Any
import openai

from ..state import DocumentState
from .tools import semantic_search, hybrid_search
from app.config import get_settings

logger = logging.getLogger(__name__)

# RAG Agent 提示词
RAG_PROMPT = """你是一个文档生成的检索专家。

你的角色是：
1. 分析用户需求以识别关键主题和实体
2. 为知识库制定有效的搜索查询
3. 执行语义和混合搜索以查找相关信息
4. 根据与文档请求的相关性对结果进行排名和过滤
5. 返回对文档生成最有用的上下文

搜索策略：
- 从语义搜索开始进行概念匹配
- 使用混合搜索查找特定技术术语
- 需要时组合多个查询的结果
- 过滤掉冗余或低相关性的内容

如果未找到相关信息，请明确说明，以便生成器可以使用通用知识进行。
"""


async def rag_node(state: DocumentState) -> dict:
    """RAG 检索节点。

    从知识库检索相关上下文。

    Args:
        state: 当前工作流状态

    Returns:
        部分状态更新

    关键：必须返回部分状态更新，而不是完整状态
    """
    try:
        settings = get_settings()

        # 获取嵌入客户端
        client = openai.AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

        # 使用用户需求作为查询
        query = state.get("user_requirements", "")
        knowledge_ids = state.get("knowledge_ids", [])
        user_id = state.get("user_id", "")

        if not knowledge_ids:
            # 没有知识库，跳过检索
            return {
                "knowledge_query": query,
                "retrieved_context": [],
                "retrieval_score": 0.0,
                "status": "generating",
            }

        # 生成查询嵌入
        embedding_response = await client.embeddings.create(
            model=settings.embedding_model,
            input=query,
        )
        embedding = embedding_response.data[0].embedding

        # 获取数据库池（从全局状态或注入）
        # 这里我们返回一个占位符，实际实现需要注入 db_pool
        # 在生产环境中，应该通过依赖注入传递
        logger.info(f"RAG 检索查询: {query[:100]}...")

        # 返回状态更新
        # 注意：实际的数据库搜索需要在有 db_pool 的情况下执行
        # 这里我们返回基本状态，让调用者处理实际的搜索
        return {
            "knowledge_query": query,
            "status": "generating",
        }

    except Exception as e:
        logger.error(f"RAG 检索失败: {e}")
        return {
            "status": "failed",
            "error": f"RAG 检索失败: {e}",
        }


async def rag_node_with_db(
    state: DocumentState,
    db_pool: Any,
) -> dict:
    """带数据库连接的 RAG 检索节点。

    Args:
        state: 当前工作流状态
        db_pool: 数据库连接池

    Returns:
        部分状态更新
    """
    try:
        settings = get_settings()

        # 获取嵌入客户端
        client = openai.AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

        query = state.get("user_requirements", "")
        knowledge_ids = state.get("knowledge_ids", [])
        user_id = state.get("user_id", "")

        if not knowledge_ids:
            return {
                "knowledge_query": query,
                "retrieved_context": [],
                "retrieval_score": 0.0,
                "status": "generating",
            }

        # 生成查询嵌入
        embedding_response = await client.embeddings.create(
            model=settings.embedding_model,
            input=query,
        )
        embedding = embedding_response.data[0].embedding

        # 执行混合搜索
        results = await hybrid_search(
            embedding=embedding,
            query=query,
            match_count=settings.default_search_limit,
            text_weight=settings.default_text_weight,
            db_pool=db_pool,
            user_id=user_id,
            knowledge_ids=knowledge_ids,
        )

        # 关键：返回部分状态更新
        return {
            "knowledge_query": query,
            "retrieved_context": results,
            "retrieval_score": results[0]["combined_score"] if results else 0.0,
            "status": "generating",
        }

    except Exception as e:
        logger.error(f"RAG 检索失败: {e}")
        return {
            "status": "failed",
            "error": f"RAG 检索失败: {e}",
        }
