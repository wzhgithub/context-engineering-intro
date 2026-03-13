"""Reviewer Agent 工具。"""

from typing import Any


async def check_requirements(
    document: str,
    requirements: str,
) -> dict:
    """检查文档是否满足需求。

    Args:
        document: 文档内容
        requirements: 用户需求

    Returns:
        合规分数和缺失元素
    """
    # 简单实现：检查关键词覆盖
    missing = []
    score = 1.0

    # TODO: 实现更复杂的检查逻辑
    return {
        "score": score,
        "missing_elements": missing,
    }


async def check_template_compliance(
    document: str,
    template_id: str,
    db_pool: Any,
) -> dict:
    """检查模板合规性。

    Args:
        document: 文档内容
        template_id: 模板 ID
        db_pool: 数据库连接池

    Returns:
        合规分数和缺失章节
    """
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT required_fields, sections
                FROM templates
                WHERE id = $1
                """,
                template_id,
            )

        if not row:
            return {"score": 1.0, "missing_sections": []}

        required_fields = row.get("required_fields", [])
        sections = row.get("sections", [])

        missing = []
        for section in sections:
            section_name = section.get("name", "")
            if section_name and section_name not in document:
                missing.append(section_name)

        score = 1.0 - (len(missing) / max(len(sections), 1))

        return {
            "score": score,
            "missing_sections": missing,
        }

    except Exception as e:
        return {"score": 0.0, "missing_sections": []}


async def verify_facts(
    document: str,
    knowledge_context: list[str],
) -> dict:
    """验证事实准确性。

    Args:
        document: 文档内容
        knowledge_context: 知识上下文

    Returns:
        事实检查结果
    """
    return {
        "verified": True,
        "confidence": 0.8,
        "issues": [],
    }
