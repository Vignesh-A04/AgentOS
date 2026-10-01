# AgentOS

AgentOS is a tool-using AI agent platform built to explore and implement
agentic AI systems from the ground up.

## Current Capabilities

- LLM-powered AI agent
- Gemini API integration
- Function/tool calling
- Dynamic tool registry
- Multi-step tool execution
- Calculator tool
- Agent execution loop
- Tool iteration limits

## Architecture

```text
User
  ↓
FastAPI
  ↓
Agent
  ↓
Gemini
  ↓
Tool Call
  ↓
Tool Registry
  ↓
Tool Execution
  ↓
Tool Result
  ↓
Gemini
  ↓
Final Response