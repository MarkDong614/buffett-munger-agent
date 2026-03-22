## Context

当前 `get_price_history` 接口在 `TushareProvider` 层将 `adj` 硬编码为 `"hfq"`（后复权），`freq` 参数接受裸字符串 `"D"/"W"/"M"`，无静态类型约束。此次改动涉及数据层的 Protocol、Fetcher、Provider 以及 MCP Server 层，属于跨模块的接口契约变更。

## Goals / Non-Goals

**Goals:**
- 将 `adjust` 复权参数显式化，允许调用方选择 `hfq`/`qfq`/`""`，默认为不复权（`""`）
- 用 `Literal` 类型约束 `freq` 和 `adjust`，提升静态类型检查覆盖率
- 在 MCP Tool `get_price_history` 中暴露 `adjust` 参数，供 Claude Code CLI 使用
- 向后兼容：所有新参数均有默认值，现有调用无需修改

**Non-Goals:**
- 不引入枚举类（保持轻量，用 `Literal` + `type` 别名即可）
- 不修改 `PriceBar` 数据模型字段
- 不支持多股票批量查询（超出本次范围）
- 不修改 `freq` 参数的取值范围（仍为 `"D"/"W"/"M"`，Tushare 原生格式）

## Decisions

### 1. 用 `Literal` 而非 `Enum` 表达类型约束

**决策**：在 `models.py` 中定义 `type Freq = Literal["D", "W", "M"]` 和 `type Adjust = Literal["hfq", "qfq", ""]`。

**理由**：
- `Literal` 别名轻量，无运行时开销，序列化天然为字符串（Pydantic / JSON 兼容）
- `Enum` 需要额外转换（`.value`），且 Tushare API 接受字符串而非枚举对象，引入 `Enum` 反而增加摩擦
- 现有代码风格未使用 `Enum`，保持一致

**备选**：`StrEnum`——被排除，原因同上，且 Python 3.11+ 才内置，项目要求 >= 3.14 虽满足，但无额外收益。

### 2. 在哪一层定义类型别名

**决策**：在 `models.py` 中定义，与 `PriceBar` 等模型并列。

**理由**：`models.py` 已是数据层的"类型汇聚点"，所有层（base.py、fetcher.py、tushare.py、mcp_server.py）均导入该模块，避免循环依赖。

### 3. MCP Tool 的 `adjust` 参数类型

**决策**：MCP Tool 中 `adjust` 参数类型为 `str`（而非 `Adjust` 类型别名），并在 docstring 中说明合法值。

**理由**：FastMCP 根据函数签名生成 JSON Schema，`Literal` 类型别名在 FastMCP 当前版本中可能无法正确映射为 `enum` 约束。使用 `str` + 文档描述更稳健；若 FastMCP 后续支持 `Literal`，可再升级。

### 4. 默认值选择

**决策**：`adjust` 默认为 `""`（不复权），`freq` 默认保持 `"D"`。

**理由**：不复权是最"原始"的数据，适合调用方自行决定复权策略；同时避免隐式修改价格数据，降低误用风险。这是一个 BREAKING 变更，原有硬编码 `hfq` 行为的调用方需显式传入 `adjust="hfq"`。

## Risks / Trade-offs

- **[风险] MCP Tool 未做 adjust 合法值校验** → 传入非法值时 Tushare API 可能静默返回空数据或报错。缓解：在 `StockFetcher` 层加断言或 `Literal` 运行时检查（可选，本次不强制）。
- **[风险] Tushare `pro_bar` 对某些 `freq`+`adjust` 组合的支持不完整**（如月线+前复权）→ 遇到时由现有 `DataFetchError` 捕获并上报，行为与现有一致。
- **[Trade-off] `Literal` 别名在运行时无法枚举合法值**，调试时不如 `Enum` 直观 → 接受，文档补充说明。

## Migration Plan

1. 更新 `models.py`：新增 `Freq`、`Adjust` 类型别名
2. 更新 `base.py`：`DataProvider.get_price_history` 签名加 `adjust: Adjust = ""`
3. 更新 `fetcher.py`：`StockFetcher.get_price_history` 签名加 `adjust: Adjust = ""`，透传给 provider
4. 更新 `tushare.py`：`TushareProvider.get_price_history` 签名加 `adjust: Adjust = ""`，替换硬编码的 `adj="hfq"`
5. 更新 `mcp_server.py`：`get_price_history` Tool 加 `adjust: str = ""` 参数，透传给 fetcher
6. 更新测试：补充 `adjust` 参数的测试场景

无数据库迁移，无部署风险。回滚方式：还原上述文件修改。

## Open Questions

无。
