## ADDED Requirements

### Requirement: 通过 MCP Tool 获取公司基础信息
系统 SHALL 通过名为 `get_company_info` 的 MCP Tool 暴露公司基础信息获取能力，接受 `ts_code` 参数（Tushare 格式股票代码），返回 JSON 序列化的 `CompanyInfo` 数据。

#### Scenario: 成功调用 get_company_info Tool
- **WHEN** MCP 客户端调用 `get_company_info` 并传入有效的 `ts_code`（如 "600519.SH"）
- **THEN** Server SHALL 返回包含 name、sector、industry、market_cap、exchange、currency、description 字段的 JSON 文本内容

#### Scenario: 无效代码时返回 MCP 错误
- **WHEN** MCP 客户端调用 `get_company_info` 并传入不存在的股票代码
- **THEN** Server SHALL 返回包含错误描述的 MCP 错误响应
