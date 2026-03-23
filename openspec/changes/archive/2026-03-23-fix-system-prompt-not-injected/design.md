## Context

`agent.py` 定义了 `SYSTEM_PROMPT` 常量（含分析框架、工具使用约定、报告格式要求），但 `run_once` 和 `run_interactive` 构建消息列表时均未包含该 system 消息。DashScope 千问 API 完全支持 OpenAI 兼容的 `{"role": "system", ...}` 消息，注入方式无兼容性风险。

## Goals / Non-Goals

**Goals:**
- 确保每次调用 `_run_loop` 前，消息列表第一条为 system 消息
- 使实现符合 `qwen-agent` spec 中"价值投资分析 System Prompt"需求

**Non-Goals:**
- 不修改 `SYSTEM_PROMPT` 内容
- 不修改工具定义、数据层、MCP Server

## Decisions

**在消息列表初始化时注入，而非在 `_run_loop` 内部注入**

`_run_loop` 接收外部传入的 `messages`，若在其内部自动前置 system 消息，会导致多轮交互时 system 消息被重复追加。正确做法是在构建初始消息列表的两处调用点注入：

- `run_once`：`messages = [{"role": "system", ...}, {"role": "user", ...}]`
- `run_interactive`：`conversation_messages = [{"role": "system", ...}]`

这样 system 消息只出现一次，`_run_loop` 保持职责单一，不需要感知 system 消息的存在。

## Risks / Trade-offs

- **测试断言变化**：现有测试中对 `_run_loop` 的 `messages` 参数断言（如 `assert messages[0]["role"] == "user"`）将失败 → 更新断言索引或改为检查消息是否包含特定内容
- **无功能风险**：DashScope 支持 system 角色，注入不会影响 API 调用成功率

## Migration Plan

无需迁移。修改仅影响本地进程内的消息构建逻辑，重启即生效。
