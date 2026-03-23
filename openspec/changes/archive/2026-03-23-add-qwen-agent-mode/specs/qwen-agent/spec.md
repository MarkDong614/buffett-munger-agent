## ADDED Requirements

### Requirement: Agent 模式启动

程序 SHALL 支持通过 `--agent` 命令行参数以 agent 模式启动。`--agent` 与 `--mcp` MUST 互斥，不得同时使用。agent 模式启动前 MUST 验证环境变量 `DASHSCOPE_API_KEY` 和 `TUSHARE_TOKEN` 均已设置，任一缺失 MUST 打印明确错误信息并以退出码 1 退出。

#### Scenario: 正常启动交互式模式

- **WHEN** 用户执行 `DASHSCOPE_API_KEY=<k> TUSHARE_TOKEN=<t> uv run buffett-munger-agent --agent`
- **THEN** 程序进入交互式 REPL，打印欢迎信息并等待用户输入

#### Scenario: DASHSCOPE_API_KEY 缺失时启动失败

- **WHEN** 用户执行 `TUSHARE_TOKEN=<t> uv run buffett-munger-agent --agent`（未设置 DASHSCOPE_API_KEY）
- **THEN** 程序打印包含"DASHSCOPE_API_KEY"的错误信息并以退出码 1 退出

#### Scenario: --agent 与 --mcp 不可同时使用

- **WHEN** 用户同时传入 `--agent` 和 `--mcp` 参数
- **THEN** argparse 输出错误信息并以非零退出码退出

---

### Requirement: 单次分析模式

agent 模式 SHALL 支持 `--query <text>` 参数，传入时执行单次分析后退出（退出码 0）。分析结果 MUST 打印到 stdout，可被重定向到文件。

#### Scenario: 单次分析正常执行

- **WHEN** 用户执行 `... --agent --query "分析贵州茅台600519.SH"`
- **THEN** 程序执行分析，将 Markdown 格式报告打印到 stdout，然后退出

#### Scenario: --query 不与 --agent 配合时无效

- **WHEN** 用户执行 `uv run buffett-munger-agent --query "分析茅台"`（不带 `--agent`）
- **THEN** 程序进入普通模式（`--query` 被忽略或 argparse 提示需配合 `--agent`）

---

### Requirement: 交互式对话模式

不传 `--query` 时 agent MUST 进入交互式 REPL 模式。每轮对话的历史消息 MUST 在会话内保留（跨轮次上下文）。用户输入 `exit`、`quit` 或 `退出` 时 MUST 正常退出（退出码 0）。

#### Scenario: 多轮对话保留上下文

- **WHEN** 用户在第一轮询问"介绍一下贵州茅台"，第二轮询问"它的 PE 历史区间如何"
- **THEN** 第二轮回复能结合第一轮的股票上下文作答，无需重复指定股票代码

#### Scenario: 退出命令

- **WHEN** 用户在交互式模式输入 `exit`
- **THEN** 程序打印告别信息并正常退出

---

### Requirement: 价值投资工具调用

Agent MUST 将以下 5 个 StockFetcher 方法暴露为千问模型可调用的工具（OpenAI function calling 格式）：`get_company_info`、`get_fundamentals`、`get_price_history`、`get_stock_daily_indicators`、`get_market_daily_indicators`。工具的 `description` 字段 MUST 说明其在价值投资分析中的具体用途。

#### Scenario: 模型调用工具获取公司信息

- **WHEN** 千问模型在分析过程中发起 `get_company_info(ts_code="600519.SH")` 工具调用
- **THEN** `_execute_tool` 调用 `StockFetcher.get_company_info`，将结果序列化为 JSON 字符串返回给模型

#### Scenario: 工具调用失败时不中断分析

- **WHEN** `get_fundamentals` 因数据源错误抛出 `DataFetchError`
- **THEN** `_execute_tool` 捕获异常，返回包含错误描述的字符串（而非抛出），让模型决定后续处理

---

### Requirement: Agent Loop 安全限制

Agent loop MUST 设置最大工具调用轮次上限（`MAX_TOOL_ROUNDS = 10`）。达到上限后 MUST 抛出 `RuntimeError`，由外层捕获并向用户打印友好提示。

#### Scenario: 正常分析在轮次上限内完成

- **WHEN** 模型在 10 轮内完成分析（`finish_reason == "stop"`）
- **THEN** loop 正常返回最终文本，不触发上限错误

#### Scenario: 达到最大轮次时终止

- **WHEN** 模型在 10 轮内仍未返回 `stop`（持续发起工具调用）
- **THEN** loop 抛出 `RuntimeError`，用户看到"达到最大工具调用轮次"提示

---

### Requirement: 价值投资分析 System Prompt

Agent MUST 使用包含巴菲特/芒格投资理念的 system prompt 初始化每次对话。System prompt MUST 包含：分析框架（护城河、管理层质量、财务健康度、估值安全边际）和输出格式要求（Markdown 报告，含公司概述/财务质量/估值分析/投资风险/综合结论五个章节）。

#### Scenario: 分析报告包含必要章节

- **WHEN** 用户请求对某只股票进行完整的价值投资分析
- **THEN** 最终报告包含"公司概述"、"财务质量"、"估值分析"、"投资风险"、"综合结论"章节

#### Scenario: 综合结论给出明确投资吸引力判断

- **WHEN** 分析完成
- **THEN** 综合结论章节包含明确的投资吸引力评级（高/中/低）及关键假设说明
