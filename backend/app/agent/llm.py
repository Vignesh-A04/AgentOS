import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.mcp.manager import MCPManager

from app.tools.definitions import (
    CALCULATOR_TOOL,
    CREATE_FILE_TOOL,
    READ_FILE_TOOL,
    LIST_FILES_TOOL,
    API_GET_TOOL,
    WEB_SEARCH_TOOL,
)


load_dotenv()


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.mcp_manager = MCPManager()

        # Build local tools first.
        # MCP tools are loaded asynchronously during FastAPI startup.
        self.tools = self._build_local_tools()

    def _build_local_tools(self):
        """
        Build the local AgentOS tool catalog.
        """

        tool_definitions = [
            CALCULATOR_TOOL,
            CREATE_FILE_TOOL,
            READ_FILE_TOOL,
            LIST_FILES_TOOL,
            API_GET_TOOL,
            WEB_SEARCH_TOOL,
        ]

        function_declarations = [
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=tool["parameters"],
            )
            for tool in tool_definitions
        ]

        return types.Tool(
            function_declarations=function_declarations
        )

    async def load_mcp_tools(self):
        """
        Discover MCP tools and add them
        to the Gemini tool catalog.
        """

        mcp_tools = await self.mcp_manager.list_tools()

        print("\nMCP TOOLS DISCOVERED")

        for tool in mcp_tools:
            print(
                f"Name: {tool.name}"
            )

            print(
                f"Description: {tool.description}"
            )

            print(
                f"Schema: {tool.input_schema}"
            )

            self.tools.function_declarations.append(
                types.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description or "",
                    parameters=tool.input_schema,
                )
            )

    def _config(self):
        return types.GenerateContentConfig(
            system_instruction=(
                "You are AgentOS, a helpful AI engineering agent. "
                "Use available tools when they are useful. "
                "Some tools are provided directly by AgentOS, "
                "while others are provided through MCP servers."
            ),
            tools=[
                self.tools
            ],
            automatic_function_calling=(
                types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )

    def generate(self, message: str):
        return self.client.models.generate_content(
            model=self.model,
            contents=message,
            config=self._config(),
        )

    def generate_with_tool_results(
        self,
        message: str,
        original_response,
        tool_results,
    ):
        function_response_parts = []

        for item in tool_results:
            function_call = item["function_call"]
            tool_result = item["result"]

            function_response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=function_call.name,
                        response={
                            "result": tool_result
                        },
                        id=function_call.id,
                    )
                )
            )

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=message
                    )
                ],
            ),
            original_response.candidates[0].content,
            types.Content(
                role="user",
                parts=function_response_parts,
            ),
        ]

        return self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=self._config(),
        )