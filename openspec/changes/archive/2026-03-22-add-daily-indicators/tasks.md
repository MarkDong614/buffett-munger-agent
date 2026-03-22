## 1. 数据模型

- [x] 1.1 在 `src/buffett_munger_agent/data/models.py` 中新增 `DailyIndicators` Pydantic 模型，包含 `ts_code`、`trade_date`、`pe`、`pe_ttm`、`pb`、`ps_ttm`、`turnover_rate`、`total_mv`、`circ_mv` 字段（估值字段均为 `Optional[float]`）

## 2. DataProvider Protocol

- [x] 2.1 在 `src/buffett_munger_agent/data/base.py` 的 `DataProvider` Protocol 中新增 `get_stock_daily_indicators(ts_code, start_date, end_date)` 方法签名
- [x] 2.2 在 `DataProvider` Protocol 中新增 `get_market_daily_indicators(trade_date)` 方法签名

## 3. TushareProvider 实现

- [x] 3.1 在 `src/buffett_munger_agent/data/providers/tushare.py` 中实现 `get_stock_daily_indicators` 方法，以 `ts_code` 为主键调用 `pro.daily_basic()`，将结果映射为 `DailyIndicators` 列表（按日期升序）
- [x] 3.2 实现 `get_market_daily_indicators` 方法，以 `trade_date` 为主键调用 `pro.daily_basic()`，返回全市场 `DailyIndicators` 列表
- [x] 3.3 两个方法均需处理：Optional 字段为 None、空结果返回空列表、异常时抛出 `DataFetchError`

## 4. StockFetcher 委托

- [x] 4.1 在 `src/buffett_munger_agent/data/fetcher.py` 的 `StockFetcher` 中新增 `get_stock_daily_indicators` 委托方法
- [x] 4.2 新增 `get_market_daily_indicators` 委托方法

## 5. MCP Server

- [x] 5.1 在 `src/buffett_munger_agent/mcp_server.py` 中注册 `get_stock_daily_indicators` MCP Tool，参数：`ts_code`（必填）、`start_date`（可选）、`end_date`（可选）
- [x] 5.2 注册 `get_market_daily_indicators` MCP Tool，参数：`trade_date`（必填）
- [x] 5.3 两个 Tool 均返回 JSON 序列化列表，异常时转为 `ValueError`

## 6. 测试

- [x] 6.1 为 `DailyIndicators` 模型编写单元测试，验证字段类型和 Optional 处理
- [x] 6.2 为 `TushareProvider.get_stock_daily_indicators` 编写集成测试（标记 `@pytest.mark.integration`）
- [x] 6.3 为 `TushareProvider.get_market_daily_indicators` 编写集成测试（标记 `@pytest.mark.integration`）
- [x] 6.4 运行 `uv run pytest -m "not integration"` 确认无回归
