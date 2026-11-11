import { useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import { Send, Loader2, ExternalLink, X, ShieldCheck, CheckCircle2, AlertCircle } from "lucide-react";
import { request, streamSSE } from "../lib/api";
import type { ChatMessage, Citation, DocumentOut, EntailmentAuditOut } from "../lib/types";

type DisplayMessage = Pick<ChatMessage, "role" | "content" | "citations">;

interface Props {
  doc: DocumentOut;
  onSelectCitation?: (citation: Citation) => void;
}

export function ChatPanel({ doc, onSelectCitation }: Props) {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [audits, setAudits] = useState<Record<number, EntailmentAuditOut>>({});
  const [auditingIdx, setAuditingIdx] = useState<number | null>(null);
  const [activeAuditModal, setActiveAuditModal] = useState<EntailmentAuditOut | null>(null);
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

  const handleAudit = async (msgIdx: number, content: string, citations: Citation[] | null) => {
    if (!citations || citations.length === 0) return;
    setAuditingIdx(msgIdx);
    try {
      const res = await request<EntailmentAuditOut>("/chat/audit", {
        method: "POST",
        body: JSON.stringify({ answer: content, citations }),
      });
      setAudits((prev) => ({ ...prev, [msgIdx]: res }));
      setActiveAuditModal(res);
    } catch (err) {
      console.error("Entailment audit failed", err);
    } finally {
      setAuditingIdx(null);
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
    <div className="flex h-[600px] flex-col rounded-xl border border-neutral-200 bg-white p-4 relative shadow-xs">
      {/* Messages Scroll Area */}
      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto pr-1">
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
              className={`max-w-[85%] rounded-lg p-3.5 text-xs sm:text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-neutral-900 text-white"
                  : "border border-neutral-200 bg-neutral-50/70 text-neutral-800"
              }`}
            >
              {m.role === "assistant" ? (
                <>
                  <div className="prose-xs max-w-none text-neutral-800 [&_p]:my-1.5 [&_ul]:my-1.5 [&_ul]:list-disc [&_ul]:pl-4 [&_li]:my-0.5 [&_strong]:text-neutral-950 font-serif">
                    <Markdown>{m.content || "Searching document…"}</Markdown>
                  </div>

                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-neutral-200/80 flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap gap-1.5 items-center">
                        <span className="text-[10px] text-neutral-400 font-mono mr-1">Citations:</span>
                        {m.citations.map((c) => (
                          <button
                            key={c.n}
                            onClick={() => {
                              setActiveCitation(c);
                              if (onSelectCitation) onSelectCitation(c);
                            }}
                            className="flex items-center gap-1 rounded bg-white border border-neutral-200 px-2 py-0.5 text-[10px] font-mono text-neutral-700 hover:text-neutral-950 hover:border-neutral-400 transition"
                            title="Inspect in document"
                          >
                            <span>
                              [{c.n}] {c.page !== null ? `p. ${c.page}` : "Doc"}
                            </span>
                            <ExternalLink className="h-2.5 w-2.5 opacity-50" />
                          </button>
                        ))}
                      </div>

                      {/* Entailment Audit Trigger */}
                      <div>
                        {audits[i] ? (
                          <button
                            onClick={() => setActiveAuditModal(audits[i])}
                            className="inline-flex items-center gap-1 rounded border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-800 hover:bg-emerald-100 transition"
                          >
                            <ShieldCheck className="h-3 w-3 text-emerald-600" />
                            <span>{audits[i].status_label}</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => handleAudit(i, m.content, m.citations)}
                            disabled={auditingIdx === i}
                            className="inline-flex items-center gap-1 rounded border border-neutral-200 bg-white px-2 py-0.5 text-[10px] font-medium text-neutral-600 hover:text-neutral-900 hover:border-neutral-300 transition"
                            title="Verify sentence-level entailment against cited snippets"
                          >
                            {auditingIdx === i ? (
                              <Loader2 className="h-3 w-3 animate-spin text-neutral-400" />
                            ) : (
                              <ShieldCheck className="h-3 w-3 text-neutral-500" />
                            )}
                            <span>Audit Entailment</span>
                          </button>
                        )}
                      </div>
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
              <blockquote className="rounded-lg border-l-2 border-neutral-900 bg-neutral-50 p-3 text-xs italic text-neutral-700 leading-relaxed font-serif">
                "{activeCitation.quote}"
              </blockquote>
            </div>

            <div className="mt-4 flex justify-between items-center">
              {onSelectCitation && (
                <button
                  onClick={() => {
                    onSelectCitation(activeCitation);
                    setActiveCitation(null);
                  }}
                  className="text-xs text-neutral-600 hover:text-neutral-900 underline font-medium"
                >
                  Locate in Split Canvas
                </button>
              )}
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

      {/* Entailment Audit Modal */}
      {activeAuditModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-xl border border-neutral-200 bg-white p-5 shadow-xl max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between border-b border-neutral-100 pb-3 mb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-600" />
                <h4 className="text-xs font-semibold text-neutral-900">Entailment & Fidelity Certificate</h4>
                <span className="rounded bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 text-[10px] font-bold text-emerald-800">
                  {Math.round(activeAuditModal.fidelity_score * 100)}% Match
                </span>
              </div>
              <button
                onClick={() => setActiveAuditModal(null)}
                className="text-neutral-400 hover:text-neutral-800"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <p className="text-[11px] text-neutral-600 mb-3">
              Every sentence in the generated legal answer is mathematically evaluated against the cited
              contract passages to guarantee claims are strictly grounded in fact.
            </p>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
              {activeAuditModal.sentence_audits.map((item) => (
                <div
                  key={item.sentence_index}
                  className={`rounded-lg border p-3 ${
                    item.status === "VERIFIED"
                      ? "border-emerald-200/80 bg-emerald-50/30"
                      : item.status === "EXTRAPOLATED"
                      ? "border-amber-200 bg-amber-50/30"
                      : "border-rose-200 bg-rose-50/40"
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] font-semibold mb-1">
                    <span className="flex items-center gap-1">
                      {item.status === "VERIFIED" ? (
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                      ) : (
                        <AlertCircle className="h-3 w-3 text-amber-600" />
                      )}
                      Claim #{item.sentence_index} ({item.status})
                    </span>
                    <span className="font-mono text-neutral-400">
                      Entailment: {Math.round(item.entailment_score * 100)}%
                    </span>
                  </div>
                  <p className="font-serif text-neutral-900 mb-2">"{item.sentence_text}"</p>
                  {item.supporting_quote && (
                    <div className="text-[10px] text-neutral-500 bg-white/70 rounded p-1.5 border border-neutral-100">
                      <strong>Supporting Evidence:</strong> "{item.supporting_quote}"
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-4 pt-3 border-t border-neutral-100 flex justify-end">
              <button
                onClick={() => setActiveAuditModal(null)}
                className="rounded-lg bg-neutral-900 px-4 py-1.5 text-xs font-medium text-white hover:bg-neutral-800"
              >
                Close Audit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
