import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import { request, streamSSE } from "../lib/api";
import type { ChatMessage, Citation, DocumentOut } from "../lib/types";

type DisplayMessage = Pick<ChatMessage, "role" | "content" | "citations">;

function CitationChips({ citations }: { citations: Citation[] | null }) {
  if (!citations || citations.length === 0) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {citations.map((c) => (
        <span
          key={c.n}
          title={`${c.filename}${c.page ? ` · p. ${c.page}` : ""}\n\n${c.quote}…`}
          className="cursor-help rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 hover:bg-indigo-100"
        >
          [{c.n}] {c.page !== null ? `p. ${c.page}` : c.filename}
        </span>
      ))}
    </div>
  );
}

export function ChatPanel({ doc }: { doc: DocumentOut }) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void (async () => {
      try {
        const history = await request<ChatMessage[]>(`/documents/${doc.id}/messages`);
        setMessages(history.map(({ role, content, citations }) => ({ role, content, citations })));
      } catch {
        /* start with an empty thread */
      }
    })();
  }, [doc.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const ask = async (question: string) => {
    setError(null);
    setStreaming(true);
    setMessages((m) => [
      ...m,
      { role: "user", content: question, citations: null },
      { role: "assistant", content: "", citations: null },
    ]);
    try {
      for await (const event of streamSSE<{
        type: string;
        text?: string;
        citations?: Citation[];
        error?: string;
      }>(`/documents/${doc.id}/chat?stream=true`, { question })) {
        if (event.type === "citations") {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = {
              ...copy[copy.length - 1],
              citations: event.citations ?? null,
            };
            return copy;
          });
        } else if (event.type === "delta") {
          setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = {
              ...copy[copy.length - 1],
              content: copy[copy.length - 1].content + (event.text ?? ""),
            };
            return copy;
          });
        } else if (event.type === "error") {
          throw new Error(event.error ?? "Stream failed");
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get an answer");
    } finally {
      setStreaming(false);
    }
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || streaming) return;
    setInput("");
    void ask(question);
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto">
        {messages.length === 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white py-12 text-center">
            <div className="text-2xl">💬</div>
            <p className="mt-2 text-sm text-slate-500">Ask anything about this document.</p>
            <p className="mt-1 text-xs text-slate-400">
              e.g. “What is the notice period for termination?” · “Who are the parties?”
            </p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                m.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "border border-slate-200 bg-white text-slate-700"
              }`}
            >
              {m.role === "assistant" ? (
                <>
                  <Markdown>{m.content || "…"}</Markdown>
                  <CitationChips citations={m.citations} />
                </>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <form onSubmit={submit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this document…"
          disabled={streaming}
          className="flex-1 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={streaming || !input.trim()}
          className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-50"
        >
          {streaming ? "…" : "Ask"}
        </button>
      </form>
    </div>
  );
}
