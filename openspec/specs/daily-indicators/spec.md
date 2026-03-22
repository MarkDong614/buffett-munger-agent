## Purpose

本模块提供 A 股每日行情指标（估值、市值、换手率等）的数据查询能力，支持按股票代码查询历史序列，也支持按交易日期查询全市场快照。

## Requirements

### Requirement: DailyIndicators 数据模型包含核心估值字段
`DailyIndicators` 模型 SHALL 包含以下字段：`ts_code`（股票代码）、`trade_date`（交易日期，YYYYMMDD）、`pe`（市盈率，可选）、`pe_ttm`（滚动市盈率，可选）、`pb`（市净率，可选）、`ps_ttm`（滚动市销率，可选）、`turnover_rate`（换手率%，可选）、`total_mv`（总市值，万元，可选）、`circ_mv`（流通市值，万元，可选）。所有估值字段 SHALL 为 `Optional[float]` 以处理新股等无数据情形。

#### Scenario: 模型字段完整返回
- **WHEN** Tushare 返回完整数据行
- **THEN** `DailyIndicators` 对象 SHALL 包含所有字段的非 None 值

#### Scenario: 估值字段缺失时模型仍可构造
- **WHEN** Tushare 返回的某行 `pe` 字段为 None（如新股上市初期）
- **THEN** 系统 SHALL 成功构造 `DailyIndicators` 对象，`pe` 字段值为 `None`

### Requirement: 按股票代码查询每日指标序列
系统 SHALL 支持输入股票代码和可选日期范围，返回该股票按时间排列的 `DailyIndicators` 列表。

#### Scenario: 查询指定日期范围的每日指标
- **WHEN** 调用 `get_stock_daily_indicators(ts_code="600519.SH", start_date="20240101", end_date="20240131")`
- **THEN** 系统 SHALL 返回该区间内每个交易日的 `DailyIndicators` 列表，按日期升序排列

#### Scenario: 不传日期范围时返回最近交易日数据
- **WHEN** 调用 `get_stock_daily_indicators(ts_code="600519.SH")` 不传 `start_date` 和 `end_date`
- **THEN** 系统 SHALL 返回最近一个交易日的指标数据（列表长度为 1）

#### Scenario: 无效股票代码时抛出 DataFetchError
- **WHEN** 调用 `get_stock_daily_indicators(ts_code="999999.XX")`
- **THEN** 系统 SHALL 抛出 `DataFetchError`

### Requirement: 按交易日期查询全市场每日指标快照
系统 SHALL 支持输入交易日期，返回该日期全市场所有股票的 `DailyIndicators` 列表。

#### Scenario: 查询指定交易日全市场指标
- **WHEN** 调用 `get_market_daily_indicators(trade_date="20240115")`
- **THEN** 系统 SHALL 返回该交易日全市场所有股票的 `DailyIndicators` 列表，每支股票对应一条记录

#### Scenario: 非交易日或无数据时返回空列表
- **WHEN** 调用 `get_market_daily_indicators(trade_date="20240101")`（元旦，非交易日）
- **THEN** 系统 SHALL 返回空列表，不抛出异常

#### Scenario: 未传交易日期时抛出错误
- **WHEN** 调用 `get_market_daily_indicators` 不传 `trade_date`
- **THEN** 系统 SHALL 抛出参数校验错误
