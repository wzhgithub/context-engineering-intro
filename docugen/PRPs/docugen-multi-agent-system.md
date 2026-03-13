name: "DocuGen 多智能体文档生成系统 - 完整 PRP（含架构升级）"
description: |

## Purpose
使用 LangGraph 进行智能体编排，构建生产级多智能体文档生成系统。在已完成基础实现的基础上，升级为 CLAUDE.md 定义的完整架构：BaseAgent 抽象基类、BaseSubgraph 子图模式、Human-in-the-Loop 支持、任务恢复能力。

## Core Principles
1. **Context is King**: 包含所有必要的文档、示例和注意事项
2. **Validation Loops**: 提供 AI 可以运行和修复的可执行测试/lint
3. **Information Dense**: 使用代码库中的关键词和模式
4. **Progressive Success**: 从简单开始，验证，然后增强
5. **Global rules**: 遵循 docugen/CLAUDE.md 中的所有规则

---

## Goal
创建一个生产就绪的多智能体文档生成平台，完整实现 CLAUDE.md 架构设计：
1. 通过 WebUI 输入自然语言需求 ✅ 已完成
2. 定义和持久化自定义文档模板 ✅ 已完成
3. 导入知识文档进行 RAG 增强生成 ✅ 已完成（后台导入待完善）
4. 生成带有自动审查和迭代优化的文档 ✅ 已完成（扁平模式）
5. 持久化跟踪所有任务状态以便恢复和监控 ✅ 已完成
6. **BaseAgent + BaseSubgraph 架构** ⬜ 待实现
7. **Generator Subgraph (Planner→Writer→Formatter)** ⬜ 待实现
8. **Reviewer Subgraph (Validator→Scorer→Feedback)** ⬜ 待实现
9. **Human-in-the-Loop (interrupt/resume)** ⬜ 待实现
10. **任务恢复/跳转 API** ⬜ 待实现

## Why
- **商业价值**: 自动化专业文档创建并提供质量保证
- **架构对齐**: 当前扁平实现与 CLAUDE.md 架构设计文档存在结构性差距
- **可扩展性**: BaseAgent 模式支持统一的工具管理、提示词管理、输入验证和错误处理
- **子图复用**: Subgraph 模式允许不同文档类型定制不同的生成/审查流程
- **用户控制**: Human-in-the-Loop 让用户可以在审查后决定是否继续修订
- **生产就绪**: 任务恢复能力支持断点续传

## What
一个基于 WebUI 的应用程序：
- 用户以自然语言输入文档需求
- RAG Agent 从知识库检索相关上下文
- Generator Subgraph (Planner→Writer→Formatter) 创建结构化文档
- Reviewer Subgraph (Validator→Scorer→Feedback) 评估并提供反馈
- FeedbackAgent 使用 interrupt() 暂停等待用户确认
- Coordinator 编排多轮修订循环
- 所有状态持久化以便恢复和监控

### Success Criteria
**Phase 1 (已完成):**
- [x] LangGraph 工作流使用 StateGraph 编译
- [x] RAG Agent 使用 PGVector 检索相关上下文
- [x] Generator Agent 按照模板创建文档
- [x] Reviewer Agent 提供可操作的反馈
- [x] 多轮修订循环工作（最多 3 次修订）
- [x] 所有任务状态持久化到 PostgreSQL
- [x] WebUI 允许完整的用户交互
- [x] 基础测试覆盖

**Phase 2 (待实现 - 架构升级):**
- [ ] `BaseAgent` 抽象类定义在 `app/agents/base/agent.py`
- [ ] `BaseSubgraph` 抽象类定义在 `app/agents/base/subgraph.py`
- [ ] RAG Agent 继承 BaseAgent 并实现所有抽象方法
- [ ] Generator Subgraph 包含 PlannerAgent→WriterAgent→FormatterAgent
- [ ] Reviewer Subgraph 包含 ValidatorAgent→ScorerAgent→FeedbackAgent
- [ ] 主图使用编译后的子图作为节点
- [ ] FeedbackAgent 使用 `interrupt()` 暂停等待用户确认
- [ ] 新增 `/api/tasks/{task_id}/resume` 端点
- [ ] 知识库上传触发后台分块+嵌入任务
- [ ] 所有测试通过，覆盖率 >80%

## All Needed Context

