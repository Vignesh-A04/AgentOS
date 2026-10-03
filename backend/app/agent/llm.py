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

        # Local AgentOS tools
        self.tools = self._build_local_tools()

    # ---------------------------------------------------------
    # LOCAL TOOLS
    # ---------------------------------------------------------

    def _build_local_tools(self):
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

    # ---------------------------------------------------------
    # MCP TOOLS
    # ---------------------------------------------------------

    async def load_mcp_tools(self):
        """
        Discover MCP tools and add them to
        the Gemini function catalog.
        """

        mcp_tools = await self.mcp_manager.list_tools()

        print("\nMCP TOOLS DISCOVERED")

        for tool in mcp_tools:
            print(f"Name: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Schema: {tool.input_schema}")

            # Avoid duplicate registration
            existing_names = {
                declaration.name
                for declaration in self.tools.function_declarations
            }

            if tool.name not in existing_names:
                self.tools.function_declarations.append(
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description or "",
                        parameters=tool.input_schema,
                    )
                )

    # ---------------------------------------------------------
    # GEMINI CONFIG
    # ---------------------------------------------------------

    def _config(self):
        return types.GenerateContentConfig(
            system_instruction=(
                "You are AgentOS, a helpful AI engineering agent. "

                "Use available tools when they are useful. "

                "Some tools are provided directly by AgentOS, "
                "while others are provided through MCP servers. "

                "After receiving a tool result, use that result "
                "to answer the user's request. "

                "Do not repeat the same tool call with the same "
                "arguments unless there is a clear reason to do so. "

                "When a tool returns an error, explain the error "
                "clearly and do not repeatedly retry the same "
                "invalid operation. "

                "The filesystem is sandboxed to the AgentOS workspace, "
                "so paths outside that workspace cannot be accessed. "

                "Use the conversation history to understand previous "
                "messages and facts provided by the user. "
                "When the user refers to something mentioned earlier "
                "in the conversation, use that information."
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

    # ---------------------------------------------------------
    # HISTORY CONVERSION
    # ---------------------------------------------------------

    def _build_history_contents(
        self,
        history,
        current_message,
    ):
        """
        Convert frontend conversation history into
        Gemini Content objects.

        Frontend roles:
            user
            assistant

        Gemini roles:
            user
            model
        """

        contents = []

        for item in history or []:
            role = item.get("role")
            content = item.get("content", "")

            if not content:
                continue

            # Gemini only accepts user/model roles.
            if role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"

            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[
                        types.Part.from_text(
                            text=str(content)
                        )
                    ],
                )
            )

        # IMPORTANT:
        # The request must end with a USER message.
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=current_message
                    )
                ],
            )
        )

        return contents

    # ---------------------------------------------------------
    # NORMAL GENERATION
    # ---------------------------------------------------------

    def generate(self, message: str):
        """
        Generate a response without conversation history.
        """

        return self.client.models.generate_content(
            model=self.model,
            contents=message,
            config=self._config(),
        )

    # ---------------------------------------------------------
    # GENERATION WITH HISTORY
    # ---------------------------------------------------------

    def generate_with_history(
        self,
        message: str,
        history=None,
    ):
        """
        Generate a response using previous conversation history.
        """

        contents = self._build_history_contents(
            history=history,
            current_message=message,
        )

        return self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=self._config(),
        )

    # ---------------------------------------------------------
    # GENERATION FROM CONTENTS
    # ---------------------------------------------------------

    def generate_from_contents(self, contents):
        return self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=self._config(),
        )

    # ---------------------------------------------------------
    # TOOL RESULT GENERATION
    # ---------------------------------------------------------

    def generate_with_tool_results(
        self,
        message: str,
        original_response,
        tool_results,
        history=None,
    ):
        """
        Send Gemini's previous function call plus the
        corresponding function responses back to Gemini.

        Conversation structure:

            previous history
            current user message
            model function call
            user function response
        """

        # Start with previous conversation.
        contents = self._build_history_contents(
            history=history,
            current_message=message,
        )

        # Add Gemini's function-call response.
        contents.append(
            original_response.candidates[0].content
        )

        # Add tool results.
        function_response_parts = []

        for item in tool_results:
            function_call = item["function_call"]
            tool_result = item["result"]

            function_response = types.FunctionResponse(
                name=function_call.name,
                response={
                    "result": tool_result
                },
            )

            # Function-call IDs are supported when present.
            if getattr(function_call, "id", None):
                function_response.id = function_call.id

            function_response_parts.append(
                types.Part(
                    function_response=function_response
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts,
            )
        )

        return self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=self._config(),
        )