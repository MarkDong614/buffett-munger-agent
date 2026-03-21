## Context

项目当前已有 `StockFetcher` 统一数据入口，提供三类能力：公司基础信息、基本面财务数据、历史价格数据。入口模块 `__main__.py` 目前仅打印占位信息，尚未实现任何实际逻辑。

MCP（Model Context Protocol）是 Anthropic 定义的标准协议，Claude Code CLI 可通过 stdio transport 调用本地 MCP Server 中注册的 Tools。实现目标是将现有数据获取能力无侵入地包装为 MCP Tools。

## Goals / Non-Goals

**Goals:**
- 新增 `mcp_server.py` 模块，注册三个 MCP Tools（`get_company_info`、`get_fundamentals`、`get_price_history`）
- 通过 `--mcp` 启动参数以 stdio 模式运行 MCP Server
- 支持通过环境变量 `TUSHARE_TOKEN` 传入 API token
- 提供 Claude Code 注册配置示例

**Non-Goals:**
- 不实现 HTTP/SSE transport（仅 stdio，满足本地 CLI 场景）
- 不实现认证/鉴权（本地工具，信任调用方）
- 不引入新的数据源或分析逻辑

## Decisions

### 决策 1：使用官方 MCP Python SDK（`mcp`）

**选择**：`mcp` 官方 SDK（`pip install mcp`）

**理由**：与 Claude Code 协议保持一致，无需手写协议解析；SDK 提供装饰器风格 Tool 注册，代码简洁。

**备选**：手写 JSON-RPC over stdio — 维护成本高，放弃。

---

### 决策 2：单文件 `mcp_server.py` 模块，不新增子包

**选择**：`src/buffett_munger_agent/mcp_server.py`

**理由**：当前 MCP 逻辑仅为薄包装层，无需独立子包；保持项目扁平结构，降低导入复杂度。

---

### 决策 3：Token 通过环境变量注入，不硬编码也不新增配置文件

**选择**：`os.environ["TUSHARE_TOKEN"]`，Server 启动时读取，失败则报错退出

**理由**：与现有约定一致；Claude Code 的 MCP server 配置支持 `env` 字段，可在注册时传入。

---

### 决策 4：`--mcp` 启动参数控制模式

**选择**：`__main__.py` 解析 `--mcp` 参数，有则启动 MCP Server，无则保留原有行为

**理由**：一个入口点兼容两种模式，Claude Code 注册时指定 `--mcp`，日后 CLI 功能扩展不受影响。

## Risks / Trade-offs

- **Tushare 接口限速** → MCP Tool 调用受 Tushare 免费账户 QPS 限制，高频调用可能触发限流。缓解：当前场景为交互式分析，调用频率低，暂不处理缓存。
- **MCP SDK 版本兼容** → `mcp` SDK 尚在快速迭代，API 可能变动。缓解：在 `pyproject.toml` 中锁定 minor 版本。
- **stdio 阻塞** → MCP stdio Server 在单线程同步模式下可能阻塞。缓解：MCP Python SDK 默认使用 asyncio，Tushare 调用可在线程池中执行。

## Migration Plan

1. `uv add mcp` 添加依赖
2. 新增 `src/buffett_munger_agent/mcp_server.py`
3. 修改 `__main__.py` 增加 `--mcp` 分支
4. 在 Claude Code 中通过 `/mcp` 命令或 `~/.claude/mcp_settings.json` 注册 server
5. 无需迁移旧数据或处理回滚（纯新增，不破坏现有接口）
