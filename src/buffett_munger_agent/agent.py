"""Agent 模块：使用阿里千问（Qwen）模型驱动价值投资分析 Agent。

通过 DashScope OpenAI 兼容端点调用千问模型，将 StockFetcher 的数据能力
暴露为 OpenAI function calling 工具，自主完成 A 股价值投资分析。

运行模式：
- 交互式（默认）：持续对话，跨轮次保留历史上下文
- 单次分析：通过 query 参数传入，执行后打印结果并退出

所需环境变量：
- DASHSCOPE_API_KEY：阿里云 DashScope API 密钥（必须）
- TUSHARE_TOKEN：Tushare 数据接口密钥（必须）
- QWEN_MODEL：千问模型名称（可选，默认 qwen-max）
"""

from __future__ import annotations

import json
import os
import sys

from openai import OpenAI

from buffett_munger_agent.data.fetcher import StockFetcher
from buffett_munger_agent.data.models import DataFetchError

# ── 常量 ──────────────────────────────────────────────────────────────────────

QWEN_MODEL: str = os.environ.get("QWEN_MODEL", "qwen-max")
DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_TOKENS: int = 8192
MAX_TOOL_ROUNDS: int = 10  # 防止 agent 陷入无限工具调用循环

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT: str = """你是一位专注于 A 股价值投资分析的 AI 助手，运用巴菲特和查理·芒格的价值投资理念，
帮助用户分析个股的内在价值与投资吸引力。

## 分析框架

请按照以下维度对股票进行评估：

1. **护城河分析**：品牌护城河、专利技术壁垒、规模经济效应、客户转换成本、网络效应。
   评估企业的竞争优势是否持久、是否正在加固或消退。

2. **管理层质量**：ROE（净资产收益率）的长期稳定性（优秀标准：持续 > 15%）；
   净利润增长的可持续性；资本配置能力（分红政策、回购、再投资收益率）。

3. **财务健康度**：自由现金流是否充裕且稳定；资产负债率是否处于合理水平；
   毛利率水平（消费品类优秀标准：> 40%）；净利率趋势。

4. **估值安全边际**：当前 PE/PB 相对历史均值是否被低估；
   与同行业估值水平比较；内在价值是否高于当前市价（巴菲特原则：以合理价格买入优秀公司）。

## 工具使用约定

- 分析个股时，**首先**获取公司基础信息（get_company_info），了解公司背景
- **其次**获取基本面数据（get_fundamentals），评估财务质量
- 需要评估历史估值区间时，调用 get_stock_daily_indicators 查询近 1-3 年的 PE/PB 变化
- 需要横向比较行业估值时，使用 get_market_daily_indicators（建议 limit=50）
- 若数据获取失败，说明数据缺失情况，基于已有信息给出尽量完整的分析

## 分析报告格式

完成分析后，请以 Markdown 格式输出结构化报告，包含以下五个章节：

### 一、公司概述
公司名称、行业定位、主营业务、上市信息、实控人性质。

### 二、财务质量
ROE/ROA 水平与趋势、毛利率/净利率、自由现金流、负债情况。

### 三、估值分析
当前 PE/PB 水平、历史估值区间、与行业比较、安全边际判断。

### 四、投资风险
主要风险因素（行业风险、监管风险、竞争风险、财务风险等）。

### 五、综合结论
给出明确的**投资吸引力评级**（高 / 中 / 低），并说明关键假设和核心逻辑。
"""

# ── 工具定义（OpenAI function calling 格式）─────────────────────────────────

TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": (
                "获取 A 股公司基础信息，包括公司名称、所属行业、上市日期、实控人、主营业务描述等。"
                "是价值投资分析的第一步，用于了解公司业务边界和竞争地位。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ts_code": {
                        "type": "string",
                        "description": "Tushare 格式股票代码，如 '600519.SH'（贵州茅台）或 '000001.SZ'（平安银行）",
                    }
                },
                "required": ["ts_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_fundamentals",
            "description": (
                "获取股票基本面财务数据，包括 PE、PB、ROE、ROA、营业收入、净利润、"
                "自由现金流、资产负债表关键指标、毛利率、净利率等。"
                "是评估企业内在价值和财务健康度的核心数据。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ts_code": {
                        "type": "string",
                        "description": "Tushare 格式股票代码，如 '600519.SH'",
                    }
                },
                "required": ["ts_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_history",
            "description": (
                "获取股票历史价格数据（OHLCV K 线），用于分析股价走势、"
                "计算历史估值区间、判断当前价格是否具有足够的安全边际。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ts_code": {
                        "type": "string",
                        "description": "Tushare 格式股票代码",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "开始日期，格式 YYYYMMDD，如 '20220101'",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期，格式 YYYYMMDD，如 '20241231'",
                    },
                    "freq": {
                        "type": "string",
                        "enum": ["D", "W", "M"],
                        "description": "时间粒度：D 日线（默认）/ W 周线 / M 月线",
                    },
                    "adjust": {
                        "type": "string",
                        "enum": ["", "qfq", "hfq"],
                        "description": "复权方式：'' 不复权（默认）/ 'qfq' 前复权 / 'hfq' 后复权",
                    },
                },
                "required": ["ts_code", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_daily_indicators",
            "description": (
                "获取个股每日市场指标（PE、PB、换手率、总市值），可查询一段时间区间。"
                "用于分析历史估值变化趋势，判断当前估值所处的历史分位。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ts_code": {
                        "type": "string",
                        "description": "Tushare 格式股票代码",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "开始日期，格式 YYYYMMDD；不传则不限制",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期，格式 YYYYMMDD；不传则返回最近交易日数据",
                    },
                },
                "required": ["ts_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_market_daily_indicators",
            "description": (
                "获取全市场指定交易日的市场指标快照，可按 PE/PB/市值等字段排序筛选。"
                "用于横向比较行业估值水平，或寻找低估值标的。"
                "建议保持默认 limit=50，避免返回数据过多。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "trade_date": {
                        "type": "string",
                        "description": "交易日期，格式 YYYYMMDD，如 '20241231'",
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": [
                            "pe",
                            "pe_ttm",
                            "pb",
                            "ps_ttm",
                            "turnover_rate",
                            "total_mv",
                            "circ_mv",
                        ],
                        "description": "排序字段，可选；不传则不排序",
                    },
                    "ascending": {
                        "type": "boolean",
                        "description": "true 升序（默认）/ false 降序",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回条数上限，默认 50；传 null 返回全部（慎用）",
                    },
                },
                "required": ["trade_date"],
            },
        },
    },
]


# ── Agent 类 ──────────────────────────────────────────────────────────────────