### Documentation & References
```yaml
# MUST READ - 在上下文窗口中包含这些内容

# 项目核心文档
- file: docugen/CLAUDE.md
  why: BaseAgent、BaseSubgraph 的完整接口定义，状态结构，架构约束，反模式警告

- file: docugen/INITIAL.md
  why: 完整的功能需求、工具定义、提示词模板、开发示例（RetrieverAgent 实现、
       GeneratorSubgraph、ReviewerSubgraph、主图构建、interrupt() 用法、
       任务恢复服务、FastAPI 端点）

# 现有实现文件（需要修改）
- file: docugen/app/agents/graph.py
  why: 当前主图实现（需要修改为使用子图）

- file: docugen/app/agents/state.py
  why: 当前 DocumentState 定义（需要新增 GeneratorState、ReviewerState）

- file: docugen/app/agents/nodes.py
  why: 当前节点包装函数（将被子图替代）

- file: docugen/app/agents/rag/agent.py
  why: 当前 RAG 实现（需要重构为 BaseAgent 子类）

- file: docugen/app/agents/generator/agent.py
  why: 当前 Generator 实现（需要拆分为 Planner+Writer+Formatter）

- file: docugen/app/agents/reviewer/agent.py
  why: 当前 Reviewer 实现（需要拆分为 Validator+Scorer+Feedback）

# 配置和工具
- file: docugen/app/config.py
  why: Settings 配置模式（pydantic-settings + load_dotenv）

- file: docugen/app/utils/llm.py
  why: LLM 客户端工具（get_llm_client, get_llm_model）

- file: docugen/app/utils/db.py
  why: 数据库连接池和初始化

# 测试
- file: docugen/tests/conftest.py
  why: 现有测试 fixtures 模式（mock_settings, mock_db_pool, mock_openai_client）

- file: docugen/tests/test_agents/test_workflow.py
  why: 现有测试模式（TestShouldRevise, TestCreateInitialState, TestBuildWorkflow）

# 参考实现
- file: use-cases/agent-factory-with-subagents/agents/rag_agent/tools.py
  why: semantic_search 和 hybrid_search 实现模式

- file: use-cases/agent-factory-with-subagents/agents/rag_agent/dependencies.py
  why: 带有 db_pool 和 openai_client 的 AgentDependencies 模式

- file: use-cases/agent-factory-with-subagents/agents/rag_agent/ingestion/embedder.py
  why: 带重试逻辑的嵌入生成模式

# LangGraph 文档
- url: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams
  why: 分层多智能体编排模式（子图嵌入父图）

- url: https://langchain-ai.github.io/langgraph/how-tos/subgraph
  why: LangGraph 子图 API（add_node 接受编译后的子图）

- url: https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/breakpoints
  why: interrupt() 和 Command(resume=...) 用法

- url: https://langchain-ai.github.io/langgraph/concepts/persistence
  why: PostgresSaver checkpointer + 状态恢复

- url: https://langchain-ai.github.io/langgraph/how-tos/state-model
  why: 使用 TypedDict 状态定义的 StateGraph

- url: https://docs.langchain.com/oss/python/langgraph/overview
  why: LangGraph 核心概念和 API 参考

# 框架文档
- url: https://fastapi.tiangolo.com/tutorial/background-tasks/
  why: 长时间文档生成的后台任务模式

- url: https://www.gradio.app/docs/
  why: WebUI 组件文档
```

### Current Codebase tree (实际已存在的文件)
```bash
docugen/
├── CLAUDE.md                   # 架构设计文档（目标规范）
├── INITIAL.md                  # 初始化指南+开发示例
├── pyproject.toml              # UV 包配置
├── .env.example                # 环境模板
├── README.md                   # 文档
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI + Gradio 入口
│   ├── config.py               # pydantic-settings 配置
│   │
│   ├── agents/
│   │   ├── __init__.py         # 导出 DocumentState, build_workflow 等
│   │   ├── graph.py            # StateGraph（当前：扁平节点模式）
│   │   ├── state.py            # DocumentState, RetrievedContext, ReviewFeedback
│   │   ├── nodes.py            # rag_node, generator_node, reviewer_node 包装
│   │   ├── coordinator/
│   │   │   ├── __init__.py
│   │   │   └── routing.py      # should_revise, route_on_status, route_on_error
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py        # rag_node + rag_node_with_db 函数
│   │   │   ├── tools.py        # semantic_search, hybrid_search
│   │   │   └── prompts.py
│   │   ├── generator/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py        # generator_node 函数 + _format_feedback
│   │   │   ├── tools.py
│   │   │   └── prompts.py
│   │   └── reviewer/
│   │       ├── __init__.py
│   │       ├── agent.py        # reviewer_node + parse_review_response 等
│   │       ├── tools.py
│   │       └── prompts.py
│   │
│   ├── api/
│   │   ├── __init__.py         # api_router 注册 documents, templates, knowledge, tasks
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── documents.py    # POST /generate + run_workflow 后台任务
│   │       ├── templates.py    # CRUD: create, list, get, delete
│   │       ├── knowledge.py    # upload, list, delete (TODO: 后台分块嵌入)
│   │       └── tasks.py        # GET /{task_id}, GET /
│   │
│   ├── models/__init__.py      # User, Task, Template, KnowledgeDocument,
│   │                           # KnowledgeChunk, GeneratedDocument (SQLModel)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py     # TaskService (CRUD + workflow state)
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── chunker.py          # chunk_document, ChunkingConfig
│   │   ├── embedder.py         # Embedder (OpenAI)
│   │   └── ingest.py           # ingest_document 管道
│   │
│   ├── webui/
│   │   ├── __init__.py
│   │   └── app.py              # Gradio 4-tab 界面
│   │
│   └── utils/
│       ├── __init__.py
│       ├── db.py               # asyncpg pool, init_db (所有 DDL)
│       └── llm.py              # AsyncOpenAI + ChatOpenAI 客户端
│
└── tests/
    ├── __init__.py
    ├── conftest.py             # mock_settings, mock_db_pool, mock_openai_client 等
    ├── test_agents/
    │   ├── __init__.py
    │   ├── test_workflow.py    # TestShouldRevise, TestCreateInitialState, TestBuildWorkflow
    │   ├── test_rag.py
    │   ├── test_generator.py
    │   └── test_reviewer.py
    ├── test_api/
    │   ├── __init__.py
    │   └── test_routes.py
    └── test_services/
        ├── __init__.py
        └── test_services.py
```

