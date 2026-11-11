import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Briefcase,
  Search,
  Download,
  Loader2,
  Send,
  ExternalLink,
  Layers,
  Sparkles,
} from "lucide-react";
import Markdown from "react-markdown";
import { request } from "../lib/api";
import type { Citation, PortfolioAnswerOut, PortfolioItem, PortfolioMatrixOut } from "../lib/types";

export function PortfolioPage() {
  const [matrix, setMatrix] = useState<PortfolioMatrixOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [queryInput, setQueryInput] = useState("");
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<PortfolioAnswerOut | null>(null);

  useEffect(() => {
    void (async () => {
      setLoading(true);
      try {
        const data = await request<PortfolioMatrixOut>("/portfolio/matrix");
        setMatrix(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load contract portfolio");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

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

  const filteredDocs = (matrix?.documents || []).filter((d) => {
    const q = search.toLowerCase();
    return (
      d.filename.toLowerCase().includes(q) ||
      (d.agreement_type && d.agreement_type.toLowerCase().includes(q)) ||
      (d.governing_law && d.governing_law.toLowerCase().includes(q)) ||
      d.parties.some((p) => p.toLowerCase().includes(q))
    );
  });

  return (
    <div className="mx-auto flex h-full max-w-6xl flex-col px-8 py-6 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-neutral-500" />
            <h1 className="text-lg font-semibold text-neutral-900">Contract Vault & Repository Due Diligence</h1>
          </div>
          <p className="mt-1 text-xs text-neutral-500">
            Cross-contract intelligence, portfolio queries, and automated tabular metadata extraction
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCSV}
            disabled={!matrix || matrix.documents.length === 0}
            className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 hover:text-neutral-900 transition disabled:opacity-50"
            title="Download structured spreadsheet for M&A due diligence"
          >
            <Download className="h-3.5 w-3.5 text-neutral-500" />
            <span>Export Due Diligence (CSV)</span>
          </button>
        </div>
      </div>

      {/* Multi-Document Cross-Repository AI Examiner */}
      <div className="rounded-xl border border-neutral-200/90 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-semibold text-neutral-900 mb-2">
          <Sparkles className="h-3.5 w-3.5 text-amber-600" />
          <span>Cross-Repository Legal Query</span>
          <span className="rounded bg-neutral-100 px-1.5 py-0.2 text-[10px] font-mono text-neutral-500">
            Searches across all {matrix?.total_documents ?? 0} contracts
          </span>
        </div>

        <form onSubmit={handlePortfolioQuery} className="flex gap-2">
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Ask across your contract repository (e.g. 'Compare payment terms and liability caps', 'Which contracts expire in 2026?')"
            disabled={queryLoading}
            className="flex-1 rounded-lg border border-neutral-200 bg-neutral-50/50 px-3.5 py-2 text-xs text-neutral-900 placeholder-neutral-400 outline-none focus:bg-white focus:border-neutral-400 transition"
          />
          <button
            type="submit"
            disabled={queryLoading || !queryInput.trim()}
            className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-900 px-4 py-2 text-xs font-medium text-white hover:bg-neutral-800 transition disabled:opacity-50"
          >
            {queryLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Send className="h-3.5 w-3.5" />
            )}
            <span>Analyze Vault</span>
          </button>
        </form>

        {/* Query Suggestions */}
        <div className="mt-2.5 flex flex-wrap items-center gap-1.5 text-[11px] text-neutral-400">
          <span>Try:</span>
          <button
            onClick={() => {
              setQueryInput("Compare governing law and jurisdiction across all contracts.");
            }}
            className="rounded bg-neutral-50 border border-neutral-200/80 px-2 py-0.5 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 transition"
          >
            "Compare governing law across contracts"
          </button>
          <button
            onClick={() => {
              setQueryInput("Summarize all termination for convenience clauses.");
            }}
            className="rounded bg-neutral-50 border border-neutral-200/80 px-2 py-0.5 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 transition"
          >
            "Summarize termination for convenience clauses"
          </button>
        </div>

        {/* Synthesized Cross-Contract Answer */}
        {queryResult && (
          <div className="mt-4 rounded-lg border border-neutral-200 bg-neutral-50/70 p-4 font-serif text-xs leading-relaxed text-neutral-800">
            <div className="font-sans text-[11px] font-semibold uppercase tracking-wider text-neutral-400 mb-2 flex items-center justify-between">
              <span>Vault Cross-Examination Synthesis</span>
              <span>Referenced: {queryResult.documents_referenced.join(", ")}</span>
            </div>

            <div className="prose-xs max-w-none [&_p]:my-1.5 [&_ul]:list-disc [&_ul]:pl-4 [&_li]:my-0.5">
              <Markdown>{queryResult.answer}</Markdown>
            </div>

            {queryResult.citations.length > 0 && (
              <div className="mt-3 pt-2.5 border-t border-neutral-200/80 flex flex-wrap gap-1.5">
                {queryResult.citations.map((c: Citation, idx: number) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1 rounded bg-white border border-neutral-200 px-2 py-0.5 text-[10px] font-mono text-neutral-700"
                  >
                    [{c.n}] {c.filename} {c.page ? `p. ${c.page}` : ""}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Due Diligence Data Grid Header & Filter */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-neutral-500" />
            <h3 className="text-xs font-semibold text-neutral-900">
              Due Diligence Metadata Matrix ({filteredDocs.length})
            </h3>
          </div>

          <div className="relative">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-neutral-400" />
            <input
              type="text"
              placeholder="Filter by title, party, law…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="h-8 w-60 rounded-md border border-neutral-200 bg-white pl-8 pr-3 text-xs text-neutral-800 focus:border-neutral-400 focus:outline-none"
            />
          </div>
        </div>

        {/* Data Grid Table */}
        <div className="overflow-x-auto rounded-xl border border-neutral-200/90 bg-white shadow-sm">
          {loading ? (
            <div className="flex items-center justify-center py-16 text-xs text-neutral-400">
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Loading portfolio matrix…
            </div>
          ) : error ? (
            <div className="p-6 text-xs text-rose-700">{error}</div>
          ) : filteredDocs.length === 0 ? (
            <div className="p-12 text-center text-xs text-neutral-400">
              No documents found matching "{search}".
            </div>
          ) : (
            <table className="w-full text-left text-xs text-neutral-700">
              <thead className="border-b border-neutral-200 bg-neutral-50/70 text-[11px] font-semibold text-neutral-900">
                <tr>
                  <th className="px-4 py-3">Contract File</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Identified Parties</th>
                  <th className="px-4 py-3">Effective Date</th>
                  <th className="px-4 py-3">Governing Law</th>
                  <th className="px-4 py-3">Payment Terms</th>
                  <th className="px-4 py-3">Liability Cap</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 font-sans">
                {filteredDocs.map((doc: PortfolioItem) => (
                  <tr key={doc.id} className="hover:bg-neutral-50/60 transition">
                    <td className="px-4 py-3 font-medium text-neutral-900 max-w-[200px] truncate">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="hover:text-amber-800 hover:underline flex items-center gap-1.5"
                      >
                        <span className="truncate">{doc.filename}</span>
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-neutral-600 font-mono text-[11px]">
                      {doc.agreement_type || "Commercial Agreement"}
                    </td>
                    <td className="px-4 py-3 text-neutral-600 max-w-[180px] truncate">
                      {doc.parties.length > 0 ? doc.parties.join(", ") : "—"}
                    </td>
                    <td className="px-4 py-3 text-neutral-600 font-mono text-[11px]">
                      {doc.effective_date || "—"}
                    </td>
                    <td className="px-4 py-3">
                      {doc.governing_law ? (
                        <span className="rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-medium text-neutral-800">
                          {doc.governing_law}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-4 py-3 text-neutral-600 text-[11px] truncate max-w-[140px]">
                      {doc.payment_terms || "—"}
                    </td>
                    <td className="px-4 py-3 text-neutral-600 text-[11px] truncate max-w-[140px]">
                      {doc.liability_cap || "—"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center gap-1 text-[11px] font-medium text-neutral-700 hover:text-neutral-950 underline"
                      >
                        <span>Open</span>
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
