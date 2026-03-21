import argparse

from buffett_munger_agent.mcp_server import run_mcp_server


def main() -> None:
    parser = argparse.ArgumentParser(description="buffett-munger-agent")
    parser.add_argument(
        "--mcp",
        action="store_true",
        help="以 MCP Server 模式启动（stdio transport），供 Claude Code CLI 调用。",
    )
    args = parser.parse_args()

    if args.mcp:
        run_mcp_server()
    else:
        print("Hello from buffett-munger-agent!")


if __name__ == "__main__":
    main()
