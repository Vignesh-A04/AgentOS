import asyncio
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MCP_SERVER_PATH = (
    PROJECT_ROOT / "mcp_servers" / "demo_server.py"
)


async def main():
    server = StdioServerParameters(
        command="python",
        args=[str(MCP_SERVER_PATH)],
    )

    async with Client(server) as client:

        print("\nConnected to MCP server")

        # 1. Discover available MCP tools
        result = await client.list_tools()

        print("\nAvailable MCP tools:")

        for tool in result.tools:
            print(f"- {tool.name}")
            print(f"  Description: {tool.description}")
            print(f"  Schema: {tool.input_schema}")

        # 2. Call get_project_info
        print("\nCalling get_project_info...")

        result = await client.call_tool(
            "get_project_info",
            {},
        )

        print("\nTool result:")
        print(result)

        # 3. Call multiply_numbers
        print("\nCalling multiply_numbers...")

        result = await client.call_tool(
            "multiply_numbers",
            {
                "a": 125,
                "b": 48,
            },
        )

        print("\nTool result:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())