import type { DocStatus } from "../lib/types";

const styles: Record<DocStatus, { label: string; cls: string }> = {
  uploaded: { label: "Queued", cls: "bg-slate-100 text-slate-600" },
  parsing: { label: "Parsing", cls: "bg-amber-100 text-amber-700" },
  embedding: { label: "Indexing", cls: "bg-amber-100 text-amber-700" },
  ready: { label: "Ready", cls: "bg-emerald-100 text-emerald-700" },
  failed: { label: "Failed", cls: "bg-red-100 text-red-700" },
};

export function StatusBadge({ status }: { status: DocStatus }) {
  const s = styles[status] ?? styles.uploaded;
  const busy = status === "parsing" || status === "embedding" || status === "uploaded";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${s.cls}`}
    >
      {busy && (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current opacity-70" />
      )}
      {s.label}
    </span>
  );
}
