# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 语言规范

所有产出物（代码注释、文档、提交信息、回复内容等）均使用中文。

## 常用命令

```bash
# 安装依赖
uv sync

# 运行 agent
uv run buffett-munger-agent

# 添加依赖
uv add <package>

# 运行测试
uv run pytest

# 运行单个测试
uv run pytest tests/path/to/test_file.py::test_name

# 代码检查 / 格式化
uv run ruff check .
uv run ruff format .
```

## 架构说明

本项目采用 **src layout** 结构，所有源码位于 `src/buffett_munger_agent/` 下。

项目目标是构建一个由大模型驱动的 agent，按照巴菲特/芒格价值投资理念生成股票分析报告。当前处于早期开发阶段，架构将随开发演进持续更新。

- 入口：`src/buffett_munger_agent/__main__.py` → `main()`
- 包通过 `uv sync` 以可编辑模式安装，导入路径使用 `buffett_munger_agent.*`
- 虚拟环境由 uv 管理，路径为 `.venv/`
