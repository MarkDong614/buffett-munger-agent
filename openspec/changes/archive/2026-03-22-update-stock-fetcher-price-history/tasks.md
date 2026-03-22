## 1. 类型定义

- [x] 1.1 在 `src/buffett_munger_agent/data/models.py` 中新增 `Freq = Literal["D", "W", "M"]` 和 `Adjust = Literal["hfq", "qfq", ""]` 类型别名

## 2. 数据层接口更新

- [x] 2.1 在 `src/buffett_munger_agent/data/base.py` 的 `DataProvider.get_price_history` 签名中新增 `adjust: Adjust = ""` 参数，并更新 docstring
- [x] 2.2 在 `src/buffett_munger_agent/data/fetcher.py` 的 `StockFetcher.get_price_history` 签名中新增 `adjust: Adjust = ""` 参数，透传给 provider，并更新 docstring
- [x] 2.3 在 `src/buffett_munger_agent/data/providers/tushare.py` 的 `TushareProvider.get_price_history` 签名中新增 `adjust: Adjust = ""` 参数，将 `ts.pro_bar()` 调用中的硬编码 `adj="hfq"` 替换为 `adj=adjust`

## 3. MCP Server 更新

- [x] 3.1 在 `src/buffett_munger_agent/mcp_server.py` 的 `get_price_history` Tool 中新增 `adjust: str = ""` 参数，透传给 fetcher，更新 docstring 说明合法值（`"hfq"`/`"qfq"`/`""`）

## 4. 测试

- [x] 4.1 在相关测试文件中，为 `get_price_history` 补充 `adjust="qfq"` 和 `adjust=""` 场景的单元测试（mock TushareProvider）
- [x] 4.2 验证默认值场景（不传 `adjust`）的行为与修改前完全一致
- [x] 4.3 运行 `uv run pytest -m "not integration"` 确认所有测试通过
