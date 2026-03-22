## Why

当前 `get_price_history` 接口将复权方式硬编码为后复权，调用方无法按需选择前复权或不复权数据；同时 `freq` 参数仅接受裸字符串（"D"/"W"/"M"），缺乏类型约束，易误用。为支持价值投资分析中不同场景对复权方式的差异化需求，需将这两个参数显式化、类型化。

## What Changes

- **新增** `adjust` 参数：支持 `"hfq"`（后复权）、`"qfq"`（前复权）、`""`（不复权，默认）三种模式
- **新增** `Freq` / `Adjust` 枚举类型（或 `Literal` 类型），替代现有裸字符串，提供静态类型约束
- `DataProvider` Protocol、`StockFetcher`、`TushareProvider` 的 `get_price_history` 方法签名同步更新
- MCP Tool `get_price_history` 暴露 `adjust` 参数（可选，默认 `""`）
- **BREAKING**：默认复权方式由原先硬编码的后复权（`hfq`）变更为不复权（`""`），现有调用方若依赖后复权行为需显式传入 `adjust="hfq"`

## Capabilities

### New Capabilities

无新能力，为现有能力的参数扩展。

### Modified Capabilities

- `stock-price-history`：新增 `adjust` 复权参数（`hfq`/`qfq`/`""`），将 `freq` 参数类型从裸字符串改为受约束的字面量类型；MCP Tool 同步暴露 `adjust` 参数

## Impact

- `src/buffett_munger_agent/data/models.py`：新增 `Freq`、`Adjust` 类型别名
- `src/buffett_munger_agent/data/base.py`：`DataProvider.get_price_history` 签名更新
- `src/buffett_munger_agent/data/fetcher.py`：`StockFetcher.get_price_history` 签名更新
- `src/buffett_munger_agent/data/providers/tushare.py`：`TushareProvider.get_price_history` 实现更新，传递 `adjust` 给 Tushare API
- `src/buffett_munger_agent/mcp_server.py`：MCP Tool 定义更新，新增 `adjust` 参数
- 现有测试需补充 `adjust` 参数场景
