"""ValueInvestingAgent 单元测试（Mock StockFetcher 和 OpenAI 客户端）。"""

from __future__ import annotations

import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from buffett_munger_agent.agent import SYSTEM_PROMPT, TOOLS, ValueInvestingAgent, run_agent
from buffett_munger_agent.data.models import (
    CompanyInfo,
    DataFetchError,
    DailyIndicators,
    PriceBar,
    StockFundamentals,
)


# ── 测试夹具 ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_fetcher():
    """返回 Mock 的 StockFetcher 实例。"""
    return MagicMock()


@pytest.fixture
def agent(mock_fetcher):
    """返回注入 Mock fetcher 的 ValueInvestingAgent 实例（不调用真实 OpenAI）。"""
    with patch("buffett_munger_agent.agent.OpenAI"):
        return ValueInvestingAgent(fetcher=mock_fetcher, api_key="fake-api-key")


# ── 工具定义完整性测试 ────────────────────────────────────────────────────────


class TestToolsDefinition:
    def test_contains_five_tools(self):
        """TOOLS 列表应包含恰好 5 个工具。"""
        assert len(TOOLS) == 5

    def test_all_tool_names_present(self):
        """TOOLS 应包含所有 5 个预期工具名。"""
        names = {t["function"]["name"] for t in TOOLS}
        assert names == {
            "get_company_info",
            "get_fundamentals",
            "get_price_history",
            "get_stock_daily_indicators",
            "get_market_daily_indicators",
        }

    def test_each_tool_has_required_fields(self):
        """每个工具都应有 type、function.name、function.description、function.parameters 字段。"""
        for tool in TOOLS:
            assert tool["type"] == "function"
            fn = tool["function"]
            assert "name" in fn
            assert "description" in fn and fn["description"]
            assert "parameters" in fn
            assert "required" in fn["parameters"]

    def test_get_price_history_has_optional_freq_and_adjust(self):
        """get_price_history 工具应包含 freq 和 adjust 可选参数。"""
        tool = next(t for t in TOOLS if t["function"]["name"] == "get_price_history")
        props = tool["function"]["parameters"]["properties"]
        assert "freq" in props
        assert "adjust" in props
        # freq 和 adjust 不在 required 中（可选）
        assert "freq" not in tool["function"]["parameters"]["required"]
        assert "adjust" not in tool["function"]["parameters"]["required"]

    def test_get_market_daily_indicators_has_optional_params(self):
        """get_market_daily_indicators 工具应包含 sort_by、ascending、limit 可选参数。"""
        tool = next(
            t for t in TOOLS if t["function"]["name"] == "get_market_daily_indicators"
        )
        props = tool["function"]["parameters"]["properties"]
        assert "sort_by" in props
        assert "ascending" in props
        assert "limit" in props


# ── _execute_tool 正常路径测试 ────────────────────────────────────────────────


