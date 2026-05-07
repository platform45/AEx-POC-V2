"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { postQuery } from "@/lib/api";
import type { QueryResponse } from "@/lib/api";

type Message =
  | { role: "user"; text: string }
  | { role: "assistant"; response: QueryResponse };

// Renders query result rows as a dynamic table
function DataTable({ data }: { data: Record<string, unknown>[] }) {
  const columns = Object.keys(data[0]);

  return (
    <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm">
      <div className="px-3 py-2 bg-gray-50 border-b border-gray-200 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Data
        </span>
      </div>
      <div className="overflow-x-auto bg-white">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-100">
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-2.5 text-left text-gray-500 font-semibold uppercase tracking-wider"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.map((row, i) => (
              <tr key={i} className="hover:bg-blue-50/50 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2.5 text-gray-700 font-medium">
                    {String(row[col] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Small AEx icon used in the assistant avatar
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
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
        />
      </svg>
    </div>
  );
}

// Assistant response card with answer, dark SQL block, and data table
function AssistantMessage({ response }: { response: QueryResponse }) {
  return (
    <div className="flex gap-3 items-start">
      <AExIcon />

      <div className="flex-1 space-y-3 min-w-0">
        {/* Markdown-rendered answer */}
        <div className="bg-white rounded-2xl rounded-tl-sm border border-gray-200 shadow-sm px-4 py-3 text-sm text-gray-800 leading-relaxed">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Headings
              h1: ({ children }) => (
                <h1 className="text-base font-bold text-gray-900 mb-2 mt-1">{children}</h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-sm font-bold text-gray-900 mb-2 mt-3">{children}</h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-sm font-semibold text-gray-800 mb-1.5 mt-2">{children}</h3>
              ),
              // Paragraphs
              p: ({ children }) => (
                <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>
              ),
              // Bold and italic
              strong: ({ children }) => (
                <strong className="font-semibold text-gray-900">{children}</strong>
              ),
              em: ({ children }) => (
                <em className="italic text-gray-700">{children}</em>
              ),
              // Bullet and numbered lists
              ul: ({ children }) => (
                <ul className="list-disc list-inside space-y-1 mb-2 pl-1">{children}</ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-inside space-y-1 mb-2 pl-1">{children}</ol>
              ),
              li: ({ children }) => (
                <li className="text-gray-700">{children}</li>
              ),
              // Inline code
              code: ({ children }) => (
                <code className="bg-gray-100 text-blue-700 rounded px-1 py-0.5 text-xs font-mono">
                  {children}
                </code>
              ),
              // GFM tables
              table: ({ children }) => (
                <div className="overflow-x-auto my-2 rounded-lg border border-gray-200">
                  <table className="w-full text-xs">{children}</table>
                </div>
              ),
              thead: ({ children }) => (
                <thead className="bg-gray-50 border-b border-gray-200">{children}</thead>
              ),
              th: ({ children }) => (
                <th className="px-3 py-2 text-left font-semibold text-gray-600 uppercase tracking-wider">
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td className="px-3 py-2 text-gray-700 border-t border-gray-100">{children}</td>
              ),
              // Horizontal rule
              hr: () => <hr className="border-gray-200 my-3" />,
              // Blockquote
              blockquote: ({ children }) => (
                <blockquote className="border-l-2 border-blue-400 pl-3 text-gray-600 italic my-2">
                  {children}
                </blockquote>
              ),
            }}
          >
            {response.answer}
          </ReactMarkdown>
        </div>

        {/* SQL block with dark code theme */}
        {response.sql && (
          <div className="rounded-xl overflow-hidden border border-gray-800 shadow-sm">
            <div className="px-3 py-2 bg-gray-900 border-b border-gray-700 flex items-center gap-2">
              <div className="flex gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500/60" />
                <span className="w-2 h-2 rounded-full bg-yellow-500/60" />
                <span className="w-2 h-2 rounded-full bg-green-500/60" />
              </div>
              <span className="text-xs text-gray-400 ml-1 font-medium">
                SQL Query
              </span>
            </div>
            <pre className="px-4 py-3 text-xs font-mono text-emerald-400 bg-gray-950 overflow-x-auto whitespace-pre-wrap leading-relaxed">
              {response.sql}
            </pre>
          </div>
        )}

        {/* Results table */}
        {response.data && response.data.length > 0 && (
          <DataTable data={response.data} />
        )}
      </div>
    </div>
  );
}

export default function QueryPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function submit() {
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    try {
      const result = await postQuery(question);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", response: result },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          response: {
            answer: "Something went wrong. Please try again.",
            sql: null,
            data: null,
          },
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  // Submit on Enter, Shift+Enter for newline
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
        <div className="max-w-3xl mx-auto flex items-center gap-2.5">
          <AExIcon />
          <div>
            <h1 className="text-sm font-semibold text-gray-900 leading-none">
              Ask AEx
            </h1>
            <p className="text-xs text-gray-400 mt-0.5">
              Network diagnostics assistant
            </p>
          </div>
        </div>
      </header>

      {/* Message list */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">
          {/* Empty state with suggestion chips */}
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="w-10 h-10 rounded-2xl bg-blue-600 flex items-center justify-center mb-4 shadow-md">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
              <h2 className="text-base font-semibold text-gray-800">
                Ask a question
              </h2>
              <p className="text-sm text-gray-400 mt-1.5 max-w-xs leading-relaxed">
                Query your network diagnostics in plain language
              </p>
              {/* Clickable suggestion chips */}
              <div className="flex flex-wrap gap-2 mt-5 justify-center">
                {[
                  "How many issues this week?",
                  "Show unresolved cases",
                  "Most affected devices",
                ].map((s) => (
                  <button
                    key={s}
                    onClick={() => setInput(s)}
                    className="text-xs border border-gray-200 rounded-full px-3 py-1.5 text-gray-600 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50 transition-colors bg-white shadow-sm cursor-pointer"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Render messages */}
          {messages.map((msg, i) =>
            msg.role === "user" ? (
              // User message — right-aligned blue bubble with small user avatar
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
              <AssistantMessage key={i} response={msg.response} />
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

      {/* Input bar — floating card style */}
      <div className="bg-gray-50 border-t border-gray-200 px-4 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-md flex items-end gap-2 px-4 py-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your network diagnostics..."
              rows={1}
              className="flex-1 resize-none text-sm text-gray-900 placeholder-gray-400 focus:outline-none leading-relaxed bg-transparent"
            />
            {/* Icon-only send button */}
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
        </div>
      </div>
    </div>
  );
}
