import { useState } from "react";
import Markdown from "react-markdown";
import { request } from "../lib/api";
import type { DocumentOut } from "../lib/types";

export function SummaryPanel({ doc }: { doc: DocumentOut }) {
  const [summary, setSummary] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async (refresh: boolean) => {
    setBusy(true);
    setError(null);
    try {
      const r = await request<{ summary_md: string }>(
        `/documents/${doc.id}/summary${refresh ? "?refresh=true" : ""}`,
      );
      setSummary(r.summary_md);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate summary");
    } finally {
      setBusy(false);
    }
  };

  if (summary === null && !busy) {
    void generate(false);
    return <div className="py-10 text-center text-sm text-slate-400">Generating summary…</div>;
  }

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <button
          onClick={() => void generate(true)}
          disabled={busy}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-indigo-300 hover:text-indigo-700 disabled:opacity-50"
        >
          {busy ? "Working…" : "Regenerate"}
        </button>
      </div>
      {error && <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
      <article className="prose-sm max-w-none rounded-2xl border border-slate-200 bg-white p-6 leading-relaxed text-slate-700 [&_h2]:mt-5 [&_h2]:mb-2 [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-slate-900 [&_li]:mt-1 [&_p]:my-2 [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5">
        <Markdown>{summary ?? ""}</Markdown>
      </article>
    </div>
  );
}
