import { useEffect, useState } from "react";
import {
  ShieldCheck,
  Download,
  Search,
  Filter,
  RefreshCw,
  User,
  FileText,
  Lock,
  Code,
  X,
} from "lucide-react";
import { getAccessToken, request } from "../lib/api";
import { useTenant } from "../stores/tenant";
import type { AuditLog } from "../lib/types";

export function AuditLogsPage() {
  const { currentOrg } = useTenant();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState("ALL");
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [exporting, setExporting] = useState(false);

  const loadLogs = async () => {
    if (!currentOrg) return;
    setLoading(true);
    setError(null);
    try {
      const data = await request<AuditLog[]>(`/organizations/${currentOrg.id}/audit-logs?limit=200`);
      setLogs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load audit logs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadLogs();
  }, [currentOrg?.id]);

  const handleExportCsv = async () => {
    if (!currentOrg) return;
    setExporting(true);
    try {
      const token = getAccessToken();
      const res = await fetch(`/api/organizations/${currentOrg.id}/audit-logs/export-csv`, {
        headers: {
          Authorization: `Bearer ${token}`,
          "X-Organization-Id": currentOrg.id,
        },
      });
      if (!res.ok) throw new Error("Failed to export compliance CSV");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `LegalIQ_Audit_Log_${currentOrg.slug}_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  };

  const getActionBadge = (action: string) => {
    if (action.includes("upload") || action.includes("create")) {
      return (
        <span className="inline-flex items-center rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
          {action}
        </span>
      );
    }
    if (action.includes("export") || action.includes("download")) {
      return (
        <span className="inline-flex items-center rounded-md border border-sky-200 bg-sky-50 px-2 py-0.5 text-[10px] font-semibold text-sky-800">
          {action}
        </span>
      );
    }
    if (action.includes("delete") || action.includes("remove")) {
      return (
        <span className="inline-flex items-center rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-800">
          {action}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center rounded-md border border-neutral-200 bg-neutral-100 px-2 py-0.5 text-[10px] font-semibold text-neutral-700">
        {action}
      </span>
    );
  };

  const filteredLogs = logs.filter((l) => {
    const matchesSearch =
      (l.actor_email && l.actor_email.toLowerCase().includes(search.toLowerCase())) ||
      (l.action && l.action.toLowerCase().includes(search.toLowerCase())) ||
      (l.resource_id && l.resource_id.toLowerCase().includes(search.toLowerCase())) ||
      (l.resource_type && l.resource_type.toLowerCase().includes(search.toLowerCase()));

    const matchesFilter = actionFilter === "ALL" || l.action.toLowerCase().includes(actionFilter.toLowerCase());

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6 px-6 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E2E8F0] pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono text-neutral-400 uppercase tracking-wider font-semibold">
              {currentOrg?.name ?? "Firm Governance"}
            </span>
            <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-[10px] font-bold text-emerald-800 uppercase font-mono">
              <ShieldCheck className="h-3 w-3 text-emerald-600" />
              <span>SOC 2 Type II Immutable</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#0F172A] font-serif-legal">
            Compliance Audit Ledger & Governance
          </h1>
          <p className="mt-1 text-xs text-neutral-500 max-w-2xl leading-relaxed">
            Cryptographically signed ledger recording all document access, redline exports, client member invitations, and playbook policy modifications.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={loadLogs}
            className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3.5 py-2 text-xs font-semibold text-neutral-700 hover:bg-[#F8F9FA] transition shadow-2xs"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleExportCsv}
            disabled={exporting}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[#0F172A] px-4 py-2 text-xs font-semibold text-white hover:bg-neutral-800 disabled:opacity-50 transition shadow-sm"
          >
            {exporting ? <RefreshCw className="h-3.5 w-3.5 animate-spin text-amber-400" /> : <Download className="h-3.5 w-3.5 text-amber-400" />}
            <span>Export Compliance CSV</span>
          </button>
        </div>
      </div>

      {/* Governance Banner */}
      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5 text-xs text-neutral-600 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-2xs">
        <div className="flex items-center gap-3.5">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#F8F9FA] border border-[#E2E8F0] text-[#0F172A] shadow-2xs">
            <Lock className="h-4 w-4 text-amber-700" />
          </div>
          <div>
            <div className="font-bold text-sm text-[#0F172A] font-serif-legal">Zero Data Egress & Tamper-Evident Ledger</div>
            <div className="text-[11px] text-neutral-500 leading-relaxed">
              Inference is executed exclusively in-process or via Sovereign Local LLMs. Audit records cannot be altered or purged.
            </div>
          </div>
        </div>
        <div className="text-[11px] text-neutral-400 font-mono bg-[#F8F9FA] px-2.5 py-1 rounded-md border border-[#E2E8F0]">
          Tenant UID: {currentOrg?.id}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative max-w-md flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by actor email, action, or resource ID…"
            className="w-full rounded-xl border border-[#E2E8F0] bg-white pl-9 pr-3 py-2 text-xs text-[#0F172A] placeholder-neutral-400 focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-neutral-400" />
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="rounded-xl border border-[#E2E8F0] bg-white px-3 py-2 text-xs text-[#0F172A] font-medium focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
          >
            <option value="ALL">All Recorded Actions</option>
            <option value="upload">Document Uploads (document.upload)</option>
            <option value="export">Redline Exports (export_redline)</option>
            <option value="delete">Deletions (document.delete)</option>
            <option value="member">Team Governance & Invites</option>
          </select>
        </div>
      </div>

      {/* Audit Logs Table */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
          <RefreshCw className="h-5 w-5 animate-spin mb-2" />
          <span className="text-xs">Fetching immutable audit records…</span>
        </div>
      ) : error ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
          {error}
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="rounded-xl border border-neutral-200 bg-white p-12 text-center text-xs text-neutral-500">
          No audit records found matching your filters.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-neutral-200/90 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-neutral-200/80 bg-neutral-50/60 text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
                <tr>
                  <th className="px-4 py-3">Timestamp (UTC)</th>
                  <th className="px-4 py-3">Actor</th>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Resource</th>
                  <th className="px-4 py-3">Client IP</th>
                  <th className="px-4 py-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {filteredLogs.map((log) => {
                  const dateObj = new Date(log.created_at);
                  const timeFormatted = dateObj.toLocaleString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    timeZoneName: "short",
                  });

                  return (
                    <tr key={log.id} className="hover:bg-neutral-50/50 transition">
                      <td className="px-4 py-3 whitespace-nowrap font-mono text-[11px] text-neutral-500">
                        {timeFormatted}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-1.5 font-medium text-neutral-900">
                          <User className="h-3 w-3 text-neutral-400" />
                          <span>{log.actor_email ?? "system_internal"}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        {getActionBadge(log.action)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div className="flex items-center gap-1 text-neutral-600">
                          <FileText className="h-3 w-3 text-neutral-400" />
                          <span className="font-mono text-[10px]">{log.resource_type}:</span>
                          <span className="font-mono text-[10px] text-neutral-400">
                            {log.resource_id ? `${log.resource_id.slice(0, 8)}…` : "—"}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap font-mono text-[10px] text-neutral-400">
                        {log.ip_address || "127.0.0.1 (Sovereign)"}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-right">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="inline-flex items-center gap-1 rounded border border-neutral-200 bg-white px-2 py-0.5 text-[11px] font-medium text-neutral-700 hover:bg-neutral-100 transition"
                        >
                          <Code className="h-3 w-3 text-neutral-400" />
                          <span>Inspect</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Detail JSON Modal */}
      {selectedLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="relative flex flex-col w-full max-w-lg rounded-2xl bg-white shadow-2xl border border-neutral-200 overflow-hidden">
            <div className="flex items-center justify-between border-b border-neutral-200 px-5 py-3.5 bg-neutral-50">
              <div className="flex items-center gap-2">
                <Code className="h-4 w-4 text-neutral-600" />
                <h3 className="text-xs font-bold text-neutral-900">Audit Event Metadata</h3>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="rounded-lg p-1 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-5 space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-neutral-400">Action:</span>{" "}
                  <strong className="text-neutral-800">{selectedLog.action}</strong>
                </div>
                <div>
                  <span className="text-neutral-400">Actor:</span>{" "}
                  <strong className="text-neutral-800">{selectedLog.actor_email ?? "System"}</strong>
                </div>
                <div>
                  <span className="text-neutral-400">Event ID:</span>{" "}
                  <code className="text-neutral-700">{selectedLog.id}</code>
                </div>
                <div>
                  <span className="text-neutral-400">Timestamp:</span>{" "}
                  <span className="text-neutral-700">{selectedLog.created_at}</span>
                </div>
              </div>
              <div className="rounded-lg bg-neutral-900 p-3 text-[11px] font-mono text-emerald-400 overflow-x-auto max-h-60">
                <pre>{JSON.stringify(selectedLog.details, null, 2)}</pre>
              </div>
            </div>
            <div className="flex justify-end border-t border-neutral-200 px-5 py-3 bg-neutral-50">
              <button
                onClick={() => setSelectedLog(null)}
                className="rounded-lg bg-neutral-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-neutral-800 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
