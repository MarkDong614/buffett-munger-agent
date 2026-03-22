## Context

`get_market_daily_indicators` 当前返回全市场所有股票（~5000 条），AI 调用后因超出 token 限制无法直接处理结果。改动范围极小：仅在 MCP Tool 函数内增加排序和截断，不触及数据层。

## Goals / Non-Goals

**Goals:**
- MCP Tool 支持 `sort_by`（排序字段）、`ascending`（升降序）、`limit`（条数上限）三个可选参数
- 默认 `limit=50`，使 AI 在不传参时也能拿到可用大小的结果
- `None` 值（无数据）在排序时统一排到末尾，不论升降序

**Non-Goals:**
- 不改动 TushareProvider、DataProvider Protocol、StockFetcher
- 不在 Provider 层做过滤（保持数据层纯粹）
- 不支持多字段组合排序
- 不支持按字段值范围过滤（如 `pe < 10`）

## Decisions

### 排序和截断在 MCP Tool 层完成，而非 Provider 层

Provider 层职责是"如实返回数据源的数据"，不应内嵌业务逻辑。MCP Tool 层是 AI 接口，负责把原始数据加工成 AI 可用的形式。排序/截断属于展示逻辑，放在 MCP Tool 层符合分层原则，也避免 Protocol 接口膨胀。

### `limit` 默认值为 50

50 条约 3-4KB JSON，远低于 token 限制，且足以覆盖大多数"找 Top N"的分析场景。用户需要全量数据时可传 `limit=None`。

### None 值排在末尾

PE 为 None 通常代表亏损股或数据缺失，排在末尾符合"找低估值"场景的直觉。实现方式：`key=lambda x: (val is None, val or 0)`，让 None 在升序和降序时都沉底。

### 合法 sort_by 字段白名单校验

`sort_by` 接受字符串输入，需防止 AI 传入无效字段名导致静默错误。使用白名单 `VALID_SORT_FIELDS` 集合校验，不合法时抛 `ValueError` 并列出合法值。

## Risks / Trade-offs

- **全量数据仍从 Tushare 拉取** → 网络开销与之前相同，排序/截断发生在内存中。可接受，性能瓶颈在网络 I/O 而非内存排序。
- **`limit=None` 时仍可能超 token 限制** → 属于用户主动选择，文档说明清楚即可。
