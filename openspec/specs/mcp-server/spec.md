### Requirement: MCP Server 以 stdio 模式启动
系统 SHALL 在传入 `--mcp` 命令行参数时，以 stdio transport 启动 MCP Server，并保持监听直至进程退出。

#### Scenario: 通过 --mcp 启动 MCP Server
- **WHEN** 执行 `uv run buffett-munger-agent --mcp`
- **THEN** 进程 SHALL 启动 MCP Server 并通过 stdin/stdout 处理 MCP 协议消息

#### Scenario: 不带 --mcp 参数时保持原有行为
- **WHEN** 执行 `uv run buffett-munger-agent`（不带 --mcp）
- **THEN** 进程 SHALL 执行原有逻辑，不启动 MCP Server

### Requirement: MCP Server 从环境变量读取 Tushare Token
系统 SHALL 在 MCP Server 启动时从环境变量 `TUSHARE_TOKEN` 读取 API token；若该变量未设置，SHALL 输出错误信息并退出。

#### Scenario: Token 正确配置时正常启动
- **WHEN** 环境变量 `TUSHARE_TOKEN` 已设置且值有效
- **THEN** MCP Server SHALL 成功初始化 `StockFetcher` 并开始接受工具调用

#### Scenario: Token 未配置时启动失败
- **WHEN** 环境变量 `TUSHARE_TOKEN` 未设置
- **THEN** 进程 SHALL 输出明确错误信息并以非零状态码退出

### Requirement: MCP Server 注册三个 Tools
系统 SHALL 通过 MCP 协议暴露以下三个 Tools：`get_company_info`、`get_fundamentals`、`get_price_history`，每个 Tool 均包含参数 schema 和描述。

#### Scenario: 客户端列举可用 Tools
- **WHEN** MCP 客户端发送 `tools/list` 请求
- **THEN** Server SHALL 返回包含 `get_company_info`、`get_fundamentals`、`get_price_history` 的 Tool 列表，每个 Tool 包含名称、描述和输入 schema

### Requirement: Tool 调用错误时返回 MCP 错误响应
系统 SHALL 在 Tool 调用过程中发生 `DataFetchError` 或其他异常时，返回包含错误信息的 MCP 错误响应，而非使进程崩溃。

#### Scenario: 无效股票代码时返回错误响应
- **WHEN** 客户端以无效股票代码调用任意 Tool
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应，进程保持运行
