# 🚀 DocuGen 初始化指南

本文档提供 DocuGen 多智能体文档生成系统的初始化配置、工具定义、提示词模板和开发示例。

---

## 📦 依赖配置

### Python 后端依赖 (pyproject.toml)

```toml
[project]
name = "docugen"
version = "0.1.0"
description = "多智能体文档生成系统"
requires-python = ">=3.11"
dependencies = [
    # LangGraph 核心
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-anthropic>=0.3.0",

    # Web 框架
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",

    # 数据库
    "sqlmodel>=0.0.22",
    "asyncpg>=0.30.0",
    "pgvector>=0.3.0",
    "alembic>=1.14.0",

    # 数据验证
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",

    # LLM 客户端
    "openai>=1.60.0",
    "anthropic>=0.40.0",

    # 工具库
    "python-dotenv>=1.0.0",
    "numpy>=1.26.0",
    "tenacity>=9.0.0",
    "aiofiles>=24.1.0",
    "httpx>=0.28.0",
    "rich>=13.9.0",

    # 文档解析
    "pypdf>=5.0.0",
    "python-docx>=1.1.0",
    "beautifulsoup4>=4.12.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "black>=25.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

### Node.js 前端依赖 (package.json)

```json
{
  "name": "docugen-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "react-hook-form": "^7.48.0",
    "tailwindcss": "^3.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0",
    "eslint": "^8.55.0",
    "eslint-config-next": "^14.0.0"
  }
}
```

---

## 🛠️ 工具定义

### 召回工具 (Retriever Tools)

```python
# app/agents/retriever/tools.py
from langchain_core.tools import tool
from typing import Optional

@tool
async def vector_search(
    query: str,
    knowledge_ids: list[str],
    top_k: int = 10,
    threshold: float = 0.7
) -> list[dict]:
    """在知识库中执行向量相似度搜索。

    Args:
        query: 搜索查询文本
        knowledge_ids: 要搜索的知识库文档ID列表
        top_k: 返回结果数量
        threshold: 相似度阈值

    Returns:
        匹配的文档块列表，包含内容和相似度分数
    """
    # 使用 PGVector 进行向量搜索
    # SELECT ... ORDER BY embedding <=> query_embedding LIMIT top_k
    pass


@tool
async def keyword_search(
    query: str,
    knowledge_ids: list[str],
    top_k: int = 10
) -> list[dict]:
    """在知识库中执行关键词搜索。

    Args:
        query: 搜索关键词
        knowledge_ids: 知识库范围
        top_k: 返回结果数量

    Returns:
        匹配的文档块列表
    """
    # 使用 PostgreSQL 全文搜索
    # SELECT ... WHERE to_tsvector(content) @@ to_tsquery(query)
    pass


@tool
async def hybrid_search(
    query: str,
    knowledge_ids: list[str],
    vector_weight: float = 0.7,
    top_k: int = 10
) -> list[dict]:
    """混合搜索：结合向量和关键词搜索。

    Args:
        query: 搜索查询
        knowledge_ids: 知识库范围
        vector_weight: 向量搜索权重 (0-1)
        top_k: 返回结果数量

    Returns:
        混合排序后的文档块列表
    """
    pass


@tool
async def ingest_document(
    file_path: str,
    user_id: str,
    chunk_size: int = 512,
    chunk_overlap: int = 50
) -> dict:
    """将文档导入知识库。

    Args:
        file_path: 上传文件路径
        user_id: 所有者用户ID
        chunk_size: 分块大小（字符）
        chunk_overlap: 分块重叠（字符）

    Returns:
        文档元数据，包含片段数量和处理状态
    """
    pass
```

### 生成工具 (Generator Tools)

```python
# app/agents/generator/tools.py
from langchain_core.tools import tool
from typing import Optional

@tool
def create_outline(
    requirements: str,
    spec: Optional[dict],
    retrieved_docs: list[dict]
) -> dict:
    """根据需求和规范创建文档大纲。

    Args:
        requirements: 用户需求描述
        spec: 文档规范
        retrieved_docs: 召回的参考文档

    Returns:
        文档大纲结构
    """
    pass


