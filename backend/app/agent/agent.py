from app.agent.llm import LLMClient
from app.tools.registry import TOOL_REGISTRY
from app.tools.permissions import is_tool_allowed


class Agent:
    def __init__(self):
        self.name = "AgentOS"
        self.llm = LLMClient()

        # MCP tools discovered from MCP servers
        self.mcp_tools = set()

    async def load_mcp_tools(self):
        """
        Discover MCP tools and store their names
        for routing decisions.
        """

        tools = await self.llm.mcp_manager.list_tools()

        self.mcp_tools = {
            tool.name
            for tool in tools
        }

        print("\nMCP TOOL ROUTER")

        for tool_name in self.mcp_tools:
            print(
                f"Registered MCP tool: {tool_name}"
            )

    def run(self, message: str) -> str:
        response = self.llm.generate(message)

        max_iterations = 10

        for iteration in range(max_iterations):
            candidate = response.candidates[0]

            tool_calls = [
                part.function_call
                for part in candidate.content.parts
                if part.function_call
            ]

            if not tool_calls:
                return response.text

            tool_results = []

            for function_call in tool_calls:
                tool_name = function_call.name
                tool_args = dict(function_call.args)

                print("\nTOOL CALL")
                print(
                    f"Iteration: {iteration + 1}"
                )
                print(
                    f"Name: {tool_name}"
                )
                print(
                    f"Arguments: {tool_args}"
                )

                # -------------------------
                # PERMISSION CHECK
                # -------------------------

                if not is_tool_allowed(tool_name):
                    print(
                        "Permission: denied"
                    )

                    raise PermissionError(
                        f"Tool execution denied: {tool_name}"
                    )

                print(
                    "Permission: allowed"
                )

                # -------------------------
                # LOCAL TOOL
                # -------------------------

                if tool_name in TOOL_REGISTRY:

                    print(
                        "Tool source: local"
                    )

                    tool_function = (
                        TOOL_REGISTRY[tool_name]
                    )

                    tool_result = tool_function(
                        **tool_args
                    )

                # -------------------------
                # MCP TOOL
                # -------------------------

                elif tool_name in self.mcp_tools:

                    print(
                        "Tool source: MCP"
                    )

                    tool_result = (
                        self.llm.mcp_manager.call_tool_sync(
                            tool_name,
                            tool_args,
                        )
                    )

                # -------------------------
                # UNKNOWN TOOL
                # -------------------------

                else:

                    raise ValueError(
                        f"Unknown tool: {tool_name}"
                    )

                # -------------------------
                # STORE TOOL RESULT
                # -------------------------

                print(
                    f"Tool result: {tool_result}"
                )

                tool_results.append(
                    {
                        "function_call": function_call,
                        "result": tool_result,
                    }
                )

            # -------------------------
            # SEND RESULTS BACK TO GEMINI
            # -------------------------

            response = (
                self.llm.generate_with_tool_results(
                    message=message,
                    original_response=response,
                    tool_results=tool_results,
                )
            )

        raise RuntimeError(
            "Agent exceeded the maximum number "
            "of tool iterations."
        )