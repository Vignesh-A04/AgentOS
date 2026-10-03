# AgentOS

> A tool-using AI agent platform built with FastAPI, LangGraph, Gemini, MCP, and React.

AgentOS is an AI agent application that can understand a user's request, decide whether a tool is required, execute the appropriate tool, process the result, and generate a final response.

The project demonstrates how modern AI agents can combine LLM reasoning with external tools, APIs, filesystem operations, web search, and MCP-based tools.

---

## 🚀 Features

- Gemini-powered AI agent
- LangGraph-based agent workflow
- Tool calling
- Calculator tool
- File creation and reading
- Workspace file listing
- External API requests
- Web search using Tavily
- MCP server integration
- MCP tool discovery
- MCP tool execution
- Tool permission control
- Sandboxed filesystem access
- Conversation history / memory
- React + TypeScript frontend
- FastAPI backend
- Docker support
- Render deployment

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │   React Frontend     │
                    │   TypeScript + Vite  │
                    └──────────┬───────────┘
                               │
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      LangGraph       │
                    │   Agent Workflow     │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Gemini 3.5         │
                    │    Flash-Lite        │
                    └──────────┬───────────┘
                               │
                     Tool decision / calls
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    Local Tools           Web / APIs             MCP Tools
    ───────────           ──────────             ─────────
    Calculator            Tavily Search          multiply_numbers
    Filesystem            API GET                get_project_info


    AgentOS/
│
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   └── llm.py
│   │   │
│   │   ├── tools/
│   │   │   ├── calculator.py
│   │   │   ├── filesystem.py
│   │   │   ├── api.py
│   │   │   ├── web_search.py
│   │   │   ├── definitions.py
│   │   │   ├── registry.py
│   │   │   └── permissions.py
│   │   │
│   │   ├── mcp/
│   │   │   └── manager.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── mcp_servers/
│   └── demo_server.py
│
├── workspace/
│   ├── documents/
│   ├── outputs/
│   └── temporary/
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── .gitignore
└── README.md

Environment Variables
The backend requires a Gemini API key.
Create:
backend/.env

Add:
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
TAVILY_API_KEY=your_tavily_api_key

Never commit .env or API keys to GitHub.
Google recommends using environment variables such as GEMINI_API_KEY for API-key configuration rather than hardcoding secrets in source code. Google AI for Developers
▶️ Run Locally
1. Clone the repository
git clone https://github.com/Vignesh-A04/AgentOS.git

Move into the project:
cd AgentOS

🐍 Backend Setup
Open PowerShell inside the backend directory:
cd backend

Create a virtual environment:
python -m venv .venv

Activate it:
.\.venv\Scripts\Activate.ps1

Install dependencies:
pip install -r requirements.txt

Create:
backend/.env

Configure:
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
TAVILY_API_KEY=your_tavily_api_key

🚀 Start Backend
From:
AgentOS/backend

run:
uvicorn app.main:app --reload

Backend:
http://127.0.0.1:8000

Health check:
http://127.0.0.1:8000/health

Expected response:
{
  "status": "healthy",
  "service": "AgentOS"
}

📚 FastAPI Documentation
Open:
http://127.0.0.1:8000/docs

Available endpoints include:
GET  /health
POST /agent/run

⚛️ Frontend Setup
Open a second PowerShell terminal.
From the project root:
cd frontend

Install dependencies:
npm install

Create:
frontend/.env

For local development:
VITE_API_URL=http://localhost:8000

Start the frontend:
npm run dev

Open:
http://localhost:5173

🐳 Run with Docker
Docker can run both the backend and frontend.
From the project root:
docker compose up --build

Backend:
http://localhost:8000

Frontend:
http://localhost:5173

To stop the containers:
docker compose down

To rebuild after code changes:
docker compose up --build

🔌 MCP Integration
AgentOS supports Model Context Protocol (MCP).
The demo MCP server is located at:
mcp_servers/demo_server.py

It exposes:
get_project_info
multiply_numbers

