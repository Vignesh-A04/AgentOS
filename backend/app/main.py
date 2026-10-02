from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.agent import Agent


app = FastAPI(
    title="AgentOS",
    description="Tool-using AI agent platform",
    version="0.1.0",
)


agent = Agent()

@app.on_event("startup")
async def startup_event():
    await agent.llm.load_mcp_tools()
    await agent.load_mcp_tools()

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
    response = agent.run(request.message)

    return AgentResponse(
        response=response
    )