### Desired Codebase tree (Phase 2 新增/修改的文件)
```bash
docugen/app/agents/
├── __init__.py                 # [修改] 更新导出
├── graph.py                    # [修改] 使用子图替代扁平节点
├── state.py                    # [修改] 新增 GeneratorState, ReviewerState
├── nodes.py                    # [修改] 简化为子图调用
│
├── base/                       # [新建] 基类模块
│   ├── __init__.py
│   ├── agent.py                # BaseAgent 抽象类
│   └── subgraph.py             # BaseSubgraph 抽象类
│
├── rag/
│   ├── agent.py                # [修改] 继承 BaseAgent
│   ├── tools.py                # 保持不变
│   └── prompts.py              # 保持不变
│
├── generator/
│   ├── __init__.py             # [修改] 导出
│   ├── graph.py                # [新建] GeneratorSubgraph
│   ├── agent.py                # [修改] 拆分为 PlannerAgent 调用入口
│   ├── agents/                 # [新建]
│   │   ├── __init__.py
│   │   ├── planner.py          # PlannerAgent(BaseAgent)
│   │   ├── writer.py           # WriterAgent(BaseAgent)
│   │   └── formatter.py        # FormatterAgent(BaseAgent)
│   ├── tools.py
│   └── prompts.py              # [修改] 新增 PLANNER/WRITER/FORMATTER 提示词
│
├── reviewer/
│   ├── __init__.py             # [修改] 导出
│   ├── graph.py                # [新建] ReviewerSubgraph
│   ├── agent.py                # [修改] 拆分为子图入口
│   ├── agents/                 # [新建]
│   │   ├── __init__.py
│   │   ├── validator.py        # ValidatorAgent(BaseAgent)
│   │   ├── scorer.py           # ScorerAgent(BaseAgent)
│   │   └── feedback.py         # FeedbackAgent(BaseAgent) + interrupt()
│   ├── tools.py
│   └── prompts.py              # [修改] 新增 VALIDATOR/SCORER/FEEDBACK 提示词
│
└── coordinator/
    ├── __init__.py
    └── routing.py              # 保持不变

docugen/app/api/routes/
├── tasks.py                    # [修改] 新增 POST /{task_id}/resume 端点
└── knowledge.py                # [修改] 上传后触发后台分块+嵌入

docugen/tests/
├── conftest.py                 # [修改] 新增子图相关 fixtures
└── test_agents/
    ├── test_base.py            # [新建] BaseAgent/BaseSubgraph 测试
    ├── test_workflow.py        # [修改] 适配新架构
    ├── test_generator.py       # [修改] 测试子图
    └── test_reviewer.py        # [修改] 测试子图
```

