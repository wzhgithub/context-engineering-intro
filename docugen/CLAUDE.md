# 📄 DocuGen - 专业文档生成多智能体系统

本文档定义了DocuGen专业文档生成系统的全局规则和架构设计。这是一个基于LangGraph框架的多智能体协作系统，用于生成高质量的专业文档。

**核心理念**：通过LangGraph的有状态图编排多个专业智能体，实现可中断、可恢复、可追溯的文档生成工作流。

---

## 🎯 项目概述

DocuGen是一个专业文档生成系统，用户可以通过自然语言需求和专业规范(spec)生成符合要求的专业文档。系统支持：

- **知识库召回**：从本地知识库中检索相关文档作为参考
- **迭代生成**：生成 → 审核 → 修订的闭环流程
- **流程控制**：用户可以从任意步骤暂停、恢复或重新开始
- **规范驱动**：严格按照用户定义的文档规范进行生成和评审

### 核心能力

1. **多智能体协作**：召回Agent、生成Agent、评审Agent各司其职
2. **Subgraph架构**：生成和评审作为独立子图，支持不同文档类型的定制流程
3. **状态持久化**：每个步骤状态持久化，支持断点恢复
4. **Human-in-the-Loop**：用户可随时介入、修改、审批

---

## 🏗️ 技术栈

