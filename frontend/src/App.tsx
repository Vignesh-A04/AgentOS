import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

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

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [backendOnline, setBackendOnline] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function checkBackend() {
    try {
      const response = await fetch(`${API_URL}/health`);

      setBackendOnline(response.ok);
    } catch {
      setBackendOnline(false);
    }
  }

  useEffect(() => {
    checkBackend();

    const interval = setInterval(checkBackend, 10000);

    return () => clearInterval(interval);
  }, []);

  async function sendMessage() {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: message,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        `${API_URL}/agent/run`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        body: JSON.stringify({
          message,
          history: messages.map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Backend returned ${response.status}`
        );
      }

      const data: AgentResponse =
        await response.json();

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          data.response ||
          "I couldn't generate a response.",
        tools: data.tools || [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);

      setBackendOnline(true);
    } catch (error) {
      console.error(error);

      setBackendOnline(false);

      const errorMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          "Sorry, I couldn't connect to the AgentOS backend.",
      };

      setMessages((previous) => [
        ...previous,
        errorMessage,
      ]);
    } finally {
      setLoading(false);
    }
  }

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

  function startNewChat() {
    setMessages([]);
    setInput("");
  }

  function formatValue(value: unknown): string {
    if (value === null || value === undefined) {
      return "";
    }

    if (typeof value === "string") {
      return value;
    }

    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

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
        tool.result.length === 1 ? "" : "s"
      } found`;
    }

    return formatValue(tool.result);
  }

  function getToolIcon(name: string) {
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

  function renderToolActivity(
    tools?: ToolCall[]
  ) {
    if (!tools || tools.length === 0) {
      return null;
    }

    return (
      <div className="agent-activity">
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

        <div className="activity-list">
          {tools.map((tool, index) => (
            <div
              className="tool-card"
              key={`${tool.name}-${index}`}
            >
              <div className="tool-top">
                <div className="tool-name">
                  <span className="tool-success">
                    ✓
                  </span>

                  <span className="tool-icon">
                    {getToolIcon(tool.name)}
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

              {tool.arguments &&
                Object.keys(tool.arguments)
                  .length > 0 && (
                  <div className="tool-arguments">
                    {formatArguments(
                      tool.arguments
                    )}
                  </div>
                )}

              <div className="tool-result">
                <span className="result-label">
                  Result:
                </span>

                <span>
                  {getToolResult(tool)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">
            A
          </div>

          <div>
            <h1>AgentOS</h1>

            <p>
              AI Agent Platform
            </p>
          </div>
        </div>

        <button
          className="new-chat-button"
          onClick={startNewChat}
        >
          <span>＋</span>
          New Chat
        </button>

        <div className="tools-section">
          <div className="section-title">
            TOOLS
          </div>

          <div className="tool-sidebar-item">
            <span>🧮</span>
            <span>Calculator</span>
            <span className="status-dot" />
          </div>

          <div className="tool-sidebar-item">
            <span>🌐</span>
            <span>Web Search</span>
            <span className="status-dot" />
          </div>

          <div className="tool-sidebar-item">
            <span>📁</span>
            <span>Filesystem</span>
            <span className="status-dot" />
          </div>

          <div className="tool-sidebar-item">
            <span>🔌</span>
            <span>MCP</span>
            <span className="status-dot" />
          </div>
        </div>

        <div className="sidebar-bottom">
          <div className="backend-status">
            <span
              className={`backend-dot ${
                backendOnline
                  ? "online"
                  : "offline"
              }`}
            />

            <span>
              {backendOnline
                ? "Backend connected"
                : "Backend offline"}
            </span>
          </div>

          <div className="version">
            AgentOS v0.1.0
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <main className="main">
        {/* HEADER */}
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

          <div
            className={`online-badge ${
              backendOnline
                ? "online"
                : "offline"
            }`}
          >
            <span className="online-dot" />

            {backendOnline
              ? "Online"
              : "Offline"}
          </div>
        </header>

        {/* CHAT */}
        <div className="chat-container">
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

          {messages.map((message) => (
            <div
              className={`message-row ${
                message.role
              }`}
              key={message.id}
            >
              <div className="avatar">
                {message.role === "user"
                  ? "You"
                  : "A"}
              </div>

              <div className="message-content">
                <div className="message-author">
                  {message.role === "user"
                    ? "You"
                    : "AgentOS"}
                </div>

                {message.role ===
                  "assistant" &&
                  renderToolActivity(
                    message.tools
                  )}

                <div className="message-text">
                  <ReactMarkdown>
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          ))}

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

        {/* INPUT */}
        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask AgentOS anything..."
              rows={1}
              disabled={loading}
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
            AgentOS can use tools when needed
            · Enter to send
            · Shift + Enter for new line
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;