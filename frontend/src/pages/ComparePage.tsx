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
    <div className="mx-auto max-w-4xl px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-semibold tracking-tight text-neutral-900">Compare Documents</h1>
        <p className="mt-0.5 text-xs text-neutral-500">
          Aligns clauses between two versions and summarizes changes.
        </p>
      </div>

      {/* Selectors */}
      <div className="rounded-xl border border-neutral-200 bg-white p-4">
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <select
            value={aId}
            onChange={(e) => setAId(e.target.value)}
            className="w-full flex-1 rounded-lg border border-neutral-200 px-3 py-2 text-xs text-neutral-800 outline-none focus:border-neutral-400"
          >
            <option value="">Version A (Original)…</option>
            {ready.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename}
              </option>
            ))}
          </select>

          <span className="text-xs text-neutral-400 font-medium">vs</span>

          <select
            value={bId}
            onChange={(e) => setBId(e.target.value)}
            className="w-full flex-1 rounded-lg border border-neutral-200 px-3 py-2 text-xs text-neutral-800 outline-none focus:border-neutral-400"
          >
            <option value="">Version B (Revised)…</option>
            {ready.map((d) => (
              <option key={d.id} value={d.id}>
                {d.filename}
              </option>
            ))}
          </select>

          <button
            onClick={() => void run()}
            disabled={busy || !aId || !bId || aId === bId}
            className="w-full sm:w-auto rounded-lg bg-neutral-900 px-4 py-2 text-xs font-medium text-white hover:bg-neutral-800 transition disabled:opacity-40"
          >
            {busy ? "Comparing…" : "Compare"}
          </button>
        </div>

        {ready.length < 2 && (
          <p className="mt-2.5 text-[11px] text-amber-700">
            You need at least two ready documents to run a comparison.
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
          <div className="rounded-xl border border-neutral-200 bg-white p-4">
            <div className="text-xs font-semibold text-neutral-900 mb-1">Summary of Changes</div>
            <p className="text-xs text-neutral-700 leading-relaxed">{result.summary}</p>

            <div className="mt-3 pt-2.5 border-t border-neutral-100 flex flex-wrap gap-4 text-[11px] text-neutral-500 font-mono">
              <span>{result.counts.unchanged} unchanged</span>
              <span>{result.counts.modified} modified</span>
              <span>{result.counts.added} added in B</span>
              <span>{result.counts.removed} removed from A</span>
            </div>
          </div>

          {/* Compared Clauses */}
          <div className="space-y-3">
            {result.items.map((item, i) => (
              <div key={i} className="rounded-xl border border-neutral-200 bg-white p-4 space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-xs sm:text-sm font-semibold text-neutral-900 truncate">
                    {item.a?.title || item.b?.title || "(untitled clause)"}
                  </div>
                  <span
                    className={`rounded-md border px-2 py-0.5 text-[10px] font-medium uppercase font-mono ${
                      LEVEL_STYLES[item.status === "modified" ? item.change_level : item.status] ??
                      LEVEL_STYLES.unchanged
                    }`}
                  >
                    {item.status === "modified" ? item.change_level : item.status}
                  </span>
                </div>

                {item.change_summary && (
                  <p className="text-xs text-neutral-600 leading-relaxed bg-neutral-50 p-2.5 rounded-lg border border-neutral-100">
                    {item.change_summary}
                  </p>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                  {item.a && (
                    <div className="rounded-lg border border-neutral-100 bg-neutral-50/50 p-3 text-xs leading-relaxed text-neutral-700">
                      <div className="text-[10px] font-mono text-neutral-400 mb-1">
                        Version A{item.a.page_start !== null ? ` · p. ${item.a.page_start}` : ""}
                      </div>
                      <div className="whitespace-pre-wrap">{item.a.text}</div>
                    </div>
                  )}
                  {item.b && (
                    <div className="rounded-lg border border-neutral-100 bg-neutral-50/50 p-3 text-xs leading-relaxed text-neutral-700">
                      <div className="text-[10px] font-mono text-neutral-400 mb-1">
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
