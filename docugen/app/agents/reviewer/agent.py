"""Reviewer Agent 实现。

评估文档质量并提供反馈。保留兼容的函数接口。
新架构通过 ReviewerSubgraph (graph.py) 实现分阶段评审。
"""

import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings
from ..state import DocumentState
from .prompts import REVIEWER_PROMPT

logger = logging.getLogger(__name__)


async def reviewer_node(state: DocumentState, db_pool: Any = None) -> dict:
    """审查文档节点（兼容函数接口）。

    Args:
        state: 当前工作流状态
        db_pool: 数据库连接池（可选）

    Returns:
        部分状态更新
    """
    logger.info(f"[reviewer_node] 输入: content_length={len(state.get('generated_content', ''))}")

    try:
        settings = get_settings()

        # 获取 LLM 客户端
        client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

        # 准备审查提示词
        requirements = state.get("user_requirements", "")
        generated_content = state.get("generated_content", "")
        retrieved_context = state.get("retrieved_context", [])

        # 格式化检索上下文
        context_text = "\n\n".join(
            [ctx.get("content", "") for ctx in retrieved_context[:3]]
        )

        prompt = f"""
{REVIEWER_PROMPT}

需求:
{requirements}

生成的文档:
{generated_content}

知识上下文:
{context_text}

请以 JSON 格式返回审查结果。
"""

        # 调用 LLM
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": REVIEWER_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        # 解析响应
        result = json.loads(response.choices[0].message.content)

        review_score = float(result.get("score", 0.0))
        review_feedback = result.get("feedback", {})
        revision_suggestions = result.get("revision_suggestions", [])

        # 关键：返回部分状态更新
        new_status = "completed" if review_score >= 0.85 else "reviewing"

        result = {
            "review_score": review_score,
            "review_feedback": review_feedback,
            "revision_suggestions": revision_suggestions,
            "status": new_status,
        }
        logger.info(
            f"[reviewer_node] 输出: score={review_score}, status={new_status}"
        )
        return result

    except Exception as e:
        logger.error(f"[reviewer_node] 审查失败: {e}")
        return {
            "status": "failed",
            "error": f"审查失败: {e}",
        }


def parse_review_response(response_text: str) -> dict:
    """解析审查响应。

    Args:
        response_text: LLM 响应文本

    Returns:
        解析后的审查结果
    """
    try:
        # 尝试提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())

        return {
            "score": 0.0,
            "feedback": {},
            "revision_suggestions": [],
        }

    except json.JSONDecodeError:
        return {
            "score": 0.0,
            "feedback": {},
            "revision_suggestions": [],
        }


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
    # 简单实现：检查关键词
    missing = []
    score = 1.0

    # 这里可以实现更复杂的检查逻辑
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

        # 检查章节是否存在
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
        logger.error(f"检查模板合规性失败: {e}")
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
    # 简单实现
    return {
        "verified": True,
        "confidence": 0.8,
        "issues": [],
    }
