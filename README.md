# buffett-munger-agent

由大模型驱动的 agent，按照巴菲特/芒格价值投资理念生成股票分析报告。

## 快速开始

```bash
# 安装依赖
uv sync

# 运行 agent（默认模式）
uv run buffett-munger-agent
```

## 作为 MCP Server 供 Claude Code 调用

本项目可作为 MCP Server 运行，让 Claude Code CLI 直接调用股票数据获取工具。

### 前置条件

- 申请 [Tushare](https://tushare.pro) API token
- 安装 [Claude Code CLI](https://claude.ai/code)

### 注册到 Claude Code

**方式一：命令行注册（推荐）**

```bash
claude mcp add buffett-munger-agent \
  -e TUSHARE_TOKEN=<your_token> \
  -- uv --directory /path/to/buffett-munger-agent run buffett-munger-agent --mcp
```

**方式二：编辑配置文件**

在 `~/.claude/mcp_settings.json` 中添加：

```json
{
  "mcpServers": {
    "buffett-munger-agent": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/buffett-munger-agent",
        "run", "buffett-munger-agent", "--mcp"
      ],
      "env": {
        "TUSHARE_TOKEN": "<your_token>"
      }
    }
  }
}
```

将 `/path/to/buffett-munger-agent` 替换为本项目的实际绝对路径。

### 可用工具

注册成功后，Claude Code 可调用以下三个工具：

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `get_company_info` | 获取公司基础信息（名称、行业、市值等） | `ts_code` |
| `get_fundamentals` | 获取基本面财务数据（PE、PB、ROE、营收等） | `ts_code` |
| `get_price_history` | 获取历史 K 线数据（后复权 OHLCV） | `ts_code`, `start_date`, `end_date`, `freq` |

股票代码格式：Tushare 标准格式，如 `600519.SH`（贵州茅台）、`000001.SZ`（平安银行）。

### 手动测试

```bash
# token 缺失时会报错退出
uv run buffett-munger-agent --mcp

# 正常启动（通过 stdin 发送 MCP 协议消息）
TUSHARE_TOKEN=<your_token> uv run buffett-munger-agent --mcp
```

## 开发

```bash
uv run pytest          # 运行测试
uv run ruff check .    # 代码检查
uv run ruff format .   # 代码格式化
```
