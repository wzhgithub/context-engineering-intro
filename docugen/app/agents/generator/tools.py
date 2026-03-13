"""Generator Agent 工具。"""

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


async def apply_template(
    content: str,
    template: dict,
) -> str:
    """应用文档模板结构。

    Args:
        content: 原始生成内容
        template: 模板定义

    Returns:
        格式化后的文档
    """
    sections = template.get("sections", [])
    formatting_rules = template.get("formatting_rules", {})

    # 简单实现：添加模板标题
    if sections:
        header = "# " + sections[0].get("name", "文档")
        return f"{header}\n\n{content}"

    return content


async def get_template_info(
    template_id: str,
    db_pool: Any,
) -> Optional[dict]:
    """获取模板信息。

    Args:
        template_id: 模板 ID
        db_pool: 数据库连接池

    Returns:
        模板信息字典
    """
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, name, description, sections, formatting_rules, required_fields
                FROM templates
                WHERE id = $1
                """,
                template_id,
            )

        if row:
            return {
                "id": str(row["id"]),
                "name": row["name"],
                "description": row["description"],
                "sections": row["sections"],
                "formatting_rules": row["formatting_rules"],
                "required_fields": row["required_fields"],
            }
        return None

    except Exception as e:
        logger.error(f"获取模板失败: {e}")
        return None


async def format_section(
    section_name: str,
    content: str,
    style_rules: dict,
) -> str:
    """格式化文档章节。

    Args:
        section_name: 章节名称
        content: 章节内容
        style_rules: 格式规则

    Returns:
        格式化后的章节内容
    """
    style = style_rules.get("style", "default")

    if style == "formal":
        return f"## {section_name}\n\n{content}"
    elif style == "bullet":
        return f"## {section_name}\n\n- {content}"
    else:
        return f"## {section_name}\n\n{content}"
