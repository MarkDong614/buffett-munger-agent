## Why

当前项目缺乏从外部数据源获取股票数据的能力，无法为后续的价值投资分析提供所需的财务指标、历史价格及公司基本面数据。构建数据获取模块是整个 agent 分析流程的基础，需优先实现。

## What Changes

- 新增股票基本面数据获取能力（财务报表、关键指标）
- 新增历史价格数据获取能力（日/周/月级别 OHLCV 数据）
- 新增公司信息获取能力（行业、市值、简介等元数据）
- 定义统一的数据获取接口与数据模型，供 agent 其他模块调用

## Capabilities

### New Capabilities

- `stock-fundamentals`: 获取股票基本面数据，包括财务报表（利润表、资产负债表、现金流量表）及核心财务指标（PE、PB、ROE、FCF 等）
- `stock-price-history`: 获取股票历史价格数据（OHLCV），支持不同时间粒度
- `company-info`: 获取公司基础信息，包括行业分类、市值、公司描述等元数据

### Modified Capabilities

（无现有 capability 需修改）

## Impact

- 新增对外部数据提供方的依赖（Tushare Python 库）
- 新增 `src/buffett_munger_agent/data/` 子包，包含数据获取器与数据模型
- 为后续 LLM Agent 分析模块提供标准化的数据输入接口