class TestExecuteToolSuccess:
    def test_get_company_info_returns_json(self, agent, mock_fetcher):
        """get_company_info 工具应返回包含公司名称的 JSON 字符串。"""
        mock_fetcher.get_company_info.return_value = CompanyInfo(
            ts_code="600519.SH", name="贵州茅台"
        )
        result = agent._execute_tool(
            "get_company_info", json.dumps({"ts_code": "600519.SH"})
        )
        parsed = json.loads(result)
        assert parsed["name"] == "贵州茅台"
        assert parsed["ts_code"] == "600519.SH"

    def test_get_fundamentals_returns_json(self, agent, mock_fetcher):
        """get_fundamentals 工具应返回包含财务指标的 JSON 字符串。"""
        mock_fetcher.get_fundamentals.return_value = StockFundamentals(
            ts_code="600519.SH", pe=30.0, roe=0.35
        )
        result = agent._execute_tool(
            "get_fundamentals", json.dumps({"ts_code": "600519.SH"})
        )
        parsed = json.loads(result)
        assert parsed["pe"] == 30.0
        assert parsed["roe"] == 0.35

    def test_get_price_history_returns_json_array(self, agent, mock_fetcher):
        """get_price_history 工具应返回 JSON 数组。"""
        mock_fetcher.get_price_history.return_value = [
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
        args = json.dumps(
            {"ts_code": "600519.SH", "start_date": "20240101", "end_date": "20240131"}
        )
        result = agent._execute_tool("get_price_history", args)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        assert parsed[0]["close"] == 1830.0

    def test_get_price_history_passes_optional_params(self, agent, mock_fetcher):
        """get_price_history 工具应将 freq 和 adjust 正确传递给 fetcher。"""
        mock_fetcher.get_price_history.return_value = []
        args = json.dumps(
            {
                "ts_code": "600519.SH",
                "start_date": "20240101",
                "end_date": "20240131",
                "freq": "W",
                "adjust": "qfq",
            }
        )
        agent._execute_tool("get_price_history", args)
        mock_fetcher.get_price_history.assert_called_once_with(
            ts_code="600519.SH",
            start_date="20240101",
            end_date="20240131",
            freq="W",
            adjust="qfq",
        )

    def test_get_stock_daily_indicators_returns_json_array(self, agent, mock_fetcher):
        """get_stock_daily_indicators 工具应返回 JSON 数组。"""
        mock_fetcher.get_stock_daily_indicators.return_value = [
            DailyIndicators(ts_code="600519.SH", trade_date="20240102", pe=35.0)
        ]
        args = json.dumps({"ts_code": "600519.SH"})
        result = agent._execute_tool("get_stock_daily_indicators", args)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert parsed[0]["pe"] == 35.0

    def test_get_market_daily_indicators_returns_json_array(self, agent, mock_fetcher):
        """get_market_daily_indicators 工具应返回 JSON 数组。"""
        mock_fetcher.get_market_daily_indicators.return_value = [
            DailyIndicators(ts_code="600519.SH", trade_date="20240102", pe=35.0),
            DailyIndicators(ts_code="000001.SZ", trade_date="20240102", pe=8.0),
        ]
        args = json.dumps({"trade_date": "20240102"})
        result = agent._execute_tool("get_market_daily_indicators", args)
        parsed = json.loads(result)
        assert isinstance(parsed, list)


# ── _execute_tool 异常路径测试 ────────────────────────────────────────────────


class TestExecuteToolErrors:
    def test_data_fetch_error_is_captured_not_raised(self, agent, mock_fetcher):
        """DataFetchError 应被捕获并转为错误描述字符串，不抛出异常。"""
        mock_fetcher.get_fundamentals.side_effect = DataFetchError("数据接口超时")
        result = agent._execute_tool(
            "get_fundamentals", json.dumps({"ts_code": "600519.SH"})
        )
        assert isinstance(result, str)
        assert (
            "失败" in result or "DataFetchError" in result or "数据接口超时" in result
        )

    def test_unknown_tool_name_returns_error_string(self, agent):
        """未知工具名应返回包含'未知工具'的错误字符串，不抛出异常。"""
        result = agent._execute_tool("nonexistent_tool", json.dumps({}))
        assert isinstance(result, str)
        assert "未知工具" in result

    def test_invalid_json_arguments_returns_error_string(self, agent):
        """无效 JSON 参数应返回错误描述字符串，不抛出异常。"""
        result = agent._execute_tool("get_company_info", "not-valid-json")
        assert isinstance(result, str)
        assert "失败" in result or "解析" in result


# ── _run_loop 测试 ────────────────────────────────────────────────────────────


class TestRunLoop:
    def test_stops_on_finish_reason_stop(self, mock_fetcher):
        """finish_reason='stop' 时应返回模型文本，不继续调用。"""
        with patch("buffett_munger_agent.agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            # 构造 stop 响应
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].finish_reason = "stop"
            mock_response.choices[
                0
            ].message.content = "分析完成：贵州茅台具有极强护城河。"
            mock_client.chat.completions.create.return_value = mock_response

            agent = ValueInvestingAgent(fetcher=mock_fetcher, api_key="fake")
            messages = [{"role": "user", "content": "分析茅台"}]
            result = agent._run_loop(messages)

            assert result == "分析完成：贵州茅台具有极强护城河。"
            assert mock_client.chat.completions.create.call_count == 1

    def test_executes_tool_calls_and_continues(self, mock_fetcher):
        """finish_reason='tool_calls' 时应执行工具并追加结果消息，然后继续循环。"""
        mock_fetcher.get_company_info.return_value = CompanyInfo(
            ts_code="600519.SH", name="贵州茅台"
        )

        with patch("buffett_munger_agent.agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            # 第一次调用：返回工具调用请求
            tool_call_response = MagicMock()
            tool_call_response.choices = [MagicMock()]
            tool_call_response.choices[0].finish_reason = "tool_calls"
            tool_call_response.choices[0].message.content = None
            tc = MagicMock()
            tc.id = "call_001"
            tc.function.name = "get_company_info"
            tc.function.arguments = json.dumps({"ts_code": "600519.SH"})
            tool_call_response.choices[0].message.tool_calls = [tc]
            tool_call_response.choices[0].message.model_dump.return_value = {
                "role": "assistant",
                "content": None,
                "tool_calls": [tc],
            }

            # 第二次调用：返回最终文本
            final_response = MagicMock()
            final_response.choices = [MagicMock()]
            final_response.choices[0].finish_reason = "stop"
            final_response.choices[0].message.content = "分析完成。"

            mock_client.chat.completions.create.side_effect = [
                tool_call_response,
                final_response,
            ]

            agent = ValueInvestingAgent(fetcher=mock_fetcher, api_key="fake")
            messages = [{"role": "user", "content": "分析茅台"}]
            result = agent._run_loop(messages)

            assert result == "分析完成。"
            assert mock_client.chat.completions.create.call_count == 2
            # 验证工具结果消息被追加
            tool_result_messages = [
                m for m in messages if isinstance(m, dict) and m.get("role") == "tool"
            ]
            assert len(tool_result_messages) == 1
            assert tool_result_messages[0]["tool_call_id"] == "call_001"


# ── System Prompt 注入测试 ────────────────────────────────────────────────────


class TestSystemPromptInjection:
    def test_run_once_injects_system_message(self, mock_fetcher):
        """run_once 传入 _run_loop 的 messages 第一条应为 system 消息。"""
        with patch("buffett_munger_agent.agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].finish_reason = "stop"
            mock_response.choices[0].message.content = "分析结果"
            mock_client.chat.completions.create.return_value = mock_response

            agent = ValueInvestingAgent(fetcher=mock_fetcher, api_key="fake")
            agent.run_once("分析茅台")

            call_messages = mock_client.chat.completions.create.call_args[1]["messages"]
            assert call_messages[0]["role"] == "system"
            assert call_messages[0]["content"] == SYSTEM_PROMPT
            assert call_messages[1]["role"] == "user"

    def test_run_interactive_injects_system_message(self, mock_fetcher, monkeypatch):
        """run_interactive 的对话消息第一条应为 system 消息，且全程只有一条。"""
        with patch("buffett_munger_agent.agent.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_openai_cls.return_value = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].finish_reason = "stop"
            mock_response.choices[0].message.content = "回复"
            mock_client.chat.completions.create.return_value = mock_response

            # 模拟用户依次输入两条消息后退出
            inputs = iter(["第一条消息", "第二条消息", "exit"])
            monkeypatch.setattr("builtins.input", lambda _: next(inputs))

            agent = ValueInvestingAgent(fetcher=mock_fetcher, api_key="fake")
            agent.run_interactive()

            # 第二轮调用时 messages 中 system 消息应只有一条
            last_call_messages = mock_client.chat.completions.create.call_args[1]["messages"]
            system_messages = [m for m in last_call_messages if m.get("role") == "system"]
            assert len(system_messages) == 1
            assert system_messages[0]["content"] == SYSTEM_PROMPT
            assert last_call_messages[0]["role"] == "system"


# ── run_agent 环境变量校验测试 ────────────────────────────────────────────────


class TestRunAgentEnvValidation:
    def test_exits_when_dashscope_api_key_missing(self, monkeypatch):
        """未设置 DASHSCOPE_API_KEY 时应 sys.exit(1)。"""
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
        monkeypatch.setenv("TUSHARE_TOKEN", "fake-token")
        with pytest.raises(SystemExit) as exc_info:
            run_agent()
        assert exc_info.value.code == 1

    def test_exits_when_tushare_token_missing(self, monkeypatch):
        """未设置 TUSHARE_TOKEN 时应 sys.exit(1)。"""
        monkeypatch.setenv("DASHSCOPE_API_KEY", "fake-key")
        monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
        with pytest.raises(SystemExit) as exc_info:
            run_agent()
        assert exc_info.value.code == 1

    def test_exits_when_both_env_vars_missing(self, monkeypatch):
        """两个环境变量都未设置时应 sys.exit(1)。"""
        monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
        monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
        with pytest.raises(SystemExit) as exc_info:
            run_agent()
        assert exc_info.value.code == 1
