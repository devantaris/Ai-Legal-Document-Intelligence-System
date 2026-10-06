import { useEffect, useMemo, useState } from "react";
import { Search, ChevronDown, ChevronRight, RefreshCw } from "lucide-react";
import { request } from "../lib/api";
import type { Clause, DocumentOut } from "../lib/types";

const TYPE_LABELS: Record<string, string> = {
  confidentiality: "Confidentiality",
  indemnification: "Indemnification",
  limitation_of_liability: "Limitation of liability",
  termination: "Termination",
  payment: "Payment",
  intellectual_property: "IP rights",
  governing_law: "Governing law",
  dispute_resolution: "Dispute resolution",
  arbitration: "Arbitration",
  force_majeure: "Force majeure",
  non_compete: "Non-compete",
  assignment: "Assignment",
  notices: "Notices",
  warranties: "Warranties",
  insurance: "Insurance",
  data_protection: "Data protection",
  entire_agreement: "Entire agreement",
  amendment: "Amendment",
  severability: "Severability",
  other: "Other",
};

export function ClausesPanel({ doc }: { doc: DocumentOut }) {
  const [clauses, setClauses] = useState<Clause[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [openIds, setOpenIds] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");

  const load = async (refresh: boolean) => {
    setBusy(true);
    setError(null);
    try {
      setClauses(
        await request<Clause[]>(`/documents/${doc.id}/clauses${refresh ? "?refresh=true" : ""}`),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to extract clauses");
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    void load(false);
  }, [doc.id]);

  const types = useMemo(() => {
    if (!clauses) return [];
    return [...new Set(clauses.map((c) => c.clause_type))];
  }, [clauses]);

  const toggleOpen = (id: string) => {
    setOpenIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const visible = useMemo(() => {
    if (!clauses) return [];
    return clauses.filter((c) => {
      const matchesFilter = filter === "all" || c.clause_type === filter;
      const q = searchQuery.toLowerCase();
      const matchesSearch =
        !q ||
        c.title.toLowerCase().includes(q) ||
        c.text.toLowerCase().includes(q) ||
        c.section_path.toLowerCase().includes(q);
      return matchesFilter && matchesSearch;
    });
  }, [clauses, filter, searchQuery]);

  if (busy && !clauses)
    return <div className="py-12 text-center text-xs text-neutral-400">Classifying clauses…</div>;

  if (error)
    return (
      <div className="rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700">
        {error}
      </div>
    );

  if (!clauses || clauses.length === 0)
    return (
      <div className="rounded-xl border border-neutral-200 bg-white py-12 text-center text-xs text-neutral-500">
        No clauses extracted yet.
      </div>
    );

  return (
    <div className="space-y-3">
      {/* Search & Actions Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-neutral-400" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search clause text..."
            className="w-full rounded-lg border border-neutral-200 bg-white pl-8 pr-3 py-1.5 text-xs text-neutral-900 placeholder-neutral-400 outline-none focus:border-neutral-400"
          />
        </div>

        <button
          onClick={() => void load(true)}
          disabled={busy}
          className="flex items-center gap-1 rounded-lg border border-neutral-200 bg-white px-2.5 py-1 text-xs text-neutral-600 hover:bg-neutral-50 transition disabled:opacity-50"
        >
          <RefreshCw className={`h-3 w-3 ${busy ? "animate-spin" : ""}`} />
          <span>{busy ? "Working…" : "Re-extract"}</span>
        </button>
      </div>

      {/* Filter Category Pills */}
      <div className="flex flex-wrap items-center gap-1">
        <button
          onClick={() => setFilter("all")}
          className={`rounded-md px-2.5 py-1 text-xs font-medium transition ${
            filter === "all"
              ? "bg-neutral-900 text-white"
              : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
          }`}
        >
          All ({clauses.length})
        </button>
        {types.map((t) => {
          const count = clauses.filter((c) => c.clause_type === t).length;
          return (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition ${
                filter === t
                  ? "bg-neutral-900 text-white"
                  : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
              }`}
            >
              <span>{TYPE_LABELS[t] ?? t}</span>{" "}
              <span className="font-mono text-[10px] opacity-70">({count})</span>
            </button>
          );
        })}
      </div>

      {/* Clause Accordion Cards */}
      <div className="space-y-2 pt-1">
        {visible.map((c) => {
          const isOpen = openIds.has(c.id);
          return (
            <div
              key={c.id}
              className="rounded-xl border border-neutral-200 bg-white transition hover:border-neutral-300"
            >
              <button
                onClick={() => toggleOpen(c.id)}
                className="flex w-full items-center justify-between gap-4 p-3.5 text-left"
              >
                <div className="min-w-0">
                  <div className="truncate text-xs sm:text-sm font-semibold text-neutral-900">
                    {c.title || c.section_path || TYPE_LABELS[c.clause_type] || c.clause_type}
                  </div>
                  <div className="text-[11px] text-neutral-400 mt-0.5">
                    {TYPE_LABELS[c.clause_type] ?? c.clause_type}
                    {c.section_path && c.section_path !== c.title ? ` · ${c.section_path}` : ""}
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-2 text-neutral-400">
                  {c.page_start !== null && (
                    <span className="rounded bg-neutral-100 px-1.5 py-0.5 text-[11px] font-mono text-neutral-600">
                      p. {c.page_start}
                    </span>
                  )}
                  {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                </div>
              </button>

              {isOpen && (
                <div className="border-t border-neutral-100 p-4 text-xs leading-relaxed text-neutral-700 whitespace-pre-wrap bg-neutral-50/50 rounded-b-xl font-sans">
                  {c.text}
                </div>
              )}
            </div>
          );
        })}

        {visible.length === 0 && (
          <div className="py-8 text-center text-xs text-neutral-400">No matching clauses found.</div>
        )}
      </div>
    </div>
  );
}
