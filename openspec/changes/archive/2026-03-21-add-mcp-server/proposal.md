## Why

当前项目的股票数据获取能力（公司信息、基本面、历史价格）仅能通过命令行或 Python API 调用，无法被 Claude Code CLI 及其他 MCP 客户端直接使用。将项目暴露为 MCP Server，可让 Claude Code 在对话中实时调用这些能力，提升分析工作流的自动化程度。

## What Changes

- 新增 `mcp_server` 模块，基于 MCP Python SDK 实现 MCP Server
- 将现有的股票数据获取能力（公司信息、基本面数据、历史价格）封装为 MCP Tools
- 新增 `uv run buffett-munger-agent --mcp` 启动模式（stdio transport），供 Claude Code CLI 注册调用
- 在 `pyproject.toml` 中添加 MCP 相关依赖

## Capabilities

### New Capabilities

- `mcp-server`: MCP Server 入口，通过 stdio transport 提供工具调用接口，支持 Claude Code CLI 注册

### Modified Capabilities

- `company-info`: 在 MCP Server 中以 Tool 形式暴露（需求层面新增 MCP 调用路径）
- `stock-fundamentals`: 在 MCP Server 中以 Tool 形式暴露（需求层面新增 MCP 调用路径）
- `stock-price-history`: 在 MCP Server 中以 Tool 形式暴露（需求层面新增 MCP 调用路径）

## Impact

- 新增依赖：`mcp`（MCP Python SDK）
- 新增模块：`src/buffett_munger_agent/mcp_server.py`
- 修改入口：`src/buffett_munger_agent/__main__.py` 增加 `--mcp` 参数分支
- 外部依赖：Tushare API token 需通过环境变量配置（现有机制不变）
- Claude Code 用户需在 `~/.claude/mcp_settings.json` 中注册本 server
