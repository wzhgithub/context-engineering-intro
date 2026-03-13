"""知识库管理 API 路由。"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter()


class KnowledgeDocumentResponse(BaseModel):
    """知识文档响应。"""

    id: str
    title: str
    source: Optional[str]
    file_type: str
    created_at: datetime


@router.post("/upload", response_model=KnowledgeDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
):
    """上传知识文档。

    Args:
        file: 上传的文件
        title: 可选的文档标题

    Returns:
        创建的知识文档
    """
    from app.utils.db import get_db_pool
    from app.ingestion import ingest_document
    import uuid

    try:
        db_pool = await get_db_pool()

        # 读取文件内容
        content = await file.read()
        text_content = content.decode("utf-8", errors="ignore")

        # 确定文件类型
        file_type = file.filename.split(".")[-1] if file.filename else "txt"

        # 创建知识文档
        doc_id = str(uuid.uuid4())

        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO knowledge_documents
                (id, user_id, title, content, source, file_type)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
                """,
                doc_id,
                "default_user",
                title or file.filename or "未命名文档",
                text_content,
                file.filename,
                file_type,
            )

        # 在后台进行文档分块和嵌入
        # TODO: 添加后台任务进行分块和嵌入

        return KnowledgeDocumentResponse(
            id=str(row["id"]),
            title=row["title"],
            source=row["source"],
            file_type=row["file_type"],
            created_at=row["created_at"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文档失败: {e}")


@router.get("", response_model=list[KnowledgeDocumentResponse])
async def list_documents():
    """列出所有知识文档。"""
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, title, source, file_type, created_at
                FROM knowledge_documents
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                "default_user",
            )

        return [
            KnowledgeDocumentResponse(
                id=str(row["id"]),
                title=row["title"],
                source=row["source"],
                file_type=row["file_type"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档列表失败: {e}")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """删除知识文档。"""
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            # 先删除关联的分块
            await conn.execute(
                """
                DELETE FROM knowledge_chunks WHERE document_id = $1
                """,
                document_id,
            )

            # 删除文档
            result = await conn.execute(
                """
                DELETE FROM knowledge_documents WHERE id = $1
                """,
                document_id,
            )

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="文档不存在")

        return {"message": "文档已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文档失败: {e}")
