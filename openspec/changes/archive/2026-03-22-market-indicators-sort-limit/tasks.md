## 1. MCP Tool 实现

- [x] 1.1 在 `src/buffett_munger_agent/mcp_server.py` 中更新 `get_market_daily_indicators` 函数签名，新增 `sort_by: str | None = None`、`ascending: bool = True`、`limit: int | None = 50` 三个参数
- [x] 1.2 在函数内定义 `VALID_SORT_FIELDS` 白名单集合（`pe`、`pe_ttm`、`pb`、`ps_ttm`、`turnover_rate`、`total_mv`、`circ_mv`）
- [x] 1.3 实现 `sort_by` 字段合法性校验，不合法时抛 `ValueError` 并列出合法字段
- [x] 1.4 实现排序逻辑：按 `sort_by` 字段排序，None 值统一排到末尾（升降序均如此）
- [x] 1.5 实现 `limit` 截断：`limit` 不为 None 时取前 `limit` 条
- [x] 1.6 更新函数 docstring，说明三个新参数的含义和合法值

## 2. 测试

- [x] 2.1 为 `get_market_daily_indicators` MCP Tool 编写单元测试，mock `_get_fetcher()`，验证默认 limit=50 截断行为
- [x] 2.2 验证 `sort_by="pe"`、`ascending=True` 时返回结果按 pe 升序排列
- [x] 2.3 验证 `sort_by="turnover_rate"`、`ascending=False` 时返回结果按换手率降序排列
- [x] 2.4 验证 pe 为 None 的记录在升序和降序时均排在末尾
- [x] 2.5 验证传入无效 `sort_by` 时抛出 `ValueError`
- [x] 2.6 验证 `limit=None` 时返回全量数据
- [x] 2.7 运行 `uv run pytest -m "not integration"` 确认无回归
