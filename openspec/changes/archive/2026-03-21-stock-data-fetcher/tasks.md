## 1. 项目依赖与目录结构

- [x] 1.1 通过 `uv add tushare pydantic` 添加依赖
- [x] 1.2 创建 `src/buffett_munger_agent/data/` 子包（`__init__.py`）
- [x] 1.3 创建 `src/buffett_munger_agent/data/providers/` 子包（`__init__.py`）

## 2. 数据模型

- [x] 2.1 在 `data/models.py` 中定义 `StockFundamentals` Pydantic 模型（含 PE、PB、ROE、FCF 等 Optional 字段）
- [x] 2.2 在 `data/models.py` 中定义 `PriceBar` Pydantic 模型（date、open、high、low、close、volume）
- [x] 2.3 在 `data/models.py` 中定义 `CompanyInfo` Pydantic 模型（name、sector、industry、market_cap、exchange、currency、description）
- [x] 2.4 在 `data/models.py` 中定义 `DataFetchError` 异常类

## 3. DataProvider 接口

- [x] 3.1 在 `data/base.py` 中使用 `typing.Protocol` 定义 `DataProvider` 接口，声明 `get_fundamentals`、`get_price_history`、`get_company_info` 方法签名

## 4. Tushare 数据提供者（A 股）

- [x] 4.1 在 `data/providers/tushare.py` 中实现 `TushareProvider` 类，初始化时接受 `token` 参数并调用 `ts.set_token()` 完成鉴权
- [x] 4.2 实现 `get_fundamentals` 方法，调用 Tushare 财务接口（如 `daily_basic`、`income`、`balancesheet`、`cashflow`）并映射到 `StockFundamentals`
- [x] 4.3 实现 `get_price_history` 方法，调用 `ts.pro_bar()` 获取日线/周线/月线数据并映射到 `list[PriceBar]`，使用后复权（`adj='hfq'`）
- [x] 4.4 实现 `get_company_info` 方法，调用 `pro.stock_basic()` 及 `pro.bak_basic()` 获取公司信息并映射到 `CompanyInfo`
- [x] 4.5 在无效代码、鉴权失败或网络错误时抛出 `DataFetchError`

## 5. 统一 Fetcher 入口

- [x] 5.1 在 `data/fetcher.py` 中实现 `StockFetcher` 类，初始化时接受 `tushare_token` 参数并构造 `TushareProvider`
- [x] 5.2 暴露 `get_fundamentals(ticker)`、`get_price_history(ticker, start, end, interval)`、`get_company_info(ticker)` 三个公共方法
- [x] 5.3 在 `data/__init__.py` 中导出 `StockFetcher`、数据模型及 `DataFetchError`

## 6. 测试

- [x] 6.1 在 `tests/data/` 下创建测试文件结构
- [x] 6.2 为 `StockFetcher` 的初始化与方法调用编写单元测试（Mock `TushareProvider`）
- [x] 6.3 为 `TushareProvider` 编写集成测试（需要有效 token，标记 `@pytest.mark.integration` 以便在 CI 中跳过）
- [x] 6.4 验证数据缺失时（Optional 字段）模型正确返回 None 而非抛出异常
- [x] 6.5 验证无效股票代码时 `TushareProvider` 正确抛出 `DataFetchError`
