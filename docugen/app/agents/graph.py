"""LangGraph 工作流图定义。

构建文档生成的多智能体工作流。
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import Optional

from .state import DocumentState


async def build_workflow() -> StateGraph:
    """构建文档生成工作流图。

    工作流结构:
    ┌─────────────┐
    │ rag_retrieval │
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   generate   │◄──────┐
    └──────┬──────┘        │
           │               │
           ▼               │
    ┌─────────────┐        │
    │    review    │────────┘
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │     END     │
    └─────────────┘

    Returns:
        编译后的工作流图
    """
    # 导入节点函数
    from .nodes import rag_node, generator_node, reviewer_node

    # 创建状态图
    workflow = StateGraph(DocumentState)

    # 添加节点
    workflow.add_node("rag_retrieval", rag_node)
    workflow.add_node("generate", generator_node)
    workflow.add_node("review", reviewer_node)

    # 设置入口点
    workflow.set_entry_point("rag_retrieval")

    # 添加确定性边
    workflow.add_edge("rag_retrieval", "generate")
    workflow.add_edge("generate", "review")

    # 添加条件边用于修订循环
    # 关键：条件边必须返回字符串键，不能是布尔值
    workflow.add_conditional_edges(
        "review",
        should_revise,
        {
            "revise": "generate",
            "complete": END,
        }
    )

    return workflow


async def compile_workflow(
    checkpointer: Optional[PostgresSaver] = None,
    store: Optional[dict] = None,
) -> StateGraph:
    """编译工作流并可选地添加持久化。

    Args:
        checkpointer: PostgresSaver 用于状态持久化
        store: 内存存储（用于测试）

    Returns:
        编译后的可执行工作流

    关键：在生产环境中必须使用 checkpointer 进行状态持久化
    """
    workflow = await build_workflow()

    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    elif store:
        return workflow.compile(store=store)
    else:
        return workflow.compile()


def should_revise(state: DocumentState) -> str:
    """确定文档是否需要修订。

    决策逻辑:
    1. 如果分数 >= 0.85，完成
    2. 如果达到最大修订次数，完成
    3. 否则，继续修订

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
