## 1. 修复 agent.py 中的 system 消息注入

- [x] 1.1 修改 `run_once`：将 `messages` 初始化改为以 system 消息开头，后接用户消息
- [x] 1.2 修改 `run_interactive`：将 `conversation_messages` 初始化改为包含 system 消息的列表（而非空列表）

## 2. 更新测试

- [x] 2.1 更新 `tests/test_agent.py` 中涉及 `run_once` 和 `run_interactive` 的测试，确认 messages 首条为 system 消息
- [x] 2.2 运行 `uv run pytest tests/test_agent.py -m "not integration"` 确认全部通过
