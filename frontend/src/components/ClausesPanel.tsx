import { useEffect, useMemo, useState } from "react";
import { request } from "../lib/api";
import type { Clause, DocumentOut } from "../lib/types";

const TYPE_LABELS: Record<string, string> = {
  confidentiality: "Confidentiality",
  indemnification: "Indemnification",
  limitation_of_liability: "Limitation of liability",
  termination: "Termination",
  payment: "Payment",
  intellectual_property: "IP",
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
  const [openId, setOpenId] = useState<string | null>(null);

  const load = async (refresh: boolean) => {
    setBusy(true);
    setError(null);
    try {
      setClauses(await request<Clause[]>(`/documents/${doc.id}/clauses${refresh ? "?refresh=true" : ""}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to extract clauses");
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    void load(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doc.id]);

  const types = useMemo(() => {
    if (!clauses) return [];
    return [...new Set(clauses.map((c) => c.clause_type))];
  }, [clauses]);

  const visible = clauses?.filter((c) => filter === "all" || c.clause_type === filter) ?? [];

  if (busy && !clauses)
    return (
      <div className="py-10 text-center text-sm text-slate-400">
        Classifying clauses with the LLM — this can take a minute on long documents…
      </div>
    );
  if (error)
    return <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>;
  if (!clauses) return null;
  if (clauses.length === 0)
    return (
      <div className="rounded-2xl border border-slate-200 bg-white py-12 text-center text-sm text-slate-500">
        No clauses were recognized in this document.
      </div>
    );

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setFilter("all")}
          className={`rounded-full px-3 py-1 text-xs font-medium transition ${
            filter === "all" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
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
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                filter === t ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {TYPE_LABELS[t] ?? t} ({count})
            </button>
          );
        })}
        <button
          onClick={() => void load(true)}
          disabled={busy}
          className="ml-auto rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-indigo-300 hover:text-indigo-700 disabled:opacity-50"
        >
          {busy ? "Working…" : "Re-extract"}
        </button>
      </div>

      <div className="space-y-2">
        {visible.map((c) => {
          const open = openId === c.id;
          return (
            <div key={c.id} className="rounded-xl border border-slate-200 bg-white">
              <button
                onClick={() => setOpenId(open ? null : c.id)}
                className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left"
              >
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-slate-800">
                    {c.title || c.section_path || TYPE_LABELS[c.clause_type] || c.clause_type}
                  </div>
                  <div className="mt-0.5 text-xs text-slate-400">
                    {(TYPE_LABELS[c.clause_type] ?? c.clause_type)}
                    {c.section_path && c.section_path !== c.title ? ` · ${c.section_path}` : ""}
                  </div>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  {c.page_start !== null && (
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                      p. {c.page_start}
                    </span>
                  )}
                  <span className="text-slate-300">{open ? "▾" : "▸"}</span>
                </div>
              </button>
              {open && (
                <div className="border-t border-slate-100 px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap text-slate-600">
                  {c.text}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
