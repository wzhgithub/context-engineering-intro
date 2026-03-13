"""RAG 搜索工具。

使用 PGVector 进行语义和混合搜索。
"""

import logging
from typing import Any, Optional
import json

logger = logging.getLogger(__name__)


async def semantic_search(
    embedding: list[float],
    match_count: int,
    db_pool: Any,
    user_id: str,
) -> list[dict]:
    """使用 PGVector 执行语义相似度搜索。

    Args:
        embedding: 查询嵌入向量
        match_count: 返回结果数量
        db_pool: 数据库连接池
        user_id: 用户 ID（用于访问控制）

    Returns:
        包含内容、相似度分数和元数据的片段列表
    """
    try:
        # 关键：PGVector 格式是字符串 '[1.0,2.0,3.0]'
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"

        async with db_pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT
                    kc.id as chunk_id,
                    kc.document_id,
                    kc.content,
                    kc.chunk_index,
                    kd.title as document_title,
                    kd.source as document_source,
                    1 - (kc.embedding <=> $1::vector) as similarity
                FROM knowledge_chunks kc
                JOIN knowledge_documents kd ON kc.document_id = kd.id
                WHERE kd.user_id = $2
                ORDER BY kc.embedding <=> $1::vector
                LIMIT $3
                """,
                embedding_str,
                user_id,
                match_count,
            )

        return [
            {
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "content": row["content"],
                "chunk_index": row["chunk_index"],
                "document_title": row["document_title"],
                "document_source": row["document_source"],
                "similarity": float(row["similarity"]),
            }
            for row in results
        ]

    except Exception as e:
        logger.error(f"语义搜索失败: {e}")
        return []


async def hybrid_search(
    embedding: list[float],
    query: str,
    match_count: int,
    text_weight: float,
    db_pool: Any,
    user_id: str,
    knowledge_ids: Optional[list[str]] = None,
) -> list[dict]:
    """执行混合搜索，结合语义和关键词匹配。

    Args:
        embedding: 查询嵌入向量
        query: 搜索查询文本
        match_count: 返回结果数量
        text_weight: 文本匹配权重 (0-1)
        db_pool: 数据库连接池
        user_id: 用户 ID
        knowledge_ids: 可选的知识库 ID 过滤

    Returns:
        带有组合分数的结果列表
    """
    try:
        # 关键：PGVector 格式是字符串
        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        vector_weight = 1.0 - text_weight

        async with db_pool.acquire() as conn:
            # 构建查询
            knowledge_filter = ""
            params = [embedding_str, query, user_id, match_count, text_weight, vector_weight]

            if knowledge_ids:
                knowledge_filter = " AND kc.document_id = ANY($7)"
                params.append(knowledge_ids)

            sql = f"""
                SELECT
                    kc.id as chunk_id,
                    kc.document_id,
                    kc.content,
                    kc.chunk_index,
                    kd.title as document_title,
                    kd.source as document_source,
                    (1 - (kc.embedding <=> $1::vector)) * $6 +
                    ts_rank_cd(to_tsvector('english', kc.content), plainto_tsquery('english', $2)) * $5
                    as combined_score,
                    1 - (kc.embedding <=> $1::vector) as vector_similarity,
                    ts_rank_cd(to_tsvector('english', kc.content), plainto_tsquery('english', $2)) as text_similarity
                FROM knowledge_chunks kc
                JOIN knowledge_documents kd ON kc.document_id = kd.id
                WHERE kd.user_id = $3
                {knowledge_filter}
                ORDER BY combined_score DESC
                LIMIT $4
            """

            results = await conn.fetch(sql, *params)

        return [
            {
                "chunk_id": str(row["chunk_id"]),
                "document_id": str(row["document_id"]),
                "content": row["content"],
                "chunk_index": row["chunk_index"],
                "document_title": row["document_title"],
                "document_source": row["document_source"],
                "combined_score": float(row["combined_score"]),
                "vector_similarity": float(row["vector_similarity"]),
                "text_similarity": float(row["text_similarity"]),
            }
            for row in results
        ]

    except Exception as e:
        logger.error(f"混合搜索失败: {e}")
        return []
