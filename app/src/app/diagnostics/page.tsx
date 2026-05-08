"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { startIssueSession, respondToIssueSession } from "@/lib/api";

// resolved and escalated are only set on the final assistant message to
// trigger the correct colour styling once the conversation ends
type Message = {
  role: "user" | "assistant";
  text: string;
  resolved?: boolean;
  escalated?: boolean;
};

function AExIcon() {
  return (
    <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0 shadow-sm">
      <svg
        className="w-3.5 h-3.5 text-white"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2.5}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    </div>
  );
}

// Bubble for an agent message, coloured by outcome when the session ends
function AssistantBubble({ message }: { message: Message }) {
  const base = "flex-1 min-w-0 rounded-2xl rounded-tl-sm border shadow-sm px-4 py-3 text-sm leading-relaxed";
  const colour = message.escalated
    ? `${base} border-amber-200 bg-amber-50 text-amber-900`
    : message.resolved
    ? `${base} border-green-200 bg-green-50 text-green-900`
    : `${base} border-gray-200 bg-white text-gray-800`;

  return (
    <div className="flex gap-3 items-start">
      <AExIcon />
      <div className={colour}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
      </div>
    </div>
  );
}

export default function DiagnosticsPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [escalated, setEscalated] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Start a session automatically when the page loads
  useEffect(() => {
    beginSession();
  }, []);

  // Keep the latest message in view
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Resets all session state before starting fresh so previous messages
  // and session ID never bleed into the new conversation
  async function beginSession() {
    setLoading(true);
    setDone(false);
    setEscalated(false);
    setMessages([]);
    setInput("");
    setSessionId(null);
    try {
      const result = await startIssueSession();
      setSessionId(result.session_id);
      setMessages([{ role: "assistant", text: result.message }]);
    } catch {
      setMessages([
        { role: "assistant", text: "Failed to connect. Please refresh and try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Sends the user's input to the backend and appends both sides of the turn.
  // resolved/escalated flags are derived here so AssistantBubble can style
  // the final message without needing to know about the session lifecycle.
  async function submit() {
    const text = input.trim();
    if (!text || loading || done || !sessionId) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);

    try {
      const result = await respondToIssueSession(sessionId, text);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: result.message,
          resolved: result.done && !result.escalated,
          escalated: result.done && result.escalated,
        },
      ]);
      setDone(result.done);
      setEscalated(result.escalated);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Enter submits; Shift+Enter inserts a newline
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 shadow-sm">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <AExIcon />
            <div>
              <h1 className="text-sm font-semibold text-gray-900 leading-none">
                Issue Resolution
              </h1>
              <p className="text-xs text-gray-400 mt-0.5">
                AI-guided network issue diagnostics
              </p>
            </div>
          </div>
          {/* Show restart button once a session ends */}
          {done && (
            <button
              onClick={beginSession}
              className="text-xs font-medium text-blue-600 border border-blue-200 rounded-lg px-3 py-1.5 hover:bg-blue-50 transition-colors cursor-pointer"
            >
              New session
            </button>
          )}
        </div>
      </header>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
          {messages.map((msg, i) =>
            msg.role === "user" ? (
              // Right-aligned user bubble
              <div key={i} className="flex justify-end gap-2.5 items-start">
                <div className="bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 max-w-sm text-sm leading-relaxed shadow-sm">
                  {msg.text}
                </div>
                <div className="w-7 h-7 rounded-lg bg-gray-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg
                    className="w-3.5 h-3.5 text-gray-500"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z" />
                  </svg>
                </div>
              </div>
            ) : (
              <AssistantBubble key={i} message={msg} />
            )
          )}

          {/* Typing indicator */}
          {loading && (
            <div className="flex gap-3 items-start">
              <AExIcon />
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm flex gap-1.5 items-center">
                {[0, 150, 300].map((delay) => (
                  <span
                    key={delay}
                    className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input bar */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-4">
        <div className="max-w-3xl mx-auto">
          {done ? (
            // Session ended — show outcome and offer restart
            <p
              className={`text-center text-sm font-medium py-2 ${
                escalated ? "text-amber-600" : "text-green-600"
              }`}
            >
              {escalated ? "Escalated to support." : "Issue resolved."}{" "}
              <button
                onClick={beginSession}
                className="underline underline-offset-2 cursor-pointer"
              >
                Start a new session
              </button>
            </p>
          ) : (
            <>
              <div className="bg-white rounded-2xl border border-gray-200 shadow-md flex items-end gap-2 px-4 py-3">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your response..."
                  rows={1}
                  disabled={loading}
                  className="flex-1 resize-none text-sm text-gray-900 placeholder-gray-400 focus:outline-none leading-relaxed bg-transparent disabled:opacity-50"
                />
                <button
                  onClick={submit}
                  disabled={!input.trim() || loading}
                  className="w-8 h-8 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 flex items-center justify-center transition-colors flex-shrink-0 cursor-pointer disabled:cursor-not-allowed"
                >
                  <svg
                    className="w-3.5 h-3.5 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2.5}
                      d="M12 19V5m0 0l-7 7m7-7l7 7"
                    />
                  </svg>
                </button>
              </div>
              <p className="text-xs text-gray-400 mt-2 text-center">
                Enter to send · Shift+Enter for new line
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
