## ADDED Requirements

### Requirement: 获取公司基础信息
系统 SHALL 根据 A 股股票代码获取公司基础元数据，包括公司全称、所属行业、市值、交易所、货币单位及公司简介。

#### Scenario: 成功获取公司信息
- **WHEN** 调用 fetcher 并传入有效的 A 股代码（如 "600519.SH"）
- **THEN** 返回包含 name、sector、industry、market_cap、exchange、currency、description 字段的 `CompanyInfo` 对象

#### Scenario: 公司简介缺失时正常返回
- **WHEN** 数据源对该股票无公司简介
- **THEN** description 字段返回 None，其他字段正常填充

#### Scenario: 无效股票代码时抛出异常
- **WHEN** 调用 fetcher 并传入不存在的股票代码
- **THEN** 系统 SHALL 抛出 `DataFetchError` 异常

### Requirement: 使用 Tushare 股票代码格式
系统 SHALL 接受 Tushare 标准格式的股票代码（`{6位数字}.{交易所后缀}`，如 "600519.SH"、"000001.SZ"）作为输入。

#### Scenario: 上交所股票代码正确识别
- **WHEN** 传入格式为 `xxxxxx.SH` 的股票代码
- **THEN** 系统 SHALL 通过 `TushareProvider` 正确获取数据

#### Scenario: 深交所股票代码正确识别
- **WHEN** 传入格式为 `xxxxxx.SZ` 的股票代码
- **THEN** 系统 SHALL 通过 `TushareProvider` 正确获取数据
