from typing import TypedDict

from google.genai import types
from langgraph.graph import StateGraph, START, END

from app.agent.llm import LLMClient
from app.tools.registry import TOOL_REGISTRY
from app.tools.permissions import is_tool_allowed


class AgentState(TypedDict):
    message: str
    response: object
    tool_results: list
    final_response: str
    iteration: int
    history: list


llm = LLMClient()

mcp_tools = set()


async def initialize_mcp_tools():
    global mcp_tools

    # Discover MCP tools
    tools = await llm.mcp_manager.list_tools()

    mcp_tools = {
        tool.name
        for tool in tools
    }

    # Add MCP tools to Gemini's tool catalog
    await llm.load_mcp_tools()

    print("\nMCP TOOL ROUTER")

    for tool_name in mcp_tools:
        print(
            f"Registered MCP tool: {tool_name}"
        )


def _build_history_from_request(state: AgentState):
    """
    Convert frontend conversation history into
    Gemini Content objects.

    Frontend:
        user
        assistant

    Gemini:
        user
        model
    """

    contents = []

    for item in state.get("history", []):
        role = item.get("role")
        content = item.get("content", "")

        if not content:
            continue

        gemini_role = (
            "model"
            if role == "assistant"
            else "user"
        )

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

    return contents


def agent_node(state: AgentState):
    """
    Ask Gemini to reason about the current request.

    On the first graph iteration, use the frontend
    conversation history.

    On later iterations, preserve the LangGraph
    history containing model tool calls and
    function responses.
    """

    # ---------------------------------------------------------
    # FIRST AGENT CALL
    # ---------------------------------------------------------

    if state["response"] is None:

        history = _build_history_from_request(
            state
        )

        # Always append the current user message.
        history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=state["message"]
                    )
                ],
            )
        )

    # ---------------------------------------------------------
    # SUBSEQUENT AGENT CALLS
    # ---------------------------------------------------------

    else:
        history = state["history"]

    # ---------------------------------------------------------
    # CALL GEMINI
    # ---------------------------------------------------------

    response = llm.generate_from_contents(
        history
    )

    model_content = (
        response.candidates[0].content
    )

    # ---------------------------------------------------------
    # CHECK FOR TOOL CALLS
    # ---------------------------------------------------------

    tool_calls = [
        part.function_call
        for part in model_content.parts
        if part.function_call
    ]

    # ---------------------------------------------------------
    # PRESERVE GEMINI RESPONSE
    # ---------------------------------------------------------

    updated_history = (
        history + [model_content]
    )

    # No tool call means Gemini produced
    # the final answer.

    if not tool_calls:
        final_response = response.text
    else:
        final_response = ""

    return {
        "response": response,
        "final_response": final_response,
        "history": updated_history,
    }


def tool_node(state: AgentState):
    """
    Execute requested local or MCP tools.
    """

    response = state["response"]

    tool_calls = [
        part.function_call
        for part in response.candidates[0].content.parts
        if part.function_call
    ]

    tool_results = []
    function_response_parts = []

    for function_call in tool_calls:

        tool_name = function_call.name
        tool_args = dict(function_call.args)

        print("\nTOOL CALL")
        print(
            f"Iteration: {state['iteration'] + 1}"
        )
        print(
            f"Name: {tool_name}"
        )
        print(
            f"Arguments: {tool_args}"
        )

        # -----------------------------------------------------
        # PERMISSION
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # LOCAL TOOL
        # -----------------------------------------------------

        if tool_name in TOOL_REGISTRY:

            print(
                "Tool source: local"
            )

            try:

                tool_result = TOOL_REGISTRY[
                    tool_name
                ](
                    **tool_args
                )

            except Exception as exc:

                tool_result = {
                    "error": str(exc)
                }

            tool_source = "local"

        # -----------------------------------------------------
        # MCP TOOL
        # -----------------------------------------------------

        elif tool_name in mcp_tools:

            print(
                "Tool source: MCP"
            )

            try:

                tool_result = (
                    llm.mcp_manager.call_tool_sync(
                        tool_name,
                        tool_args,
                    )
                )

            except Exception as exc:

                tool_result = {
                    "error": str(exc)
                }

            tool_source = "MCP"

        # -----------------------------------------------------
        # UNKNOWN TOOL
        # -----------------------------------------------------

        else:

            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        print(
            f"Tool result: {tool_result}"
        )

        # -----------------------------------------------------
        # SAVE TOOL RESULT
        # -----------------------------------------------------

        tool_results.append(
            {
                "name": tool_name,
                "source": tool_source,
                "arguments": tool_args,
                "result": tool_result,
            }
        )

        # -----------------------------------------------------
        # GEMINI FUNCTION RESPONSE
        # -----------------------------------------------------

        function_response = (
            types.FunctionResponse(
                name=tool_name,
                response={
                    "result": tool_result
                },
            )
        )

        if getattr(function_call, "id", None):
            function_response.id = (
                function_call.id
            )

        function_response_parts.append(
            types.Part(
                function_response=function_response
            )
        )

    # ---------------------------------------------------------
    # ADD TOOL RESULTS TO GEMINI HISTORY
    # ---------------------------------------------------------

    function_response_content = (
        types.Content(
            role="user",
            parts=function_response_parts,
        )
    )

    updated_history = (
        state["history"]
        + [function_response_content]
    )

    return {
        "tool_results": (
            state["tool_results"]
            + tool_results
        ),
        "history": updated_history,
        "iteration": (
            state["iteration"] + 1
        ),
    }


def route_after_agent(state: AgentState):
    """
    Decide whether to execute tools or finish.
    """

    response = state["response"]

    tool_calls = [
        part.function_call
        for part in response.candidates[0].content.parts
        if part.function_call
    ]

    # ---------------------------------------------------------
    # FINAL ANSWER
    # ---------------------------------------------------------

    if not tool_calls:
        return END

    # ---------------------------------------------------------
    # SAFETY LIMIT
    # ---------------------------------------------------------

    if state["iteration"] >= 5:

        raise RuntimeError(
            "Agent exceeded the maximum number "
            "of tool iterations."
        )

    return "tools"


# =============================================================
# BUILD LANGGRAPH
# =============================================================

graph_builder = StateGraph(
    AgentState
)

graph_builder.add_node(
    "agent",
    agent_node,
)

graph_builder.add_node(
    "tools",
    tool_node,
)

graph_builder.add_edge(
    START,
    "agent",
)

graph_builder.add_conditional_edges(
    "agent",
    route_after_agent,
)

graph_builder.add_edge(
    "tools",
    "agent",
)

agent_graph = (
    graph_builder.compile()
)