"""数据模型单元测试：验证 Optional 字段和异常类行为。"""

import pytest

from buffett_munger_agent.data.models import (
    CompanyInfo,
    DataFetchError,
    PriceBar,
    StockFundamentals,
)


class TestStockFundamentals:
    def test_required_field_only(self):
        f = StockFundamentals(ts_code="600519.SH")
        assert f.ts_code == "600519.SH"

    def test_optional_fields_default_to_none(self):
        f = StockFundamentals(ts_code="600519.SH")
        assert f.pe is None
        assert f.pb is None
        assert f.roe is None
        assert f.free_cash_flow is None
        assert f.revenue is None
        assert f.net_income is None

    def test_partial_data_does_not_raise(self):
        # 只提供部分字段，其余为 None，不抛出异常
        f = StockFundamentals(ts_code="000001.SZ", pe=15.0, roe=12.5)
        assert f.pe == 15.0
        assert f.roe == 12.5
        assert f.pb is None
        assert f.free_cash_flow is None


class TestPriceBar:
    def test_required_fields(self):
        from datetime import date

        bar = PriceBar(
            ts_code="600519.SH",
            trade_date=date(2024, 1, 2),
            open=1800.0,
            high=1850.0,
            low=1790.0,
            close=1830.0,
            volume=10000.0,
        )
        assert bar.close == 1830.0
        assert bar.amount is None  # Optional 字段默认 None


class TestCompanyInfo:
    def test_optional_description_defaults_to_none(self):
        info = CompanyInfo(ts_code="600519.SH", name="贵州茅台")
        assert info.description is None

    def test_curr_type_defaults_to_none(self):
        # curr_type 来自 stock_basic，未传入时为 None
        info = CompanyInfo(ts_code="600519.SH", name="贵州茅台")
        assert info.curr_type is None

    def test_partial_data_does_not_raise(self):
        info = CompanyInfo(ts_code="000001.SZ", name="平安银行", industry="银行")
        assert info.sector is None
        assert info.market_cap is None


class TestDataFetchError:
    def test_is_exception(self):
        err = DataFetchError("出错了")
        assert isinstance(err, Exception)
        assert str(err) == "出错了"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(DataFetchError, match="无效代码"):
            raise DataFetchError("无效代码")
