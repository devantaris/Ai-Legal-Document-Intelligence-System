import { useEffect, useState } from "react";
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
      className={`rounded-xl border border-slate-200 bg-white p-4 ${wide ? "sm:col-span-2" : ""}`}
    >
      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</div>
      <div className={`mt-1.5 text-sm ${value ? "text-slate-800" : "italic text-slate-300"}`}>
        {value || "Not specified"}
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doc.id]);

  if (busy && !terms)
    return <div className="py-10 text-center text-sm text-slate-400">Extracting key terms…</div>;
  if (error)
    return <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>;
  if (!terms) return null;

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <button
          onClick={() => void load(true)}
          disabled={busy}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 transition hover:border-indigo-300 hover:text-indigo-700 disabled:opacity-50"
        >
          {busy ? "Working…" : "Re-extract"}
        </button>
      </div>

      {terms.agreement_type && (
        <div className="mb-4 rounded-xl bg-indigo-50 px-4 py-3 text-sm font-medium text-indigo-800">
          {terms.agreement_type}
        </div>
      )}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <TermCard
          label="Parties"
          value={terms.parties.map((p) => `${p.name}${p.role ? ` (${p.role})` : ""}`).join(" · ")}
          wide
        />
        <TermCard label="Effective date" value={terms.effective_date} />
        <TermCard label="Term" value={terms.term} />
        <TermCard label="Governing law" value={terms.governing_law} />
        <TermCard label="Renewal" value={terms.renewal} />
        <TermCard label="Payment terms" value={terms.payment_terms} wide />
        <TermCard label="Termination" value={terms.termination} wide />
        <TermCard label="Confidentiality" value={terms.confidentiality} wide />
        <TermCard label="Indemnification" value={terms.indemnification} wide />
        <TermCard label="Dispute resolution" value={terms.dispute_resolution} wide />
        {terms.obligations.length > 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-4 sm:col-span-2">
            <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Key obligations
            </div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
              {terms.obligations.map((o, i) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </div>
        )}
        {terms.special_notes.length > 0 && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 sm:col-span-2">
            <div className="text-xs font-medium uppercase tracking-wide text-amber-600">
              Worth noting
            </div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-900">
              {terms.special_notes.map((o, i) => (
                <li key={i}>{o}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
