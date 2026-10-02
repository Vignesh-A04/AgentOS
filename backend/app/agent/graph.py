import asyncio
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.agent.agent import Agent


class AgentState(TypedDict):
    message: str
    response: str


agent = Agent()

asyncio.run(agent.load_mcp_tools())


def agent_node(state: AgentState):
    response = agent.run(state["message"])

    return {
        "response": response
    }


graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)

graph_builder.add_edge(START, "agent")
graph_builder.add_edge("agent", END)

agent_graph = graph_builder.compile()