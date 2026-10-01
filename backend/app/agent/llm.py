import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.definitions import CALCULATOR_TOOL


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

        self.calculator_tool = self._build_calculator_tool()

    def _build_calculator_tool(self):

        calculator_declaration = types.FunctionDeclaration(
            name=CALCULATOR_TOOL["name"],
            description=CALCULATOR_TOOL["description"],
            parameters=CALCULATOR_TOOL["parameters"],
        )

        return types.Tool(
            function_declarations=[
                calculator_declaration
            ]
        )

    def _config(self):

        return types.GenerateContentConfig(
            system_instruction=(
                "You are AgentOS, a helpful AI engineering agent. "
                "Use available tools when they are useful."
            ),
            tools=[
                self.calculator_tool
            ],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
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