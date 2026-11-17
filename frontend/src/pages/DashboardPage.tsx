import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import confetti from "canvas-confetti";
import {
  FileText,
  Upload,
  Search,
  Trash2,
  Loader2,
  Lock,
  ShieldCheck,
  AlertTriangle,
  FileDown,
  LayoutGrid,
  List,
  Sparkles,
  ArrowRight,
  Plus,
} from "lucide-react";
import { getAccessToken, request, uploadDocument } from "../lib/api";
import type { DocumentOut } from "../lib/types";
import { StatusBadge } from "../components/StatusBadge";
import { useTenant } from "../stores/tenant";

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

const PROCESSING = new Set(["uploaded", "parsing", "embedding"]);

function celebrateReady() {
  const defaults = {
    origin: { y: 0.7 },
    colors: ["#0F172A", "#B45309", "#10B981", "#E2E8F0"],
    ticks: 160,
  };
  confetti({ ...defaults, particleCount: 50, spread: 60, startVelocity: 35 });
}

export function DashboardPage() {
  const { currentOrg, currentWorkspace } = useTenant();
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploadPct, setUploadPct] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const fileInput = useRef<HTMLInputElement>(null);
  const prevStatuses = useRef<Map<string, string>>(new Map());
  const [docProgress, setDocProgress] = useState<Record<string, { pct: number; step: string }>>({});
  const navigate = useNavigate();

  const isViewer = currentOrg?.role === "viewer";

  const load = useCallback(async () => {
    try {
      const qs = currentWorkspace?.id ? `?workspace_id=${currentWorkspace.id}` : "";
      const fresh = await request<DocumentOut[]>(`/documents${qs}`);
      for (const d of fresh) {
        const before = prevStatuses.current.get(d.id);
        if (before && PROCESSING.has(before) && d.status === "ready") celebrateReady();
      }
      prevStatuses.current = new Map(fresh.map((d) => [d.id, d.status]));
      setDocs(fresh);
      setError(null);

      // Query live progress for any active ingestion jobs
      const processingDocs = fresh.filter((d) => PROCESSING.has(d.status));
      if (processingDocs.length > 0) {
        for (const pd of processingDocs) {
          try {
            const prog = await request<{ progress_pct: number; step: string }>(`/documents/${pd.id}/progress`);
            setDocProgress((prev) => ({
              ...prev,
              [pd.id]: { pct: prog.progress_pct, step: prog.step },
            }));
          } catch {
            /* ignore individual progress fetch */
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, [currentWorkspace?.id]);

  useEffect(() => {
    void load();
    const handleTenantChange = () => void load();
    window.addEventListener("lda:tenant_changed", handleTenantChange);
    return () => window.removeEventListener("lda:tenant_changed", handleTenantChange);
  }, [load, currentOrg?.id, currentWorkspace?.id]);

  useEffect(() => {
    if (!docs.some((d) => PROCESSING.has(d.status))) return;
    const t = setInterval(() => void load(), 2500);
    return () => clearInterval(t);
  }, [docs, load]);

  const upload = useCallback(
    async (file: File) => {
      if (isViewer) return;
      setError(null);
      setUploadPct(0);
      try {
        await uploadDocument(file, setUploadPct);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploadPct(null);
      }
    },
    [load, isViewer],
  );

  const removeDoc = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (isViewer) {
      alert("Viewers cannot delete documents");
      return;
    }
    if (!window.confirm("Permanently purge this agreement from the matter vault?")) return;
    try {
      await request(`/documents/${id}`, { method: "DELETE" });
      void load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete document");
    }
  };

  const handleExportDocx = async (doc: DocumentOut, e: React.MouseEvent) => {
    e.stopPropagation();
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
    }
  };

  // KPI Calculations
  const totalDocs = docs.length;
  const readyDocs = docs.filter((d) => d.status === "ready").length;
  const totalClauses = docs.reduce((acc, d) => acc + (d.clause_count || 0), 0);
  const totalPages = docs.reduce((acc, d) => acc + (d.page_count || 0), 0);
  const totalBytes = docs.reduce((acc, d) => acc + (d.size_bytes || 0), 0);

  const filteredDocs = docs.filter((d) => {
    const matchesSearch = d.filename.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus =
      statusFilter === "ALL" ||
      (statusFilter === "ready" && d.status === "ready") ||
      (statusFilter === "processing" && PROCESSING.has(d.status)) ||
      (statusFilter === "failed" && d.status === "failed");
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="mx-auto max-w-7xl px-6 py-8 space-y-6">
      {/* Executive Matter Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
            <span className="font-semibold text-neutral-700">{currentOrg?.name ?? "Firm Portfolio"}</span>
            <span>•</span>
            <span className="text-amber-700 font-semibold flex items-center gap-1">
              📁 {currentWorkspace?.name ?? "General Matter Repository"}
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#0F172A] font-serif-legal">
            Matter Agreements Docket
          </h1>
          <p className="mt-1 text-xs text-neutral-500 max-w-2xl leading-relaxed">
            Institutional contract repository with automated 10-standard compliance auditing, native Word redlining, and cross-contract due diligence.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => navigate("/portfolio")}
            className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3.5 py-2 text-xs font-semibold text-neutral-700 hover:bg-[#F8F9FA] transition shadow-2xs"
          >
            <Sparkles className="h-3.5 w-3.5 text-amber-600" />
            <span>Vault Due Diligence Grid</span>
          </button>
          {!isViewer && (
            <button
              onClick={() => fileInput.current?.click()}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[#0F172A] px-4 py-2 text-xs font-semibold text-white hover:bg-neutral-800 transition shadow-sm"
            >
              <Plus className="h-3.5 w-3.5 text-amber-400" />
              <span>Upload Agreement</span>
            </button>
          )}
        </div>
      </div>

      {/* KPI Intelligence Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400 uppercase">
            <span>Indexed Agreements</span>
            <FileText className="h-4 w-4 text-neutral-400" />
          </div>
          <div className="mt-2 text-2xl font-bold tracking-tight text-[#0F172A]">
            {totalDocs}
          </div>
          <div className="mt-1 text-[11px] text-neutral-500 flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            <span>{readyDocs} fully ready for analysis</span>
          </div>
        </div>

        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400 uppercase">
            <span>Contract Provisions</span>
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-bold tracking-tight text-[#0F172A]">
            {totalClauses}
          </div>
          <div className="mt-1 text-[11px] text-neutral-500">
            Across {totalPages} parsed pages
          </div>
        </div>

        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400 uppercase">
            <span>Institutional Playbook</span>
            <AlertTriangle className="h-4 w-4 text-amber-600" />
          </div>
          <div className="mt-2 text-2xl font-bold tracking-tight text-amber-700">
            10 Standards
          </div>
          <div className="mt-1 text-[11px] text-neutral-500">
            Automated liability & risk review
          </div>
        </div>

        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="flex items-center justify-between text-[11px] font-mono text-neutral-400 uppercase">
            <span>Sovereign Storage</span>
            <Lock className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-bold tracking-tight text-[#0F172A]">
            {formatBytes(totalBytes)}
          </div>
          <div className="mt-1 text-[11px] text-emerald-700 font-medium">
            AES-256 On-Premise Encrypted
          </div>
        </div>
      </div>

      {/* Considerate Legal Drag & Drop Ingestion Zone */}
      {!isViewer && (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const file = e.dataTransfer.files?.[0];
            if (file) void upload(file);
          }}
          onClick={() => fileInput.current?.click()}
          className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-7 text-center transition-all ${
            dragging
              ? "border-[#0F172A] bg-amber-50/40 shadow-md ring-4 ring-amber-500/10"
              : "border-[#CBD5E1] bg-white hover:border-[#94A3B8] hover:bg-[#FAFAFA] shadow-2xs"
          }`}
        >
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void upload(file);
              e.target.value = "";
            }}
          />

          {uploadPct !== null ? (
            <div className="py-2 max-w-md mx-auto">
              <div className="text-xs font-semibold text-[#0F172A] flex items-center justify-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-amber-600" />
                <span>Ingesting contract into {currentWorkspace?.name ?? "Matter"}… {uploadPct}%</span>
              </div>
              <div className="mx-auto mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[#E2E8F0]">
                <div
                  className="h-full bg-[#0F172A] transition-all duration-300"
                  style={{ width: `${uploadPct}%` }}
                />
              </div>
              <p className="mt-2 text-[11px] text-neutral-400 font-mono">
                Computing SHA-256 checksum • AES-256 encryption • Sovereign Queue dispatch
              </p>
            </div>
          ) : (
            <div>
              <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-[#F8F9FA] text-[#0F172A] border border-[#E2E8F0] shadow-2xs">
                <Upload className="h-5 w-5 text-amber-700" />
              </div>
              <div className="mt-3 text-sm font-bold text-[#0F172A]">
                Ingest Agreement into <span className="underline decoration-amber-400 decoration-2">{currentWorkspace?.name ?? "Active Matter"}</span>
              </div>
              <p className="mt-1 text-xs text-neutral-500 max-w-lg mx-auto">
                Drag and drop PDF contracts (scanned or native), Word DOCX redlines, or legal text briefs.
              </p>
              <div className="mt-3 flex items-center justify-center gap-2">
                <span className="rounded bg-[#F1F5F9] px-2 py-0.5 text-[10px] font-mono text-neutral-600 font-medium">
                  PDF / OCR
                </span>
                <span className="rounded bg-[#F1F5F9] px-2 py-0.5 text-[10px] font-mono text-neutral-600 font-medium">
                  Word DOCX
                </span>
                <span className="rounded bg-[#F1F5F9] px-2 py-0.5 text-[10px] font-mono text-neutral-600 font-medium">
                  Up to 50 MB
                </span>
                <span className="rounded bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 text-[10px] font-mono font-semibold">
                  Zero Data Egress
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-800 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="font-semibold underline">Dismiss</button>
        </div>
      )}

      {/* Filter, Search & View Controls */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            placeholder="Search contracts by filename, counterparty, or matter…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-[#E2E8F0] bg-white pl-9 pr-3 py-2 text-xs placeholder:text-neutral-400 focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
          />
        </div>

        <div className="flex items-center gap-2">
          {/* Status Filter */}
          <div className="flex items-center rounded-lg border border-[#E2E8F0] bg-white p-0.5 text-xs">
            <button
              onClick={() => setStatusFilter("ALL")}
              className={`rounded-md px-2.5 py-1 text-[11px] font-medium transition ${
                statusFilter === "ALL"
                  ? "bg-[#0F172A] text-white"
                  : "text-neutral-600 hover:text-neutral-900"
              }`}
            >
              All ({docs.length})
            </button>
            <button
              onClick={() => setStatusFilter("ready")}
              className={`rounded-md px-2.5 py-1 text-[11px] font-medium transition ${
                statusFilter === "ready"
                  ? "bg-[#0F172A] text-white"
                  : "text-neutral-600 hover:text-neutral-900"
              }`}
            >
              Ready ({readyDocs})
            </button>
            <button
              onClick={() => setStatusFilter("processing")}
              className={`rounded-md px-2.5 py-1 text-[11px] font-medium transition ${
                statusFilter === "processing"
                  ? "bg-[#0F172A] text-white"
                  : "text-neutral-600 hover:text-neutral-900"
              }`}
            >
              Active Queue ({docs.length - readyDocs})
            </button>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center rounded-lg border border-[#E2E8F0] bg-white p-0.5">
            <button
              onClick={() => setViewMode("table")}
              className={`rounded p-1 text-xs transition ${
                viewMode === "table" ? "bg-[#0F172A] text-white" : "text-neutral-500 hover:text-neutral-900"
              }`}
              title="Dense Docket Table"
            >
              <List className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode("grid")}
              className={`rounded p-1 text-xs transition ${
                viewMode === "grid" ? "bg-[#0F172A] text-white" : "text-neutral-500 hover:text-neutral-900"
              }`}
              title="Dossier Cards"
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Docket Content View */}
      {loading ? (
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-16 text-center text-xs text-neutral-400">
          <Loader2 className="mx-auto h-6 w-6 animate-spin text-amber-600 mb-2" />
          <span>Synchronizing matter agreement docket…</span>
        </div>
      ) : filteredDocs.length === 0 ? (
        <div className="rounded-2xl border border-[#E2E8F0] bg-white p-16 text-center">
          <FileText className="mx-auto h-8 w-8 text-neutral-300 mb-2" />
          <div className="text-sm font-bold text-[#0F172A] font-serif-legal">
            {searchQuery ? "No agreements match query" : "No contracts in this matter yet"}
          </div>
          <p className="mt-1 text-xs text-neutral-400 max-w-sm mx-auto">
            {searchQuery
              ? "Check spelling or clear search filters."
              : "Upload an NDA, Master Services Agreement, or commercial lease above to activate analysis."}
          </p>
        </div>
      ) : viewMode === "table" ? (
        /* High-Density Legal Table */
        <div className="rounded-2xl border border-[#E2E8F0] bg-white overflow-hidden shadow-2xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-[#E2E8F0] bg-[#F8F9FA] text-[11px] font-mono text-neutral-500 uppercase tracking-wider">
                  <th className="py-3 px-4 font-semibold">Agreement Docket</th>
                  <th className="py-3 px-3 font-semibold">Status & Stage</th>
                  <th className="py-3 px-3 font-semibold">Pages</th>
                  <th className="py-3 px-3 font-semibold">Extracted Clauses</th>
                  <th className="py-3 px-3 font-semibold">File Size</th>
                  <th className="py-3 px-3 font-semibold">Date Indexed</th>
                  <th className="py-3 px-4 text-right font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9] text-neutral-700">
                {filteredDocs.map((doc) => {
                  const isReady = doc.status === "ready";
                  const prog = docProgress[doc.id];
                  return (
                    <tr
                      key={doc.id}
                      onClick={() => isReady && navigate(`/documents/${doc.id}`)}
                      className={`group transition ${
                        isReady
                          ? "cursor-pointer hover:bg-amber-50/20"
                          : "opacity-85"
                      }`}
                    >
                      <td className="py-3.5 px-4 font-medium text-[#0F172A]">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#F8F9FA] border border-[#E2E8F0] text-neutral-600 group-hover:border-amber-400 transition">
                            <FileText className="h-4 w-4" />
                          </div>
                          <div>
                            <span className="font-semibold text-xs text-[#0F172A] group-hover:text-amber-800 transition line-clamp-1 max-w-md">
                              {doc.filename}
                            </span>
                            <span className="text-[10px] text-neutral-400 font-mono">
                              ID: {doc.id.slice(0, 8)}…
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-3 whitespace-nowrap">
                        <StatusBadge
                          status={doc.status}
                          progressPct={prog?.pct}
                          stepText={prog?.step}
                        />
                      </td>
                      <td className="py-3.5 px-3 font-mono text-neutral-600 text-xs">
                        {doc.page_count !== null ? `${doc.page_count} pp.` : "—"}
                      </td>
                      <td className="py-3.5 px-3 font-mono text-neutral-600 text-xs">
                        {doc.clause_count > 0 ? (
                          <span className="inline-flex items-center gap-1 rounded bg-neutral-100 px-1.5 py-0.5 text-[11px] font-semibold text-neutral-800">
                            {doc.clause_count} clauses
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="py-3.5 px-3 font-mono text-neutral-400 text-[11px]">
                        {formatBytes(doc.size_bytes)}
                      </td>
                      <td className="py-3.5 px-3 font-mono text-neutral-400 text-[11px]">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3.5 px-4 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          {isReady && (
                            <>
                              <button
                                onClick={() => navigate(`/documents/${doc.id}`)}
                                className="inline-flex items-center gap-1 rounded-md border border-[#E2E8F0] bg-white px-2 py-1 text-[11px] font-medium text-neutral-700 hover:bg-[#F8F9FA] transition"
                                title="Inspect Contract in Split Canvas"
                              >
                                <span>Inspect</span>
                                <ArrowRight className="h-3 w-3" />
                              </button>
                              <button
                                onClick={(e) => handleExportDocx(doc, e)}
                                className="rounded p-1 text-neutral-400 hover:text-[#0F172A] hover:bg-neutral-100 transition"
                                title="Download Track Changes Redline (.docx)"
                              >
                                <FileDown className="h-3.5 w-3.5" />
                              </button>
                            </>
                          )}
                          {!isViewer && (
                            <button
                              onClick={(e) => removeDoc(doc.id, e)}
                              className="rounded p-1 text-neutral-400 hover:text-rose-600 hover:bg-rose-50 transition"
                              title="Delete from Matter"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Executive Dossier Card Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredDocs.map((doc) => {
            const isReady = doc.status === "ready";
            const prog = docProgress[doc.id];
            return (
              <div
                key={doc.id}
                onClick={() => isReady && navigate(`/documents/${doc.id}`)}
                className={`flex flex-col justify-between rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-2xs transition hover:shadow-md hover:border-amber-300 ${
                  isReady ? "cursor-pointer" : "opacity-85"
                }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#F8F9FA] border border-[#E2E8F0] text-[#0F172A]">
                      <FileText className="h-4 w-4" />
                    </div>
                    <StatusBadge
                      status={doc.status}
                      progressPct={prog?.pct}
                      stepText={prog?.step}
                    />
                  </div>

                  <h3 className="text-xs font-bold text-[#0F172A] line-clamp-2 mb-2 font-serif-legal">
                    {doc.filename}
                  </h3>

                  <div className="flex items-center gap-3 text-[11px] font-mono text-neutral-500 mb-4">
                    <span>{doc.page_count ?? 0} pages</span>
                    <span>•</span>
                    <span>{doc.clause_count} clauses</span>
                    <span>•</span>
                    <span>{formatBytes(doc.size_bytes)}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-[#F1F5F9] pt-3 text-xs">
                  <span className="font-mono text-[10px] text-neutral-400">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </span>

                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    {isReady && (
                      <button
                        onClick={(e) => handleExportDocx(doc, e)}
                        className="inline-flex items-center gap-1 rounded border border-[#E2E8F0] bg-white px-2 py-0.5 text-[10px] font-medium text-neutral-600 hover:bg-[#F8F9FA]"
                        title="Export Redline (.docx)"
                      >
                        <FileDown className="h-3 w-3" />
                        <span>Redline</span>
                      </button>
                    )}
                    <button
                      onClick={() => navigate(`/documents/${doc.id}`)}
                      className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#0F172A] hover:text-amber-800"
                    >
                      <span>Open</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
