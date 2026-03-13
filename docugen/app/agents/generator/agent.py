"""Generator Agent 实现。

使用 LLM 生成专业文档。
"""

import logging
from typing import Any, Optional
import openai

from ..state import DocumentState
from app.config import get_settings

logger = logging.getLogger(__name__)

# Generator Agent 提示词
GENERATOR_PROMPT = """你是一个专业的文档生成专家。

你的职责：
1. 彻底分析用户需求以理解文档目的
2. 准确整合检索到的知识上下文
3. 在指定时应用文档模板
4. 生成清晰、结构化、专业的内容
5. 根据审查反馈修订内容

文档生成指南：
- 结构：遵循逻辑流程（引言 → 主体 → 结论）
- 清晰度：使用适合受众的清晰简洁语言
- 准确性：仅使用来自知识上下文或通用知识的信息
- 完整性：解决用户需求的所有方面
- 风格：匹配模板中指定的语气和格式

修订处理：
- 仔细分析审查反馈
- 进行针对性改进，同时保留好的内容
- 跟踪为响应反馈所做的更改
- 在修订中保持一致性

输出：
生成一个完整、结构良好的文档，充分解决用户的需求，同时整合相关知识。
"""


async def generator_node(state: DocumentState) -> dict:
    """文档生成节点。

    使用 LLM 生成文档内容。

    Args:
        state: 当前工作流状态

    Returns:
        部分状态更新

    关键：必须返回部分状态更新，而不是完整状态
    """
    try:
        settings = get_settings()

        # 获取 LLM 客户端
        client = openai.AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

        # 提取状态数据
        user_requirements = state.get("user_requirements", "")
        retrieved_context = state.get("retrieved_context", [])
        revision_count = state.get("revision_count", 0)
        review_feedback = state.get("review_feedback", {})
        template_id = state.get("template_id")

        # 构建上下文文本
        context_text = ""
        if retrieved_context:
            context_parts = []
            for ctx in retrieved_context:
                source = ctx.get("document_source", "未知来源")
                content = ctx.get("content", "")
                context_parts.append(f"[来源: {source}]\n{content}")
            context_text = "\n\n---\n\n".join(context_parts)

        # 构建提示词
        prompt = f"""{GENERATOR_PROMPT}

## 用户需求
{user_requirements}

## 知识上下文
{context_text if context_text else "无检索到的上下文，请使用通用知识。"}
"""

        # 添加模板信息（如果有）
        if template_id:
            prompt += f"\n## 模板 ID\n请遵循模板 ID 为 {template_id} 的文档结构。\n"

        # 添加修订反馈（如果适用）
        if revision_count > 0 and review_feedback:
            feedback_text = _format_feedback(review_feedback)
            prompt += f"""
## 之前的审查反馈
{feedback_text}

请根据以上反馈改进文档内容。
"""

        # 调用 LLM
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": GENERATOR_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

        generated_content = response.choices[0].message.content

        # 关键：返回部分状态更新
        return {
            "generated_content": generated_content,
            "revision_count": revision_count + 1,
            "status": "reviewing",
            "generation_metadata": {
                "model": settings.llm_model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
            },
        }

    except Exception as e:
        logger.error(f"文档生成失败: {e}")
        return {
            "status": "failed",
            "error": f"文档生成失败: {e}",
        }


def _format_feedback(feedback: dict) -> str:
    """格式化审查反馈。

    Args:
        feedback: 审查反馈字典

    Returns:
        格式化的反馈文本
    """
    lines = []

    for category, data in feedback.items():
        score = data.get("score", "N/A")
        issues = data.get("issues", [])

        lines.append(f"### {category.upper()} (分数: {score})")
        if issues:
            for issue in issues:
                lines.append(f"- {issue}")
        lines.append("")

    return "\n".join(lines)


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