### Known Gotchas & Library Quirks
```python
# === LangGraph 核心规则 ===

# 关键: LangGraph 节点必须返回部分状态更新，不是完整状态
# 正确: return {"status": "completed", "generated_content": content}
# 错误: return {**state, "status": "completed"}

# 关键: 子图的 checkpointer 从父图继承，不要手动传入
# 正确: graph.add_node("generator", generator_subgraph.compile())
# 错误: graph.add_node("generator", generator_subgraph.compile(checkpointer=cp))

# 关键: 条件边返回字符串键，不是布尔值
# 正确: return "complete" or "revise"
# 错误: return True / False

# 关键: interrupt() 会暂停整个工作流，恢复时通过 Command(resume=value) 传入用户响应
# 正确: user_input = interrupt({"message": "确认?"})
#        → 外部: app.ainvoke(Command(resume={"action": "continue"}), config)

# 关键: BaseAgent.__call__ 是异步的，必须用 async def
# 正确: async def __call__(self, state, config=None) -> dict

# 关键: StateGraph 的节点可以是 callable 对象（实现 __call__ 的类实例）
# 正确: graph.add_node("planner", planner_agent)  # planner_agent 是 PlannerAgent 实例

# 关键: 子图状态和父图状态是独立的，需要通过输入/输出映射传递
# 主图 DocumentState 中的字段需要映射到子图的 GeneratorState/ReviewerState

# 关键: PostgresCheckpointer 需要异步上下文
# 必须: await checkpointer.aget(thread_id) / await checkpointer.aput(thread_id, checkpoint)

# 关键: LangGraph 节点必须是异步函数
# 必须: async def node_name(state: DocumentState) -> dict:

# === 数据库和嵌入 ===

# 关键: PGVector 嵌入格式是字符串 '[1.0,2.0,3.0]' 不是 Python 列表
# 正确: embedding_str = '[' + ','.join(map(str, embedding)) + ']'

# 关键: 嵌入维度必须在模型和数据库列之间匹配
# text-embedding-3-small = 1536 维度

# 关键: SQLModel 需要异步引擎进行异步操作
# 必须: from sqlalchemy.ext.asyncio import create_async_engine

# === 项目结构 ===

# 关键: app/utils/db.py 中的 settings 是直接导入的模块级变量
# 在 db.py 中: from app.config import settings (不是 get_settings())

# 关键: 现有 reviewer/agent.py 的 reviewer_node 函数签名有 db_pool 参数
# 在 nodes.py 中调用时用了别名: from .reviewer import reviewer_node as _reviewer_node

# 关键: uv 需要 pyproject.toml，而不是 requirements.txt
# 必须: 使用带 [project] 部分的 pyproject.toml

# 关键: Gradio 必须在与 FastAPI 相同的进程中运行以共享状态
# 必须: 将 Gradio 挂载到路径，不要作为单独进程运行
```

## Implementation Blueprint

### Data Models

#### 已有的 DocumentState（保持不变）
```python
# app/agents/state.py - 已存在
class DocumentState(TypedDict):
    task_id: str
    user_id: str
    thread_id: str
    user_requirements: str
    template_id: Optional[str]
    knowledge_ids: list[str]
    knowledge_query: str
    retrieved_context: Annotated[list[RetrievedContext], add]
    retrieval_score: float
    generated_content: str
    generation_metadata: dict
    review_score: float
    review_feedback: ReviewFeedback
    revision_suggestions: list[str]
    revision_count: int
    max_revisions: int
    status: str
    error: Optional[str]
```

#### 新增的子图状态
```python
# 新增到 app/agents/state.py

class GeneratorState(TypedDict):
    """生成子图状态。"""
    requirements: str
    retrieved_context: list[dict]
    template_id: Optional[str]
    revision_count: int
    review_feedback: dict
    outline: dict
    sections: list[str]
    current_section: str
    section_content: str
    full_draft: str
    formatted_document: str
    generation_metadata: dict

class ReviewerState(TypedDict):
    """评审子图状态。"""
    document: str
    requirements: str
    template_id: Optional[str]
    retrieved_context: list[dict]
    validation_passed: bool
    missing_fields: list[str]
    structure_issues: list[str]
    scores: dict[str, float]
    overall_score: float
    feedback: dict[str, list[str]]
    suggestions: list[str]
    decision: str  # "approved" | "needs_revision"
```

#### 已有的 SQLModel 模型（保持不变）
```python
# app/models/__init__.py - 已存在
# User, Task, Template, KnowledgeDocument, KnowledgeChunk, GeneratedDocument
```

### Tasks List (Phase 1 已完成 + Phase 2 待实现)

