"""MCP Server 模块：将股票数据获取能力暴露为 MCP Tools，供 Claude Code CLI 调用。"""

from __future__ import annotations

import json
import os
import sys

from mcp.server.fastmcp import FastMCP

from buffett_munger_agent.data.fetcher import StockFetcher
from buffett_munger_agent.data.models import DataFetchError

# MCP Server 实例
mcp = FastMCP("buffett-munger-agent")

# StockFetcher 延迟初始化（run_mcp_server 启动时注入）
_fetcher: StockFetcher | None = None


def _get_fetcher() -> StockFetcher:
    if _fetcher is None:
        raise RuntimeError("StockFetcher 尚未初始化，请通过 run_mcp_server() 启动 Server。")
    return _fetcher


@mcp.tool()
def get_company_info(ts_code: str) -> str:
    """获取 A 股公司基础信息。

    Args:
        ts_code: Tushare 格式股票代码，如 "600519.SH"（贵州茅台）或 "000001.SZ"（平安银行）。

    Returns:
        包含公司名称、行业、市值、交易所等字段的 JSON 字符串。
    """
    try:
        info = _get_fetcher().get_company_info(ts_code)
        return info.model_dump_json(indent=2)
    except DataFetchError as exc:
        raise ValueError(f"数据获取失败：{exc}") from exc
    except Exception as exc:
        raise ValueError(f"未知错误：{exc}") from exc


@mcp.tool()
def get_fundamentals(ts_code: str) -> str:
    """获取 A 股股票基本面财务数据（PE、PB、ROE、营收、净利润等）。

    Args:
        ts_code: Tushare 格式股票代码，如 "600519.SH"。

    Returns:
        包含估值指标、利润表、资产负债表、现金流量表关键字段的 JSON 字符串，缺失字段以 null 表示。
    """
    try:
        fundamentals = _get_fetcher().get_fundamentals(ts_code)
        return fundamentals.model_dump_json(indent=2)
    except DataFetchError as exc:
        raise ValueError(f"数据获取失败：{exc}") from exc
    except Exception as exc:
        raise ValueError(f"未知错误：{exc}") from exc


@mcp.tool()
def get_price_history(
    ts_code: str,
    start_date: str,
    end_date: str,
    freq: str = "D",
) -> str:
    """获取 A 股历史价格数据（后复权 OHLCV）。

    Args:
        ts_code: Tushare 格式股票代码，如 "600519.SH"。
        start_date: 开始日期，格式 "YYYYMMDD"，如 "20240101"。
        end_date: 结束日期，格式 "YYYYMMDD"，如 "20241231"。
        freq: 时间粒度，"D" 日线（默认）/ "W" 周线 / "M" 月线。

    Returns:
        按日期升序排列的 K 线数据 JSON 数组，每条记录包含 date、open、high、low、close、volume。
        时间范围内无数据时返回空数组 []。
    """
    try:
        bars = _get_fetcher().get_price_history(ts_code, start_date, end_date, freq)
        return json.dumps(
            [bar.model_dump(mode="json") for bar in bars],
            ensure_ascii=False,
            indent=2,
        )
    except DataFetchError as exc:
        raise ValueError(f"数据获取失败：{exc}") from exc
    except Exception as exc:
        raise ValueError(f"未知错误：{exc}") from exc


def run_mcp_server() -> None:
    """以 stdio transport 启动 MCP Server。

    从环境变量 TUSHARE_TOKEN 读取 API token；若未设置则报错退出。
    """
    global _fetcher  # noqa: PLW0603

    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        print(
            "错误：未找到环境变量 TUSHARE_TOKEN。\n"
            "请先设置：export TUSHARE_TOKEN=<your_token>",
            file=sys.stderr,
        )
        sys.exit(1)

    _fetcher = StockFetcher(tushare_token=token)
    mcp.run(transport="stdio")
