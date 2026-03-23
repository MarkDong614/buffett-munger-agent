## Context

项目当前有两层结构：数据层（StockFetcher + TushareProvider）和 MCP Server 层（FastMCP 暴露 5 个工具）。MCP 模式下 Claude Code CLI 作为 agent 驱动方，本项目只提供数据。

新增 agent 模式后，项目本身成为 agent 驱动方，需要：
1. 选择 LLM 提供商和 SDK
2. 将现有 5 个数据方法转为 LLM 可调用的工具
3. 实现 agentic loop（工具调用 → 执行 → 回传结果 → 继续推理）
4. 设计交互界面（交互式 REPL / 单次分析）

**约束**：用户指定使用阿里千问（Qwen）模型。

## Goals / Non-Goals

**Goals:**
- 通过 DashScope OpenAI 兼容端点调用千问模型（function calling）
- 5 个 StockFetcher 方法映射为 OpenAI function calling 格式的工具
- 支持交互式 REPL 和单次分析两种运行模式
- 懒加载 agent 模块，不影响 `--mcp` 模式的正常运行
- 单元测试覆盖工具执行层和 agent loop 的主要逻辑

**Non-Goals:**
- 不实现流式输出（streaming）
- 不持久化对话历史（重启即清空）
- 不支持多股票并行分析
- 不修改现有 MCP Server 和数据层

## Decisions

### 决策 1：使用 `openai` SDK + DashScope 兼容端点，而非 `dashscope` 原生 SDK

**选择**：`openai>=1.50.0`，配置 `base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"`

**理由**：
- DashScope 官方文档推荐此方式，function calling API 与 OpenAI 完全兼容
- `openai` SDK 更成熟，类型注解完整，测试时 Mock 更方便
- 避免引入 `dashscope` 包的额外依赖（pandas 版本冲突风险）

**替代方案**：原生 `dashscope` SDK — 被排除，因为其 function calling 接口与 OpenAI 格式不同，增加维护成本。

---

### 决策 2：工具定义采用 OpenAI function calling 格式（`type: "function"`）

**选择**：`TOOLS` 列表，每项格式为 `{"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}`

**理由**：与 DashScope 兼容端点要求一致；工具定义在模块级作为常量，便于测试验证完整性。

**与 MCP 工具的关系**：工具语义完全对称，但格式不同（MCP 用 `input_schema`，OpenAI 用 `parameters`）。两者独立维护，不共享定义，避免格式转换的复杂性。

---

### 决策 3：`ValueInvestingAgent` 类封装 agent loop，`run_agent` 作为对外入口

**选择**：

```
run_agent(query)              # 对外入口，负责环境变量检查和初始化
  └─ ValueInvestingAgent      # 封装 openai 客户端和 fetcher
       ├─ _execute_tool()     # 工具分发，捕获 DataFetchError
       ├─ _run_loop()         # agentic loop（最多 MAX_TOOL_ROUNDS=10 轮）
       ├─ run_once()          # 单次分析
       └─ run_interactive()   # 交互式 REPL
```

**理由**：类封装便于单元测试（Mock openai 客户端和 fetcher）；`run_agent` 保持简单的函数接口，与 `run_mcp_server` 风格一致。

---

### 决策 4：`MAX_TOOL_ROUNDS = 10` 作为 agent loop 上限

**理由**：防止模型陷入工具调用循环（如反复查询同一股票）。10 轮足以完成单只股票的完整分析（通常 3-6 次工具调用）。超出后抛出 `RuntimeError`，由 `run_agent` 捕获并打印友好提示。

---

### 决策 5：工具执行失败时返回错误字符串而非抛出异常

**理由**：让模型自行决定如何处理数据缺失（可能降级分析或告知用户），而非强制中断整个分析流程。`DataFetchError` 在 `_execute_tool` 层捕获，转为可读的中文错误描述返回给模型。

## Risks / Trade-offs

- **DashScope 兼容性风险** → 千问模型的 function calling 行为与 OpenAI 存在细微差异（如并行工具调用支持程度）。缓解：在 `_run_loop` 中同时处理 `finish_reason == "tool_calls"` 和单个 `tool_call` 的情况，并在集成测试中验证。

- **上下文窗口超限** → `get_market_daily_indicators` 默认 `limit=50`，但若模型传入 `limit=None` 可能返回 5000+ 条数据。缓解：在工具 description 中注明默认值建议，`_execute_tool` 中对 limit 做保护性上限（如 200）。

- **费用控制** → 千问 `qwen-max` 每次分析约消耗 5k-20k tokens。缓解：通过 `QWEN_MODEL` 环境变量允许切换到 `qwen-turbo` 降低开发测试成本。

- **历史消息膨胀** → 交互式模式下多轮对话会累积大量消息（含工具调用和结果），可能超出上下文窗口。当前版本不做截断，作为已知限制记录。

## Migration Plan

无破坏性变更，无需迁移。新增功能通过独立参数（`--agent`）启用，不影响现有 `--mcp` 模式。

## Open Questions

- 千问模型是否支持一次返回多个 `tool_calls`（parallel function calling）？实现时需验证并处理。
