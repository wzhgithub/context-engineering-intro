# DocuGen 多智能体文档生成系统

使用 LangGraph 进行智能体编排的生产级多智能体文档生成系统。该系统使用户能够通过自然语言需求生成专业文档，支持自定义模板、通过 RAG 进行知识库集成，以及通过自动化审查循环进行迭代优化。

## 功能特性

- **多智能体协作**: 专门的智能体负责生成、审查和迭代优化
- **RAG 增强生成**: 使用知识检索进行上下文感知的文档创建
- **可自定义模板**: 用户定义的文档规范持久化到数据库
- **迭代优化**: 多轮生成和审查循环
- **任务持久化**: 每个生成任务的完整状态管理

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 15+ with PGVector extension
- uv 包管理器 (推荐) 或 pip

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/docugen.git
cd docugen

# 使用 uv 安装依赖
uv sync

# 或使用 pip
pip install -e .

# 复制环境变量模板
cp .env.example .env
# 编辑 .env 文件，填入您的配置
```

### 配置

在 `.env` 文件中配置以下环境变量:

```bash
# LLM 配置
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-4
LLM_BASE_URL=https://api.openai.com/v1

# 嵌入模型配置
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/docugen

# 任务配置
MAX_REVISIONS=3
DEFAULT_SEARCH_LIMIT=10

# WebUI
WEBUI_HOST=0.0.0.0
WEBUI_PORT=7860
```

### 数据库设置

```bash
# 创建 PostgreSQL 数据库
createdb docugen

# 启用 PGVector 扩展
psql -d docugen -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 运行迁移 (如果有)
alembic upgrade head
```

### 运行应用

```bash
# 使用 uv
uv run python -m app.main

# 或使用 Python
python -m app.main
```

应用将在以下地址启动:
- API: http://localhost:8000
- WebUI: http://localhost:8000/webui

## 项目结构

```
docugen/
├── app/
│   ├── main.py                 # FastAPI + Gradio 入口
│   ├── config.py               # 配置管理
│   │
│   ├── agents/                 # LangGraph 智能体
│   │   ├── graph.py            # StateGraph 工作流定义
│   │   ├── state.py            # DocumentState TypedDict
│   │   ├── rag/                # RAG Agent
│   │   ├── generator/          # Generator Agent
│   │   ├── reviewer/           # Reviewer Agent
│   │   └── coordinator/        # 路由逻辑
│   │
│   ├── models/                 # SQLModel 数据库模型
│   ├── services/               # 业务逻辑层
│   ├── api/                    # FastAPI 路由
│   ├── webui/                  # Gradio WebUI
│   ├── ingestion/              # 文档导入处理
│   └── utils/                  # 工具函数
│
├── tests/                      # 测试套件
└── migrations/                 # 数据库迁移
```

## 工作流架构

```
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
```

## API 端点

### 文档生成

```bash
# 创建文档生成任务
POST /api/documents/generate
{
  "requirements": "创建项目提案",
  "template_id": null,
  "knowledge_ids": [],
  "max_revisions": 3
}

# 获取任务状态
GET /api/tasks/{task_id}

# 列出所有任务
GET /api/tasks
```

### 模板管理

```bash
# 创建模板
POST /api/templates
{
  "name": "提案模板",
  "description": "项目提案模板",
  "sections": [{"name": "摘要", "required": true}],
  "formatting_rules": {"style": "formal"},
  "required_fields": ["title", "content"]
}

# 列出模板
GET /api/templates
```

### 知识库

```bash
# 上传知识文档
POST /api/knowledge/upload

# 列出知识文档
GET /api/knowledge
```

## 测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行特定测试
uv run pytest tests/test_agents/test_workflow.py -v

# 运行测试并生成覆盖率报告
uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

## 开发指南

### 代码风格

- 遵循 PEP8
- 使用 type hints
- 使用 black 格式化
- 使用 Google 风格的 docstrings

### 添加新智能体

1. 在 `app/agents/` 下创建新目录
2. 实现 `agent.py` (节点函数)
3. 添加 `tools.py` (工具函数)
4. 添加 `prompts.py` (提示词)
5. 在 `graph.py` 中添加节点和边
6. 编写测试

## 技术栈

- **LangGraph**: 智能体编排
- **FastAPI**: Web 框架
- **Gradio**: WebUI
- **SQLModel**: ORM
- **PostgreSQL + PGVector**: 数据库和向量存储
- **OpenAI**: LLM 和嵌入

## 许可证

MIT License
