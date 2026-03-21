# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 语言规范

所有产出物（代码注释、文档、提交信息、回复内容等）均使用中文。

## 常用命令

```bash
# 安装依赖
uv sync

# 运行 agent（普通模式）
uv run buffett-munger-agent

# 以 MCP Server 模式启动（供 Claude Code CLI 调用）
TUSHARE_TOKEN=<your_token> uv run buffett-munger-agent --mcp

# 添加依赖
uv add <package>

# 运行测试
uv run pytest

# 运行单个测试
uv run pytest tests/path/to/test_file.py::test_name

# 跳过需要外部服务的集成测试
uv run pytest -m "not integration"

# 代码检查 / 格式化
uv run ruff check .
uv run ruff format .
```

## 架构说明

本项目采用 **src layout** 结构，所有源码位于 `src/buffett_munger_agent/` 下。

项目目标是构建一个由大模型驱动的 agent，按照巴菲特/芒格价值投资理念对 A 股进行分析并生成报告。当前处于早期开发阶段，已实现数据获取层和 MCP Server 层。

### 模块结构

```
src/buffett_munger_agent/
├── __main__.py          # 入口，main() → 普通模式 或 MCP Server 模式（--mcp）
├── mcp_server.py        # MCP Server，将数据能力暴露为 MCP Tools
└── data/
    ├── base.py          # DataProvider Protocol（数据提供者接口定义）
    ├── fetcher.py       # StockFetcher（对外统一入口，当前使用 TushareProvider）
    ├── models.py        # Pydantic 数据模型：StockFundamentals、PriceBar、CompanyInfo
    └── providers/
        └── tushare.py   # TushareProvider（Tushare A 股数据实现）
```

### 关键约定

- **数据层**：`DataProvider` 是 Protocol 接口，新数据源实现该接口后注入 `StockFetcher` 即可。
- **MCP Tools**：`mcp_server.py` 暴露三个工具 —— `get_company_info`、`get_fundamentals`、`get_price_history`。
- **环境变量**：MCP Server 启动需设置 `TUSHARE_TOKEN`，通过环境变量注入，不硬编码。
- **股票代码格式**：统一使用 Tushare 格式，如 `"600519.SH"`（上交所）/ `"000001.SZ"`（深交所）。
- **错误处理**：数据获取失败统一抛出 `DataFetchError`，MCP Tool 层捕获后转为 `ValueError`。
- 包通过 `uv sync` 以可编辑模式安装，导入路径使用 `buffett_munger_agent.*`
- 虚拟环境由 uv 管理，路径为 `.venv/`
- Python 版本要求 >= 3.14
