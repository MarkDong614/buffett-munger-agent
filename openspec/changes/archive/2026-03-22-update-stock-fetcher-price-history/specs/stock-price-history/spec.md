## MODIFIED Requirements

### Requirement: 历史价格数据包含复权价格
系统 SHALL 支持调用方通过 `adjust` 参数指定复权方式：`"hfq"`（后复权）、`"qfq"`（前复权）或 `""`（不复权），默认为 `""`（不复权）。

#### Scenario: 默认返回不复权价格
- **WHEN** 调用 `get_price_history` 时未传入 `adjust` 参数
- **THEN** 收盘价字段 SHALL 为原始不复权价格

#### Scenario: 指定前复权
- **WHEN** 调用 `get_price_history` 时传入 `adjust="qfq"`
- **THEN** 收盘价字段 SHALL 为前复权（qfq）价格

#### Scenario: 指定不复权
- **WHEN** 调用 `get_price_history` 时传入 `adjust=""`
- **THEN** 收盘价字段 SHALL 为原始不复权价格

### Requirement: 通过 MCP Tool 获取历史价格数据
系统 SHALL 通过名为 `get_price_history` 的 MCP Tool 暴露历史价格数据获取能力，接受 `ts_code`、`start_date`、`end_date`、`freq`（可选，默认 `"D"`）、`adjust`（可选，默认 `""`）参数，返回 JSON 序列化的 `PriceBar` 列表。

#### Scenario: 成功调用 get_price_history Tool（默认不复权）
- **WHEN** MCP 客户端调用 `get_price_history` 并传入有效的 `ts_code`、`start_date`、`end_date`，未指定 `adjust`
- **THEN** Server SHALL 返回按日期升序排列的不复权 OHLCV 数据 JSON 列表

#### Scenario: 调用 get_price_history Tool 并指定复权方式
- **WHEN** MCP 客户端调用 `get_price_history` 并传入 `adjust="qfq"` 或 `adjust=""`
- **THEN** Server SHALL 将 `adjust` 参数透传至底层 provider，返回对应复权方式的 OHLCV 数据

#### Scenario: 时间范围内无数据时返回空列表
- **WHEN** MCP 客户端调用 `get_price_history` 时指定的时间范围无对应数据
- **THEN** Server SHALL 返回空 JSON 数组，不返回错误

#### Scenario: 无效代码时返回 MCP 错误
- **WHEN** MCP 客户端调用 `get_price_history` 并传入不存在的股票代码
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应

## ADDED Requirements

### Requirement: get_price_history 接口使用类型约束参数
系统 SHALL 在数据层（`DataProvider` Protocol、`StockFetcher`、`TushareProvider`）的 `get_price_history` 方法中，使用 `Freq`（`Literal["D", "W", "M"]`）和 `Adjust`（`Literal["hfq", "qfq", ""]`）类型别名约束 `freq` 和 `adjust` 参数。

#### Scenario: 合法参数通过类型检查
- **WHEN** 调用 `get_price_history` 时传入 `freq="D"` 和 `adjust="hfq"`
- **THEN** 静态类型检查（mypy/pyright）SHALL 通过，无类型错误

#### Scenario: 非法参数被类型检查捕获
- **WHEN** 调用 `get_price_history` 时传入 `freq="1d"`（非 Literal 合法值）
- **THEN** 静态类型检查 SHALL 报告类型错误
