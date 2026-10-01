from app.agent.llm import LLMClient
from app.tools.registry import TOOL_REGISTRY


class Agent:
    def __init__(self):
        self.name = "AgentOS"
        self.llm = LLMClient()

    def run(self, message: str) -> str:

        response = self.llm.generate(message)

        while True:

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
                print(f"Name: {tool_name}")
                print(f"Arguments: {tool_args}")

                if tool_name not in TOOL_REGISTRY:
                    raise ValueError(
                        f"Unknown tool: {tool_name}"
                    )

                tool_function = TOOL_REGISTRY[tool_name]

                tool_result = tool_function(**tool_args)

                print(f"Tool result: {tool_result}")

                tool_results.append(
                    {
                        "function_call": function_call,
                        "result": tool_result,
                    }
                )

            response = self.llm.generate_with_tool_results(
                message=message,
                original_response=response,
                tool_results=tool_results,
            )