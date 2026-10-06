import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  GitCompare,
  ArrowLeft,
  Loader2,
} from "lucide-react";
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
  const navigate = useNavigate();
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
      <div className="mx-auto max-w-4xl p-8">
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
          <div className="font-semibold mb-1">Error</div>
          {error}
        </div>
        <Link
          to="/"
          className="mt-4 inline-flex items-center gap-1.5 text-xs text-neutral-600 hover:text-neutral-900"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to documents</span>
        </Link>
      </div>
    );

  if (!doc)
    return (
      <div className="flex h-full items-center justify-center p-8 text-xs text-neutral-400">
        Loading document…
      </div>
    );

  const busy = ["uploaded", "parsing", "embedding"].includes(doc.status);

  return (
    <div className="mx-auto flex h-full max-w-5xl flex-col px-8 py-6">
      {/* Top Bar */}
      <div className="flex items-start justify-between gap-4 border-b border-neutral-200/80 pb-4">
        <div>
          <Link
            to="/"
            className="inline-flex items-center gap-1 text-[11px] text-neutral-400 hover:text-neutral-700 transition mb-1"
          >
            <ArrowLeft className="h-3 w-3" />
            <span>All documents</span>
          </Link>
          <h1 className="truncate text-lg font-semibold text-neutral-900">{doc.filename}</h1>
          <div className="mt-1 flex items-center gap-2.5 text-xs text-neutral-500">
            <StatusBadge status={doc.status} />
            {doc.page_count !== null && <span>{doc.page_count} pages</span>}
            <span>{doc.chunk_count} chunks</span>
            {doc.clause_count > 0 && <span>{doc.clause_count} clauses</span>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate(`/compare?a=${doc.id}`)}
            className="flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
          >
            <GitCompare className="h-3.5 w-3.5" />
            <span>Compare</span>
          </button>
        </div>
      </div>

      {busy ? (
        <div className="mt-12 flex flex-col items-center justify-center rounded-xl border border-neutral-200 bg-white py-16 text-center">
          <Loader2 className="h-6 w-6 animate-spin text-neutral-500" />
          <div className="mt-3 text-xs font-medium text-neutral-700">
            Processing document — extracting text, chunking, and indexing
          </div>
          <div className="mt-1 text-[11px] text-neutral-400">Updates automatically</div>
        </div>
      ) : doc.status === "failed" ? (
        <div className="mt-6 rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-700">
          Ingestion failed: {doc.error ?? "unknown error"}
        </div>
      ) : (
        <>
          {/* Minimalist Tabs */}
          <div className="mt-4 flex border-b border-neutral-200">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`-mb-px border-b-2 px-4 py-2.5 text-xs font-medium transition ${
                  tab === t
                    ? "border-neutral-900 text-neutral-900 font-semibold"
                    : "border-transparent text-neutral-500 hover:text-neutral-800"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="min-h-0 flex-1 overflow-y-auto pt-5 pb-8">
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
