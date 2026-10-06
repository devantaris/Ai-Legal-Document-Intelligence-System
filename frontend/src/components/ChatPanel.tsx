import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import { Send, Loader2, ExternalLink, X } from "lucide-react";
import { request, streamSSE } from "../lib/api";
import type { ChatMessage, Citation, DocumentOut } from "../lib/types";

type DisplayMessage = Pick<ChatMessage, "role" | "content" | "citations">;

export function ChatPanel({ doc }: { doc: DocumentOut }) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void (async () => {
      try {
        const history = await request<ChatMessage[]>(`/documents/${doc.id}/messages`);
        setMessages(history.map(({ role, content, citations }) => ({ role, content, citations })));
      } catch {
        /* thread starts clean */
      }
    })();
  }, [doc.id]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming]);

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
      setError(err instanceof Error ? err.message : "Failed to generate answer");
    } finally {
      setStreaming(false);
    }
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || streaming) return;
    setInput("");
    void ask(q);
  };

  return (
    <div className="flex h-[560px] flex-col rounded-xl border border-neutral-200 bg-white p-4 relative">
      {/* Messages Scroll Area */}
      <div className="min-h-0 flex-1 space-y-3.5 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-xs text-neutral-400">
            Ask any question grounded in this agreement.
            <span className="text-[11px] text-neutral-400 mt-1">
              e.g. "What is the governing law?" · "Summarize termination terms"
            </span>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-lg p-3 text-xs sm:text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-neutral-900 text-white"
                  : "border border-neutral-200 bg-neutral-50/60 text-neutral-800"
              }`}
            >
              {m.role === "assistant" ? (
                <>
                  <div className="prose-xs max-w-none text-neutral-800 [&_p]:my-1.5 [&_ul]:my-1.5 [&_ul]:list-disc [&_ul]:pl-4 [&_li]:my-0.5 [&_strong]:text-neutral-950">
                    <Markdown>{m.content || "Searching document…"}</Markdown>
                  </div>

                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-neutral-200/80 flex flex-wrap gap-1.5">
                      {m.citations.map((c) => (
                        <button
                          key={c.n}
                          onClick={() => setActiveCitation(c)}
                          className="flex items-center gap-1 rounded bg-white border border-neutral-200 px-2 py-0.5 text-[10px] font-mono text-neutral-600 hover:text-neutral-900 hover:border-neutral-300 transition"
                        >
                          <span>
                            [{c.n}] {c.page !== null ? `p. ${c.page}` : "Doc"}
                          </span>
                          <ExternalLink className="h-2.5 w-2.5 opacity-50" />
                        </button>
                      ))}
                    </div>
                  )}
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
        <div className="mt-2 rounded-lg bg-rose-50 border border-rose-200 p-2 text-xs text-rose-700">
          {error}
        </div>
      )}

      {/* Input */}
      <form onSubmit={submit} className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this contract..."
          disabled={streaming}
          className="flex-1 rounded-lg border border-neutral-200 bg-white px-3.5 py-2 text-xs text-neutral-900 placeholder-neutral-400 outline-none focus:border-neutral-400 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={streaming || !input.trim()}
          className="flex items-center gap-1.5 rounded-lg bg-neutral-900 px-4 py-2 text-xs font-medium text-white hover:bg-neutral-800 transition disabled:opacity-50"
        >
          {streaming ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
          <span>Ask</span>
        </button>
      </form>

      {/* Citation Popover Modal */}
      {activeCitation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
          <div className="w-full max-w-md rounded-xl border border-neutral-200 bg-white p-5 shadow-lg">
            <div className="flex items-center justify-between border-b border-neutral-100 pb-2 mb-3">
              <span className="text-xs font-medium text-neutral-500 font-mono">
                Citation [{activeCitation.n}] · Page {activeCitation.page ?? "N/A"}
              </span>
              <button
                onClick={() => setActiveCitation(null)}
                className="text-neutral-400 hover:text-neutral-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-2">
              <div className="text-[11px] font-mono text-neutral-400">
                {activeCitation.filename}
                {activeCitation.section_path && ` · ${activeCitation.section_path}`}
              </div>
              <blockquote className="rounded-lg border-l-2 border-neutral-900 bg-neutral-50 p-3 text-xs italic text-neutral-700 leading-relaxed">
                "{activeCitation.quote}"
              </blockquote>
            </div>

            <div className="mt-4 flex justify-end">
              <button
                onClick={() => setActiveCitation(null)}
                className="rounded-lg bg-neutral-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-neutral-800"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
