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
系统 SHALL 通过 MCP 协议暴露以下五个 Tools：`get_company_info`、`get_fundamentals`、`get_price_history`、`get_stock_daily_indicators`、`get_market_daily_indicators`，每个 Tool 均包含参数 schema 和描述。

#### Scenario: 客户端列举可用 Tools
- **WHEN** MCP 客户端发送 `tools/list` 请求
- **THEN** Server SHALL 返回包含 `get_company_info`、`get_fundamentals`、`get_price_history`、`get_stock_daily_indicators`、`get_market_daily_indicators` 的 Tool 列表，每个 Tool 包含名称、描述和输入 schema

### Requirement: get_stock_daily_indicators Tool 支持按股票代码查询指标序列
`get_stock_daily_indicators` Tool SHALL 接受 `ts_code`（必填）、`start_date`（可选，YYYYMMDD）、`end_date`（可选，YYYYMMDD）参数，返回 JSON 序列化的该股票每日指标列表。

#### Scenario: 成功调用 get_stock_daily_indicators
- **WHEN** 客户端以有效股票代码调用 `get_stock_daily_indicators`
- **THEN** Server SHALL 返回包含该股票每日指标数据的 JSON 字符串

#### Scenario: get_stock_daily_indicators 调用失败时返回错误响应
- **WHEN** 客户端以无效参数调用 `get_stock_daily_indicators`
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应，进程保持运行

### Requirement: get_market_daily_indicators Tool 支持按交易日期查询全市场指标快照
`get_market_daily_indicators` Tool SHALL 接受以下参数：
- `trade_date`（必填，YYYYMMDD）：交易日期
- `sort_by`（可选，默认 None）：排序字段，合法值为 `pe`、`pe_ttm`、`pb`、`ps_ttm`、`turnover_rate`、`total_mv`、`circ_mv`；传入不合法字段名时 SHALL 抛出错误
- `ascending`（可选，默认 True）：True 为升序，False 为降序
- `limit`（可选，默认 50）：返回条数上限；传入 None 时返回全部数据；传入负值时 SHALL 抛出错误

返回 JSON 序列化的股票指标列表，结果已按指定字段排序并截取到 `limit` 条。字段值为 None 的记录 SHALL 排在列表末尾，不论升降序。

#### Scenario: 成功调用 get_market_daily_indicators（不传可选参数）
- **WHEN** 客户端仅传 `trade_date` 调用 `get_market_daily_indicators`
- **THEN** Server SHALL 返回最多 50 条指标数据的 JSON 字符串（使用默认 limit=50，不排序）

#### Scenario: 按 pe 升序取前 20 条
- **WHEN** 客户端传 `trade_date`、`sort_by="pe"`、`ascending=True`、`limit=20` 调用
- **THEN** Server SHALL 返回当日 pe 最低的 20 条记录，pe 为 None 的记录排在末尾

#### Scenario: 按 turnover_rate 降序取前 10 条
- **WHEN** 客户端传 `trade_date`、`sort_by="turnover_rate"`、`ascending=False`、`limit=10` 调用
- **THEN** Server SHALL 返回当日换手率最高的 10 条记录，turnover_rate 为 None 的记录排在末尾

#### Scenario: 传入无效 sort_by 字段时返回错误响应
- **WHEN** 客户端传入 `sort_by="invalid_field"` 调用
- **THEN** Server SHALL 返回包含合法字段列表的 MCP 错误响应，进程保持运行

#### Scenario: limit=None 时返回全量数据
- **WHEN** 客户端传 `limit=None` 调用
- **THEN** Server SHALL 返回该交易日全市场所有股票的指标数据

#### Scenario: 传入负数 limit 时返回错误响应
- **WHEN** 客户端传 `limit=-1` 调用 `get_market_daily_indicators`
- **THEN** Server SHALL 返回包含 limit 非法说明的 MCP 错误响应，进程保持运行

#### Scenario: get_market_daily_indicators 调用失败时返回错误响应
- **WHEN** 客户端调用 `get_market_daily_indicators` 时发生异常
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应，进程保持运行

### Requirement: Tool 调用错误时返回 MCP 错误响应
系统 SHALL 在 Tool 调用过程中发生 `DataFetchError` 或其他异常时，返回包含错误信息的 MCP 错误响应，而非使进程崩溃。

#### Scenario: 无效股票代码时返回错误响应
- **WHEN** 客户端以无效股票代码调用任意 Tool
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应，进程保持运行
