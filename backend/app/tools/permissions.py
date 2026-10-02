ALLOWED_TOOLS = {
    "calculator",
    "create_file",
    "read_file",
    "list_files",
    "api_get",
    "web_search",
}


def is_tool_allowed(tool_name: str) -> bool:
    """
    Check whether AgentOS is allowed to execute a tool.
    """

    return tool_name in ALLOWED_TOOLS