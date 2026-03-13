"""模板管理 API 路由。"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

router = APIRouter()


class TemplateCreate(BaseModel):
    """模板创建请求。"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    sections: dict = Field(default_factory=dict)
    formatting_rules: dict = Field(default_factory=dict)
    required_fields: list[str] = Field(default_factory=list)


class TemplateResponse(BaseModel):
    """模板响应。"""

    id: str
    name: str
    description: Optional[str]
    sections: dict
    formatting_rules: dict
    required_fields: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@router.post("", response_model=TemplateResponse)
async def create_template(template: TemplateCreate):
    """创建模板。"""
    from app.utils.db import get_db_pool
    import uuid

    try:
        db_pool = await get_db_pool()
        template_id = str(uuid.uuid4())

        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO templates
                (id, user_id, name, description, sections, formatting_rules, required_fields)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING *
                """,
                template_id,
                "default_user",
                template.name,
                template.description,
                template.sections,
                template.formatting_rules,
                template.required_fields,
            )

        return TemplateResponse(
            id=str(row["id"]),
            name=row["name"],
            description=row["description"],
            sections=row["sections"],
            formatting_rules=row["formatting_rules"],
            required_fields=row["required_fields"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建模板失败: {e}")


@router.get("", response_model=list[TemplateResponse])
async def list_templates():
    """列出所有模板。"""
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM templates
                WHERE user_id = $1 AND is_active = true
                ORDER BY created_at DESC
                """,
                "default_user",
            )

        return [
            TemplateResponse(
                id=str(row["id"]),
                name=row["name"],
                description=row["description"],
                sections=row["sections"],
                formatting_rules=row["formatting_rules"],
                required_fields=row["required_fields"],
                is_active=row["is_active"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板列表失败: {e}")


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """获取模板详情。"""
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM templates WHERE id = $1
                """,
                template_id,
            )

        if not row:
            raise HTTPException(status_code=404, detail="模板不存在")

        return TemplateResponse(
            id=str(row["id"]),
            name=row["name"],
            description=row["description"],
            sections=row["sections"],
            formatting_rules=row["formatting_rules"],
            required_fields=row["required_fields"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {e}")


@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """删除模板（软删除）。"""
    from app.utils.db import get_db_pool

    try:
        db_pool = await get_db_pool()

        async with db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE templates SET is_active = false WHERE id = $1
                """,
                template_id,
            )

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="模板不存在")

        return {"message": "模板已删除"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除模板失败: {e}")
