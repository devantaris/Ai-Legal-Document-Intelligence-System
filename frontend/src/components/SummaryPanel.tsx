import { useState } from "react";
import Markdown from "react-markdown";
import { Copy, Check, RefreshCw } from "lucide-react";
import { request } from "../lib/api";
import type { DocumentOut } from "../lib/types";

export function SummaryPanel({ doc }: { doc: DocumentOut }) {
  const [summary, setSummary] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

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
    return <div className="py-12 text-center text-xs text-neutral-400">Generating summary…</div>;
  }

  const handleCopy = () => {
    if (!summary) return;
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-3">
      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-neutral-500">Executive Summary</span>
        <div className="flex items-center gap-2">
          {summary && (
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 rounded-lg border border-neutral-200 bg-white px-2.5 py-1 text-xs text-neutral-600 hover:bg-neutral-50 transition"
            >
              {copied ? <Check className="h-3 w-3 text-emerald-600" /> : <Copy className="h-3 w-3" />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
          )}

          <button
            onClick={() => void generate(true)}
            disabled={busy}
            className="flex items-center gap-1 rounded-lg border border-neutral-200 bg-white px-2.5 py-1 text-xs text-neutral-600 hover:bg-neutral-50 transition disabled:opacity-50"
          >
            <RefreshCw className={`h-3 w-3 ${busy ? "animate-spin" : ""}`} />
            <span>{busy ? "Working…" : "Regenerate"}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700">
          {error}
        </div>
      )}

      {/* Clean High-Legibility Typography Card */}
      <article className="rounded-xl border border-neutral-200 bg-white p-6 sm:p-8 text-xs sm:text-sm leading-relaxed text-neutral-800 [&_h1]:text-lg [&_h1]:font-semibold [&_h1]:text-neutral-900 [&_h1]:mt-5 [&_h1]:mb-2 [&_h2]:text-sm [&_h2]:font-semibold [&_h2]:text-neutral-900 [&_h2]:mt-5 [&_h2]:mb-2 [&_h3]:text-xs [&_h3]:font-semibold [&_h3]:text-neutral-900 [&_h3]:mt-4 [&_h3]:mb-1 [&_p]:my-2 [&_ul]:my-2 [&_ul]:list-disc [&_ul]:pl-5 [&_li]:my-1 [&_strong]:text-neutral-950 [&_blockquote]:border-l-2 [&_blockquote]:border-neutral-300 [&_blockquote]:pl-3 [&_blockquote]:my-2 [&_blockquote]:italic text-justify">
        <Markdown>{summary ?? ""}</Markdown>
      </article>
    </div>
  );
}