@tool
def write_section(
    section_title: str,
    section_requirements: str,
    reference_content: list[str],
    style_guide: Optional[dict]
) -> str:
    """撰写单个章节内容。

    Args:
        section_title: 章节标题
        section_requirements: 章节要求
        reference_content: 参考内容
        style_guide: 风格指南

    Returns:
        章节文本内容
    """
    pass


@tool
def format_document(
    content: str,
    format_spec: dict
) -> str:
    """根据规范格式化文档。

    Args:
        content: 原始文档内容
        format_spec: 格式规范

    Returns:
        格式化后的文档
    """
    pass


@tool
def merge_sections(
    sections: list[dict],
    order: list[str]
) -> str:
    """合并多个章节为完整文档。

    Args:
        sections: 章节列表
        order: 章节顺序

    Returns:
        完整文档文本
    """
    pass


@tool
async def get_spec_info(spec_id: str) -> dict:
    """获取文档规范信息。

    Args:
        spec_id: 规范标识符

    Returns:
        规范章节、格式规则、必填字段
    """
    pass
```

### 评审工具 (Reviewer Tools)

```python
# app/agents/reviewer/tools.py
from langchain_core.tools import tool
from typing import Optional

@tool
def validate_completeness(
    document: str,
    required_sections: list[str],
    required_fields: list[str]
) -> dict:
    """验证文档完整性。

    Args:
        document: 文档内容
        required_sections: 必需章节列表
        required_fields: 必需字段列表

    Returns:
        验证结果，包含缺失项列表
    """
    pass


@tool
def check_compliance(
    document: str,
    spec: dict
) -> dict:
    """检查文档是否符合规范。

    Args:
        document: 文档内容
        spec: 文档规范

    Returns:
        合规性检查结果
    """
    pass


@tool
def score_quality(
    document: str,
    dimensions: list[str],
    rubric: dict
) -> dict:
    """对文档进行多维度评分。

    Args:
        document: 文档内容
        dimensions: 评分维度列表
        rubric: 评分标准

    Returns:
        各维度分数和总分
    """
    pass


@tool
def generate_suggestions(
    issues: list[dict],
    document: str
) -> list[str]:
    """根据问题生成改进建议。

    Args:
        issues: 检测到的问题列表
        document: 文档内容

    Returns:
        具体改进建议列表
    """
    pass


@tool
def verify_facts(
    document: str,
    knowledge_context: list[str]
) -> dict:
    """根据知识库验证事实陈述。

    Args:
        document: 待验证文档
        knowledge_context: 用于生成的检索上下文

    Returns:
        带置信度分数的事实检查结果
    """
    pass
```

---

## 📝 提示词模板

### 召回智能体提示词

```python
# app/agents/retriever/prompts.py

RETRIEVER_SYSTEM_PROMPT = """你是一个专业的知识检索智能体。

你的任务是：
1. 理解用户的文档需求
2. 从知识库中检索最相关的参考资料
3. 过滤和排序检索结果，确保相关性

检索策略：
- 对于具体技术问题，优先使用关键词搜索
- 对于概念性和综合性需求，优先使用向量搜索
- 复杂需求使用混合搜索

输出格式：
返回检索到的文档片段，标注来源和相关性分数。
"""

RETRIEVER_USER_PROMPT = """
用户需求：
{requirements}

文档规范：
{spec}

知识库范围：
{knowledge_ids}

请检索相关参考资料。
"""
```

### 生成智能体提示词

```python
# app/agents/generator/prompts.py

PLANNER_SYSTEM_PROMPT = """你是一个文档规划智能体。

你的任务是根据用户需求和文档规范，规划文档结构。

规划原则：
1. 严格遵循文档规范中的章节要求
2. 合理组织内容层次
3. 确保逻辑连贯性
4. 参考核对资料中的有效信息

输出格式：
返回JSON格式的文档大纲，包含：
- 章节标题
- 章节顺序
- 每个章节的要点
"""

