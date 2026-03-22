from __future__ import annotations

from buffett_munger_agent.data.models import Adjust, CompanyInfo, Freq, PriceBar, StockFundamentals
from buffett_munger_agent.data.providers.tushare import TushareProvider


class StockFetcher:
    """对外统一的股票数据获取入口，当前使用 TushareProvider 获取 A 股数据。"""

    def __init__(self, tushare_token: str) -> None:
        self._provider = TushareProvider(token=tushare_token)

    def get_fundamentals(self, ts_code: str) -> StockFundamentals:
        """获取股票基本面财务数据。

        Args:
            ts_code: Tushare 格式股票代码，如 "600519.SH"
        """
        return self._provider.get_fundamentals(ts_code)

    def get_price_history(
        self,
        ts_code: str,
        start_date: str,
        end_date: str,
        freq: Freq = "D",
        adjust: Adjust = "",
    ) -> list[PriceBar]:
        """获取股票历史价格数据（OHLCV）。

        Args:
            ts_code: Tushare 格式股票代码
            start_date: 开始日期，格式 "YYYYMMDD"
            end_date: 结束日期，格式 "YYYYMMDD"
            freq: 时间粒度，"D" 日线 / "W" 周线 / "M" 月线
            adjust: 复权方式，"" 不复权（默认）/ "qfq" 前复权 / "hfq" 后复权
        """
        return self._provider.get_price_history(ts_code, start_date, end_date, freq, adjust)

    def get_company_info(self, ts_code: str) -> CompanyInfo:
        """获取公司基础信息。

        Args:
            ts_code: Tushare 格式股票代码，如 "600519.SH"
        """
        return self._provider.get_company_info(ts_code)
