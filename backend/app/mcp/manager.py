import asyncio
import json
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parents[3]

MCP_SERVER_PATH = (
    PROJECT_ROOT / "mcp_servers" / "demo_server.py"
)


class MCPManager:
    def __init__(self):
        self.server = StdioServerParameters(
            command="python",
            args=[str(MCP_SERVER_PATH)],
        )

    async def list_tools(self):
        async with Client(self.server) as client:
            result = await client.list_tools()
            return result.tools

    async def call_tool(
        self,
        name: str,
        arguments: dict,
    ):
        async with Client(self.server) as client:
            result = await client.call_tool(
                name,
                arguments,
            )

            return self._extract_result(result)

    def _extract_result(self, result):
        """
        Convert the MCP response into a simple
        value that AgentOS can pass back to Gemini.
        """

        # Preferred: structured MCP result
        if result.structured_content:
            if "result" in result.structured_content:
                return result.structured_content["result"]

            return result.structured_content

        # Fallback: text content
        if result.content:
            text = result.content[0].text

            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text

        return None

    def call_tool_sync(
        self,
        name: str,
        arguments: dict,
    ):
        return asyncio.run(
            self.call_tool(
                name,
                arguments,
            )
        )