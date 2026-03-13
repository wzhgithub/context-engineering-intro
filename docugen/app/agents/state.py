"""LangGraph 状态定义。

定义文档生成工作流的状态结构。
"""

from typing import TypedDict, Annotated, Optional
from operator import add


class RetrievedContext(TypedDict):
    """RAG 检索的上下文结果。"""
    content: str
    document_id: str
    source: str
    chunk_index: int
    similarity: float


class ReviewFeedback(TypedDict):
    """审查反馈结构。"""
    completeness: dict
    accuracy: dict
    quality: dict
    compliance: dict


class DocumentState(TypedDict):
    """文档生成工作流状态。

    关键：LangGraph 节点必须返回部分状态更新，而不是完整状态。

    状态流转:
    pending -> rag -> generating -> reviewing -> completed/failed

    修订循环:
    如果 review_score < 0.85 且 revision_count < max_revisions，
    则从 reviewing 返回 generating 进行修订。
    """

    # 标识符
    task_id: str
    user_id: str
    thread_id: str

    # 用户输入
    user_requirements: str
    template_id: Optional[str]
    knowledge_ids: list[str]

    # RAG 阶段
    knowledge_query: str
    retrieved_context: Annotated[list[RetrievedContext], add]
    retrieval_score: float

    # 生成阶段
    generated_content: str
    generation_metadata: dict

    # 审查阶段
    review_score: float
    review_feedback: ReviewFeedback
    revision_suggestions: list[str]

    # 工作流控制
    revision_count: int
    max_revisions: int
    status: str  # pending, rag, generating, reviewing, completed, failed
    error: Optional[str]


def create_initial_state(
    task_id: str,
    user_id: str,
    thread_id: str,
    requirements: str,
    template_id: Optional[str] = None,
    knowledge_ids: Optional[list[str]] = None,
    max_revisions: int = 3,
) -> DocumentState:
    """创建初始状态。

    Args:
        task_id: 任务 ID
        user_id: 用户 ID
        thread_id: LangGraph 线程 ID（用于检查点）
        requirements: 用户需求
        template_id: 可选的模板 ID
        knowledge_ids: 知识库 ID 列表
        max_revisions: 最大修订次数

    Returns:
        初始化的 DocumentState
    """
    return DocumentState(
        task_id=task_id,
        user_id=user_id,
        thread_id=thread_id,
        user_requirements=requirements,
        template_id=template_id,
        knowledge_ids=knowledge_ids or [],
        knowledge_query="",
        retrieved_context=[],
        retrieval_score=0.0,
        generated_content="",
        generation_metadata={},
        review_score=0.0,
        review_feedback={},
        revision_suggestions=[],
        revision_count=0,
        max_revisions=max_revisions,
        status="pending",
        error=None,
    )