```yaml
# ========== Phase 1: 基础系统 (已完成 ✅) ==========

任务 1: 项目设置和配置 ✅
  - pyproject.toml, .env.example, app/config.py

任务 2: 数据库模型和初始化 ✅
  - app/models/__init__.py (SQLModel)
  - app/utils/db.py (init_db DDL)

任务 3: LangGraph 状态和工作流定义 ✅
  - app/agents/state.py (DocumentState)
  - app/agents/graph.py (扁平 StateGraph)
  - app/agents/nodes.py (节点包装)

任务 4: RAG Agent 实现 ✅
  - app/agents/rag/ (agent, tools, prompts)
  - app/ingestion/ (chunker, embedder, ingest)

任务 5: Generator Agent 实现 ✅
  - app/agents/generator/ (agent, tools, prompts) - 扁平模式

任务 6: Reviewer Agent 实现 ✅
  - app/agents/reviewer/ (agent, tools, prompts) - 扁平模式

任务 7: Coordinator 和路由逻辑 ✅
  - app/agents/coordinator/routing.py

任务 8: 服务层 ✅
  - app/services/task_service.py

任务 9: FastAPI 路由 ✅
  - app/api/routes/ (documents, templates, knowledge, tasks)

任务 10: Gradio WebUI ✅
  - app/webui/app.py (4-tab 界面)

任务 11: 主应用入口 ✅
  - app/main.py (FastAPI + Gradio 挂载)

任务 12: 基础测试 ✅
  - tests/ (conftest, test_agents, test_api, test_services)

# ========== Phase 2: 架构升级 (待实现 ⬜) ==========

任务 13: 创建 BaseAgent 和 BaseSubgraph 基类
CREATE app/agents/base/__init__.py:
  - 导出 BaseAgent, BaseSubgraph
CREATE app/agents/base/agent.py:
  - 照搬 CLAUDE.md 217-314 行的 BaseAgent 定义
  - ABC + Generic[StateT]
  - 抽象方法: name, description, __call__, get_tools, get_prompt
  - 默认方法: validate_input, handle_error
CREATE app/agents/base/subgraph.py:
  - 照搬 CLAUDE.md 318-381 行的 BaseSubgraph 定义
  - ABC + Generic[StateT]
  - 抽象方法: name, build_graph, get_state_schema
  - 默认方法: compile

任务 14: 新增 GeneratorState 和 ReviewerState 到 state.py
MODIFY app/agents/state.py:
  - 新增 GeneratorState(TypedDict) - 见上方 Data Models
  - 新增 ReviewerState(TypedDict) - 见上方 Data Models
  - 保持 DocumentState, RetrievedContext, ReviewFeedback 不变

任务 15: 重构 RAG Agent 为 BaseAgent 子类
MODIFY app/agents/rag/agent.py:
  - RagAgent(BaseAgent[DocumentState])
  - 实现 name, description, __call__, get_tools, get_prompt
  - __call__ 保留现有 rag_node_with_db 逻辑
  - validate_input 检查 user_requirements 非空
  - 保留 rag_node 和 rag_node_with_db 函数作为兼容接口

任务 16: 创建 Generator Subgraph 子图
CREATE app/agents/generator/agents/__init__.py
CREATE app/agents/generator/agents/planner.py:
  - PlannerAgent(BaseAgent[GeneratorState])
  - 调用 LLM 生成文档大纲
  - 返回 {"outline": ..., "sections": [...]}
CREATE app/agents/generator/agents/writer.py:
  - WriterAgent(BaseAgent[GeneratorState])
  - 遍历 sections 逐段撰写
  - 返回 {"full_draft": ..., "generation_metadata": {...}}
CREATE app/agents/generator/agents/formatter.py:
  - FormatterAgent(BaseAgent[GeneratorState])
  - 格式化最终文档
  - 返回 {"formatted_document": ...}
CREATE app/agents/generator/graph.py:
  - GeneratorSubgraph(BaseSubgraph[GeneratorState])
  - build_graph: START → PLANNER → WRITER → FORMATTER → END
MODIFY app/agents/generator/prompts.py:
  - 新增 PLANNER_SYSTEM_PROMPT, WRITER_SYSTEM_PROMPT, FORMATTER_SYSTEM_PROMPT
  - 参考 INITIAL.md 中的提示词模板（第 427-472 行）

任务 17: 创建 Reviewer Subgraph 子图
CREATE app/agents/reviewer/agents/__init__.py
CREATE app/agents/reviewer/agents/validator.py:
  - ValidatorAgent(BaseAgent[ReviewerState])
  - 验证文档完整性
  - 返回 {"validation_passed": ..., "missing_fields": [...], "structure_issues": [...]}
CREATE app/agents/reviewer/agents/scorer.py:
  - ScorerAgent(BaseAgent[ReviewerState])
  - 多维度评分 (completeness, accuracy, compliance, readability)
  - 返回 {"scores": {...}, "overall_score": float}
CREATE app/agents/reviewer/agents/feedback.py:
  - FeedbackAgent(BaseAgent[ReviewerState])
  - 生成反馈 + interrupt() 等待用户确认
  - 返回 {"feedback": {...}, "suggestions": [...], "decision": str}
CREATE app/agents/reviewer/graph.py:
  - ReviewerSubgraph(BaseSubgraph[ReviewerState])
  - build_graph: START → VALIDATOR → SCORER → FEEDBACK → END
MODIFY app/agents/reviewer/prompts.py:
  - 新增 VALIDATOR_SYSTEM_PROMPT, SCORER_SYSTEM_PROMPT, FEEDBACK_SYSTEM_PROMPT
  - 参考 INITIAL.md 中的提示词模板（第 477-544 行）

任务 18: 更新主图使用子图
MODIFY app/agents/graph.py:
  - 导入 RagAgent, GeneratorSubgraph, ReviewerSubgraph
  - build_workflow() 中:
    - workflow.add_node("rag_retrieval", RagAgent())
    - workflow.add_node("generator", GeneratorSubgraph().compile())
    - workflow.add_node("reviewer", ReviewerSubgraph().compile())
  - 保持 should_revise 条件边
MODIFY app/agents/nodes.py:
  - 简化：generator_node 和 reviewer_node 通过子图自动处理
MODIFY app/agents/__init__.py:
  - 更新导出

任务 19: 新增任务恢复 API
MODIFY app/api/routes/tasks.py:
  - 新增 ResumeTaskRequest (action: continue|modify|cancel, modifications)
  - 新增 POST /{task_id}/resume 端点
  - 实现 resume_task 调用 app.ainvoke(Command(resume=...), config)

任务 20: 完善知识库上传后台处理
MODIFY app/api/routes/knowledge.py:
  - upload_document 中添加 BackgroundTasks 参数
  - background_tasks.add_task(run_ingestion, ...)
  - 新增 run_ingestion 异步函数调用 ingestion.ingest_document

任务 21: 更新测试
CREATE tests/test_agents/test_base.py:
  - TestBaseAgent: 测试抽象类不能直接实例化
  - TestBaseSubgraph: 测试 compile() 行为
MODIFY tests/test_agents/test_workflow.py:
  - 适配新的子图架构
  - TestBuildWorkflow 验证子图节点名
MODIFY tests/test_agents/test_generator.py:
  - 测试 PlannerAgent, WriterAgent, FormatterAgent
  - 测试 GeneratorSubgraph.build_graph() 节点和边
MODIFY tests/test_agents/test_reviewer.py:
  - 测试 ValidatorAgent, ScorerAgent, FeedbackAgent
  - 测试 ReviewerSubgraph.build_graph() 节点和边
  - 测试 interrupt() 行为
MODIFY tests/conftest.py:
  - 新增 sample_generator_state, sample_reviewer_state fixtures
```

