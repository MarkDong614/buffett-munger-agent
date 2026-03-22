## Why

`get_market_daily_indicators` 目前直接使用 `indicators[:limit]` 做截断，`limit` 为负值时会返回非预期数量的数据（例如 `-1` 返回除最后一条外的几乎全量数据）。这会让 MCP/LLM 生成参数时出现隐性错误，导致 API 行为不可预测。

## What Changes

- 在 `get_market_daily_indicators` 中为 `limit` 增加输入校验：仅接受 `None` 或非负整数
- 当 `limit < 0` 时抛出 `ValueError`，错误信息明确说明参数约束
- 增加/更新单元测试，覆盖 `limit=-1` 等负值输入场景，确保不会发生静默截断
- 补充函数说明，明确 `limit` 的合法取值语义

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `mcp-server`：`get_market_daily_indicators` 的 `limit` 参数行为变更，新增负值校验并在非法输入时返回错误

## Impact

- `src/buffett_munger_agent/mcp_server.py`：增加 `limit` 合法性校验逻辑与说明
- `tests/` 下 MCP Server 相关测试：新增或更新负值 `limit` 的测试用例
- 无新增依赖，无数据层接口变更
