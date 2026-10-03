import { useEffect, useState } from "react";
import { request } from "../lib/api";
import type { CompareResult, DocumentOut } from "../lib/types";

const LEVEL_STYLES: Record<string, string> = {
  unchanged: "bg-slate-100 text-slate-500",
  minor: "bg-sky-100 text-sky-700",
  moderate: "bg-amber-100 text-amber-700",
  major: "bg-red-100 text-red-700",
};

export function ComparePage() {
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [aId, setAId] = useState("");
  const [bId, setBId] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CompareResult | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setDocs(await request<DocumentOut[]>("/documents"));
      } catch {
        /* handled by compare attempt */
      }
    })();
  }, []);

  const ready = docs.filter((d) => d.status === "ready");

  const run = async () => {
    if (!aId || !bId || aId === bId) {
      setError("Pick two different documents.");
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(
        await request<CompareResult>("/compare", {
          method: "POST",
          body: JSON.stringify({ document_a_id: aId, document_b_id: bId }),
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Compare failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-8 py-8">
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">Compare documents</h1>
      <p className="mt-1 text-sm text-slate-500">
        Aligns clauses across two versions and summarizes what changed.
      </p>

      <div className="mt-6 flex flex-wrap items-center gap-3 rounded-2xl border border-slate-200 bg-white p-4">
        <select
          value={aId}
          onChange={(e) => setAId(e.target.value)}
          className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
        >
          <option value="">Version A…</option>
          {ready.map((d) => (
            <option key={d.id} value={d.id}>
              {d.filename}
            </option>
          ))}
        </select>
        <span className="text-slate-400">vs</span>
        <select
          value={bId}
          onChange={(e) => setBId(e.target.value)}
          className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
        >
          <option value="">Version B…</option>
          {ready.map((d) => (
            <option key={d.id} value={d.id}>
              {d.filename}
            </option>
          ))}
        </select>
        <button
          onClick={() => void run()}
          disabled={busy}
          className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-50"
        >
          {busy ? "Comparing…" : "Compare"}
        </button>
      </div>

      {ready.length < 2 && (
        <p className="mt-3 text-xs text-amber-600">
          You need at least two processed documents to compare.
        </p>
      )}
      {error && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}
      {busy && (
        <div className="mt-6 py-10 text-center text-sm text-slate-400">
          Matching clauses and analyzing changes — this can take a minute…
        </div>
      )}

      {result && (
        <div className="mt-6">
          <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-5 text-sm text-indigo-900">
            {result.summary}
          </div>
          <div className="mt-3 flex gap-4 text-xs text-slate-500">
            <span>{result.counts.unchanged} unchanged</span>
            <span>{result.counts.modified} modified</span>
            <span>{result.counts.added} added in B</span>
            <span>{result.counts.removed} removed from A</span>
          </div>

          <div className="mt-4 space-y-3">
            {result.items.map((item, i) => {
              const border =
                item.status === "added"
                  ? "border-emerald-300"
                  : item.status === "removed"
                    ? "border-red-300"
                    : item.change_level === "major"
                      ? "border-red-200"
                      : item.change_level === "moderate"
                        ? "border-amber-200"
                        : "border-slate-200";
              return (
                <div key={i} className={`rounded-xl border bg-white p-4 ${border}`}>
                  <div className="flex items-center justify-between gap-3">
                    <div className="truncate text-sm font-medium text-slate-800">
                      {item.a?.title || item.b?.title || "(untitled clause)"}
                    </div>
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ${
                        LEVEL_STYLES[item.change_level] ?? "bg-slate-100 text-slate-500"
                      }`}
                    >
                      {item.status === "modified" ? item.change_level : item.status}
                    </span>
                  </div>
                  {item.change_summary && (
                    <p className="mt-1.5 text-sm text-slate-600">{item.change_summary}</p>
                  )}
                  <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {item.a && (
                      <div className="rounded-lg bg-slate-50 p-3 text-xs leading-relaxed whitespace-pre-wrap text-slate-600">
                        <div className="mb-1 font-semibold text-slate-400">
                          A{item.a.page_start !== null ? ` · p. ${item.a.page_start}` : ""}
                        </div>
                        {item.a.text}
                      </div>
                    )}
                    {item.b && (
                      <div className="rounded-lg bg-slate-50 p-3 text-xs leading-relaxed whitespace-pre-wrap text-slate-600">
                        <div className="mb-1 font-semibold text-slate-400">
                          B{item.b.page_start !== null ? ` · p. ${item.b.page_start}` : ""}
                        </div>
                        {item.b.text}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
