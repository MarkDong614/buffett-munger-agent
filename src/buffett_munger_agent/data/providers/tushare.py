from __future__ import annotations

import math
from datetime import date

import tushare as ts

from buffett_munger_agent.data.models import (
    Adjust,
    CompanyInfo,
    DataFetchError,
    Freq,
    PriceBar,
    StockFundamentals,
)


def _to_float(series, field: str) -> float | None:
    """从 pandas Series 安全取浮点值，缺失或 NaN 返回 None。"""
    try:
        val = series[field]
        if val is None:
            return None
        f = float(val)
        return None if math.isnan(f) else f
    except (KeyError, TypeError, ValueError):
        return None


def _to_str(series, field: str) -> str | None:
    """从 pandas Series 安全取字符串，缺失或空值返回 None。"""
    try:
        val = series[field]
        return str(val) if val is not None and str(val).strip() else None
    except (KeyError, TypeError):
        return None


class TushareProvider:
    """基于 Tushare Pro API 的 A 股数据提供者。"""

    def __init__(self, token: str) -> None:
        ts.set_token(token)
        self._pro = ts.pro_api()

    def get_fundamentals(self, ts_code: str) -> StockFundamentals:
        """获取股票基本面财务数据。

        数据来源：
        - daily_basic：每日估值指标（PE、PB、PS、市值）
        - income：利润表（营业总收入、净利润）
        - balancesheet：资产负债表（总资产、总负债、股东权益）
        - cashflow：现金流量表（企业自由现金流）
        - fina_indicator：财务指标（ROE、ROA、毛利率、净利率、EPS、BPS）
        """
        try:
            # --- 估值及市值指标（最近一个交易日）---
            daily_df = self._pro.daily_basic(ts_code=ts_code, limit=1)
            if daily_df is None or daily_df.empty:
                raise DataFetchError(f"未找到股票 {ts_code} 的行情数据，请确认代码是否正确")
            daily = daily_df.iloc[0]

            # --- 利润表（合并报表，最近一期）---
            # report_type='1' 表示合并报表，取数据默认按 end_date 倒序
            income_df = self._pro.income(ts_code=ts_code, report_type="1")
            income = income_df.iloc[0] if income_df is not None and not income_df.empty else None

            # --- 资产负债表（合并报表，最近一期）---
            balance_df = self._pro.balancesheet(ts_code=ts_code, report_type="1")
            balance = balance_df.iloc[0] if balance_df is not None and not balance_df.empty else None

            # --- 现金流量表（合并报表，最近一期）---
            cashflow_df = self._pro.cashflow(ts_code=ts_code, report_type="1")
            cashflow = cashflow_df.iloc[0] if cashflow_df is not None and not cashflow_df.empty else None

            # --- 财务指标（最近一期）---
            fina_df = self._pro.fina_indicator(ts_code=ts_code)
            fina = fina_df.iloc[0] if fina_df is not None and not fina_df.empty else None

            return StockFundamentals(
                ts_code=ts_code,
                # 估值指标（来自 daily_basic）
                pe=_to_float(daily, "pe"),
                pe_ttm=_to_float(daily, "pe_ttm"),
                pb=_to_float(daily, "pb"),
                ps=_to_float(daily, "ps"),
                ps_ttm=_to_float(daily, "ps_ttm"),
                total_mv=_to_float(daily, "total_mv"),
                circ_mv=_to_float(daily, "circ_mv"),
                trade_date=_to_str(daily, "trade_date"),
                # 利润表（来自 income）
                # total_revenue = 营业总收入，revenue = 营业收入（不含其他业务收入）
                revenue=_to_float(income, "total_revenue"),
                # n_income_attr_p = 归属于母公司股东的净利润（价值投资分析更关注此口径）
                net_income=_to_float(income, "n_income_attr_p"),
                end_date=_to_str(income, "end_date") if income is not None else None,
                # 资产负债表（来自 balancesheet）
                total_assets=_to_float(balance, "total_assets"),
                total_liab=_to_float(balance, "total_liab"),
                # total_hldr_eqy_inc_min_int = 股东权益合计（含少数股东权益）
                total_equity=_to_float(balance, "total_hldr_eqy_inc_min_int"),
                # 现金流量表（来自 cashflow）
                free_cash_flow=_to_float(cashflow, "free_cashflow"),
                # 财务指标（来自 fina_indicator）
                roe=_to_float(fina, "roe"),
                roa=_to_float(fina, "roa"),
                gross_margin=_to_float(fina, "grossprofit_margin"),
                net_margin=_to_float(fina, "netprofit_margin"),
                eps=_to_float(fina, "eps"),
                bps=_to_float(fina, "bps"),
            )
        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(f"获取 {ts_code} 基本面数据失败：{e}") from e

    def get_price_history(
        self,
        ts_code: str,
        start_date: str,
        end_date: str,
        freq: Freq = "D",
        adjust: Adjust = "",
    ) -> list[PriceBar]:
        """获取股票历史价格数据（OHLCV）。

        通过 ts.pro_bar() 接口获取。vol 单位为手，amount 单位为千元。
        adjust: "" 不复权 / "qfq" 前复权 / "hfq" 后复权。
        """
        try:
            df = ts.pro_bar(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                freq=freq,
                adj=adjust or None,
                api=self._pro,
            )
            if df is None or df.empty:
                return []

            df = df.sort_values("trade_date", ascending=True)
            bars = []
            for _, row in df.iterrows():
                trade_date_str = str(row["trade_date"])
                trade_date = date(
                    int(trade_date_str[:4]),
                    int(trade_date_str[4:6]),
                    int(trade_date_str[6:8]),
                )
                amount = _to_float(row, "amount")
                bars.append(
                    PriceBar(
                        ts_code=ts_code,
                        trade_date=trade_date,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["vol"]),
                        amount=amount,
                    )
                )
            return bars
        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(f"获取 {ts_code} 历史价格数据失败：{e}") from e

    def get_company_info(self, ts_code: str) -> CompanyInfo:
        """获取公司基础信息。

        数据来源：
        - stock_basic（doc_id=25）：symbol、name、fullname、area、industry、market、
          exchange、curr_type、list_status、list_date、delist_date、is_hs、
          act_name、act_ent_type
        - stock_company（doc_id=112）：公司介绍（introduction）/ 主营业务（main_business）
        - daily_basic：最新总市值（total_mv，万元）
        """
        try:
            # --- 基础信息（stock_basic）---
            basic_df = self._pro.stock_basic(
                ts_code=ts_code,
                fields=(
                    "ts_code,symbol,name,fullname,area,industry,market,"
                    "exchange,curr_type,list_status,list_date,delist_date,"
                    "is_hs,act_name,act_ent_type"
                ),
            )
            if basic_df is None or basic_df.empty:
                raise DataFetchError(f"未找到股票 {ts_code} 的基础信息，请确认代码是否正确")
            basic = basic_df.iloc[0]

            # --- 公司详情（stock_company）：公司介绍 ---
            description = None
            try:
                company_df = self._pro.stock_company(ts_code=ts_code)
                if company_df is not None and not company_df.empty:
                    company = company_df.iloc[0]
                    intro = _to_str(company, "introduction")
                    main_biz = _to_str(company, "main_business")
                    description = intro or main_biz
            except Exception:
                pass

            # --- 最新市值（daily_basic）---
            market_cap = None
            try:
                mv_df = self._pro.daily_basic(ts_code=ts_code, limit=1, fields="ts_code,total_mv")
                if mv_df is not None and not mv_df.empty:
                    market_cap = _to_float(mv_df.iloc[0], "total_mv")
            except Exception:
                pass

            # name 优先使用 fullname（股票全称），无则退回简称
            fullname = _to_str(basic, "fullname")
            name = fullname or str(basic["name"])

            return CompanyInfo(
                ts_code=ts_code,
                symbol=_to_str(basic, "symbol"),
                name=name,
                fullname=fullname,
                area=_to_str(basic, "area"),
                industry=_to_str(basic, "industry"),
                market=_to_str(basic, "market"),
                exchange=_to_str(basic, "exchange"),
                curr_type=_to_str(basic, "curr_type"),
                list_status=_to_str(basic, "list_status"),
                list_date=_to_str(basic, "list_date"),
                delist_date=_to_str(basic, "delist_date"),
                is_hs=_to_str(basic, "is_hs"),
                act_name=_to_str(basic, "act_name"),
                act_ent_type=_to_str(basic, "act_ent_type"),
                market_cap=market_cap,
                description=description,
            )
        except DataFetchError:
            raise
        except Exception as e:
            raise DataFetchError(f"获取 {ts_code} 公司信息失败：{e}") from e
