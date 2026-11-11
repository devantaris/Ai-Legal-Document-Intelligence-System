import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  GitCompare,
  ArrowLeft,
  Loader2,
  FileDown,
  Columns,
  Maximize2,
} from "lucide-react";
import { getAccessToken, request } from "../lib/api";
import type { Citation, DocumentOut, PlaybookFinding } from "../lib/types";
import { StatusBadge } from "../components/StatusBadge";
import { SummaryPanel } from "../components/SummaryPanel";
import { KeyTermsPanel } from "../components/KeyTermsPanel";
import { ClausesPanel } from "../components/ClausesPanel";
import { ChatPanel } from "../components/ChatPanel";
import { PlaybookReviewPanel } from "../components/PlaybookReviewPanel";
import { DocumentReader } from "../components/DocumentReader";

const TABS = ["Summary", "Key Terms", "Clauses", "Playbook Review", "Chat"] as const;
type Tab = (typeof TABS)[number];

export function DocumentPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [doc, setDoc] = useState<DocumentOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<Tab>("Summary");
  const [splitView, setSplitView] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [activeHighlight, setActiveHighlight] = useState<{
    chunk_id?: string;
    quote?: string;
    page?: number;
  } | null>(null);

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

  const handleExportDocx = async () => {
    if (!doc) return;
    setDownloading(true);
    try {
      const token = getAccessToken();
      const res = await fetch(`/api/documents/${doc.id}/export-redline-docx`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error("Failed to export redline docx");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${doc.filename.replace(/\.[^/.]+$/, "")}_LegalIQ_Redline.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Export failed");
    } finally {
      setDownloading(false);
    }
  };

  const handleSelectCitation = (citation: Citation) => {
    setSplitView(true);
    setActiveHighlight({
      chunk_id: citation.chunk_id,
      quote: citation.quote,
      page: citation.page ?? undefined,
    });
  };

  const handleSelectPlaybookFinding = (finding: PlaybookFinding) => {
    setSplitView(true);
    setActiveHighlight({
      chunk_id: finding.clause_id ?? undefined,
      quote: finding.clause_text.slice(0, 80),
      page: finding.page_start ?? undefined,
    });
  };

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
    <div
      className={`mx-auto flex h-full flex-col px-6 py-6 transition-all duration-300 ${
        splitView ? "max-w-[1700px]" : "max-w-5xl"
      }`}
    >
      {/* Top Action Bar */}
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-neutral-200/80 pb-4">
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
          {/* Split Screen / Full Screen Toggle */}
          <button
            onClick={() => setSplitView((v) => !v)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition ${
              splitView
                ? "bg-neutral-900 text-white border-neutral-900"
                : "bg-white text-neutral-700 border-neutral-200 hover:bg-neutral-50"
            }`}
            title="Toggle Side-by-Side Document Reader"
          >
            {splitView ? <Maximize2 className="h-3.5 w-3.5" /> : <Columns className="h-3.5 w-3.5" />}
            <span>{splitView ? "Single Pane" : "Split Canvas"}</span>
          </button>

          {/* Export Redline Word DOCX with Track Changes */}
          <button
            onClick={handleExportDocx}
            disabled={downloading || busy}
            className="flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 hover:text-neutral-900 transition disabled:opacity-50"
            title="Download Word Document with Tracked Changes & Comments"
          >
            {downloading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin text-neutral-400" />
            ) : (
              <FileDown className="h-3.5 w-3.5 text-neutral-600" />
            )}
            <span>Export Redline (.docx)</span>
          </button>

          {/* Compare */}
          <button
            onClick={() => navigate(`/compare?a=${doc.id}`)}
            className="flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
          >
            <GitCompare className="h-3.5 w-3.5 text-neutral-600" />
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
        <div className={`mt-4 flex-1 min-h-0 ${splitView ? "grid grid-cols-1 lg:grid-cols-2 gap-6" : ""}`}>
          {/* Left Pane: Document Canvas (When Split View is Enabled) */}
          {splitView && (
            <div className="h-[750px] overflow-hidden">
              <DocumentReader
                doc={doc}
                highlight={activeHighlight}
                onClearHighlight={() => setActiveHighlight(null)}
              />
            </div>
          )}

          {/* Right Pane (or Full View): Intelligence Panels */}
          <div className="flex flex-col h-full min-h-0">
            {/* Tabs */}
            <div className="flex border-b border-neutral-200 overflow-x-auto">
              {TABS.map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`-mb-px shrink-0 border-b-2 px-4 py-2.5 text-xs font-medium transition ${
                    tab === t
                      ? "border-neutral-900 text-neutral-900 font-semibold"
                      : "border-transparent text-neutral-500 hover:text-neutral-800"
                  }`}
                >
                  {t}
                  {t === "Playbook Review" && (
                    <span className="ml-1.5 rounded-full bg-rose-100 px-1.5 py-0.2 text-[9px] font-bold text-rose-800">
                      Audit
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="min-h-0 flex-1 overflow-y-auto pt-5 pb-8">
              {tab === "Summary" && <SummaryPanel doc={doc} />}
              {tab === "Key Terms" && <KeyTermsPanel doc={doc} />}
              {tab === "Clauses" && <ClausesPanel doc={doc} />}
              {tab === "Playbook Review" && (
                <PlaybookReviewPanel doc={doc} onSelectClause={handleSelectPlaybookFinding} />
              )}
              {tab === "Chat" && <ChatPanel doc={doc} onSelectCitation={handleSelectCitation} />}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