### 后端
- **语言**: Python 3.11+
- **包管理**: uv (https://docs.astral.sh/uv/)
- **智能体框架**: LangGraph (https://docs.langchain.com/oss/python/langgraph/overview)
- **Web框架**: FastAPI
- **数据库**: PostgreSQL + PGVector
- **ORM**: SQLModel

### 前端
- **框架**: Node.js + React/Next.js
- **通信**: REST API + WebSocket (实时状态更新)

### AI/ML
- **LLM**: OpenAI/Anthropic (可配置)
- **嵌入**: text-embedding-3-small
- **向量存储**: PGVector

---

## 📁 项目结构

```
docugen/
├── pyproject.toml              # uv 包配置
├── uv.lock
├── .env.example
│
├── backend/                    # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   │
│   │   ├── agents/             # 智能体模块
│   │   │   ├── __init__.py
│   │   │   ├── base/           # 基类定义
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py    # BaseAgent 抽象类
│   │   │   │   ├── state.py    # 基础状态定义
│   │   │   │   └── tools.py    # 基础工具接口
│   │   │   │
│   │   │   ├── retriever/      # 召回 Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── agent.py    # RetrieverAgent 实现
│   │   │   │   ├── tools.py    # 召回工具
│   │   │   │   └── prompts.py
│   │   │   │
│   │   │   ├── generator/      # 生成 Agent (Subgraph)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── graph.py    # 生成子图定义
│   │   │   │   ├── agents/
│   │   │   │   │   ├── planner.py      # 规划器
│   │   │   │   │   ├── writer.py       # 写入器
│   │   │   │   │   └── formatter.py    # 格式化器
│   │   │   │   ├── tools.py
│   │   │   │   └── prompts.py
│   │   │   │
│   │   │   ├── reviewer/       # 评审 Agent (Subgraph)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── graph.py    # 评审子图定义
│   │   │   │   ├── agents/
│   │   │   │   │   ├── validator.py    # 验证器
│   │   │   │   │   ├── scorer.py       # 评分器
│   │   │   │   │   └── feedback.py     # 反馈生成器
│   │   │   │   ├── tools.py
│   │   │   │   └── prompts.py
│   │   │   │
│   │   │   └── orchestrator/   # 主编排器
│   │   │       ├── __init__.py
│   │   │       ├── graph.py    # 主图定义
│   │   │       └── routing.py  # 路由逻辑
│   │   │
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── task.py
│   │   │   ├── document.py
│   │   │   ├── spec.py
│   │   │   └── knowledge.py
│   │   │
│   │   ├── services/           # 业务服务
│   │   │   ├── __init__.py
│   │   │   ├── task_service.py
│   │   │   ├── knowledge_service.py
│   │   │   └── spec_service.py
│   │   │
│   │   ├── api/                # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── tasks.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── knowledge.py
│   │   │   │   └── specs.py
│   │   │   └── dependencies.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── db.py
│   │       └── llm.py
│   │
│   └── tests/
│       ├── conftest.py
│       ├── test_agents/
│       └── test_api/
│
├── frontend/                   # Node.js 前端
│   ├── package.json
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Generate.tsx    # 文档生成页面
│   │   │   ├── Knowledge.tsx   # 知识库管理
│   │   │   ├── Specs.tsx       # 规范管理
│   │   │   └── Tasks.tsx       # 任务监控
│   │   ├── components/
│   │   ├── hooks/
│   │   └── api/
│   └── public/
│
└── migrations/                 # 数据库迁移
```

---

## 🔄 LangGraph 工作流架构

### 主图架构

```
                    ┌─────────────────┐
                    │   START_NODE    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  RETRIEVER_NODE │
                    │  (召回Agent)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
           ┌────────│ GENERATOR_NODE  │◄───────┐
           │        │  (Subgraph)      │        │
           │        └────────┬────────┘        │
           │                 │                 │
           │                 ▼                 │
           │        ┌─────────────────┐        │
           │        │  REVIEWER_NODE  │────────┘
need_fix? │        │  (Subgraph)      │  revise
           │        └────────┬────────┘
           │                 │
           │                 │ approved
           │                 ▼
           │        ┌─────────────────┐
           └───────►│     END_NODE    │
                    └─────────────────┘
```

### 生成子图 (Generator Subgraph)

```
┌─────────────────────────────────────────────────────┐
│                  GENERATOR SUBGRAPH                  │
│                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│   │ PLANNER  │───►│  WRITER  │───►│FORMATTER │    │
│   └──────────┘    └──────────┘    └──────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 评审子图 (Reviewer Subgraph)

```
┌─────────────────────────────────────────────────────┐
│                  REVIEWER SUBGRAPH                   │
│                                                      │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    │
│   │VALIDATOR │───►│  SCORER  │───►│FEEDBACK  │    │
│   └──────────┘    └──────────┘    └──────────┘    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🤖 智能体接口设计

### BaseAgent 抽象基类

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any
from langgraph.graph import StateGraph

StateT = TypeVar("StateT")


class BaseAgent(ABC, Generic[StateT]):
    """智能体抽象基类。

    所有智能体必须实现此接口。基于LangGraph的节点函数模式，
    每个智能体是一个可执行的状态转换函数。

    参考文档:
    - https://docs.langchain.com/oss/python/langgraph/application-structure
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """智能体名称，用于日志和调试。"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """智能体功能描述。"""
        pass

    @abstractmethod
    async def __call__(
        self,
        state: StateT,
        config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        执行智能体逻辑。

        关键：必须返回部分状态更新，而不是完整状态。

        Args:
            state: 当前工作流状态
            config: 运行时配置（包含 thread_id, checkpointer 等）

        Returns:
            部分状态更新字典
        """
        pass

    @abstractmethod
    def get_tools(self) -> list[Any]:
        """
        获取智能体可用的工具列表。

        Returns:
            工具列表
        """
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        """
        获取智能体的系统提示词。

        Returns:
            系统提示词字符串
        """
        pass

    def validate_input(self, state: StateT) -> bool:
        """
        验证输入状态是否有效。

        Args:
            state: 输入状态

        Returns:
            是否有效

        Raises:
            ValidationError: 输入无效时抛出
        """
        return True

    def handle_error(self, error: Exception, state: StateT) -> dict[str, Any]:
        """
        错误处理回调。

        Args:
            error: 捕获的异常
            state: 当前状态

        Returns:
            错误状态更新
        """
        return {"error": str(error), "status": "failed"}
```

### BaseSubgraph 抽象基类

```python
from abc import ABC, abstractmethod
from typing import TypeVar
from langgraph.graph import StateGraph, CompiledGraph
from langgraph.checkpoint.base import BaseCheckpointSaver

StateT = TypeVar("StateT")


class BaseSubgraph(ABC, Generic[StateT]):
    """子图抽象基类。

    子图是一个独立的工作流，可以嵌入到父图中。
    子图有自己的状态、节点和边。

    参考文档:
    - https://docs.langchain.com/oss/python/langgraph/use-subgraphs
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """子图名称。"""
        pass

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """
        构建子图结构。

        Returns:
            未编译的 StateGraph
        """
        pass

    @abstractmethod
    def get_state_schema(self) -> type[StateT]:
        """
        获取子图状态模式。

        Returns:
            状态 TypedDict 类
        """
        pass

    def compile(
        self,
        checkpointer: BaseCheckpointSaver | None = None
    ) -> CompiledGraph:
        """
        编译子图。

        Args:
            checkpointer: 检查点保存器

        Returns:
            编译后的可执行图

        注意: 子图的 checkpointer 会从父图继承
        参考: https://docs.langchain.com/oss/python/langgraph/persistence
        """
        graph = self.build_graph()
        return graph.compile(checkpointer=checkpointer)
```

### RetrieverAgent 接口

```python
class RetrieverAgent(BaseAgent[DocumentState]):
    """召回智能体接口。

    负责从知识库中检索与用户需求相关的专业文档。
    """

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        spec: Spec | None,
        knowledge_ids: list[str] | None,
        top_k: int = 10
    ) -> list[RetrievedDocument]:
        """
        执行知识召回。

        Args:
            query: 用户需求描述
            spec: 文档规范（可选，用于过滤相关文档）
            knowledge_ids: 指定的知识库文档ID（可选）
            top_k: 返回结果数量

        Returns:
            检索到的文档列表
        """
        pass

    @abstractmethod
    async def hybrid_search(
        self,
        query: str,
        knowledge_ids: list[str],
        vector_weight: float = 0.7
    ) -> list[RetrievedDocument]:
        """
        混合搜索（向量 + 关键词）。

        Args:
            query: 搜索查询
            knowledge_ids: 知识库范围
            vector_weight: 向量搜索权重

        Returns:
            检索结果
        """
        pass
```

### GeneratorSubgraph 接口

```python
class GeneratorSubgraph(BaseSubgraph[GeneratorState]):
    """生成子图接口。

    负责根据需求和召回的知识生成专业文档。
    支持不同文档类型的定制流程。

    内部节点:
    - PlannerAgent: 规划文档结构
    - WriterAgent: 撰写文档内容
    - FormatterAgent: 格式化输出
    """

    @abstractmethod
    async def plan(self, state: GeneratorState) -> dict:
        """
        规划文档结构。

        Args:
            state: 当前状态

        Returns:
            包含文档大纲的状态更新
        """
        pass

    @abstractmethod
    async def write(self, state: GeneratorState) -> dict:
        """
        撰写文档内容。

        Args:
            state: 包含大纲的状态

        Returns:
            包含草稿的状态更新
        """
        pass

    @abstractmethod
    async def format(self, state: GeneratorState) -> dict:
        """
        格式化文档。

        Args:
            state: 包含草稿的状态

        Returns:
            格式化后的最终文档
        """
        pass
```

### ReviewerSubgraph 接口

```python
class ReviewerSubgraph(BaseSubgraph[ReviewerState]):
    """评审子图接口。

    负责评估生成文档的质量，提供改进建议。
    严格按照用户定义的 Spec 进行评审。

    内部节点:
    - ValidatorAgent: 验证文档完整性
    - ScorerAgent: 评分各维度
    - FeedbackAgent: 生成反馈建议
    """

    @abstractmethod
    async def validate(self, state: ReviewerState) -> dict:
        """
        验证文档完整性。

        检查:
        - 是否满足 Spec 中定义的必填字段
        - 文档结构是否符合规范
        - 内容是否完整

        Args:
            state: 当前状态

        Returns:
            验证结果状态更新
        """
        pass

    @abstractmethod
    async def score(self, state: ReviewerState) -> dict:
        """
        对文档进行评分。

        评分维度:
        - 完整性 (completeness)
        - 准确性 (accuracy)
        - 规范性 (compliance)
        - 可读性 (readability)

        Args:
            state: 包含验证结果的状态

        Returns:
            包含评分的状态更新
        """
        pass

    @abstractmethod
    async def generate_feedback(self, state: ReviewerState) -> dict:
        """
        生成改进反馈。

        Args:
            state: 包含评分的状态

        Returns:
            包含具体改进建议的状态更新
        """
        pass

    @abstractmethod
    def make_decision(self, state: ReviewerState) -> str:
        """
        做出评审决策。

        Args:
            state: 完整评审状态

        Returns:
            "approved" 或 "needs_revision"
        """
        pass
```

---

## 🗄️ 状态定义

### 主图状态

```python
from typing import TypedDict, Annotated
from operator import add
from datetime import datetime


class DocumentState(TypedDict):
    """文档生成主工作流状态。

    状态流转: init → retrieving → generating → reviewing → completed/failed
    """

    # 任务标识
    task_id: str
    thread_id: str  # LangGraph 持久化线程ID
    user_id: str

    # 用户输入
    requirements: str  # 自然语言需求描述
    spec_id: str | None  # 文档规范ID
    knowledge_ids: list[str]  # 指定的知识库文档

    # 召回阶段
    retrieved_docs: Annotated[list[dict], add]
    retrieval_score: float

    # 生成阶段
    document_outline: dict
    document_draft: str
    generated_document: str
    generation_metadata: dict

    # 评审阶段
    validation_result: dict
    review_score: float
    review_feedback: dict
    revision_suggestions: list[str]

    # 流程控制
    revision_count: int
    max_revisions: int
    current_step: str  # init, retrieving, generating, reviewing, completed, failed
    status: str  # pending, running, paused, completed, failed
    error: str | None

    # 检查点
    checkpoint_id: str | None
    created_at: datetime
    updated_at: datetime
```

### 生成子图状态

```python
class GeneratorState(TypedDict):
    """生成子图状态。"""

    # 输入
    requirements: str
    retrieved_docs: list[dict]
    spec: dict | None

    # 规划
    outline: dict
    sections: list[str]

    # 写入
    current_section: str
    section_content: str
    full_draft: str

    # 格式化
    formatted_document: str

    # 元数据
    generation_config: dict
```

### 评审子图状态

```python
class ReviewerState(TypedDict):
    """评审子图状态。"""

    # 输入
    document: str
    requirements: str
    spec: dict | None
    retrieved_docs: list[dict]

    # 验证
    validation_passed: bool
    missing_fields: list[str]
    structure_issues: list[str]

    # 评分
    scores: dict[str, float]  # {"completeness": 0.9, "accuracy": 0.8, ...}
    overall_score: float

    # 反馈
    feedback: dict[str, list[str]]  # {"completeness": ["缺失摘要"], ...}
    suggestions: list[str]

    # 决策
    decision: str  # "approved" | "needs_revision"
```

---

## 🔌 流程控制与恢复

### 检查点机制

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph

# 编译图时启用持久化
checkpointer = PostgresSaver(connection_string)
app = graph.compile(checkpointer=checkpointer)

# 执行时指定 thread_id
config = {"configurable": {"thread_id": "task-123"}}
result = await app.ainvoke(initial_state, config)

# 恢复执行
state = await app.aget_state(config)
# 从检查点恢复
result = await app.ainvoke(None, config)

# 从特定节点恢复
await app.aupdate_state(
    config,
    {"status": "restarted"},
    as_node="generator"
)
```

### 暂停与恢复

```python
from langgraph.types import interrupt

async def review_node(state: DocumentState) -> dict:
    """支持用户审批的评审节点。"""
    result = await review_document(state)

    if result["decision"] == "needs_revision":
        # 暂停等待用户确认
        user_input = interrupt({
            "message": "文档需要修订，是否继续？",
            "suggestions": result["suggestions"]
        })

        if user_input == "cancel":
            return {"status": "cancelled"}

    return result
```

### 步骤跳转

```python
# 用户可以从任意步骤恢复
async def resume_from_step(
    task_id: str,
    step: str,
    modifications: dict | None = None
) -> None:
    """从指定步骤恢复任务。

    Args:
        task_id: 任务ID
        step: 目标步骤 (retrieving, generating, reviewing)
        modifications: 状态修改
    """
    config = {"configurable": {"thread_id": task_id}}

    if modifications:
        await app.aupdate_state(config, modifications, as_node=step)

    # 继续执行
    await app.ainvoke(None, config)
```

---

## 🧪 测试要求

### 单元测试
- 每个Agent独立测试
- 状态转换测试
- 工具函数测试

### 集成测试
- 完整工作流测试
- 子图集成测试
- 持久化和恢复测试

### 测试覆盖率
- 目标: >80%

---

## 📚 参考文档

### LangGraph 核心
- **应用结构**: https://docs.langchain.com/oss/python/langgraph/application-structure
- **子图使用**: https://docs.langchain.com/oss/python/langgraph/use-subgraphs
- **持久化**: https://docs.langchain.com/oss/python/langgraph/persistence
- **内存管理**: https://docs.langchain.com/oss/python/langgraph/add-memory

### 工具与模式
- **LangChain**: https://python.langchain.com/docs/
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **UV**: https://docs.astral.sh/uv/

---

## 🚫 反模式警告

- ❌ 不要返回完整状态，只返回部分更新
- ❌ 不要在子图中使用独立的 checkpointer（从父图继承）
- ❌ 不要硬编码API密钥
- ❌ 不要忽略状态验证
- ❌ 不要在并发节点中修改共享状态
- ❌ 不要跳过错误处理

---

## ✅ 检查清单

在标记任务完成前:
- [ ] 所有Agent实现BaseAgent接口
- [ ] 子图正确编译并集成
- [ ] 状态持久化正常工作
- [ ] 暂停/恢复正常工作
- [ ] 步骤跳转功能可用
- [ ] API端点完整
- [ ] WebUI功能完整
- [ ] 测试覆盖率达标
