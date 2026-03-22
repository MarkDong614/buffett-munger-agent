from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel

type Freq = Literal["D", "W", "M"]
type Adjust = Literal["hfq", "qfq", ""]


class DataFetchError(Exception):
    """数据获取失败时抛出，包含可读的错误信息。"""


class StockFundamentals(BaseModel):
    """股票基本面财务数据。"""

    ts_code: str
    # 估值指标
    pe: Optional[float] = None
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    ps: Optional[float] = None
    ps_ttm: Optional[float] = None
    # 利润表
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    # 资产负债表
    total_assets: Optional[float] = None
    total_liab: Optional[float] = None
    total_equity: Optional[float] = None
    # 现金流量表
    free_cash_flow: Optional[float] = None
    # 盈利能力
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    # 每股指标
    eps: Optional[float] = None
    bps: Optional[float] = None
    # 市值
    total_mv: Optional[float] = None
    circ_mv: Optional[float] = None
    # 数据日期
    trade_date: Optional[str] = None
    end_date: Optional[str] = None


class PriceBar(BaseModel):
    """单根 K 线（OHLCV）。"""

    ts_code: str
    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: Optional[float] = None


class CompanyInfo(BaseModel):
    """公司基础信息。

    字段来源：
    - stock_basic：symbol、name、fullname、area、industry、market、exchange、
                   curr_type、list_status、list_date、delist_date、is_hs、
                   act_name、act_ent_type
    - stock_company：description（introduction / main_business）
    - daily_basic：market_cap（total_mv，单位：万元）
    """

    ts_code: str
    symbol: Optional[str] = None        # 6 位股票代码（不含交易所后缀）
    name: str                            # 股票简称
    fullname: Optional[str] = None      # 股票全称
    area: Optional[str] = None          # 地域（省份/城市）
    industry: Optional[str] = None      # 所属行业
    sector: Optional[str] = None        # 行业板块（stock_basic 无直接字段，保留扩展）
    market: Optional[str] = None        # 市场类型（主板/创业板/科创板/北交所等）
    exchange: Optional[str] = None      # 交易所代码（SSE / SZSE / BSE）
    curr_type: Optional[str] = None     # 交易货币
    list_status: Optional[str] = None   # 上市状态（L 上市 / D 退市 / P 暂停）
    list_date: Optional[str] = None     # 上市日期（YYYYMMDD）
    delist_date: Optional[str] = None   # 退市日期（YYYYMMDD）
    is_hs: Optional[str] = None         # 沪深港通标的（N / H / S）
    act_name: Optional[str] = None      # 实控人名称
    act_ent_type: Optional[str] = None  # 实控人企业性质
    market_cap: Optional[float] = None  # 总市值（万元，来自 daily_basic）
    description: Optional[str] = None   # 公司介绍（来自 stock_company）