WRITER_SYSTEM_PROMPT = """你是一个专业文档撰写智能体。

你的任务是根据大纲撰写高质量文档内容。

撰写原则：
1. 内容准确、专业
2. 语言规范、流畅
3. 结构清晰、层次分明
4. 引用参考资料时注明来源

写作风格：
- 使用专业术语
- 避免口语化表达
- 保持客观中立
"""

FORMATTER_SYSTEM_PROMPT = """你是一个文档格式化智能体。

你的任务是根据文档规范对文档进行格式化。

格式化规则：
- 标题层级
- 段落格式
- 列表格式
- 引用格式
- 表格格式
"""
```

### 评审智能体提示词

```python
# app/agents/reviewer/prompts.py

VALIDATOR_SYSTEM_PROMPT = """你是一个文档验证智能体。

你的任务是验证文档是否满足规范要求。

验证项目：
1. 完整性：所有必需章节和字段是否存在
2. 结构性：文档结构是否符合规范
3. 内容性：每个章节内容是否完整

输出格式：
返回验证结果，包含：
- 是否通过验证
- 缺失项列表
- 结构问题列表
"""

SCORER_SYSTEM_PROMPT = """你是一个文档评分智能体。

你的任务是对文档进行多维度评分。

评分维度：
- 完整性 (completeness): 0-1分
- 准确性 (accuracy): 0-1分
- 规范性 (compliance): 0-1分
- 可读性 (readability): 0-1分

评分标准：
- 0.9-1.0: 优秀
- 0.7-0.89: 良好
- 0.5-0.69: 及格
- 0-0.49: 不合格
"""

FEEDBACK_SYSTEM_PROMPT = """你是一个文档反馈智能体。

你的任务是根据验证和评分结果，生成具体的改进建议。

反馈原则：
1. 指出具体问题位置
2. 提供具体改进建议
3. 给出参考示例
4. 优先处理高优先级问题

输出格式：
{
    "decision": "approved" | "needs_revision",
    "overall_score": 0.85,
    "scores": {
        "completeness": 0.9,
        "accuracy": 0.8,
        "compliance": 0.85,
        "readability": 0.85
    },
    "feedback": {
        "completeness": ["缺失摘要部分"],
        "accuracy": ["数据来源未标注"],
        "compliance": ["章节顺序不符合规范"],
        "readability": ["部分段落过长"]
    },
    "suggestions": [
        "在文档开头添加摘要章节",
        "为所有数据添加来源引用"
    ]
}
"""
```

---

## 💡 开发示例

### 示例 1: 基础智能体实现

```python
# app/agents/retriever/agent.py
from typing import Any
from langchain_openai import ChatOpenAI

from app.agents.base.agent import BaseAgent
from app.agents.state import DocumentState
from app.agents.retriever.tools import (
    vector_search, keyword_search, hybrid_search
)
from app.agents.retriever.prompts import RETRIEVER_SYSTEM_PROMPT


