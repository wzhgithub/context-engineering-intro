"""数据库模型定义。

使用 SQLModel 进行 ORM 映射。
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid


class User(SQLModel, table=True):
    """用户模型用于认证。"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str = Field(..., min_length=1)
    hashed_password: str = Field(default="")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Task(SQLModel, table=True):
    """任务模型用于跟踪文档生成工作流。"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = Field(default="pending")

    # 输入数据
    requirements: str
    template_id: Optional[str] = Field(default=None, foreign_key="template.id")
    knowledge_ids: list[str] = Field(default_factory=list)

    # 工作流状态（序列化的 LangGraph 状态）
    workflow_state: dict = Field(default_factory=dict)
    current_stage: str = Field(default="pending")
    revision_count: int = Field(default=0)
    max_revisions: int = Field(default=3)

    # 输出
    generated_document: Optional[str] = Field(default=None)
    review_feedback: Optional[dict] = Field(default=None)

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    error: Optional[str] = Field(default=None)


class Template(SQLModel, table=True):
    """用户定义的文档模板。"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)

    # 模板结构
    sections: dict = Field(default_factory=dict)
    formatting_rules: dict = Field(default_factory=dict)
    required_fields: list[str] = Field(default_factory=list)

    # 元数据
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeDocument(SQLModel, table=True):
    """知识库中的文档。"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    title: str
    content: str
    source: Optional[str] = Field(default=None)
    file_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeChunk(SQLModel, table=True):
    """用于 RAG 检索的文档分块。"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    document_id: str = Field(foreign_key="knowledgedocument.id")
    content: str
    chunk_index: int
    # 嵌入通过 PGVector 单独存储
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GeneratedDocument(SQLModel, table=True):
    """生成的文档输出。"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="task.id")
    user_id: str = Field(foreign_key="user.id")
    title: Optional[str] = Field(default=None)
    content: str
    template_id: Optional[str] = Field(default=None, foreign_key="template.id")
    review_score: Optional[float] = Field(default=None)
    review_feedback: Optional[dict] = Field(default=None)
    status: str = Field(default="completed")
    error: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
