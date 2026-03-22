"""TushareProvider 集成测试（需要有效 token，CI 中默认跳过）。

运行方式：
    TUSHARE_TOKEN=<your_token> uv run pytest tests/data/test_tushare_provider_integration.py -m integration
"""

import os

import pytest

from buffett_munger_agent.data.models import DataFetchError
from buffett_munger_agent.data.providers.tushare import TushareProvider

pytestmark = pytest.mark.integration

TOKEN = os.environ.get("TUSHARE_TOKEN", "")


@pytest.fixture(scope="module")
def provider():
    if not TOKEN:
        pytest.skip("未设置 TUSHARE_TOKEN 环境变量，跳过集成测试")
    return TushareProvider(token=TOKEN)


class TestGetFundamentalsIntegration:
    def test_fetch_maotai_fundamentals(self, provider):
        result = provider.get_fundamentals("600519.SH")
        assert result.ts_code == "600519.SH"
        # 茅台 PE 应在合理范围内（> 0）
        if result.pe is not None:
            assert result.pe > 0

    def test_invalid_code_raises_data_fetch_error(self, provider):
        with pytest.raises(DataFetchError):
            provider.get_fundamentals("999999.XX")


class TestGetPriceHistoryIntegration:
    def test_fetch_daily_bars(self, provider):
        bars = provider.get_price_history("600519.SH", "20240101", "20240131", "D")
        assert isinstance(bars, list)
        if bars:
            bar = bars[0]
            assert bar.ts_code == "600519.SH"
            assert bar.close > 0
            assert bar.volume > 0

    def test_date_before_listing_returns_empty(self, provider):
        # 茅台上市日期 2001-08-27，查询更早的数据应返回空列表
        bars = provider.get_price_history("600519.SH", "19900101", "19901231", "D")
        assert bars == []

    def test_weekly_freq(self, provider):
        bars = provider.get_price_history("600519.SH", "20240101", "20240331", "W")
        assert isinstance(bars, list)

    def test_monthly_freq(self, provider):
        bars = provider.get_price_history("600519.SH", "20230101", "20231231", "M")
        assert isinstance(bars, list)


class TestGetCompanyInfoIntegration:
    def test_fetch_maotai_info(self, provider):
        info = provider.get_company_info("600519.SH")
        assert info.ts_code == "600519.SH"
        assert "茅台" in info.name

    def test_shenzhen_stock(self, provider):
        info = provider.get_company_info("000001.SZ")
        assert info.ts_code == "000001.SZ"
        assert info.exchange is not None

    def test_invalid_code_raises_data_fetch_error(self, provider):
        with pytest.raises(DataFetchError):
            provider.get_company_info("999999.XX")


class TestGetStockDailyIndicatorsIntegration:
    def test_fetch_with_date_range(self, provider):
        result = provider.get_stock_daily_indicators("600519.SH", "20240101", "20240131")
        assert isinstance(result, list)
        if result:
            ind = result[0]
            assert ind.ts_code == "600519.SH"
            assert ind.trade_date >= "20240101"
            assert ind.trade_date <= "20240131"
            # 按日期升序
            dates = [r.trade_date for r in result]
            assert dates == sorted(dates)

    def test_fetch_without_date_returns_latest(self, provider):
        result = provider.get_stock_daily_indicators("600519.SH")
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].ts_code == "600519.SH"

    def test_invalid_code_raises_data_fetch_error(self, provider):
        with pytest.raises(DataFetchError):
            provider.get_stock_daily_indicators("999999.XX")

    def test_optional_fields_may_be_none(self, provider):
        result = provider.get_stock_daily_indicators("600519.SH", "20240101", "20240131")
        if result:
            ind = result[0]
            # pe_ttm 可能为 None，不应抛出异常
            assert isinstance(ind.pe_ttm, (float, type(None)))


class TestGetMarketDailyIndicatorsIntegration:
    def test_fetch_trade_date(self, provider):
        result = provider.get_market_daily_indicators("20240115")
        assert isinstance(result, list)
        # 正常交易日应有大量股票
        assert len(result) > 100
        for ind in result[:5]:
            assert ind.trade_date == "20240115"
            assert ind.ts_code != ""

    def test_non_trade_date_returns_empty(self, provider):
        # 元旦非交易日
        result = provider.get_market_daily_indicators("20240101")
        assert result == []
