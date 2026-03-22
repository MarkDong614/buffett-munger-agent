## MODIFIED Requirements

### Requirement: MCP Server 注册三个 Tools
系统 SHALL 通过 MCP 协议暴露以下五个 Tools：`get_company_info`、`get_fundamentals`、`get_price_history`、`get_stock_daily_indicators`、`get_market_daily_indicators`，每个 Tool 均包含参数 schema 和描述。

#### Scenario: 客户端列举可用 Tools
- **WHEN** MCP 客户端发送 `tools/list` 请求
- **THEN** Server SHALL 返回包含 `get_company_info`、`get_fundamentals`、`get_price_history`、`get_stock_daily_indicators`、`get_market_daily_indicators` 的 Tool 列表，每个 Tool 包含名称、描述和输入 schema

## ADDED Requirements

### Requirement: get_stock_daily_indicators Tool 支持按股票代码查询指标序列
`get_stock_daily_indicators` Tool SHALL 接受 `ts_code`（必填）、`start_date`（可选，YYYYMMDD）、`end_date`（可选，YYYYMMDD）参数，返回 JSON 序列化的该股票每日指标列表。

#### Scenario: 成功调用 get_stock_daily_indicators
- **WHEN** 客户端以有效股票代码调用 `get_stock_daily_indicators`
- **THEN** Server SHALL 返回包含该股票每日指标数据的 JSON 字符串

#### Scenario: get_stock_daily_indicators 调用失败时返回错误响应
- **WHEN** 客户端以无效参数调用 `get_stock_daily_indicators`
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应，进程保持运行

### Requirement: get_market_daily_indicators Tool 支持按交易日期查询全市场指标快照
`get_market_daily_indicators` Tool SHALL 接受 `trade_date`（必填，YYYYMMDD）参数，返回 JSON 序列化的全市场当日所有股票指标列表。

#### Scenario: 成功调用 get_market_daily_indicators
- **WHEN** 客户端以有效交易日期调用 `get_market_daily_indicators`
- **THEN** Server SHALL 返回包含全市场当日指标数据的 JSON 字符串

#### Scenario: get_market_daily_indicators 调用失败时返回错误响应
- **WHEN** 客户端调用 `get_market_daily_indicators` 时发生异常
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应，进程保持运行
