## Context

项目当前处于早期阶段，仅有入口文件，尚无任何数据获取能力。需要从零构建数据获取模块，为 LLM Agent 的价值投资分析提供标准化的财务数据输入。当前阶段聚焦 A 股市场，使用 Tushare 作为数据源。

## Goals / Non-Goals

**Goals:**
- 实现从 Tushare 获取 A 股基本面、历史价格和公司信息的能力
- 定义统一的数据模型（Pydantic），供 agent 其他模块消费
- 设计可扩展的数据提供者接口，支持未来切换或新增数据源

**Non-Goals:**
- 不实现美股数据获取（后续迭代）
- 不实现数据持久化/缓存层（后续迭代）
- 不实现实时行情数据（专注历史与基本面）
- 不实现数据清洗或标准化的复杂 ETL 流程

## Decisions

### 决策 1：数据提供者抽象层

使用 Protocol（结构子类型）定义 `DataProvider` 接口，当前仅有 `TushareProvider` 一个实现。

**备选方案：** 直接调用 Tushare，无抽象层。
**选择原因：** 抽象层允许在不改动上层逻辑的情况下替换或 Mock 数据源，便于测试；同时为后续引入其他数据源预留扩展点。

### 决策 2：数据模型使用 Pydantic BaseModel

使用 Pydantic 定义 `StockFundamentals`、`PriceBar`、`CompanyInfo` 等数据模型。

**备选方案：** 使用 dataclass 或 TypedDict。
**选择原因：** Pydantic 支持数据验证、JSON 序列化，且项目未来与 LLM 集成时可直接序列化输出，减少重复工作。

### 决策 3：使用 Tushare Pro API 作为 A 股数据源

**选择原因：** Tushare Pro 提供完整的 A 股财务报表、日线行情及公司基础信息接口，数据质量可靠，接口稳定，是 A 股量化领域主流数据源之一。需要用户提供 token 进行鉴权。

### 决策 4：目录结构

```
src/buffett_munger_agent/
└── data/
    ├── __init__.py
    ├── models.py          # 统一数据模型
    ├── base.py            # DataProvider Protocol 定义
    ├── providers/
    │   ├── __init__.py
    │   └── tushare.py     # A 股数据提供者
    └── fetcher.py         # 对外暴露的统一 Fetcher 入口
```

## Risks / Trade-offs

- **[Token 鉴权依赖]** Tushare 需要有效 token，token 积分不足可能导致部分接口无法调用 → 在 `TushareProvider` 初始化时验证 token，失败时抛出明确的 `DataFetchError`
- **[网络依赖]** 数据获取需要网络连接，测试时可能不稳定 → 在 Provider 层注入依赖，便于 Mock
- **[数据质量]** 财务数据可能存在缺失或延迟 → 使用 Pydantic Optional 字段标记非必须数据，调用方自行处理缺失