class RetrieverAgent(BaseAgent[DocumentState]):
    """召回智能体实现。"""

    def __init__(self, llm: ChatOpenAI):
        self._llm = llm

    @property
    def name(self) -> str:
        return "retriever"

    @property
    def description(self) -> str:
        return "从知识库中检索相关文档"

    async def __call__(
        self,
        state: DocumentState,
        config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """执行召回逻辑。

        关键：必须返回部分状态更新，而不是完整状态。
        """
        # 验证输入
        if not state.get("requirements"):
            return {"error": "缺少需求描述", "status": "failed"}

        # 选择搜索策略
        if state.get("knowledge_ids"):
            # 混合搜索
            results = await hybrid_search.ainvoke({
                "query": state["requirements"],
                "knowledge_ids": state["knowledge_ids"],
                "top_k": 10
            })
        else:
            results = []

        # 返回部分状态更新（重要！）
        return {
            "retrieved_docs": results,
            "current_step": "generating"
        }

    def get_tools(self) -> list[Any]:
        return [vector_search, keyword_search, hybrid_search]

    def get_prompt(self) -> str:
        return RETRIEVER_SYSTEM_PROMPT

    def validate_input(self, state: DocumentState) -> bool:
        """验证输入状态是否有效。"""
        return bool(state.get("requirements"))

    def handle_error(
        self,
        error: Exception,
        state: DocumentState
    ) -> dict[str, Any]:
        """错误处理回调。"""
        return {
            "error": str(error),
            "status": "failed",
            "current_step": "retrieving"
        }
```

### 示例 2: 子图实现

```python
# app/agents/generator/graph.py
from langgraph.graph import StateGraph, START, END

from app.agents.base.subgraph import BaseSubgraph
from app.agents.generator.agents.planner import PlannerAgent
from app.agents.generator.agents.writer import WriterAgent
from app.agents.generator.agents.formatter import FormatterAgent
from app.agents.generator.state import GeneratorState


class GeneratorSubgraph(BaseSubgraph[GeneratorState]):
    """生成子图实现。

    内部流程：规划 → 撰写 → 格式化
    """

    def __init__(self):
        self.planner = PlannerAgent()
        self.writer = WriterAgent()
        self.formatter = FormatterAgent()

    @property
    def name(self) -> str:
        return "generator"

    def get_state_schema(self) -> type[GeneratorState]:
        return GeneratorState

    def build_graph(self) -> StateGraph:
        """构建生成子图。"""
        graph = StateGraph(GeneratorState)

        # 添加节点
        graph.add_node("planner", self.planner)
        graph.add_node("writer", self.writer)
        graph.add_node("formatter", self.formatter)

        # 定义边
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "writer")
        graph.add_edge("writer", "formatter")
        graph.add_edge("formatter", END)

        return graph
```

### 示例 3: 评审子图实现

```python
# app/agents/reviewer/graph.py
from langgraph.graph import StateGraph, START, END

from app.agents.base.subgraph import BaseSubgraph
from app.agents.reviewer.agents.validator import ValidatorAgent
from app.agents.reviewer.agents.scorer import ScorerAgent
from app.agents.reviewer.agents.feedback import FeedbackAgent
from app.agents.reviewer.state import ReviewerState


class ReviewerSubgraph(BaseSubgraph[ReviewerState]):
    """评审子图实现。

    内部流程：验证 → 评分 → 反馈
    """

    def __init__(self):
        self.validator = ValidatorAgent()
        self.scorer = ScorerAgent()
        self.feedback = FeedbackAgent()

    @property
    def name(self) -> str:
        return "reviewer"

    def get_state_schema(self) -> type[ReviewerState]:
        return ReviewerState

    def build_graph(self) -> StateGraph:
        """构建评审子图。"""
        graph = StateGraph(ReviewerState)

        # 添加节点
        graph.add_node("validator", self.validator)
        graph.add_node("scorer", self.scorer)
        graph.add_node("feedback", self.feedback)

        # 定义边
        graph.add_edge(START, "validator")
        graph.add_edge("validator", "scorer")
        graph.add_edge("scorer", "feedback")
        graph.add_edge("feedback", END)

        return graph

    def make_decision(self, state: ReviewerState) -> str:
        """做出评审决策。

        Returns:
            "approved" 或 "needs_revision"
        """
        # 检查验证是否通过
        if not state.get("validation_passed"):
            return "needs_revision"

        # 检查总体分数
        overall_score = state.get("overall_score", 0)
        if overall_score < 0.85:
            return "needs_revision"

        return "approved"
```

### 示例 4: 主图构建

```python
# app/agents/orchestrator/graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from app.agents.state import DocumentState
from app.agents.retriever.agent import RetrieverAgent
from app.agents.generator.graph import GeneratorSubgraph
from app.agents.reviewer.graph import ReviewerSubgraph


