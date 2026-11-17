import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  Download,
  Loader2,
  Send,
  ExternalLink,
  Layers,
  Sparkles,
  Building,
  Scale,
  ShieldCheck,
  FileText,
} from "lucide-react";
import Markdown from "react-markdown";
import { request } from "../lib/api";
import { useTenant } from "../stores/tenant";
import type { Citation, PortfolioAnswerOut, PortfolioItem, PortfolioMatrixOut } from "../lib/types";

export function PortfolioPage() {
  const { currentOrg, currentWorkspace } = useTenant();
  const [matrix, setMatrix] = useState<PortfolioMatrixOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [queryInput, setQueryInput] = useState("");
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<PortfolioAnswerOut | null>(null);

  const loadMatrix = async () => {
    setLoading(true);
    try {
      const data = await request<PortfolioMatrixOut>("/portfolio/matrix");
      setMatrix(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load contract portfolio");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadMatrix();
  }, [currentOrg?.id, currentWorkspace?.id]);

  const handlePortfolioQuery = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const q = queryInput.trim();
    if (!q || queryLoading) return;

    setQueryLoading(true);
    try {
      const res = await request<PortfolioAnswerOut>("/portfolio/query", {
        method: "POST",
        body: JSON.stringify({ question: q }),
      });
      setQueryResult(res);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Cross-portfolio query failed");
    } finally {
      setQueryLoading(false);
    }
  };

  const handleExportCSV = () => {
    if (!matrix || matrix.documents.length === 0) return;

    const headers = [
      "Filename",
      "Agreement Type",
      "Parties",
      "Effective Date",
      "Governing Law",
      "Payment Terms",
      "Liability Cap / Notes",
      "Pages",
      "Status",
    ];

    const rows = matrix.documents.map((d) => [
      `"${d.filename.replace(/"/g, '""')}"`,
      `"${(d.agreement_type || "N/A").replace(/"/g, '""')}"`,
      `"${(d.parties.join("; ") || "N/A").replace(/"/g, '""')}"`,
      `"${(d.effective_date || "N/A").replace(/"/g, '""')}"`,
      `"${(d.governing_law || "N/A").replace(/"/g, '""')}"`,
      `"${(d.payment_terms || "N/A").replace(/"/g, '""')}"`,
      `"${(d.liability_cap || "N/A").replace(/"/g, '""')}"`,
      d.page_count ?? "N/A",
      d.status,
    ]);

    const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `LegalIQ_Due_Diligence_Matrix_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const docs = matrix?.documents || [];
  const filteredDocs = docs.filter((d) => {
    const q = search.toLowerCase();
    return (
      d.filename.toLowerCase().includes(q) ||
      (d.agreement_type && d.agreement_type.toLowerCase().includes(q)) ||
      (d.governing_law && d.governing_law.toLowerCase().includes(q)) ||
      d.parties.some((p) => p.toLowerCase().includes(q))
    );
  });

  // Unique counts for KPI cards
  const distinctParties = new Set<string>();
  docs.forEach((d) => d.parties.forEach((p) => distinctParties.add(p.trim())));
  const distinctJurisdictions = new Set<string>();
  docs.forEach((d) => {
    if (d.governing_law) distinctJurisdictions.add(d.governing_law.trim());
  });

  return (
    <div className="mx-auto flex h-full max-w-7xl flex-col px-6 py-8 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
            <span className="font-semibold text-neutral-700">{currentOrg?.name ?? "Firm Organization"}</span>
            <span>•</span>
            <span className="text-amber-700 font-semibold">📁 {currentWorkspace?.name ?? "General Matter"}</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#0F172A] font-serif-legal">
            Contract Vault & Diligence Matrix
          </h1>
          <p className="mt-1 text-xs text-neutral-500 max-w-2xl leading-relaxed">
            Cross-contract transactional intelligence, portfolio due diligence queries, and automated tabular metadata extraction across all agreements.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleExportCSV}
            disabled={!matrix || matrix.documents.length === 0}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[#0F172A] px-4 py-2 text-xs font-semibold text-white hover:bg-neutral-800 transition disabled:opacity-50 shadow-sm"
            title="Download structured spreadsheet for M&A due diligence"
          >
            <Download className="h-3.5 w-3.5 text-amber-400" />
            <span>Export Diligence CSV</span>
          </button>
        </div>
      </div>

      {/* KPI Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="text-[11px] font-mono text-neutral-400 uppercase flex items-center justify-between">
            <span>Vault Contracts</span>
            <FileText className="h-4 w-4 text-neutral-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-[#0F172A] font-serif-legal">
            {matrix?.total_documents ?? 0}
          </div>
          <div className="mt-1 text-[11px] text-neutral-500">Full text indexed</div>
        </div>

        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="text-[11px] font-mono text-neutral-400 uppercase flex items-center justify-between">
            <span>Counterparties</span>
            <Building className="h-4 w-4 text-amber-600" />
          </div>
          <div className="mt-2 text-2xl font-bold text-amber-700 font-serif-legal">
            {distinctParties.size}
          </div>
          <div className="mt-1 text-[11px] text-neutral-500">Distinct legal entities</div>
        </div>

        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="text-[11px] font-mono text-neutral-400 uppercase flex items-center justify-between">
            <span>Governing Laws</span>
            <Scale className="h-4 w-4 text-neutral-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-[#0F172A] font-serif-legal">
            {distinctJurisdictions.size}
          </div>
          <div className="mt-1 text-[11px] text-neutral-500">Delaware, NY, & Regional</div>
        </div>

        <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-2xs">
          <div className="text-[11px] font-mono text-neutral-400 uppercase flex items-center justify-between">
            <span>Audit Readiness</span>
            <ShieldCheck className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-bold text-emerald-700 font-serif-legal">
            100%
          </div>
          <div className="mt-1 text-[11px] text-emerald-700 font-medium">Metadata Structured</div>
        </div>
      </div>

      {/* Cross-Repository Legal AI Query Box */}
      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-2xs space-y-4">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-50 text-amber-800 border border-amber-200">
            <Sparkles className="h-3.5 w-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-[#0F172A] font-serif-legal">
              Cross-Repository Legal Examination
            </h3>
            <span className="text-[10px] font-mono text-neutral-400">
              Queries simultaneously across all {matrix?.total_documents ?? 0} contracts in matter
            </span>
          </div>
        </div>

        <form onSubmit={handlePortfolioQuery} className="flex gap-2">
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Ask across the matter vault (e.g. 'Compare liability caps and payment terms', 'Which contracts contain unlimited indemnification?')"
            disabled={queryLoading}
            className="flex-1 rounded-xl border border-[#E2E8F0] bg-[#F8F9FA] px-4 py-2.5 text-xs text-[#0F172A] placeholder-neutral-400 focus:bg-white focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
          />
          <button
            type="submit"
            disabled={queryLoading || !queryInput.trim()}
            className="inline-flex items-center gap-1.5 rounded-xl bg-[#0F172A] px-5 py-2.5 text-xs font-semibold text-white hover:bg-neutral-800 transition disabled:opacity-50 shadow-sm"
          >
            {queryLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin text-amber-400" />
            ) : (
              <Send className="h-3.5 w-3.5 text-amber-400" />
            )}
            <span>Analyze Vault</span>
          </button>
        </form>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-neutral-400">
          <span className="font-mono text-[10px] uppercase">Example Queries:</span>
          <button
            onClick={() => setQueryInput("Compare governing law and dispute resolution venues across all contracts.")}
            className="rounded-md bg-[#F1F5F9] px-2.5 py-1 text-neutral-700 hover:text-[#0F172A] hover:bg-neutral-200 transition text-[11px]"
          >
            "Compare governing law across contracts"
          </button>
          <button
            onClick={() => setQueryInput("Summarize all limitation of liability caps and consequential damages waivers.")}
            className="rounded-md bg-[#F1F5F9] px-2.5 py-1 text-neutral-700 hover:text-[#0F172A] hover:bg-neutral-200 transition text-[11px]"
          >
            "Summarize all liability caps"
          </button>
          <button
            onClick={() => setQueryInput("Which contracts have termination for convenience without penalty?")}
            className="rounded-md bg-[#F1F5F9] px-2.5 py-1 text-neutral-700 hover:text-[#0F172A] hover:bg-neutral-200 transition text-[11px]"
          >
            "Termination for convenience terms"
          </button>
        </div>

        {/* Synthesized Cross-Contract Answer */}
        {queryResult && (
          <div className="rounded-xl border border-amber-200/80 bg-amber-50/30 p-5 space-y-3 font-serif-legal text-xs leading-relaxed text-[#0F172A]">
            <div className="font-sans-legal text-[10px] font-mono uppercase tracking-wider text-amber-800 font-bold flex items-center justify-between">
              <span>Cross-Matter Synthesis</span>
              <span>Referenced: {queryResult.documents_referenced.join(", ")}</span>
            </div>

            <div className="prose-xs max-w-none [&_p]:my-2 [&_ul]:list-disc [&_ul]:pl-4 [&_li]:my-1 text-neutral-900">
              <Markdown>{queryResult.answer}</Markdown>
            </div>

            {queryResult.citations.length > 0 && (
              <div className="pt-3 border-t border-amber-200/60 flex flex-wrap gap-2">
                {queryResult.citations.map((c: Citation, idx: number) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1 rounded-md bg-white border border-amber-200 px-2 py-0.5 text-[10px] font-mono text-neutral-800 shadow-2xs"
                  >
                    [{c.n}] {c.filename} {c.page ? `p. ${c.page}` : ""}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Due Diligence Data Grid */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-neutral-500" />
            <h3 className="text-xs font-bold text-[#0F172A] font-serif-legal">
              Matter Due Diligence Metadata Grid ({filteredDocs.length})
            </h3>
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-neutral-400" />
            <input
              type="text"
              placeholder="Filter by filename, party, or law…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-64 rounded-lg border border-[#E2E8F0] bg-white pl-8 pr-3 text-xs text-neutral-800 focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
            />
          </div>
        </div>

        {/* Data Grid Table */}
        <div className="overflow-x-auto rounded-2xl border border-[#E2E8F0] bg-white shadow-2xs">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-xs text-neutral-400">
              <Loader2 className="h-5 w-5 animate-spin text-amber-600 mr-2" />
              <span>Building due diligence metadata matrix…</span>
            </div>
          ) : error ? (
            <div className="p-6 text-xs text-rose-700">{error}</div>
          ) : filteredDocs.length === 0 ? (
            <div className="p-16 text-center text-xs text-neutral-400">
              No contracts found matching "{search}".
            </div>
          ) : (
            <table className="w-full text-left text-xs text-[#0F172A] border-collapse">
              <thead className="border-b border-[#E2E8F0] bg-[#F8F9FA] text-[11px] font-mono text-neutral-500 uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3.5 font-semibold">Contract Docket</th>
                  <th className="px-4 py-3.5 font-semibold">Agreement Type</th>
                  <th className="px-4 py-3.5 font-semibold">Identified Parties</th>
                  <th className="px-4 py-3.5 font-semibold">Effective Date</th>
                  <th className="px-4 py-3.5 font-semibold">Governing Law</th>
                  <th className="px-4 py-3.5 font-semibold">Payment Terms</th>
                  <th className="px-4 py-3.5 font-semibold">Liability Cap</th>
                  <th className="px-4 py-3.5 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F1F5F9]">
                {filteredDocs.map((item: PortfolioItem) => (
                  <tr key={item.id} className="hover:bg-amber-50/15 transition group">
                    <td className="px-4 py-3.5 font-semibold text-[#0F172A] max-w-[200px] truncate">
                      <Link
                        to={`/documents/${item.id}`}
                        className="group-hover:text-amber-800 transition line-clamp-1"
                      >
                        {item.filename}
                      </Link>
                    </td>
                    <td className="px-4 py-3.5 text-neutral-600 font-mono text-[11px]">
                      {item.agreement_type || "Commercial Contract"}
                    </td>
                    <td className="px-4 py-3.5 text-neutral-600 max-w-[180px] truncate">
                      {item.parties.length > 0 ? item.parties.join(", ") : "—"}
                    </td>
                    <td className="px-4 py-3.5 text-neutral-600 font-mono text-[11px]">
                      {item.effective_date || "—"}
                    </td>
                    <td className="px-4 py-3.5">
                      {item.governing_law ? (
                        <span className="rounded bg-neutral-100 px-2 py-0.5 text-[10px] font-semibold text-neutral-800 border border-neutral-200">
                          {item.governing_law}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-neutral-600 text-[11px] truncate max-w-[140px]">
                      {item.payment_terms || "—"}
                    </td>
                    <td className="px-4 py-3.5 text-neutral-600 text-[11px] truncate max-w-[140px]">
                      {item.liability_cap || "—"}
                    </td>
                    <td className="px-4 py-3.5 text-right whitespace-nowrap">
                      <Link
                        to={`/documents/${item.id}`}
                        className="inline-flex items-center gap-1 rounded-md border border-[#E2E8F0] bg-white px-2.5 py-1 text-[11px] font-semibold text-neutral-700 hover:bg-[#F8F9FA] transition shadow-2xs"
                      >
                        <span>Inspect</span>
                        <ExternalLink className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
