import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";
import { request } from "../lib/api";
import type { DocumentOut, KeyTerms } from "../lib/types";

function TermCard({
  label,
  value,
  wide = false,
}: {
  label: string;
  value: string | null | undefined;
  wide?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border border-neutral-200 bg-white p-4 ${
        wide ? "sm:col-span-2" : ""
      }`}
    >
      <div className="text-[11px] font-medium uppercase tracking-wider text-neutral-400">
        {label}
      </div>
      <div
        className={`mt-1.5 text-xs sm:text-sm font-medium leading-relaxed ${
          value ? "text-neutral-900" : "italic text-neutral-400"
        }`}
      >
        {value || "Not specified in document"}
      </div>
    </div>
  );
}

export function KeyTermsPanel({ doc }: { doc: DocumentOut }) {
  const [terms, setTerms] = useState<KeyTerms | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async (refresh: boolean) => {
    setBusy(true);
    setError(null);
    try {
      const r = await request<{ data: KeyTerms }>(
        `/documents/${doc.id}/key-terms${refresh ? "?refresh=true" : ""}`,
      );
      setTerms(r.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to extract key terms");
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    void load(false);
  }, [doc.id]);

  if (busy && !terms)
    return <div className="py-12 text-center text-xs text-neutral-400">Extracting key terms…</div>;

  if (error)
    return (
      <div className="rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-700">
        {error}
      </div>
    );

  if (!terms) return null;

  const partiesString = terms.parties
    .map((p) => `${p.name}${p.role ? ` (${p.role})` : ""}`)
    .join(" · ");

  return (
    <div className="space-y-4">
      {/* Action Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {terms.agreement_type && (
            <span className="rounded-md bg-neutral-100 px-2 py-0.5 text-xs font-medium text-neutral-800">
              {terms.agreement_type}
            </span>
          )}
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

      {/* Grid of Key Terms */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <TermCard label="Parties" value={partiesString} wide />
        <TermCard label="Effective Date" value={terms.effective_date} />
        <TermCard label="Contract Term" value={terms.term} />
        <TermCard label="Governing Law" value={terms.governing_law} />
        <TermCard label="Renewal Terms" value={terms.renewal} />
        <TermCard label="Payment Terms" value={terms.payment_terms} wide />
        <TermCard label="Termination" value={terms.termination} wide />
        <TermCard label="Confidentiality" value={terms.confidentiality} wide />
        <TermCard label="Indemnification" value={terms.indemnification} wide />
        <TermCard label="Dispute Resolution" value={terms.dispute_resolution} wide />

        {/* Obligations */}
        {terms.obligations && terms.obligations.length > 0 && (
          <div className="rounded-xl border border-neutral-200 bg-white p-4 sm:col-span-2">
            <div className="text-[11px] font-medium uppercase tracking-wider text-neutral-400 mb-2">
              Key Obligations
            </div>
            <ul className="space-y-1.5 text-xs text-neutral-700 pl-4 list-disc">
              {terms.obligations.map((o, i) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Special Notes */}
        {terms.special_notes && terms.special_notes.length > 0 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50/50 p-4 sm:col-span-2">
            <div className="text-[11px] font-medium uppercase tracking-wider text-amber-700 mb-2">
              Noteworthy Provisions
            </div>
            <ul className="space-y-1.5 text-xs text-amber-900 pl-4 list-disc">
              {terms.special_notes.map((n, i) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
