## Context

项目已有三层结构：`DataProvider` Protocol → `TushareProvider` 实现 → `StockFetcher` 委托 → `mcp_server.py` 暴露为 MCP Tool。新增每日指标接口完全沿用该模式，无架构变化。

Tushare `daily_basic` 接口提供以下关键字段：`ts_code`、`trade_date`、`pe`（市盈率TTM）、`pe_ttm`、`pb`（市净率）、`ps`（市销率TTM）、`dv_ratio`（股息率）、`turnover_rate`（换手率）、`total_mv`（总市值，万元）、`circ_mv`（流通市值，万元）。

## Goals / Non-Goals

**Goals:**
- 在不改变现有架构的前提下，新增 `get_daily_indicators` 能力
- 支持按股票代码 + 日期范围查询每日估值与交易指标
- 通过 MCP Tool 暴露，供 Claude Code CLI 直接调用

**Non-Goals:**
- 不引入新的数据源或第三方依赖
- 不实现批量多股票查询（保持与现有接口一致的单股票设计）
- 不缓存或持久化数据

## Decisions

### 数据模型字段选择
选择对价值投资最有参考意义的字段：PE(TTM)、PB、PS(TTM)、换手率、总市值、流通市值。省略部分衍生字段（如 `dv_ttm`），避免模型过重。

**理由**：与巴菲特/芒格投资框架对齐，PE/PB 是最核心的估值维度。

### 日期范围参数设计
`start_date` 和 `end_date` 均为可选，默认返回最近一个交易日数据（通过 Tushare 默认行为实现）。格式统一为 `YYYYMMDD`，与现有 `get_price_history` 保持一致。

**理由**：一致性优先，降低用户心智负担。

### 字段单位统一
Tushare 返回的 `total_mv` 和 `circ_mv` 单位为万元，模型中保留原始单位并在字段注释中说明，不做换算。

**理由**：避免引入精度损失，调用方自行处理单位。

## Risks / Trade-offs

- **Tushare 权限限制** → `daily_basic` 接口需要一定积分，低积分账号可能受限。缓解：文档注明接口要求，与现有接口风险一致。
- **字段缺失** → 部分股票（如新股）早期可能无 PE/PB 数据，Tushare 返回 `None`。缓解：模型字段均设为 `Optional[float]`。