At application startup, AgentOS connects to the MCP server and discovers its available tools.
Example startup output:
MCP TOOLS DISCOVERED

Name: get_project_info
Name: multiply_numbers

MCP TOOL ROUTER
Registered MCP tool: get_project_info
Registered MCP tool: multiply_numbers

The agent can then use these tools alongside the locally registered tools.
🛠️ Available Tools
Local Tools
Calculator
Performs mathematical operations.
Example:
Calculate 125 × 48

Create File
Creates a file inside the AgentOS workspace.
Example:
Create a file called notes.txt containing:
AgentOS is a tool-using AI agent.

Read File
Reads a file from the AgentOS workspace.
Example:
Read notes.txt

List Files
Lists files inside the workspace.
Example:
List the files in the workspace.

API GET
Performs GET requests against external APIs.
Example:
Get information from this API endpoint.

Web Search
Searches the web using Tavily.
Example:
Search the web for the latest Python release.

MCP Tools
AgentOS currently demonstrates:
get_project_info
multiply_numbers

🔐 Tool Permissions
AgentOS maintains an explicit list of allowed tools.
ALLOWED_TOOLS = {    "calculator",    "create_file",    "read_file",    "list_files",    "api_get",    "web_search",    "get_project_info",    "multiply_numbers",}


Before executing a tool, the agent checks whether the requested tool is permitted.
This prevents unknown or unauthorized tools from being executed.
🛡️ Filesystem Security
Filesystem operations are restricted to:
workspace/

The application resolves requested paths and verifies that they remain inside the AgentOS workspace.
For example:
workspace/documents/file.txt

is allowed.
A path attempting to access a location outside the workspace is rejected.
🧠 Agent Workflow
The agent follows a tool-use loop:
User Request
     │
     ▼
Gemini
     │
     ├── No tool required
     │        │
     │        ▼
     │      Response
     │
     └── Tool required
              │
              ▼
        Tool Permission Check
              │
              ▼
          Tool Execution
              │
              ▼
         Tool Result
              │
              ▼
            Gemini
              │
              ▼
        Final Response

LangGraph manages this agent workflow and allows the agent to repeatedly move between reasoning and tool execution until the request is complete.
💬 Conversation Memory
The frontend sends previous messages to the backend as conversation history.
Example:
User:
My name is Vignesh.

Agent:
Nice to meet you, Vignesh.

User:
What is my name?

Agent:
Your name is Vignesh.

The backend converts the conversation history into the appropriate Gemini message format before sending it to the model.
🧪 Example Prompts
Try the following prompts after starting AgentOS.
Calculator
Calculate 125 * 48

Filesystem
Create a file called test.txt containing Hello from AgentOS.

Read File
Read test.txt

List Files
List all files in the workspace.

MCP
What is the AgentOS project?

MCP Calculator
Use the multiplication tool to multiply 25 and 40.

Web Search
Search the web for the latest Python version.

API
Make a GET request to a public API and show the response.

Conversation Memory
My name is Vignesh.

Then:
What is my name?

🌐 Deployment
AgentOS is deployed using Render.
Architecture:
Browser
   │
   ▼
Render Frontend
   │
   │ HTTPS
   ▼
Render FastAPI Backend
   │
   ├── Gemini
   ├── Tavily
   └── MCP Server

Frontend environment variable:
VITE_API_URL=https://agentos-backend-knb5.onrender.com

The backend exposes:
https://agentos-backend-knb5.onrender.com

Health endpoint:
/health

📌 Important Notes
- Gemini API usage is subject to the limits of the configured Google AI project.
- Keep API keys in environment variables.
- Do not commit .env files.
- Filesystem tools are restricted to the AgentOS workspace.
- MCP tools are discovered during backend startup.
- Docker is optional for local development.
🎯 Project Goals
AgentOS was built to demonstrate practical AI Engineering concepts:
- LLM integration
- Function calling
- Agent orchestration
- Tool execution
- MCP
- API integration
- Web search
- Filesystem tools
- Permission control
- Conversation state
- Backend API design
- Frontend integration
- Docker
- Cloud deployment