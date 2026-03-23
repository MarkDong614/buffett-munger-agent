## Why

当前项目已具备完整的 A 股数据获取能力，但缺少自主分析能力——用户只能通过 MCP Server 被动提供数据，无法主动发起投资分析任务。新增 Agent 模式可让程序作为独立的价值投资分析助手运行，由阿里千问（Qwen）模型驱动，自主调用数据工具、生成符合巴菲特/芒格理念的分析报告。

## What Changes

- **新增** `--agent` 启动模式：通过 argparse 互斥组与 `--mcp` 区分，支持 `--query` 参数用于单次分析
- **新增** `agent.py` 模块：封装 ValueInvestingAgent 类，实现基于千问模型的 agentic loop（OpenAI function calling 格式）
- **新增** `openai` 依赖：通过 DashScope 兼容端点（`https://dashscope.aliyuncs.com/compatible-mode/v1`）调用千问模型
- **新增** 两种交互模式：交互式 REPL（跨轮次保留历史）和单次分析（`--query` 参数，可重定向输出）
- **新增** 价值投资 system prompt：涵盖护城河、财务健康度、估值安全边际分析框架

## Capabilities

### New Capabilities

- `qwen-agent`: 基于阿里千问模型的价值投资分析 agent，支持工具调用（function calling）、交互式对话和单次分析两种模式

### Modified Capabilities

（无，现有 MCP Server 和数据层行为不变）

## Impact

- **新增依赖**：`openai>=1.50.0`（通过 DashScope 兼容模式调用千问）
- **新增环境变量**：`DASHSCOPE_API_KEY`（千问 API 密钥）、`QWEN_MODEL`（可选，默认 `qwen-max`）
- **修改文件**：`__main__.py`（新增参数分支）、`pyproject.toml`（新增依赖）
- **新增文件**：`src/buffett_munger_agent/agent.py`、`tests/test_agent.py`
- **隔离性**：agent 模块懒加载，`--mcp` 模式不受影响
