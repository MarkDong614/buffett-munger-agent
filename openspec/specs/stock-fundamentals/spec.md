### Requirement: 获取股票基本面财务数据
系统 SHALL 根据 A 股股票代码获取基本面财务数据，包括利润表、资产负债表、现金流量表关键指标及估值指标（PE、PB、ROE、FCF 等）。

#### Scenario: 成功获取 A 股基本面数据
- **WHEN** 调用 fetcher 并传入有效的 A 股代码（如 "600519.SH"）
- **THEN** 返回包含收入、净利润、总资产、自由现金流等字段的 `StockFundamentals` 对象

#### Scenario: 股票代码无效时抛出异常
- **WHEN** 调用 fetcher 并传入不存在的股票代码
- **THEN** 系统 SHALL 抛出明确的 `DataFetchError` 异常，包含可读的错误信息

### Requirement: 数据模型包含可选字段
系统 SHALL 使用 Pydantic 模型定义基本面数据，所有非核心字段 SHALL 标记为 Optional，以处理数据源不完整的情况。

#### Scenario: 部分数据缺失时正常返回
- **WHEN** 数据源对某些指标（如 FCF）无数据
- **THEN** 对应字段返回 None，其余字段正常填充，不抛出异常

### Requirement: 通过 MCP Tool 获取基本面财务数据
系统 SHALL 通过名为 `get_fundamentals` 的 MCP Tool 暴露基本面数据获取能力，接受 `ts_code` 参数，返回 JSON 序列化的 `StockFundamentals` 数据。

#### Scenario: 成功调用 get_fundamentals Tool
- **WHEN** MCP 客户端调用 `get_fundamentals` 并传入有效的 `ts_code`
- **THEN** Server SHALL 返回包含收入、净利润、总资产、自由现金流等字段的 JSON 文本内容，缺失字段以 null 表示

#### Scenario: 无效代码时返回 MCP 错误
- **WHEN** MCP 客户端调用 `get_fundamentals` 并传入不存在的股票代码
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应
