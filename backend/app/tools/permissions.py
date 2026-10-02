ALLOWED_TOOLS = {
    # Local AgentOS tools
    "calculator",
    "create_file",
    "read_file",
    "list_files",
    "api_get",
    "web_search",

    # MCP tools
    "get_project_info",
    "multiply_numbers",
}


def is_tool_allowed(tool_name: str) -> bool:
    return tool_name in ALLOWED_TOOLS