## ADDED Requirements

### Requirement: 通过 MCP Tool 获取历史价格数据
系统 SHALL 通过名为 `get_price_history` 的 MCP Tool 暴露历史价格数据获取能力，接受 `ts_code`、`start_date`、`end_date`、`freq`（可选，默认 "D"）参数，返回 JSON 序列化的 `PriceBar` 列表。

#### Scenario: 成功调用 get_price_history Tool
- **WHEN** MCP 客户端调用 `get_price_history` 并传入有效的 `ts_code`、`start_date`、`end_date`
- **THEN** Server SHALL 返回按日期升序排列的 OHLCV 数据 JSON 列表，收盘价为后复权价格

#### Scenario: 时间范围内无数据时返回空列表
- **WHEN** MCP 客户端调用 `get_price_history` 时指定的时间范围无对应数据
- **THEN** Server SHALL 返回空 JSON 数组，不返回错误

#### Scenario: 无效代码时返回 MCP 错误
- **WHEN** MCP 客户端调用 `get_price_history` 并传入不存在的股票代码
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应
