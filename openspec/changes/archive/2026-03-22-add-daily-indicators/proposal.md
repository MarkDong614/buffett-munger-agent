## Why

当前项目已具备基本面数据和历史价格数据的获取能力，但缺少每日市场指标（如市盈率、市净率、换手率、总市值等），这些指标是价值投资分析的核心参考维度。增加每日指标接口，使 agent 能够获取个股在特定日期的估值水平和交易活跃度数据。

## What Changes

- 新增 `get_stock_daily_indicators` MCP Tool，输入股票代码和日期范围，返回该股票一段时间的每日指标序列
- 新增 `get_market_daily_indicators` MCP Tool，输入交易日期，返回该日期全市场所有股票的指标快照
- 新增 `DailyIndicators` Pydantic 数据模型，包含 PE、PB、换手率、总市值等字段
- `TushareProvider` 实现两个方法，均调用 Tushare `daily_basic` 接口（入参维度不同）
- `DataProvider` Protocol 新增两个方法签名
- `StockFetcher` 新增对应的两个委托方法

## Capabilities

### New Capabilities

- `daily-indicators`: 提供两种维度的每日市场指标查询——（1）按股票代码查询一段时间的指标序列；（2）按交易日期查询全市场当日所有股票的指标快照。指标包含 PE、PB、PS、换手率、总市值、流通市值等。

### Modified Capabilities

- `mcp-server`: 新增 `get_stock_daily_indicators` 和 `get_market_daily_indicators` 两个 MCP Tool 注册

## Impact

- `src/buffett_munger_agent/data/models.py`：新增 `DailyIndicators` 模型
- `src/buffett_munger_agent/data/base.py`：`DataProvider` Protocol 新增两个方法
- `src/buffett_munger_agent/data/fetcher.py`：`StockFetcher` 新增两个委托方法
- `src/buffett_munger_agent/data/providers/tushare.py`：实现两个方法，调用 `pro.daily_basic()`，入参维度不同
- `src/buffett_munger_agent/mcp_server.py`：注册两个新 MCP Tool
- 依赖：无新增外部依赖，Tushare SDK 已支持 `daily_basic` 接口
