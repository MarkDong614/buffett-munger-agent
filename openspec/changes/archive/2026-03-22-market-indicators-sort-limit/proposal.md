## Why

`get_market_daily_indicators` 返回全市场所有股票（~5000 条）的每日指标，序列化后体积超过 Claude MCP 的 token 上限，AI 无法直接消费返回值，必须绕道读写临时文件。为此在 MCP Tool 层增加排序和条数限制参数，让 AI 只取所需数据。

## What Changes

- `get_market_daily_indicators` MCP Tool 新增三个可选参数：`sort_by`（排序字段）、`ascending`（升降序）、`limit`（返回条数上限，默认 50）
- 排序和截断逻辑在 MCP Tool 层的 Python 代码中完成，不改动 TushareProvider 或 DataProvider Protocol

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `mcp-server`：`get_market_daily_indicators` Tool 的参数 schema 和行为发生变化，新增 `sort_by`、`ascending`、`limit` 参数，返回结果从全量变为可按需截取

## Impact

- `src/buffett_munger_agent/mcp_server.py`：仅修改 `get_market_daily_indicators` 函数签名和内部逻辑
- 无新增依赖
- **不影响** `data/` 层任何模块
