import argparse

from buffett_munger_agent.mcp_server import run_mcp_server


def main() -> None:
    parser = argparse.ArgumentParser(description="buffett-munger-agent")

    # --mcp 与 --agent 互斥，不可同时使用
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--mcp",
        action="store_true",
        help="以 MCP Server 模式启动（stdio transport），供 Claude Code CLI 调用。",
    )
    mode_group.add_argument(
        "--agent",
        action="store_true",
        help="以 Agent 模式启动，使用千问模型进行 A 股价值投资分析。",
    )

    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="单次分析模式：传入分析指令，执行后打印结果并退出。与 --agent 配合使用。",
    )

    args = parser.parse_args()

    if args.mcp:
        run_mcp_server()
    elif args.agent:
        # 懒加载 agent 模块，避免 openai 未安装时影响 --mcp 模式启动
        from buffett_munger_agent.agent import run_agent

        run_agent(query=args.query)
    else:
        print("Hello from buffett-munger-agent!")


if __name__ == "__main__":
    main()
