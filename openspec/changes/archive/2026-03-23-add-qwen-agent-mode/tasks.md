## 1. 依赖与配置

- [x] 1.1 执行 `uv add openai` 将 `openai>=1.50.0` 添加到 `pyproject.toml` 依赖列表

## 2. agent.py 核心模块

- [x] 2.1 创建 `src/buffett_munger_agent/agent.py`，定义模块级常量：`QWEN_MODEL`（从环境变量读取，默认 `qwen-max`）、`DASHSCOPE_BASE_URL`、`MAX_TOKENS = 8192`、`MAX_TOOL_ROUNDS = 10`
- [x] 2.2 定义 `SYSTEM_PROMPT` 字符串，包含：价值投资分析框架（护城河/管理层质量/财务健康度/估值安全边际）和 Markdown 报告输出格式要求（五个章节）
- [x] 2.3 定义 `TOOLS` 列表（OpenAI function calling 格式），包含 5 个工具：`get_company_info`、`get_fundamentals`、`get_price_history`（含 freq/adjust 可选参数）、`get_stock_daily_indicators`（含 start_date/end_date 可选参数）、`get_market_daily_indicators`（含 sort_by/ascending/limit 可选参数）
- [x] 2.4 实现 `ValueInvestingAgent.__init__`：接收 `fetcher: StockFetcher` 和 `api_key: str`，初始化 `openai.OpenAI` 客户端（配置 `base_url=DASHSCOPE_BASE_URL`）
- [x] 2.5 实现 `ValueInvestingAgent._execute_tool(name, arguments)`：用 `match` 语句分发工具调用到对应 `fetcher` 方法；捕获 `DataFetchError` 返回错误描述字符串；未知工具名返回错误字符串
- [x] 2.6 实现 `ValueInvestingAgent._run_loop(messages)`：循环至多 `MAX_TOOL_ROUNDS` 轮；处理 `finish_reason == "stop"` 返回文本；处理 `finish_reason == "tool_calls"` 执行工具并追加 `tool` role 消息；超出轮次抛出 `RuntimeError`
- [x] 2.7 实现 `ValueInvestingAgent.run_once(query)`：构造初始 messages，调用 `_run_loop`，返回结果字符串
- [x] 2.8 实现 `ValueInvestingAgent.run_interactive()`：打印欢迎信息；循环读取用户输入；处理 `exit`/`quit`/`退出` 退出；调用 `_run_loop` 并打印结果；跨轮次保留 `conversation_messages`
- [x] 2.9 实现 `run_agent(query=None)` 入口函数：验证 `DASHSCOPE_API_KEY` 和 `TUSHARE_TOKEN` 环境变量（缺失则 `sys.exit(1)`）；初始化 `StockFetcher` 和 `ValueInvestingAgent`；根据 `query` 是否为 `None` 分派到 `run_once` 或 `run_interactive`

## 3. 更新 __main__.py

- [x] 3.1 将 `--mcp` 和新增的 `--agent` 参数放入 `add_mutually_exclusive_group()`
- [x] 3.2 新增 `--query` 参数（`type=str, default=None`）
- [x] 3.3 新增 `elif args.agent:` 分支，懒加载 `from buffett_munger_agent.agent import run_agent` 并调用 `run_agent(query=args.query)`

## 4. 单元测试

- [x] 4.1 创建 `tests/test_agent.py`，测试 `TOOLS` 列表：验证包含 5 个工具，每个工具有 `type`/`function.name`/`function.description`/`function.parameters` 字段
- [x] 4.2 测试 `_execute_tool` 正常路径：Mock `StockFetcher`，验证返回有效 JSON 字符串
- [x] 4.3 测试 `_execute_tool` 异常路径：`DataFetchError` 被捕获，返回错误描述字符串而非抛出
- [x] 4.4 测试 `_execute_tool` 未知工具名：返回包含"未知工具"的错误字符串
- [x] 4.5 测试 `_run_loop` 正常终止：Mock `openai.OpenAI`，`finish_reason="stop"` 时正确返回文本
- [x] 4.6 测试 `run_agent` 环境变量校验：未设置 `DASHSCOPE_API_KEY` 时 `sys.exit(1)`

## 5. 验证

- [x] 5.1 执行 `uv run pytest -m "not integration"` 确认所有单元测试通过
- [x] 5.2 执行 `uv run ruff check . && uv run ruff format .` 确认代码检查通过
- [x] 5.3 手动执行 `uv run buffett-munger-agent --agent --query "用一句话介绍平安银行000001.SZ"` 验证端到端分析流程
