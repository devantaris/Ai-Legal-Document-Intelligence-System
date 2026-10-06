import type { DocStatus } from "../lib/types";
import { CheckCircle2, Clock, AlertCircle, Loader2 } from "lucide-react";

const STYLES: Record<
  DocStatus,
  { label: string; bg: string; text: string; border: string; icon: typeof CheckCircle2 }
> = {
  uploaded: {
    label: "Queued",
    bg: "bg-neutral-100",
    text: "text-neutral-600",
    border: "border-neutral-200",
    icon: Clock,
  },
  parsing: {
    label: "Parsing",
    bg: "bg-amber-50",
    text: "text-amber-800",
    border: "border-amber-200",
    icon: Loader2,
  },
  embedding: {
    label: "Indexing",
    bg: "bg-neutral-100",
    text: "text-neutral-700",
    border: "border-neutral-200",
    icon: Loader2,
  },
  ready: {
    label: "Ready",
    bg: "bg-emerald-50",
    text: "text-emerald-700",
    border: "border-emerald-200",
    icon: CheckCircle2,
  },
  failed: {
    label: "Failed",
    bg: "bg-rose-50",
    text: "text-rose-700",
    border: "border-rose-200",
    icon: AlertCircle,
  },
};

export function StatusBadge({ status }: { status: DocStatus }) {
  const s = STYLES[status] ?? STYLES.uploaded;
  const isBusy = status === "parsing" || status === "embedding" || status === "uploaded";
  const Icon = s.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-[11px] font-medium ${s.bg} ${s.text} ${s.border}`}
    >
      <Icon className={`h-3 w-3 ${isBusy && status !== "uploaded" ? "animate-spin" : ""}`} />
      <span>{s.label}</span>
    </span>
  );
}
