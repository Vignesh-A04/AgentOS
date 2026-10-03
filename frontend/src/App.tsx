import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

import "./App.css";


// =========================================
// API
// =========================================

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";


// =========================================
// TYPES
// =========================================

type ToolCall = {
  name: string;
  source: string;
  arguments?: Record<string, unknown>;
  result?: unknown;
};


type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
  tools?: ToolCall[];
};


type AgentResponse = {
  response: string;
  tools?: ToolCall[];
};


// =========================================
// APP
// =========================================

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [backendOnline, setBackendOnline] =
    useState(false);

  const [backendStarting, setBackendStarting] =
    useState(true);

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);


  // =========================================
  // AUTO SCROLL
  // =========================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);


  // =========================================
  // BACKEND HEALTH
  // =========================================

  async function checkBackend() {
    try {
      const response = await fetch(
        `${API_URL}/health`,
        {
          method: "GET",
          cache: "no-store",
        }
      );

      if (response.ok) {
        setBackendOnline(true);
        setBackendStarting(false);
      } else {
        setBackendOnline(false);
        setBackendStarting(true);
      }

    } catch {
      setBackendOnline(false);
      setBackendStarting(true);
    }
  }


  // =========================================
  // HEALTH CHECK LOOP
  // =========================================

  useEffect(() => {
    checkBackend();

    const interval = setInterval(
      checkBackend,
      10000
    );

    return () => {
      clearInterval(interval);
    };
  }, []);


  // =========================================
  // SEND MESSAGE
  // =========================================

  async function sendMessage() {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    if (!backendOnline) {
      return;
    }


    // -----------------------------------------
    // Create user message
    // -----------------------------------------

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: message,
    };


    // -----------------------------------------
    // Add user message to UI
    // -----------------------------------------

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");
    setLoading(true);


    try {

      // ---------------------------------------
      // Send request to backend
      // ---------------------------------------

      const response = await fetch(
        `${API_URL}/agent/run`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({

            message,

            // Send previous conversation
            // history to Gemini through backend
            history: messages.map((msg) => ({
              role: msg.role,
              content: msg.content,
            })),

          }),
        }
      );


      // ---------------------------------------
      // Backend error
      // ---------------------------------------

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }


      // ---------------------------------------
      // Parse response
      // ---------------------------------------

      const data: AgentResponse =
        await response.json();


      // ---------------------------------------
      // Create assistant message
      // ---------------------------------------

      const assistantMessage: Message = {
        id: Date.now() + 1,

        role: "assistant",

        content:
          data.response ||
          "I couldn't generate a response.",

        tools: data.tools || [],
      };


      // ---------------------------------------
      // Add assistant message
      // ---------------------------------------

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);


      // Backend is confirmed working
      setBackendOnline(true);
      setBackendStarting(false);

    } catch (error) {

      console.error(
        "AgentOS backend error:",
        error
      );


      setBackendOnline(false);
      setBackendStarting(true);


      // ---------------------------------------
      // Display connection error
      // ---------------------------------------

      const errorMessage: Message = {
        id: Date.now() + 1,

        role: "assistant",

        content:
          "The AgentOS backend is starting or temporarily unavailable. Please try again in a few seconds.",
      };


      setMessages((previous) => [
        ...previous,
        errorMessage,
      ]);

    } finally {
      setLoading(false);
    }
  }


  // =========================================
  // KEYBOARD HANDLER
  // =========================================

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      sendMessage();
    }
  }


  // =========================================
  // NEW CHAT
  // =========================================

  function startNewChat() {
    setMessages([]);
    setInput("");
  }


  // =========================================
  // FORMAT VALUE
  // =========================================

  function formatValue(
    value: unknown
  ): string {

    if (
      value === null ||
      value === undefined
    ) {
      return "";
    }


    if (
      typeof value === "string"
    ) {
      return value;
    }


    try {

      return JSON.stringify(value);

    } catch {

      return String(value);

    }
  }


  // =========================================
  // FORMAT ARGUMENTS
  // =========================================

  function formatArguments(
    args?: Record<string, unknown>
  ) {

    if (!args) {
      return null;
    }


    return Object.entries(args).map(
      ([key, value]) => (

        <span
          className="argument-chip"
          key={key}
        >
          {key}: {formatValue(value)}
        </span>

      )
    );
  }


  // =========================================
  // TOOL RESULT
  // =========================================

  function getToolResult(
    tool: ToolCall
  ): string {

    if (
      tool.name === "web_search" &&
      Array.isArray(tool.result)
    ) {

      return `Search completed — ${tool.result.length} results found`;

    }


    if (
      tool.name === "list_files" &&
      Array.isArray(tool.result)
    ) {

      return `${tool.result.length} item${
        tool.result.length === 1
          ? ""
          : "s"
      } found`;

    }


    return formatValue(
      tool.result
    );
  }


  // =========================================
  // TOOL ICON
  // =========================================

  function getToolIcon(
    name: string
  ) {

    switch (name) {

      case "calculator":
        return "🧮";

      case "web_search":
        return "🌐";

      case "create_file":
      case "read_file":
      case "list_files":
        return "📁";

      case "api_get":
        return "🔌";

      case "get_project_info":
      case "multiply_numbers":
        return "🔧";

      default:
        return "⚙";
    }
  }


  // =========================================
  // TOOL ACTIVITY
  // =========================================

  function renderToolActivity(
    tools?: ToolCall[]
  ) {

    if (
      !tools ||
      tools.length === 0
    ) {
      return null;
    }


    return (

      <div className="agent-activity">

        {/* Activity Header */}

        <div className="activity-header">

          <div className="activity-title">

            <span className="activity-icon">
              ⚙
            </span>

            <span>
              Agent activity
            </span>

          </div>


          <span className="activity-count">

            {tools.length}{" "}

            {tools.length === 1
              ? "tool"
              : "tools"}

          </span>

        </div>


        {/* Activity List */}

        <div className="activity-list">

          {tools.map(
            (tool, index) => (

              <div
                className="tool-card"
                key={`${tool.name}-${index}`}
              >

                {/* Tool Name */}

                <div className="tool-top">

                  <div className="tool-name">

                    <span className="tool-success">
                      ✓
                    </span>


                    <span className="tool-icon">
                      {getToolIcon(
                        tool.name
                      )}
                    </span>


                    <strong>
                      {tool.name}
                    </strong>


                    <span className="tool-source">

                      {tool.source?.toUpperCase() ||
                        "LOCAL"}

                    </span>

                  </div>

                </div>


                {/* Tool Arguments */}

                {tool.arguments &&
                  Object.keys(
                    tool.arguments
                  ).length > 0 && (

                    <div className="tool-arguments">

                      {formatArguments(
                        tool.arguments
                      )}

                    </div>

                  )}


                {/* Tool Result */}

                <div className="tool-result">

                  <span className="result-label">
                    Result:
                  </span>

                  <span>
                    {getToolResult(tool)}
                  </span>

                </div>

              </div>

            )
          )}

        </div>

      </div>

    );
  }


  // =========================================
  // UI
  // =========================================

  return (

    <div className="app">


      {/* =====================================
          SIDEBAR
          ===================================== */}

      <aside className="sidebar">


        {/* Brand */}

        <div className="brand">

          <div className="brand-logo">
            A
          </div>


          <div>

            <h1>
              AgentOS
            </h1>

            <p>
              AI Agent Platform
            </p>

          </div>

        </div>


        {/* New Chat */}

        <button
          className="new-chat-button"
          onClick={startNewChat}
        >

          <span>
            ＋
          </span>

          New Chat

        </button>


        {/* Tools */}

        <div className="tools-section">

          <div className="section-title">
            TOOLS
          </div>


          <div className="tool-sidebar-item">

            <span>
              🧮
            </span>

            <span>
              Calculator
            </span>

            <span className="status-dot" />

          </div>


          <div className="tool-sidebar-item">

            <span>
              🌐
            </span>

            <span>
              Web Search
            </span>

            <span className="status-dot" />

          </div>


          <div className="tool-sidebar-item">

            <span>
              📁
            </span>

            <span>
              Filesystem
            </span>

            <span className="status-dot" />

          </div>


          <div className="tool-sidebar-item">

            <span>
              🔌
            </span>

            <span>
              MCP
            </span>

            <span className="status-dot" />

          </div>

        </div>


        {/* Sidebar Bottom */}

        <div className="sidebar-bottom">


          {/* Backend Status */}

          <div className="backend-status">

            <span
              className={`backend-dot ${
                backendOnline
                  ? "online"
                  : backendStarting
                    ? "starting"
                    : "offline"
              }`}
            />


            <span>

              {backendOnline
                ? "Backend connected"
                : backendStarting
                  ? "Starting backend..."
                  : "Backend offline"}

            </span>

          </div>


          {/* Version */}

          <div className="version">
            AgentOS v0.1.0
          </div>

        </div>

      </aside>


      {/* =====================================
          MAIN
          ===================================== */}

      <main className="main">


        {/* Header */}

        <header className="header">


          <div>

            <h2>
              Agent Workspace
            </h2>


            <p>
              Tool-using AI agent powered by
              Gemini + LangGraph
            </p>

          </div>


          {/* Online Badge */}

          <div
            className={`online-badge ${
              backendOnline
                ? "online"
                : backendStarting
                  ? "starting"
                  : "offline"
            }`}
          >

            <span className="online-dot" />


            {backendOnline
              ? "Online"
              : backendStarting
                ? "Starting..."
                : "Offline"}

          </div>

        </header>


        {/* ===================================
            CHAT
            =================================== */}

        <div className="chat-container">


          {/* Welcome */}

          {messages.length === 0 && (

            <div className="welcome">

              <div className="welcome-logo">
                A
              </div>


              <h3>
                Welcome to AgentOS
              </h3>


              <p>
                Ask me to calculate, search
                the web, manage files, or
                use connected MCP tools.
              </p>

            </div>

          )}


          {/* Messages */}

          {messages.map(
            (message) => (

              <div
                className={`message-row ${
                  message.role
                }`}
                key={message.id}
              >


                {/* Avatar */}

                <div className="avatar">

                  {message.role === "user"
                    ? "You"
                    : "A"}

                </div>


                {/* Content */}

                <div className="message-content">


                  {/* Author */}

                  <div className="message-author">

                    {message.role === "user"
                      ? "You"
                      : "AgentOS"}

                  </div>


                  {/* Tool Activity */}

                  {message.role ===
                    "assistant" &&
                    renderToolActivity(
                      message.tools
                    )}


                  {/* Message */}

                  <div className="message-text">

                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>

                  </div>

                </div>

              </div>

            )
          )}


          {/* Loading */}

          {loading && (

            <div className="message-row assistant">

              <div className="avatar">
                A
              </div>


              <div className="message-content">

                <div className="message-author">
                  AgentOS
                </div>


                <div className="typing-indicator">

                  <span />
                  <span />
                  <span />

                </div>

              </div>

            </div>

          )}


          <div ref={messagesEndRef} />

        </div>


        {/* ===================================
            INPUT
            =================================== */}

        <div className="input-area">


          <div className="input-wrapper">


            <textarea
              value={input}

              onChange={(event) =>
                setInput(
                  event.target.value
                )
              }

              onKeyDown={handleKeyDown}

              placeholder={
                backendOnline
                  ? "Ask AgentOS anything..."
                  : backendStarting
                    ? "Starting AgentOS backend..."
                    : "Backend unavailable"
              }

              rows={1}

              disabled={
                loading ||
                !backendOnline
              }

            />


            <button
              className="send-button"

              onClick={sendMessage}

              disabled={
                !input.trim() ||
                loading ||
                !backendOnline
              }

              aria-label="Send message"
            >

              ↑

            </button>

          </div>


          <div className="input-hint">

            {backendOnline
              ? "AgentOS can use tools when needed · Enter to send · Shift + Enter for new line"
              : backendStarting
                ? "Waking up the AgentOS backend..."
                : "AgentOS backend is unavailable"}

          </div>

        </div>

      </main>

    </div>

  );
}


export default App;