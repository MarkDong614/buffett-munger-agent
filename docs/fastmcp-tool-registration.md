# FastMCP 注册 Tools 的机制

## 1. 装饰器注册（核心方式）

```python
mcp = FastMCP("my-server")

@mcp.tool()
def get_company_info(ts_code: str) -> str:
    """工具描述会自动成为 MCP Tool 的 description"""
    ...
```

`@mcp.tool()` 做了以下几件事：

### ① 提取函数签名 → 生成 `inputSchema`

FastMCP 通过 Python 的 `inspect` 模块解析函数参数的类型注解，自动生成 JSON Schema。比如：

```python
def get_price_history(ts_code: str, start_date: str, end_date: str, freq: str = "D") -> str:
```

自动生成：
```json
{
  "inputSchema": {
    "type": "object",
    "properties": {
      "ts_code": {"type": "string"},
      "start_date": {"type": "string"},
      "end_date": {"type": "string"},
      "freq": {"type": "string", "default": "D"}
    },
    "required": ["ts_code", "start_date", "end_date"]
  }
}
```

有默认值的参数自动从 `required` 中排除。

### ② 提取 docstring → 生成 `description`

函数的 docstring 直接成为 Tool 的描述，Claude 会根据这段描述决定何时调用该工具，**所以写好 docstring 非常重要**。

### ③ 包装函数 → 统一错误处理

FastMCP 将你的函数包装进一个统一的调用链。当函数抛出异常时，FastMCP 会将其转换为 MCP 协议规范的错误响应，而不是让进程崩溃。

---

## 2. Tool 注册表（ToolManager）

内部用一个 `ToolManager` 维护所有注册的 tool：

```
FastMCP
  └── _tool_manager: ToolManager
        └── _tools: dict[str, Tool]
              ├── "get_company_info" → Tool(fn, schema, description)
              ├── "get_fundamentals" → Tool(fn, schema, description)
              └── "get_price_history" → Tool(fn, schema, description)
```

当 MCP 客户端发送 `tools/list` 请求时，`ToolManager` 遍历这个字典返回所有已注册 Tool 的元信息。

---

## 3. 调用链路

```
Claude Code CLI
    │  发送 tools/call { name: "get_company_info", arguments: { ts_code: "600519.SH" } }
    ▼
FastMCP (stdio transport)
    │  从 ToolManager 查找 "get_company_info"
    │  将 arguments dict 按类型注解转换为函数参数
    ▼
你的函数 get_company_info(ts_code="600519.SH")
    │  返回 JSON 字符串
    ▼
FastMCP 包装为 MCP Content 响应
    │  { "content": [{ "type": "text", "text": "..." }] }
    ▼
Claude Code CLI 收到结果
```

---

## 4. 同步 vs 异步

FastMCP 同时支持同步和异步函数：

```python
@mcp.tool()
def sync_tool(x: str) -> str:        # 同步，FastMCP 在线程池中执行
    return x

@mcp.tool()
async def async_tool(x: str) -> str:  # 异步，直接在 event loop 中 await
    return x
```

同步函数由 `anyio` 的线程池（`run_sync_in_worker_thread`）执行，避免阻塞 asyncio event loop。
