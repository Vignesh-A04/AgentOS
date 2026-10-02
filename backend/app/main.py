from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.graph import agent_graph


app = FastAPI(
    title="AgentOS",
    description="Tool-using AI agent platform",
    version="0.1.0",
)


class AgentRequest(BaseModel):
    message: str


class AgentResponse(BaseModel):
    response: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AgentOS",
    }


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest):
    result = agent_graph.invoke({
        "message": request.message,
        "response": "",
    })

    return AgentResponse(
        response=result["response"]
    )