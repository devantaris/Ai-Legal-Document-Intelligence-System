import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { request } from "../lib/api";
import type { CompareResult, DocumentOut } from "../lib/types";

const LEVEL_STYLES: Record<string, string> = {
  unchanged: "bg-neutral-100 text-neutral-600",
  minor: "bg-sky-50 text-sky-700 border-sky-200",
  moderate: "bg-amber-50 text-amber-700 border-amber-200",
  major: "bg-rose-50 text-rose-700 border-rose-200",
  added: "bg-emerald-50 text-emerald-700 border-emerald-200",
  removed: "bg-rose-50 text-rose-700 border-rose-200",
};

export function ComparePage() {
  const [searchParams] = useSearchParams();
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [aId, setAId] = useState(searchParams.get("a") ?? "");
  const [bId, setBId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CompareResult | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setDocs(await request<DocumentOut[]>("/documents"));
      } catch {
        /* handled */
      }
    })();
  }, []);

  const ready = docs.filter((d) => d.status === "ready");

  const run = async () => {
    if (!aId || !bId || aId === bId) {
      setError("Please select two distinct documents to compare.");
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const res = await request<CompareResult>("/compare", {
        method: "POST",
        body: JSON.stringify({ document_a_id: aId, document_b_id: bId }),
      });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Comparison failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-8 py-8 space-y-6">
      {/* Header */}
      <div className="border-b border-[#E2E8F0] pb-6">
        <div className="flex items-center gap-2 text-xs font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
          <span className="font-semibold text-neutral-700">Contract Analysis</span>
          <span>•</span>
          <span className="text-amber-700 font-semibold font-mono">Bilateral Redline Diff</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-[#0F172A] font-serif-legal">
          Bilateral Contract Redline & Diff Engine
        </h1>
        <p className="mt-1 text-xs text-neutral-500 max-w-2xl leading-relaxed">
          Semantically aligns clauses between two contract versions, identifying substantive legal modifications, unilateral insertions, and omissions.
        </p>
      </div>

      {/* Selectors */}
      <div className="rounded-xl border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <select
            value={aId}
            onChange={(e) => setAId(e.target.value)}
            className="w-full flex-1 rounded-lg border border-[#E2E8F0] px-3 py-2 text-xs text-[#0F172A] outline-none focus:border-[#0F172A]"
          >
            <option value="">Version A (Original / Baseline)…</option>
            {ready.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename}
              </option>
            ))}
          </select>

          <span className="text-xs text-neutral-400 font-mono-legal px-2">vs</span>

          <select
            value={bId}
            onChange={(e) => setBId(e.target.value)}
            className="w-full flex-1 rounded-lg border border-[#E2E8F0] px-3 py-2 text-xs text-[#0F172A] outline-none focus:border-[#0F172A]"
          >
            <option value="">Version B (Counterparty Markup / Revised)…</option>
            {ready.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename}
              </option>
            ))}
          </select>

          <button
            onClick={() => void run()}
            disabled={busy || !aId || !bId || aId === bId}
            className="w-full sm:w-auto rounded-lg bg-[#0F172A] px-5 py-2 text-xs font-semibold text-white hover:bg-neutral-800 transition disabled:opacity-40 shadow-sm"
          >
            {busy ? "Comparing…" : "Execute Diff"}
          </button>
        </div>

        {ready.length < 2 && (
          <p className="mt-2.5 text-[11px] text-amber-700 font-mono-legal">
            Requires at least two processed documents in the workspace to execute bilateral comparison.
          </p>
        )}
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700">
          {error}
        </div>
      )}

      {busy && (
        <div className="mt-12 flex flex-col items-center justify-center text-center">
          <Loader2 className="h-5 w-5 animate-spin text-neutral-400" />
          <div className="mt-2 text-xs text-neutral-500">Analyzing clause alignment…</div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-6 space-y-4">
          {/* Executive Summary */}
          <div className="rounded-xl border border-[#E2E8F0] bg-white p-5 shadow-sm">
            <div className="text-sm font-semibold text-[#0F172A] font-serif-legal mb-1">Diligence Redline Summary</div>
            <p className="text-xs text-neutral-700 leading-relaxed font-sans">{result.summary}</p>

            <div className="mt-4 pt-3 border-t border-[#E2E8F0] flex flex-wrap gap-4 text-[11px] text-neutral-500 font-mono-legal">
              <span className="text-neutral-600">{result.counts.unchanged} unchanged</span>
              <span className="text-amber-800 font-semibold">{result.counts.modified} modified</span>
              <span className="text-emerald-800 font-semibold">{result.counts.added} added in B</span>
              <span className="text-rose-800 font-semibold">{result.counts.removed} removed from A</span>
            </div>
          </div>

          {/* Compared Clauses */}
          <div className="space-y-3">
            {result.items.map((item, i) => (
              <div key={i} className="rounded-xl border border-[#E2E8F0] bg-white p-5 space-y-3 shadow-2xs">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-semibold text-[#0F172A] font-serif-legal truncate">
                    {item.a?.title || item.b?.title || "(untitled clause)"}
                  </div>
                  <span
                    className={`rounded-md border px-2.5 py-0.5 text-[10px] font-semibold uppercase font-mono-legal ${
                      LEVEL_STYLES[item.status === "modified" ? item.change_level : item.status] ??
                      LEVEL_STYLES.unchanged
                    }`}
                  >
                    {item.status === "modified" ? item.change_level : item.status}
                  </span>
                </div>

                {item.change_summary && (
                  <p className="text-xs text-neutral-700 leading-relaxed bg-[#FAF9F6] p-3 rounded-lg border border-[#E2E8F0]">
                    {item.change_summary}
                  </p>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {item.a && (
                    <div className="rounded-lg border border-[#E2E8F0] bg-[#FAF9F6] p-3 text-xs leading-relaxed text-neutral-800 font-serif-legal">
                      <div className="text-[10px] font-mono-legal text-neutral-500 mb-1.5 uppercase tracking-wider font-semibold">
                        Version A{item.a.page_start !== null ? ` · p. ${item.a.page_start}` : ""}
                      </div>
                      <div className="whitespace-pre-wrap">{item.a.text}</div>
                    </div>
                  )}
                  {item.b && (
                    <div className="rounded-lg border border-[#E2E8F0] bg-white p-3 text-xs leading-relaxed text-[#0F172A] font-serif-legal">
                      <div className="text-[10px] font-mono-legal text-neutral-500 mb-1.5 uppercase tracking-wider font-semibold">
                        Version B{item.b.page_start !== null ? ` · p. ${item.b.page_start}` : ""}
                      </div>
                      <div className="whitespace-pre-wrap">{item.b.text}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