### Per-Task Pseudocode (Phase 2)

```python
# 任务 13: BaseAgent (照搬 CLAUDE.md 217-314)
# 文件: app/agents/base/agent.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

StateT = TypeVar("StateT")

class BaseAgent(ABC, Generic[StateT]):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    async def __call__(self, state: StateT, config: dict[str, Any] | None = None) -> dict[str, Any]: ...

    @abstractmethod
    def get_tools(self) -> list[Any]: ...

    @abstractmethod
    def get_prompt(self) -> str: ...

    def validate_input(self, state: StateT) -> bool:
        return True

    def handle_error(self, error: Exception, state: StateT) -> dict[str, Any]:
        return {"error": str(error), "status": "failed"}


# 任务 13: BaseSubgraph (照搬 CLAUDE.md 318-381)
# 文件: app/agents/base/subgraph.py
from langgraph.graph import StateGraph, CompiledGraph
from langgraph.checkpoint.base import BaseCheckpointSaver

class BaseSubgraph(ABC, Generic[StateT]):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def build_graph(self) -> StateGraph: ...

    @abstractmethod
    def get_state_schema(self) -> type[StateT]: ...

    def compile(self, checkpointer: BaseCheckpointSaver | None = None) -> CompiledGraph:
        graph = self.build_graph()
        return graph.compile(checkpointer=checkpointer)


# 任务 16: GeneratorSubgraph
# 文件: app/agents/generator/graph.py
from langgraph.graph import StateGraph, START, END
from app.agents.base.subgraph import BaseSubgraph
from app.agents.state import GeneratorState
from .agents.planner import PlannerAgent
from .agents.writer import WriterAgent
from .agents.formatter import FormatterAgent

class GeneratorSubgraph(BaseSubgraph[GeneratorState]):
    def __init__(self):
        self.planner = PlannerAgent()
        self.writer = WriterAgent()
        self.formatter = FormatterAgent()

    @property
    def name(self) -> str:
        return "generator"

    def get_state_schema(self):
        return GeneratorState

    def build_graph(self) -> StateGraph:
        graph = StateGraph(GeneratorState)
        graph.add_node("planner", self.planner)
        graph.add_node("writer", self.writer)
        graph.add_node("formatter", self.formatter)
        graph.add_edge(START, "planner")
        graph.add_edge("planner", "writer")
        graph.add_edge("writer", "formatter")
        graph.add_edge("formatter", END)
        return graph


# 任务 17: FeedbackAgent with interrupt()
# 文件: app/agents/reviewer/agents/feedback.py
from langgraph.types import interrupt
from app.agents.base.agent import BaseAgent
from app.agents.state import ReviewerState

class FeedbackAgent(BaseAgent[ReviewerState]):
    async def __call__(self, state, config=None) -> dict:
        feedback = await self._generate_feedback(state)
        decision = "approved" if state.get("overall_score", 0) >= 0.85 else "needs_revision"

        if decision == "needs_revision":
            user_response = interrupt({
                "message": "文档需要修订，是否继续？",
                "suggestions": feedback.get("suggestions", []),
                "current_score": state.get("overall_score", 0),
            })
            if user_response.get("action") == "cancel":
                return {**feedback, "decision": "cancelled"}

        return {**feedback, "decision": decision}


# 任务 18: 更新主图
# 文件: app/agents/graph.py
from app.agents.rag.agent import RagAgent
from app.agents.generator.graph import GeneratorSubgraph
from app.agents.reviewer.graph import ReviewerSubgraph

async def build_workflow() -> StateGraph:
    workflow = StateGraph(DocumentState)

    rag_agent = RagAgent()
    generator = GeneratorSubgraph()
    reviewer = ReviewerSubgraph()

    workflow.add_node("rag_retrieval", rag_agent)
    workflow.add_node("generator", generator.compile())
    workflow.add_node("reviewer", reviewer.compile())

    workflow.set_entry_point("rag_retrieval")
    workflow.add_edge("rag_retrieval", "generator")
    workflow.add_edge("generator", "reviewer")
    workflow.add_conditional_edges("reviewer", should_revise, {"revise": "generator", "complete": END})

    return workflow


# 任务 19: 任务恢复 API
# 文件: app/api/routes/tasks.py
from langgraph.types import Command

class ResumeTaskRequest(BaseModel):
    action: str = Field(default="continue")  # continue | modify | cancel
    modifications: Optional[dict] = None

@router.post("/{task_id}/resume")
async def resume_task(task_id: str, request: ResumeTaskRequest, background_tasks: BackgroundTasks):
    config = {"configurable": {"thread_id": task_id}}
    background_tasks.add_task(
        _resume_workflow, task_id, config, request.action, request.modifications
    )
    return {"task_id": task_id, "status": "resuming"}

async def _resume_workflow(task_id, config, action, modifications):
    app = await compile_workflow()
    resume_value = {"action": action}
    if modifications:
        resume_value["modifications"] = modifications
    await app.ainvoke(Command(resume=resume_value), config)
```