def should_revise(state: DocumentState) -> str:
    """路由函数：决定是否需要修订。

    Args:
        state: 当前工作流状态

    Returns:
        "revise" 或 "complete"
    """
    # 被取消
    if state.get("status") == "cancelled":
        return "complete"

    # 超过最大修订次数
    revision_count = state.get("revision_count", 0)
    max_revisions = state.get("max_revisions", 3)
    if revision_count >= max_revisions:
        return "complete"

    # 检查评审决策
    review_feedback = state.get("review_feedback", {})
    if review_feedback.get("decision") == "approved":
        return "complete"

    return "revise"


def build_main_graph(checkpointer: PostgresSaver):
    """构建主工作流图。

    流程：召回 → 生成 → 评审 → [修订循环]
    """
    graph = StateGraph(DocumentState)

    # 初始化智能体
    retriever = RetrieverAgent()
    generator = GeneratorSubgraph()
    reviewer = ReviewerSubgraph()

    # 添加节点
    graph.add_node("retriever", retriever)
    # 子图作为节点，checkpointer 从父图继承
    graph.add_node("generator", generator.compile())
    graph.add_node("reviewer", reviewer.compile())

    # 定义边
    graph.add_edge(START, "retriever")
    graph.add_edge("retriever", "generator")
    graph.add_edge("generator", "reviewer")

    # 条件边：根据评审结果决定下一步
    graph.add_conditional_edges(
        "reviewer",
        should_revise,
        {
            "revise": "generator",  # 需要修订，返回生成器
            "complete": END         # 通过评审，结束
        }
    )

    return graph.compile(checkpointer=checkpointer)
```

### 示例 5: 暂停与恢复 (Human-in-the-Loop)

```python
# app/agents/reviewer/agents/feedback.py
from langgraph.types import interrupt
from typing import Any

from app.agents.base.agent import BaseAgent
from app.agents.reviewer.state import ReviewerState


