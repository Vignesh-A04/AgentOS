from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent.graph import (
    agent_graph,
    initialize_mcp_tools,
)


# =========================================
# LIFESPAN
# =========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_mcp_tools()
    yield


# =========================================
# APP
# =========================================

app = FastAPI(
    title="AgentOS",
    description="Tool-using AI agent platform",
    version="0.1.0",
    lifespan=lifespan,
)


# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://agentos-frontend-orr6.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# REQUEST / RESPONSE MODELS
# =========================================

class HistoryMessage(BaseModel):
    role: str
    content: str


class AgentRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = []


class AgentResponse(BaseModel):
    response: str
    tools: list = []


# =========================================
# HEALTH
# =========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AgentOS",
    }


# =========================================
# AGENT
# =========================================

@app.post(
    "/agent/run",
    response_model=AgentResponse,
)
def run_agent(request: AgentRequest):

    try:
        result = agent_graph.invoke(
            {
                "message": request.message,
                "response": None,
                "tool_results": [],
                "final_response": "",
                "iteration": 0,
                "history": [
                    {
                        "role": item.role,
                        "content": item.content,
                    }
                    for item in request.history
                ],
            }
        )

        return AgentResponse(
            response=result["final_response"],
            tools=result.get("tool_results", []),
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    except Exception as exc:
        print(f"Agent error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Agent execution failed.",
        )