### Integration Points
```yaml
STATE_MAPPING:
  - 主图 DocumentState → 子图 GeneratorState:
      user_requirements → requirements
      retrieved_context → retrieved_context
      template_id → template_id
      revision_count → revision_count
      review_feedback → review_feedback
  - 主图 DocumentState → 子图 ReviewerState:
      generated_content → document
      user_requirements → requirements
      template_id → template_id
      retrieved_context → retrieved_context
  - 子图 GeneratorState → 主图:
      formatted_document → generated_content
      generation_metadata → generation_metadata
  - 子图 ReviewerState → 主图:
      overall_score → review_score
      feedback → review_feedback
      suggestions → revision_suggestions

DATABASE:
  - 带有 PGVector 扩展的 PostgreSQL
  - 连接: DATABASE_URL 环境变量
  - 表: users, tasks, templates, knowledge_documents, knowledge_chunks, generated_documents
  - 索引: CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)

LANGGRAPH:
  - Checkpointer: PostgresSaver(DATABASE_URL)
  - 线程 ID: 使用 task_id 作为检查点的 thread_id
  - 子图编译时不传 checkpointer（从父图继承）
  - interrupt() 会暂停整个工作流（包括父图）
  - Command(resume=value) 恢复被中断的工作流

EXISTING_CODE_PRESERVATION:
  - app/config.py: 不变
  - app/utils/db.py: 不变
  - app/utils/llm.py: 不变
  - app/models/__init__.py: 不变
  - app/ingestion/*: 不变
  - app/webui/app.py: 不变
  - app/agents/coordinator/routing.py: 不变
  - app/api/routes/documents.py: 不变
  - app/api/routes/templates.py: 不变
  - app/services/task_service.py: 不变

ENVIRONMENT:
  - LLM_API_KEY: OpenAI/Anthropic API 密钥
  - LLM_MODEL: gpt-4o-mini (默认)
  - EMBEDDING_MODEL: text-embedding-3-small
  - DATABASE_URL: postgresql://user:pass@host:port/db

WEBUI:
  - 在 /webui 路径挂载 Gradio
  - 文档生成的后台任务
  - WebSocket 或轮询用于实时更新
```

## Validation Loop

### Level 1: Syntax & Style
```bash
cd docugen
uv run ruff check app/ --fix
uv run mypy app/ --ignore-missing-imports

# Expected: No errors. If errors, read and fix.
```

### Level 2: Unit Tests
```python
# tests/test_agents/test_base.py
import pytest
from app.agents.base.agent import BaseAgent

class TestBaseAgent:
    def test_cannot_instantiate_abstract(self):
        """BaseAgent 不能直接实例化。"""
        with pytest.raises(TypeError):
            BaseAgent()

    def test_concrete_agent_must_implement_all(self):
        """具体 Agent 必须实现所有抽象方法。"""
        class IncompleteAgent(BaseAgent):
            pass
        with pytest.raises(TypeError):
            IncompleteAgent()


# tests/test_agents/test_generator.py
class TestGeneratorSubgraph:
    def test_subgraph_builds_with_correct_nodes(self):
        from app.agents.generator.graph import GeneratorSubgraph
        sg = GeneratorSubgraph()
        graph = sg.build_graph()
        assert "planner" in graph.nodes
        assert "writer" in graph.nodes
        assert "formatter" in graph.nodes

    def test_subgraph_compiles(self):
        from app.agents.generator.graph import GeneratorSubgraph
        sg = GeneratorSubgraph()
        compiled = sg.compile()
        assert compiled is not None


# tests/test_agents/test_reviewer.py
class TestReviewerSubgraph:
    def test_subgraph_builds_with_correct_nodes(self):
        from app.agents.reviewer.graph import ReviewerSubgraph
        sg = ReviewerSubgraph()
        graph = sg.build_graph()
        assert "validator" in graph.nodes
        assert "scorer" in graph.nodes
        assert "feedback" in graph.nodes


# tests/test_agents/test_workflow.py (更新)
class TestBuildWorkflow:
    @pytest.mark.asyncio
    async def test_workflow_uses_subgraphs(self):
        workflow = await build_workflow()
        assert "rag_retrieval" in workflow.nodes
        assert "generator" in workflow.nodes
        assert "reviewer" in workflow.nodes
```

