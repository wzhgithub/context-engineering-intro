"""文档导入管道。

将文档导入知识库。
"""

import logging
from typing import Optional
from datetime import datetime

from .chunker import chunk_document, ChunkingConfig, DocumentChunk
from .embedder import Embedder

logger = logging.getLogger(__name__)


async def ingest_document(
    content: str,
    title: str,
    source: Optional[str],
    file_type: str,
    user_id: str,
    db_pool,
    embedder: Embedder,
    config: Optional[ChunkingConfig] = None,
) -> dict:
    """导入文档到知识库。

    Args:
        content: 文档内容
        title: 文档标题
        source: 文档来源
        file_type: 文件类型
        user_id: 用户 ID
        db_pool: 数据库连接池
        embedder: 嵌入生成器
        config: 分块配置

    Returns:
        导入结果
    """
    import uuid

    config = config or ChunkingConfig()

    # 创建文档记录
    doc_id = str(uuid.uuid4())

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO knowledge_documents
            (id, user_id, title, content, source, file_type)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            doc_id,
            user_id,
            title,
            content,
            source,
            file_type,
        )

    # 分块
    chunks = chunk_document(
        content,
        config=config,
        metadata={
            "document_id": doc_id,
            "title": title,
            "source": source,
        },
    )

    if not chunks:
        return {
            "document_id": doc_id,
            "chunk_count": 0,
            "status": "completed",
        }

    # 生成嵌入
    texts = [chunk.content for chunk in chunks]
    embeddings = await embedder.embed_batch(texts)

    # 存储分块和嵌入
    async with db_pool.acquire() as conn:
        for chunk, embedding in zip(chunks, embeddings):
            # PGVector 格式
            embedding_str = "[" + ",".join(map(str, embedding)) + "]"

            await conn.execute(
                """
                INSERT INTO knowledge_chunks
                (id, document_id, content, chunk_index, embedding)
                VALUES ($1, $2, $3, $4, $5::vector)
                """,
                str(uuid.uuid4()),
                doc_id,
                chunk.content,
                chunk.index,
                embedding_str,
            )

    logger.info(f"文档 {doc_id} 已导入，共 {len(chunks)} 个分块")

    return {
        "document_id": doc_id,
        "chunk_count": len(chunks),
        "status": "completed",
    }
