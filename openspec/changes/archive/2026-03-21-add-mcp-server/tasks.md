## 1. 添加依赖

- [x] 1.1 执行 `uv add mcp` 将 MCP Python SDK 添加到 `pyproject.toml`

## 2. 实现 MCP Server 模块

- [x] 2.1 创建 `src/buffett_munger_agent/mcp_server.py`，初始化 MCP Server 实例
- [x] 2.2 实现 `get_company_info` Tool：接受 `ts_code` 参数，调用 `StockFetcher.get_company_info()`，返回 JSON 文本
- [x] 2.3 实现 `get_fundamentals` Tool：接受 `ts_code` 参数，调用 `StockFetcher.get_fundamentals()`，返回 JSON 文本
- [x] 2.4 实现 `get_price_history` Tool：接受 `ts_code`、`start_date`、`end_date`、`freq`（默认 "D"）参数，调用 `StockFetcher.get_price_history()`，返回 JSON 文本
- [x] 2.5 在每个 Tool 中捕获 `DataFetchError` 及其他异常，返回包含错误信息的 MCP 错误响应
- [x] 2.6 实现 `run_mcp_server()` 函数：从 `TUSHARE_TOKEN` 环境变量读取 token，token 缺失时输出错误并退出，正常时以 stdio transport 启动 Server

## 3. 修改入口

- [x] 3.1 修改 `src/buffett_munger_agent/__main__.py`，解析 `--mcp` 命令行参数
- [x] 3.2 有 `--mcp` 参数时调用 `run_mcp_server()`，无参数时保持原有逻辑

## 4. 验证与文档

- [x] 4.1 在本地执行 `TUSHARE_TOKEN=<token> uv run buffett-munger-agent --mcp`，确认进程正常启动不崩溃
- [x] 4.2 在 Claude Code 中通过 `claude mcp add` 或编辑 `~/.claude/mcp_settings.json` 注册 Server，验证 Tools 可被正常调用
- [x] 4.3 在 `README.md`（或项目文档）中添加 Claude Code 注册配置示例
