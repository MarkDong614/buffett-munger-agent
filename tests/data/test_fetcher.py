"""StockFetcher 单元测试（Mock TushareProvider）。"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from buffett_munger_agent.data import (
    CompanyInfo,
    DataFetchError,
    PriceBar,
    StockFetcher,
    StockFundamentals,
)


@pytest.fixture
def mock_provider():
    return MagicMock()


@pytest.fixture
def fetcher(mock_provider):
    with patch(
        "buffett_munger_agent.data.fetcher.TushareProvider",
        return_value=mock_provider,
    ):
        yield StockFetcher(tushare_token="fake-token"), mock_provider


class TestStockFetcherInit:
    def test_creates_tushare_provider_with_token(self):
        with patch("buffett_munger_agent.data.fetcher.TushareProvider") as mock_cls:
            StockFetcher(tushare_token="my-token")
            mock_cls.assert_called_once_with(token="my-token")


class TestGetFundamentals:
    def test_delegates_to_provider(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        expected = StockFundamentals(ts_code="600519.SH", pe=30.0, pb=10.0)
        mock_provider.get_fundamentals.return_value = expected

        result = stock_fetcher.get_fundamentals("600519.SH")

        mock_provider.get_fundamentals.assert_called_once_with("600519.SH")
        assert result == expected

    def test_propagates_data_fetch_error(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_fundamentals.side_effect = DataFetchError("无效代码")

        with pytest.raises(DataFetchError, match="无效代码"):
            stock_fetcher.get_fundamentals("INVALID")


class TestGetPriceHistory:
    def test_delegates_to_provider(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        expected = [
            PriceBar(
                ts_code="600519.SH",
                trade_date=date(2024, 1, 2),
                open=1800.0,
                high=1850.0,
                low=1790.0,
                close=1830.0,
                volume=10000.0,
            )
        ]
        mock_provider.get_price_history.return_value = expected

        result = stock_fetcher.get_price_history(
            "600519.SH", "20240101", "20240131", "D"
        )

        mock_provider.get_price_history.assert_called_once_with(
            "600519.SH", "20240101", "20240131", "D", ""
        )
        assert result == expected

    def test_default_adjust_is_no_adjustment(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_price_history.return_value = []

        stock_fetcher.get_price_history("600519.SH", "20240101", "20240131")

        _, _, _, _, adjust = mock_provider.get_price_history.call_args.args
        assert adjust == ""

    def test_passes_qfq_adjust_to_provider(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_price_history.return_value = []

        stock_fetcher.get_price_history(
            "600519.SH", "20240101", "20240131", adjust="qfq"
        )

        mock_provider.get_price_history.assert_called_once_with(
            "600519.SH", "20240101", "20240131", "D", "qfq"
        )

    def test_passes_hfq_adjust_to_provider(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_price_history.return_value = []

        stock_fetcher.get_price_history(
            "600519.SH", "20240101", "20240131", adjust="hfq"
        )

        mock_provider.get_price_history.assert_called_once_with(
            "600519.SH", "20240101", "20240131", "D", "hfq"
        )

    def test_returns_empty_list_when_no_data(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_price_history.return_value = []

        result = stock_fetcher.get_price_history("600519.SH", "19900101", "19900131")
        assert result == []

    def test_propagates_data_fetch_error(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_price_history.side_effect = DataFetchError("网络错误")

        with pytest.raises(DataFetchError):
            stock_fetcher.get_price_history("600519.SH", "20240101", "20240131")


class TestGetCompanyInfo:
    def test_delegates_to_provider(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        expected = CompanyInfo(ts_code="600519.SH", name="贵州茅台", exchange="SSE")
        mock_provider.get_company_info.return_value = expected

        result = stock_fetcher.get_company_info("600519.SH")

        mock_provider.get_company_info.assert_called_once_with("600519.SH")
        assert result == expected

    def test_propagates_data_fetch_error(self, fetcher):
        stock_fetcher, mock_provider = fetcher
        mock_provider.get_company_info.side_effect = DataFetchError("无效代码")

        with pytest.raises(DataFetchError):
            stock_fetcher.get_company_info("INVALID")
