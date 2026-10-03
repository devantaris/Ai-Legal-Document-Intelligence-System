import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { request } from "../lib/api";
import type { DocumentOut } from "../lib/types";
import { StatusBadge } from "../components/StatusBadge";
import { SummaryPanel } from "../components/SummaryPanel";
import { KeyTermsPanel } from "../components/KeyTermsPanel";
import { ClausesPanel } from "../components/ClausesPanel";
import { ChatPanel } from "../components/ChatPanel";

const TABS = ["Summary", "Key Terms", "Clauses", "Chat"] as const;
type Tab = (typeof TABS)[number];

export function DocumentPage() {
  const { id } = useParams<{ id: string }>();
  const [doc, setDoc] = useState<DocumentOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Summary");

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const d = await request<DocumentOut>(`/documents/${id}`);
        if (active) {
          setDoc(d);
          setError(null);
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load document");
      }
    };
    void load();
    // poll while the document is processing
    const t = setInterval(() => {
      if (doc && ["uploaded", "parsing", "embedding"].includes(doc.status)) void load();
    }, 2500);
    return () => {
      active = false;
      clearInterval(t);
    };
  }, [id, doc?.status]);

  if (error)
    return (
      <div className="p-8">
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
        <Link to="/" className="mt-4 inline-block text-sm text-indigo-600 hover:underline">
          ← Back to documents
        </Link>
      </div>
    );
  if (!doc) return <div className="p-8 text-sm text-slate-400">Loading…</div>;

  const busy = ["uploaded", "parsing", "embedding"].includes(doc.status);

  return (
    <div className="mx-auto flex h-full max-w-5xl flex-col px-8 py-6">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <Link to="/" className="text-xs text-slate-400 hover:text-indigo-600">
            ← All documents
          </Link>
          <h1 className="mt-1 truncate text-xl font-bold text-slate-900">{doc.filename}</h1>
          <div className="mt-1.5 flex items-center gap-3 text-xs text-slate-500">
            <StatusBadge status={doc.status} />
            {doc.page_count !== null && <span>{doc.page_count} pages</span>}
            <span>{doc.chunk_count} indexed chunks</span>
            {doc.clause_count > 0 && <span>{doc.clause_count} clauses</span>}
          </div>
          {doc.error && (
            <div className="mt-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
              {doc.error}
            </div>
          )}
        </div>
      </div>

      {busy ? (
        <div className="mt-10 flex flex-col items-center rounded-2xl border border-slate-200 bg-white py-16 text-slate-500">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
          <p className="mt-4 text-sm">Processing document — extracting text, chunking and indexing…</p>
          <p className="mt-1 text-xs text-slate-400">This page updates automatically.</p>
        </div>
      ) : doc.status === "failed" ? (
        <div className="mt-10 rounded-2xl border border-red-200 bg-red-50 p-8 text-sm text-red-700">
          Ingestion failed: {doc.error ?? "unknown error"}
        </div>
      ) : (
        <>
          <div className="mt-5 flex gap-1 border-b border-slate-200">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
                  tab === t
                    ? "border-indigo-600 text-indigo-700"
                    : "border-transparent text-slate-500 hover:text-slate-800"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto pt-6 pb-10">
            {tab === "Summary" && <SummaryPanel doc={doc} />}
            {tab === "Key Terms" && <KeyTermsPanel doc={doc} />}
            {tab === "Clauses" && <ClausesPanel doc={doc} />}
            {tab === "Chat" && <ChatPanel doc={doc} />}
          </div>
        </>
      )}
    </div>
  );
}
