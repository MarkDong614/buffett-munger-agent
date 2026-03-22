## MODIFIED Requirements

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
