"""Coordinator 路由逻辑。

定义工作流条件边函数。
"""

from ..state import DocumentState


def should_revise(state: DocumentState) -> str:
    """确定文档是否需要修订。

    决策逻辑:
    1. 如果有错误，完成
    2. 如果分数 >= 0.85，完成
    3. 如果达到最大修订次数，完成
    4. 否则，继续修订

    关键：必须返回字符串键 "revise" 或 "complete"

    Args:
        state: 当前工作流状态

    Returns:
        "revise" 或 "complete"
    """
    # 检查是否有错误
    if state.get("error"):
        return "complete"

    # 检查分数是否达标
    review_score = state.get("review_score", 0.0)
    if review_score >= 0.85:
        return "complete"

    # 检查是否达到最大修订次数
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 3)
    if revision_count >= max_revisions:
        return "complete"

    return "revise"


def route_on_status(state: DocumentState) -> str:
    """根据状态路由。

    Args:
        state: 当前工作流状态

    Returns:
        路由目标
    """
    status = state.get("status", "pending")

    if status == "failed":
        return "end"

    # 继续正常流程
    return "continue"


def route_on_error(state: DocumentState) -> str:
    """错误处理路由。

    Args:
        state: 当前工作流状态

    Returns:
        "fail" 或 "continue"
    """
    if state.get("error"):
        return "fail"
    return "continue"
