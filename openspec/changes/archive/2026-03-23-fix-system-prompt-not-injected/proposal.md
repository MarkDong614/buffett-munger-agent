## Why

`SYSTEM_PROMPT` 已在 `agent.py` 中定义，但 `run_once` 和 `run_interactive` 构建消息列表时均未将其注入，导致模型收不到工具使用约定和分析框架指令，直接用训练数据回答而不调用数据接口。

## What Changes

- `run_once`：初始化 `messages` 时在用户消息前添加 `{"role": "system", "content": SYSTEM_PROMPT}`
- `run_interactive`：初始化 `conversation_messages` 时预置 system 消息（当前为空列表）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `qwen-agent`：修复"价值投资分析 System Prompt"需求的实现缺陷——spec 已要求 MUST 用 system prompt 初始化每次对话，当前实现未满足该要求

## Impact

- 修改文件：`src/buffett_munger_agent/agent.py`（2 处）
- 不影响对外接口、MCP Server、数据层
- 现有单元测试中 mock 的 `_run_loop` 调用可能需要更新断言（messages 初始内容变化）
