## ADDED Requirements

### Requirement: 通过 MCP Tool 获取基本面财务数据
系统 SHALL 通过名为 `get_fundamentals` 的 MCP Tool 暴露基本面数据获取能力，接受 `ts_code` 参数，返回 JSON 序列化的 `StockFundamentals` 数据。

#### Scenario: 成功调用 get_fundamentals Tool
- **WHEN** MCP 客户端调用 `get_fundamentals` 并传入有效的 `ts_code`
- **THEN** Server SHALL 返回包含收入、净利润、总资产、自由现金流等字段的 JSON 文本内容，缺失字段以 null 表示

#### Scenario: 无效代码时返回 MCP 错误
- **WHEN** MCP 客户端调用 `get_fundamentals` 并传入不存在的股票代码
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应
