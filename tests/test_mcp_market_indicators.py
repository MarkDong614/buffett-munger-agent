"""get_market_daily_indicators MCP Tool 单元测试。"""

import json
from unittest.mock import MagicMock, patch

import pytest

from buffett_munger_agent.data.models import DailyIndicators
from buffett_munger_agent.mcp_server import get_market_daily_indicators


def _make_indicator(ts_code: str, pe: float | None, turnover_rate: float | None = None) -> DailyIndicators:
    return DailyIndicators(ts_code=ts_code, trade_date="20240115", pe=pe, turnover_rate=turnover_rate)


@pytest.fixture
def mock_fetcher():
    fetcher = MagicMock()
    # 构造 60 条数据（超过默认 limit=50）
    fetcher.get_market_daily_indicators.return_value = [
        _make_indicator(f"{i:06d}.SH", pe=float(i) if i % 5 != 0 else None)
        for i in range(1, 61)
    ]
    return fetcher


@pytest.fixture(autouse=True)
def patch_fetcher(mock_fetcher):
    with patch("buffett_munger_agent.mcp_server._fetcher", mock_fetcher):
        yield


class TestDefaultLimit:
    def test_default_limit_50(self, mock_fetcher):
        result = json.loads(get_market_daily_indicators("20240115"))
        assert len(result) == 50

    def test_limit_none_returns_all(self, mock_fetcher):
        result = json.loads(get_market_daily_indicators("20240115", limit=None))
        assert len(result) == 60

    def test_limit_custom(self, mock_fetcher):
        result = json.loads(get_market_daily_indicators("20240115", limit=10))
        assert len(result) == 10

    def test_limit_zero_returns_empty(self, mock_fetcher):
        result = json.loads(get_market_daily_indicators("20240115", limit=0))
        assert result == []

    def test_limit_negative_raises_value_error(self, mock_fetcher):
        with pytest.raises(ValueError, match="limit 不能为负数"):
            get_market_daily_indicators("20240115", limit=-1)

    @pytest.mark.parametrize(
        ("invalid_limit", "error_msg"),
        [(-1, "limit 不能为负数"), ("10", "limit 必须为非负整数或 None")],
    )
    def test_invalid_limit_does_not_call_fetcher(self, mock_fetcher, invalid_limit, error_msg):
        with pytest.raises(ValueError, match=error_msg):
            get_market_daily_indicators("20240115", limit=invalid_limit)  # type: ignore[arg-type]
        mock_fetcher.get_market_daily_indicators.assert_not_called()


class TestSortByPe:
    def test_sort_pe_ascending(self, mock_fetcher):
        result = json.loads(get_market_daily_indicators("20240115", sort_by="pe", ascending=True, limit=None))
        pe_values = [r["pe"] for r in result if r["pe"] is not None]
        assert pe_values == sorted(pe_values)

    def test_sort_pe_descending(self, mock_fetcher):
        result = json.loads(get_market_daily_indicators("20240115", sort_by="pe", ascending=False, limit=None))
        pe_values = [r["pe"] for r in result if r["pe"] is not None]
        assert pe_values == sorted(pe_values, reverse=True)


class TestSortByTurnoverRate:
    @pytest.fixture(autouse=True)
    def patch_with_turnover_data(self, mock_fetcher):
        mock_fetcher.get_market_daily_indicators.return_value = [
            _make_indicator("A", pe=10.0, turnover_rate=5.0),
            _make_indicator("B", pe=20.0, turnover_rate=1.0),
            _make_indicator("C", pe=5.0, turnover_rate=9.0),
        ]

    def test_sort_turnover_descending(self):
        result = json.loads(
            get_market_daily_indicators("20240115", sort_by="turnover_rate", ascending=False, limit=None)
        )
        rates = [r["turnover_rate"] for r in result]
        assert rates == [9.0, 5.0, 1.0]


class TestNoneValuesSortedToEnd:
    @pytest.fixture(autouse=True)
    def patch_with_none_data(self, mock_fetcher):
        mock_fetcher.get_market_daily_indicators.return_value = [
            _make_indicator("A", pe=None),
            _make_indicator("B", pe=5.0),
            _make_indicator("C", pe=None),
            _make_indicator("D", pe=15.0),
        ]

    def test_none_at_end_ascending(self):
        result = json.loads(
            get_market_daily_indicators("20240115", sort_by="pe", ascending=True, limit=None)
        )
        pe_values = [r["pe"] for r in result]
        # None 值在末尾
        assert pe_values == [5.0, 15.0, None, None]

    def test_none_at_end_descending(self):
        result = json.loads(
            get_market_daily_indicators("20240115", sort_by="pe", ascending=False, limit=None)
        )
        pe_values = [r["pe"] for r in result]
        assert pe_values == [15.0, 5.0, None, None]


class TestInvalidSortBy:
    def test_invalid_field_raises_value_error(self):
        with pytest.raises(ValueError, match="sort_by 字段无效"):
            get_market_daily_indicators("20240115", sort_by="invalid_field")

    def test_error_message_lists_valid_fields(self):
        with pytest.raises(ValueError, match="pe"):
            get_market_daily_indicators("20240115", sort_by="bad")
