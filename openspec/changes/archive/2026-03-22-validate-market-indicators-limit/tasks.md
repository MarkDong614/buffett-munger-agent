## 1. MCP Tool 参数校验

- [x] 1.1 在 `src/buffett_munger_agent/mcp_server.py` 的 `get_market_daily_indicators` 中新增 `limit` 合法性校验，确保仅允许 `None` 或非负整数
- [x] 1.2 对 `limit < 0` 抛出 `ValueError`，错误信息需明确说明 `limit` 不能为负数
- [x] 1.3 保持现有排序与截断逻辑不变，确保 `limit=None` 仍返回全量、非负整数仍按上限截断
- [x] 1.4 更新该函数 docstring/参数说明，写明 `limit` 的合法范围与错误行为

## 2. 测试与回归验证

- [x] 2.1 在 MCP Server 相关测试中新增 `limit=-1` 用例，验证返回错误而非截断结果
- [x] 2.2 增加边界测试 `limit=0`，验证返回空结果且不报错
- [x] 2.3 回归验证已有 `limit=None` 与正整数 `limit` 场景，确保行为未回退
- [x] 2.4 运行 `uv run pytest -m "not integration"` 确认测试通过
