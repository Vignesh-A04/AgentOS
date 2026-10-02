from mcp.server import MCPServer


mcp = MCPServer("AgentOS Demo Server")


@mcp.tool()
def get_project_info() -> dict:
    """Return information about the AgentOS project."""
    return {
        "name": "AgentOS",
        "type": "AI Agent Platform",
        "purpose": "Tool-using AI agent with LLM, APIs, web search, filesystem and MCP support",
        "status": "In development",
    }


@mcp.tool()
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    mcp.run()