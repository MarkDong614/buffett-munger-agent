## MODIFIED Requirements

### Requirement: 价值投资分析 System Prompt

Agent MUST 使用包含巴菲特/芒格投资理念的 system prompt 初始化每次对话。System prompt MUST 包含：分析框架（护城河、管理层质量、财务健康度、估值安全边际）和输出格式要求（Markdown 报告，含公司概述/财务质量/估值分析/投资风险/综合结论五个章节）。System prompt MUST 作为 `{"role": "system", "content": SYSTEM_PROMPT}` 消息注入到每次对话的消息列表第一条，确保模型在每轮分析中均能遵循工具使用约定和报告格式要求。

#### Scenario: 分析报告包含必要章节

- **WHEN** 用户请求对某只股票进行完整的价值投资分析
- **THEN** 最终报告包含"公司概述"、"财务质量"、"估值分析"、"投资风险"、"综合结论"章节

#### Scenario: 综合结论给出明确投资吸引力判断

- **WHEN** 分析完成
- **THEN** 综合结论章节包含明确的投资吸引力评级（高/中/低）及关键假设说明

#### Scenario: run_once 包含 system 消息

- **WHEN** 调用 `run_once(query)` 时
- **THEN** 传入 `_run_loop` 的 messages 列表第一条消息的 role 为 "system"，content 等于 `SYSTEM_PROMPT`

#### Scenario: run_interactive 包含 system 消息

- **WHEN** `run_interactive` 初始化会话时
- **THEN** `conversation_messages` 列表第一条消息的 role 为 "system"，content 等于 `SYSTEM_PROMPT`

#### Scenario: 多轮交互中 system 消息不重复

- **WHEN** 用户在交互式模式发送多条消息
- **THEN** `conversation_messages` 中 role 为 "system" 的消息始终只有一条（位于列表首位）
