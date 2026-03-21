from __future__ import annotations

from typing import Protocol

from buffett_munger_agent.data.models import CompanyInfo, PriceBar, StockFundamentals


class DataProvider(Protocol):
    """数据提供者接口，定义获取股票数据的标准方法签名。"""

    def get_fundamentals(self, ts_code: str) -> StockFundamentals:
        """获取股票基本面财务数据。

        Args:
            ts_code: Tushare 格式股票代码，如 "600519.SH"

        Raises:
            DataFetchError: 代码无效、鉴权失败或网络错误时
        """
        ...

    def get_price_history(
        self,
        ts_code: str,
        start_date: str,
        end_date: str,
        freq: str = "D",
    ) -> list[PriceBar]:
        """获取股票历史价格数据（后复权 OHLCV）。

        Args:
            ts_code: Tushare 格式股票代码
            start_date: 开始日期，格式 "YYYYMMDD"
            end_date: 结束日期，格式 "YYYYMMDD"
            freq: 时间粒度，"D" 日线 / "W" 周线 / "M" 月线

        Raises:
            DataFetchError: 代码无效、鉴权失败或网络错误时
        """
        ...

    def get_company_info(self, ts_code: str) -> CompanyInfo:
        """获取公司基础信息。

        Args:
            ts_code: Tushare 格式股票代码，如 "600519.SH"

        Raises:
            DataFetchError: 代码无效、鉴权失败或网络错误时
        """
        ...