class ValueInvestingAgent:
    """基于千问模型的价值投资分析 Agent。

    使用 OpenAI function calling 协议调用 StockFetcher 数据工具，
    自主完成 A 股价值投资分析并生成 Markdown 报告。
    """

    def __init__(self, fetcher: StockFetcher, api_key: str) -> None:
        """初始化 Agent。

        Args:
            fetcher: StockFetcher 实例，提供 A 股数据获取能力
            api_key: DashScope API 密钥
        """
        self._fetcher = fetcher
        self._client = OpenAI(
            api_key=api_key,
            base_url=DASHSCOPE_BASE_URL,
        )

    def _execute_tool(self, name: str, arguments: str) -> str:
        """执行工具调用，返回 JSON 字符串结果。

        Args:
            name: 工具名称
            arguments: 工具参数的 JSON 字符串

        Returns:
            工具执行结果的字符串（成功时为 JSON，失败时为错误描述）
        """
        try:
            args: dict = json.loads(arguments)
        except json.JSONDecodeError as exc:
            return f"工具参数解析失败：{exc}"

        try:
            match name:
                case "get_company_info":
                    result = self._fetcher.get_company_info(args["ts_code"])
                    return result.model_dump_json(indent=2)

                case "get_fundamentals":
                    result = self._fetcher.get_fundamentals(args["ts_code"])
                    return result.model_dump_json(indent=2)

                case "get_price_history":
                    bars = self._fetcher.get_price_history(
                        ts_code=args["ts_code"],
                        start_date=args["start_date"],
                        end_date=args["end_date"],
                        freq=args.get("freq", "D"),
                        adjust=args.get("adjust", ""),
                    )
                    return json.dumps(
                        [bar.model_dump(mode="json") for bar in bars],
                        ensure_ascii=False,
                        indent=2,
                    )

                case "get_stock_daily_indicators":
                    indicators = self._fetcher.get_stock_daily_indicators(
                        ts_code=args["ts_code"],
                        start_date=args.get("start_date"),
                        end_date=args.get("end_date"),
                    )
                    return json.dumps(
                        [ind.model_dump() for ind in indicators],
                        ensure_ascii=False,
                        indent=2,
                    )

                case "get_market_daily_indicators":
                    indicators = self._fetcher.get_market_daily_indicators(
                        args["trade_date"],
                    )
                    # 处理可选的排序和分页参数
                    sort_by: str | None = args.get("sort_by")
                    ascending: bool = args.get("ascending", True)
                    limit: int | None = args.get("limit", 50)

                    _VALID_SORT_FIELDS = {
                        "pe",
                        "pe_ttm",
                        "pb",
                        "ps_ttm",
                        "turnover_rate",
                        "total_mv",
                        "circ_mv",
                    }
                    if sort_by is not None and sort_by in _VALID_SORT_FIELDS:
                        none_items = [
                            x for x in indicators if getattr(x, sort_by) is None
                        ]
                        non_none_items = [
                            x for x in indicators if getattr(x, sort_by) is not None
                        ]
                        non_none_items.sort(
                            key=lambda x: getattr(x, sort_by),  # type: ignore[arg-type]
                            reverse=not ascending,
                        )
                        indicators = non_none_items + none_items

                    if limit is not None:
                        indicators = indicators[:limit]

                    return json.dumps(
                        [ind.model_dump() for ind in indicators],
                        ensure_ascii=False,
                        indent=2,
                    )

                case _:
                    return f"未知工具：'{name}'。可用工具：{', '.join(t['function']['name'] for t in TOOLS)}"

        except DataFetchError as exc:
            return f"数据获取失败（{name}）：{exc}"
        except KeyError as exc:
            return f"工具参数缺失（{name}）：{exc}"
        except Exception as exc:
            return f"工具执行出错（{name}）：{exc}"

    def _run_loop(self, messages: list[dict]) -> str:
        """运行 agent loop，直到模型返回最终文本或达到最大轮次。

        Args:
            messages: 对话消息列表（会被原地追加）

        Returns:
            模型生成的最终文本

        Raises:
            RuntimeError: 达到最大工具调用轮次限制
        """
        for _ in range(MAX_TOOL_ROUNDS):
            response = self._client.chat.completions.create(
                model=QWEN_MODEL,
                messages=messages,  # type: ignore[arg-type]
                tools=TOOLS,  # type: ignore[arg-type]
                max_tokens=MAX_TOKENS,
            )
            choice = response.choices[0]

            # 模型完成推理，返回最终文本
            if choice.finish_reason == "stop":
                return choice.message.content or ""

            # 模型发起工具调用
            if choice.finish_reason == "tool_calls":
                # 追加 assistant 消息（含工具调用请求）
                messages.append(choice.message.model_dump(exclude_unset=True))

                # 逐个执行工具调用，追加结果
                for tc in choice.message.tool_calls or []:
                    result = self._execute_tool(tc.function.name, tc.function.arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        }
                    )
                continue

            # 其他终止原因（length、content_filter 等）
            content = choice.message.content or ""
            return content

        raise RuntimeError(
            f"达到最大工具调用轮次限制（{MAX_TOOL_ROUNDS} 轮），分析未能完成。"
            "请尝试缩小分析范围或直接指定股票代码。"
        )

    def run_once(self, query: str) -> str:
        """执行单次分析并返回结果。

        Args:
            query: 分析指令，如 "分析贵州茅台600519.SH的投资价值"

        Returns:
            Markdown 格式的分析报告
        """
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        return self._run_loop(messages)

    def run_interactive(self) -> None:
        """以交互式 REPL 模式运行，跨轮次保留对话历史。

        输入 exit、quit 或退出 可结束会话。
        """
        print("=" * 60)
        print("巴菲特/芒格价值投资分析助手（千问驱动）")
        print(f"模型：{QWEN_MODEL}")
        print("输入 exit / quit / 退出 结束会话")
        print("=" * 60)
        print()

        conversation_messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        while True:
            try:
                user_input = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "退出"):
                print("再见！")
                break

            conversation_messages.append({"role": "user", "content": user_input})

            try:
                reply = self._run_loop(conversation_messages)
            except RuntimeError as exc:
                print(f"\n⚠️  {exc}\n")
                # 移除未完成的用户消息，避免污染历史
                conversation_messages.pop()
                continue

            conversation_messages.append({"role": "assistant", "content": reply})
            print(f"\n{reply}\n")


# ── 对外入口 ──────────────────────────────────────────────────────────────────


def run_agent(query: str | None = None) -> None:
    """以 Agent 模式运行价值投资分析。

    Args:
        query: 分析指令；为 None 时进入交互式模式。

    Environment:
        DASHSCOPE_API_KEY: 阿里云 DashScope API 密钥（必须）
        TUSHARE_TOKEN: Tushare 数据接口密钥（必须）
        QWEN_MODEL: 千问模型名称（可选，默认 qwen-max）
    """
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print(
            "错误：未找到环境变量 DASHSCOPE_API_KEY。\n"
            "请先设置：export DASHSCOPE_API_KEY=<your_key>",
            file=sys.stderr,
        )
        sys.exit(1)

    tushare_token = os.environ.get("TUSHARE_TOKEN")
    if not tushare_token:
        print(
            "错误：未找到环境变量 TUSHARE_TOKEN。\n"
            "请先设置：export TUSHARE_TOKEN=<your_token>",
            file=sys.stderr,
        )
        sys.exit(1)

    fetcher = StockFetcher(tushare_token=tushare_token)
    agent = ValueInvestingAgent(fetcher=fetcher, api_key=api_key)

    if query is not None:
        result = agent.run_once(query)
        print(result)
    else:
        agent.run_interactive()