class FeedbackAgent(BaseAgent[ReviewerState]):
    """反馈智能体，支持用户审批。"""

    @property
    def name(self) -> str:
        return "feedback"

    @property
    def description(self) -> str:
        return "生成改进反馈并等待用户确认"

    async def __call__(
        self,
        state: ReviewerState,
        config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """生成反馈，必要时暂停等待用户确认。"""
        # 生成反馈
        feedback = await self._generate_feedback(state)
        decision = self._make_decision(state)

        result = {
            "feedback": feedback,
            "suggestions": feedback.get("suggestions", []),
            "decision": decision
        }

        # 如果需要修订，暂停等待用户确认
        if decision == "needs_revision":
            # interrupt() 会暂停工作流，等待外部输入
            user_response = interrupt({
                "message": "文档需要修订，是否继续？",
                "suggestions": feedback.get("suggestions", []),
                "current_score": state.get("overall_score", 0)
            })

            # 处理用户响应
            if user_response.get("action") == "cancel":
                return {**result, "decision": "cancelled"}

            if user_response.get("action") == "modify":
                # 用户修改了需求或提供了额外信息
                return {
                    **result,
                    "user_modifications": user_response.get("modifications")
                }

        return result

    async def _generate_feedback(self, state: ReviewerState) -> dict:
        """生成改进反馈。"""
        # 实现反馈生成逻辑
        pass

    def _make_decision(self, state: ReviewerState) -> str:
        """做出决策。"""
        if state.get("overall_score", 0) >= 0.85:
            return "approved"
        return "needs_revision"

    def get_tools(self) -> list:
        return []

    def get_prompt(self) -> str:
        return "你是一个文档反馈智能体..."
```

### 示例 6: 任务恢复服务

```python
# app/services/task_service.py
import asyncio
from typing import Optional

from app.agents.orchestrator.graph import app


async def resume_task(
    task_id: str,
    action: str = "continue",
    modifications: Optional[dict] = None
) -> None:
    """恢复暂停的任务。

    Args:
        task_id: 任务ID（也是 thread_id）
        action: 操作类型
            - "continue": 继续执行
            - "modify": 修改状态后继续
            - "restart": 从指定节点重新开始
        modifications: 状态修改内容
    """
    config = {"configurable": {"thread_id": task_id}}

    # 获取当前状态
    current_state = await app.aget_state(config)

    if not current_state.values:
        raise ValueError(f"Task {task_id} not found")

    if action == "continue":
        # 继续执行（从中断点恢复）
        await app.ainvoke(None, config)

    elif action == "modify":
        # 修改状态后继续
        if modifications:
            await app.aupdate_state(config, modifications)
        await app.ainvoke(None, config)

    elif action == "restart":
        # 从指定节点重新开始
        target_node = modifications.get("target_node", "generator")
        await app.aupdate_state(
            config,
            {
                "revision_count": 0,
                "status": "running",
                **{k: v for k, v in modifications.items()
                   if k != "target_node"}
            },
            as_node=target_node
        )
        await app.ainvoke(None, config)


async def get_task_state(task_id: str) -> dict:
    """获取任务状态。

    Args:
        task_id: 任务ID

    Returns:
        包含检查点的完整任务状态
    """
    config = {"configurable": {"thread_id": task_id}}
    state = await app.aget_state(config)
    return {
        "values": state.values,
        "next": state.next,
        "config": state.config,
        "created_at": state.created_at,
        "parent_config": state.parent_config
    }
```

### 示例 7: FastAPI 端点

```python
# app/api/routes/tasks.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import uuid

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class CreateTaskRequest(BaseModel):
    """创建任务请求。"""
    requirements: str = Field(..., min_length=10, max_length=10000)
    spec_id: Optional[str] = None
    knowledge_ids: list[str] = Field(default_factory=list)
    max_revisions: int = Field(default=3, ge=1, le=10)


class TaskResponse(BaseModel):
    """任务响应。"""
    task_id: str
    status: str
    current_step: str
    thread_id: str


class ResumeTaskRequest(BaseModel):
    """恢复任务请求。"""
    action: str = Field(default="continue")
    modifications: Optional[dict] = None


@router.post("/", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks
):
    """创建文档生成任务。"""
    from app.agents.orchestrator.graph import app

    task_id = str(uuid.uuid4())

    # 初始化状态
    initial_state = {
        "task_id": task_id,
        "thread_id": task_id,
        "user_id": "default",  # TODO: 从认证获取
        "requirements": request.requirements,
        "spec_id": request.spec_id,
        "knowledge_ids": request.knowledge_ids,
        "max_revisions": request.max_revisions,
        "revision_count": 0,
        "status": "running",
        "current_step": "retrieving",
        "retrieved_docs": [],
        "generated_document": "",
        "review_feedback": {}
    }

    # 后台启动工作流
    config = {"configurable": {"thread_id": task_id}}
    background_tasks.add_task(app.ainvoke, initial_state, config)

    return TaskResponse(
        task_id=task_id,
        status="running",
        current_step="retrieving",
        thread_id=task_id
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """获取任务状态。"""
    from app.services.task_service import get_task_state

    try:
        state = await get_task_state(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        task_id=task_id,
        status=state["values"].get("status", "unknown"),
        current_step=state["values"].get("current_step", "unknown"),
        thread_id=task_id
    )


@router.post("/{task_id}/resume", response_model=TaskResponse)
async def resume_task_endpoint(
    task_id: str,
    request: ResumeTaskRequest,
    background_tasks: BackgroundTasks
):
    """恢复暂停的任务。"""
    from app.services.task_service import resume_task

    background_tasks.add_task(
        resume_task,
        task_id,
        request.action,
        request.modifications
    )

    return TaskResponse(
        task_id=task_id,
        status="resuming",
        current_step="processing",
        thread_id=task_id
    )


@router.get("/{task_id}/state")
async def get_task_state_endpoint(task_id: str):
    """获取任务完整状态（用于调试）。"""
    from app.services.task_service import get_task_state

    try:
        return await get_task_state(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
```

---

## 📚 参考文档

### LangGraph 官方文档

| 主题 | 链接 |
|------|------|
| 应用结构 | https://docs.langchain.com/oss/python/langgraph/application-structure |
| 子图使用 | https://docs.langchain.com/oss/python/langgraph/use-subgraphs |
| 持久化 | https://docs.langchain.com/oss/python/langgraph/persistence |
| 内存管理 | https://docs.langchain.com/oss/python/langgraph/add-memory |
| Human-in-the-Loop | https://docs.langchain.com/oss/python/langgraph/human_in_the_loop |
| 检查点 | https://docs.langchain.com/oss/python/langgraph/reference/checkpoints |
| 条件边 | https://docs.langchain.com/oss/python/langgraph/how-tos/branching |

### LangChain 生态

| 主题 | 链接 |
|------|------|
| LangChain Python | https://python.langchain.com/docs/ |
| LangChain Tools | https://python.langchain.com/docs/concepts/tools |
| LangChain LCEL | https://python.langchain.com/docs/concepts/lcel |

### 数据库与框架

| 主题 | 链接 |
|------|------|
| FastAPI | https://fastapi.tiangolo.com/ |
| SQLModel | https://sqlmodel.tiangolo.com/ |
| PGVector | https://github.com/pgvector/pgvector |
| UV | https://docs.astral.sh/uv/ |
| AsyncPG | https://magicstack.github.io/asyncpg/ |

---

## 🔧 环境变量模板

```bash
# .env.example

# LLM 配置
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# 嵌入模型
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/docugen
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20

# 工作流配置
MAX_REVISIONS=3
DEFAULT_SEARCH_LIMIT=10
DEFAULT_TEXT_WEIGHT=0.3

# 分块配置
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# WebUI
WEBUI_HOST=0.0.0.0
WEBUI_PORT=7860
WEBUI_SHARE=false

# 日志
LOG_LEVEL=INFO
```

---

## ⚠️ 重要注意事项

### LangGraph 状态更新规则

```python
# ✅ 正确：返回部分状态更新
async def node(state: DocumentState) -> dict[str, Any]:
    return {"status": "completed", "current_step": "done"}

# ❌ 错误：返回完整状态
async def node(state: DocumentState) -> dict[str, Any]:
    return {**state, "status": "completed"}  # 会导致问题
```

### 子图 Checkpointer 继承

```python
# ✅ 正确：子图从父图继承 checkpointer
generator = GeneratorSubgraph()
graph.add_node("generator", generator.compile())  # 不传 checkpointer

# ❌ 错误：子图使用独立的 checkpointer
checkpointer = PostgresSaver(...)
graph.add_node("generator", generator.compile(checkpointer))  # 不推荐
```

### 状态隔离

```python
# 主图和子图状态是独立的
# 主图状态：DocumentState
# 生成子图状态：GeneratorState
# 评审子图状态：ReviewerState

# 状态通过输入/输出转换传递
# 参考 CLAUDE.md 中的状态定义
```

---

## ✅ 初始化检查清单

在开始开发前，确保：

- [ ] Python 3.11+ 已安装
- [ ] uv 包管理器已安装
- [ ] PostgreSQL 15+ 已安装并启用 PGVector 扩展
- [ ] Node.js 18+ 已安装（前端开发）
- [ ] .env 文件已配置
- [ ] 数据库连接测试通过
- [ ] 依赖安装完成 (`uv sync`)
- [ ] 运行测试通过 (`uv run pytest`)

---

## 🚀 快速启动

```bash
# 1. 安装依赖
uv sync

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 初始化数据库
uv run python -c "
import asyncio
from app.utils.db import init_db
asyncio.run(init_db())
"

# 4. 启动后端服务
uv run python -m app.main

# 5. 启动前端开发服务器（另一个终端）
cd frontend
npm install
npm run dev

# 服务地址：
# - API: http://localhost:8000
# - API 文档: http://localhost:8000/docs
# - 前端: http://localhost:3000
```

---

生成日期: 2026-03-12
状态: 准备开发
