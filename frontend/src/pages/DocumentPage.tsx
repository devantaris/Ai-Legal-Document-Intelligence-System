import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import {
  GitCompare,
  ArrowLeft,
  Loader2,
  FileDown,
  Columns,
  Maximize2,
  ShieldAlert,
  MessageSquare,
  FileText,
  Key,
  Layers,
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

interface TabDef {
  id: "Summary" | "Key Terms" | "Clauses" | "Playbook Review" | "Chat";
  label: string;
  icon: typeof FileText;
  badge?: string;
}

const TABS: readonly TabDef[] = [
  { id: "Summary", label: "Executive Brief", icon: FileText },
  { id: "Key Terms", label: "Key Terms & Parties", icon: Key },
  { id: "Clauses", label: "Clause Inventory", icon: Layers },
  { id: "Playbook Review", label: "Playbook Audit", icon: ShieldAlert, badge: "Risk" },
  { id: "Chat", label: "Grounded Legal Q&A", icon: MessageSquare, badge: "AI" },
];

type TabId = (typeof TABS)[number]["id"];

export function DocumentPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [doc, setDoc] = useState<DocumentOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>("Summary");
  const [splitView, setSplitView] = useState(true);
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
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-xs text-rose-800">
          <div className="font-bold text-sm mb-1 font-serif-legal">Agreement Retrieval Error</div>
          <p>{error}</p>
        </div>
        <Link
          to="/"
          className="mt-4 inline-flex items-center gap-1.5 text-xs text-neutral-600 hover:text-neutral-900 font-semibold"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Return to Agreements Docket</span>
        </Link>
      </div>
    );

  if (!doc)
    return (
      <div className="flex h-full items-center justify-center p-12 text-xs text-neutral-400">
        <Loader2 className="h-5 w-5 animate-spin text-amber-600 mr-2" />
        <span>Loading matter agreement…</span>
      </div>
    );

  const busy = ["uploaded", "parsing", "embedding"].includes(doc.status);

  return (
    <div className="flex flex-col h-full overflow-hidden bg-[#F8F9FA]">
      {/* Top Legal Action Ribbon */}
      <div className="border-b border-[#E2E8F0] bg-white px-6 py-3.5 shadow-2xs shrink-0">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="flex h-8 w-8 items-center justify-center rounded-lg border border-[#E2E8F0] bg-[#F8F9FA] text-neutral-600 hover:text-[#0F172A] hover:bg-neutral-100 transition shrink-0"
              title="Return to Docket"
            >
              <ArrowLeft className="h-4 w-4" />
            </Link>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-[#0F172A] font-serif-legal truncate max-w-xl">
                  {doc.filename}
                </h1>
                <StatusBadge status={doc.status} />
              </div>
              <div className="flex items-center gap-2.5 text-[11px] font-mono text-neutral-400 mt-0.5">
                <span>{doc.page_count ?? 0} Pages</span>
                <span>•</span>
                <span>{doc.clause_count} Extracted Clauses</span>
                <span>•</span>
                <span>{doc.chunk_count} Indexed Chunks</span>
                <span>•</span>
                <span>{(doc.size_bytes / (1024 * 1024)).toFixed(2)} MB</span>
              </div>
            </div>
          </div>

          {/* Quick Transaction Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSplitView((v) => !v)}
              className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition shadow-2xs ${
                splitView
                  ? "bg-[#0F172A] text-white border-[#0F172A]"
                  : "bg-white text-neutral-700 border-[#E2E8F0] hover:bg-[#F8F9FA]"
              }`}
              title="Toggle Dual-Pane Split Canvas"
            >
              {splitView ? <Maximize2 className="h-3.5 w-3.5" /> : <Columns className="h-3.5 w-3.5" />}
              <span>{splitView ? "Single Focus" : "Split Canvas"}</span>
            </button>

            <button
              onClick={handleExportDocx}
              disabled={downloading || busy}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-1.5 text-xs font-semibold text-[#0F172A] hover:bg-[#F8F9FA] transition disabled:opacity-50 shadow-2xs"
              title="Download Microsoft Word document with Track Changes XML tags"
            >
              {downloading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin text-neutral-400" />
              ) : (
                <FileDown className="h-3.5 w-3.5 text-amber-700" />
              )}
              <span>Export Redline (.docx)</span>
            </button>

            <button
              onClick={() => navigate(`/compare?a=${doc.id}`)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-[#F8F9FA] transition shadow-2xs"
            >
              <GitCompare className="h-3.5 w-3.5 text-neutral-500" />
              <span>Compare</span>
            </button>
          </div>
        </div>
      </div>

      {busy ? (
        <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-8 max-w-md shadow-sm">
            <Loader2 className="h-8 w-8 animate-spin text-amber-600 mx-auto mb-3" />
            <h3 className="text-sm font-bold text-[#0F172A] font-serif-legal">
              Ingesting Contract in Sovereign Worker
            </h3>
            <p className="mt-1 text-xs text-neutral-500 leading-relaxed">
              Extracting section hierarchy, indexing capitalized definitions, and computing vector embeddings with zero external egress.
            </p>
          </div>
        </div>
      ) : doc.status === "failed" ? (
        <div className="m-6 rounded-2xl border border-rose-200 bg-rose-50 p-6 text-xs text-rose-800">
          <div className="font-bold text-sm mb-1 font-serif-legal">Ingestion Failed</div>
          <p>{doc.error ?? "An unexpected parsing error occurred."}</p>
        </div>
      ) : (
        /* Main Dual-Pane or Single-Pane Workstation */
        <div className="flex-1 min-h-0 flex flex-col lg:flex-row overflow-hidden p-4 gap-4">
          {/* Left Canvas: Document Parchment Reader */}
          {splitView && (
            <div className="w-full lg:w-1/2 h-full flex flex-col min-h-0 shadow-2xs rounded-2xl overflow-hidden border border-[#E2E8F0]">
              <DocumentReader
                doc={doc}
                highlight={activeHighlight}
                onClearHighlight={() => setActiveHighlight(null)}
              />
            </div>
          )}

          {/* Right Canvas: Intelligence Analysis Center */}
          <div className={`flex-1 h-full flex flex-col min-h-0 bg-white border border-[#E2E8F0] rounded-2xl shadow-2xs overflow-hidden ${
            splitView ? "lg:w-1/2" : "w-full max-w-6xl mx-auto"
          }`}>
            {/* Tabs Bar */}
            <div className="flex items-center border-b border-[#E2E8F0] bg-[#F8F9FA] px-3 overflow-x-auto shrink-0">
              {TABS.map((t) => {
                const Icon = t.icon;
                const isActive = tab === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setTab(t.id)}
                    className={`flex items-center gap-2 border-b-2 px-4 py-3 text-xs font-semibold transition whitespace-nowrap ${
                      isActive
                        ? "border-[#0F172A] text-[#0F172A] bg-white"
                        : "border-transparent text-neutral-500 hover:text-neutral-900"
                    }`}
                  >
                    <Icon className={`h-3.5 w-3.5 ${isActive ? "text-amber-700" : "text-neutral-400"}`} />
                    <span>{t.label}</span>
                    {t.badge && (
                      <span className={`rounded px-1.5 py-0.2 text-[9px] font-mono font-bold uppercase ${
                        t.id === "Playbook Review"
                          ? "bg-rose-100 text-rose-800"
                          : "bg-amber-100 text-amber-800"
                      }`}>
                        {t.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Tab Pane Body */}
            <div className="flex-1 min-h-0 overflow-y-auto p-6 bg-white">
              {tab === "Summary" && <SummaryPanel doc={doc} />}
              {tab === "Key Terms" && <KeyTermsPanel doc={doc} />}
              {tab === "Clauses" && <ClausesPanel doc={doc} />}
              {tab === "Playbook Review" && (
                <PlaybookReviewPanel
                  doc={doc}
                  onSelectClause={handleSelectPlaybookFinding}
                />
              )}
              {tab === "Chat" && (
                <ChatPanel doc={doc} onSelectCitation={handleSelectCitation} />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