```bash
cd docugen
uv run pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
# If failing: Read error, fix code, re-run
```

### Level 3: Integration Test
```bash
# 启动服务
cd docugen && uv run python -m app.main

# 测试文档生成
curl -X POST http://localhost:7860/api/documents/generate \
  -H "Content-Type: application/json" \
  -d '{"requirements": "创建一个项目提案", "max_revisions": 2}'

# 轮询任务状态
curl http://localhost:7860/api/tasks/{task_id}

# 测试任务恢复
curl -X POST http://localhost:7860/api/tasks/{task_id}/resume \
  -H "Content-Type: application/json" \
  -d '{"action": "continue"}'

# 访问 WebUI
open http://localhost:7860/webui
```

## Final Validation Checklist
**Phase 1 (已完成):**
- [x] 项目配置和依赖安装
- [x] 数据库模型和初始化
- [x] LangGraph 扁平工作流编译
- [x] RAG 检索返回相关结果
- [x] 生成器创建文档
- [x] 审查者提供反馈
- [x] 修订循环遵守 max_revisions
- [x] API 端点返回预期响应
- [x] WebUI 可访问

**Phase 2 (待验证):**
- [ ] BaseAgent 和 BaseSubgraph 抽象类定义完整
- [ ] 所有 Agent 继承 BaseAgent 并实现所有抽象方法
- [ ] GeneratorSubgraph 包含 3 个内部 Agent 节点 (planner, writer, formatter)
- [ ] ReviewerSubgraph 包含 3 个内部 Agent 节点 (validator, scorer, feedback)
- [ ] 主图使用子图作为节点
- [ ] FeedbackAgent 使用 interrupt() 实现 Human-in-the-Loop
- [ ] /api/tasks/{task_id}/resume 端点可用
- [ ] 知识库上传触发后台处理
- [ ] 所有测试通过: `cd docugen && uv run pytest tests/ -v`
- [ ] 无 lint 错误: `cd docugen && uv run ruff check app/`
- [ ] 错误情况被优雅处理
- [ ] 每个新函数都有 logging（打印输入参数和输出结果）

---

## Anti-Patterns to Avoid
- ❌ 不要从节点返回完整状态 - 只返回部分更新
- ❌ 不要在子图中使用独立的 checkpointer - 从父图继承
- ❌ 不要在条件边中返回布尔值 - 使用字符串键
- ❌ 不要硬编码 API 密钥 - 使用 app/config.py 和环境变量
- ❌ 不要跳过 validate_input - 每个 Agent 应验证输入
- ❌ 不要在并发节点中修改共享状态
- ❌ 不要创建超过 500 行的文件 - 按模块拆分
- ❌ 不要删除现有的工作代码 - 重构时保留行为
- ❌ 不要在异步上下文中使用同步函数
- ❌ 不要在编译图之前忘记初始化 checkpointer
- ❌ 不要将嵌入存储为 Python 列表 - 使用 PGVector 格式
- ❌ 不要跳过状态持久化 - 始终使用 checkpointer
- ❌ 不要将 Gradio 作为单独进程运行 - 挂载在 FastAPI 中

## Confidence Score: 8/10

### High Confidence Factors:
- CLAUDE.md 提供了完整清晰的接口定义（BaseAgent 217-314, BaseSubgraph 318-381）
- INITIAL.md 提供了详细的实现示例代码（7 个完整示例）
- 现有代码库结构良好，所有基础设施已就位
- LangGraph 的 StateGraph + 子图模式文档充分
- 现有测试模式可以复用
- Phase 1 已完成验证，重构路径清晰

### Minor Uncertainties:
- 子图状态映射（父图 ↔ 子图）的具体实现方式可能需要运行时调试
- `interrupt()` + `Command(resume=...)` 的精确 API 可能因 LangGraph 版本而异
- 子图内部 Agent 共享 LLM client 的方式需要确认
- PostgresSaver 确切 API 可能与文档不同（运行时验证）
- Gradio + FastAPI 集成细节可能需要调整

### Risk Mitigation:
- 先实现 BaseAgent + BaseSubgraph 并测试（任务 13）
- 再逐步迁移各 Agent，每次迁移后运行测试
- 子图状态映射如有问题，可降级为共享同一 State
- interrupt() 如有兼容性问题，可先用简单的 score 阈值判断
- 从简单工作流开始，逐步增加复杂性
- 在测试中模拟外部服务以实现可靠验证
