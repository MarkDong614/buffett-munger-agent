### Requirement: 获取股票历史价格数据
系统 SHALL 根据股票代码、时间范围和时间粒度获取 OHLCV（开盘价、最高价、最低价、收盘价、成交量）历史数据。

#### Scenario: 成功获取指定时间范围的日线数据
- **WHEN** 调用 fetcher 并传入有效股票代码、开始日期、结束日期及 "1d" 粒度
- **THEN** 返回按日期升序排列的 `PriceHistory` 列表，每条记录包含 date、open、high、low、close、volume

#### Scenario: 支持多种时间粒度
- **WHEN** 调用 fetcher 时指定粒度为 "1w" 或 "1mo"
- **THEN** 返回对应周线或月线数据

#### Scenario: 时间范围内无数据时返回空列表
- **WHEN** 调用 fetcher 时指定的时间范围早于股票上市日期
- **THEN** 系统 SHALL 返回空列表，不抛出异常

### Requirement: 历史价格数据包含复权价格
系统 SHALL 默认返回后复权（adjusted close）价格，以保证历史价格的可比性。

#### Scenario: 返回复权收盘价
- **WHEN** 获取含有分红或拆股历史的股票数据
- **THEN** 收盘价字段 SHALL 为后复权价格

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
