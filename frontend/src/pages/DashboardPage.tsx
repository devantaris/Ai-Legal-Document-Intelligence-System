import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import confetti from "canvas-confetti";
import {
  FileText,
  Upload,
  Search,
  Trash2,
  Loader2,
  FolderKanban,
  Building2,
  Lock,
} from "lucide-react";
import { request, uploadDocument } from "../lib/api";
import type { DocumentOut } from "../lib/types";
import { StatusBadge } from "../components/StatusBadge";
import { useTenant } from "../stores/tenant";

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

const PROCESSING = new Set(["uploaded", "parsing", "embedding"]);

function celebrateReady() {
  const defaults = {
    origin: { y: 0.7 },
    colors: ["#18181b", "#6366f1", "#10b981", "#a1a1aa"],
    ticks: 160,
  };
  confetti({ ...defaults, particleCount: 60, spread: 70, startVelocity: 38 });
  setTimeout(
    () => confetti({ ...defaults, particleCount: 35, spread: 110, startVelocity: 30 }),
    220,
  );
}

export function DashboardPage() {
  const { currentOrg, currentWorkspace } = useTenant();
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploadPct, setUploadPct] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const prevStatuses = useRef<Map<string, string>>(new Map());
  const navigate = useNavigate();

  const isViewer = currentOrg?.role === "viewer";

  const load = useCallback(async () => {
    try {
      const fresh = await request<DocumentOut[]>("/documents");
      // celebrate documents that just finished processing
      for (const d of fresh) {
        const before = prevStatuses.current.get(d.id);
        if (before && PROCESSING.has(before) && d.status === "ready") celebrateReady();
      }
      prevStatuses.current = new Map(fresh.map((d) => [d.id, d.status]));
      setDocs(fresh);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const handleTenantChange = () => void load();
    window.addEventListener("lda:tenant_changed", handleTenantChange);
    return () => window.removeEventListener("lda:tenant_changed", handleTenantChange);
  }, [load, currentOrg?.id, currentWorkspace?.id]);

  // Poll while any document is still processing
  useEffect(() => {
    if (!docs.some((d) => PROCESSING.has(d.status))) return;
    const t = setInterval(() => void load(), 2500);
    return () => clearInterval(t);
  }, [docs, load]);

  const upload = useCallback(
    async (file: File) => {
      if (isViewer) return;
      setError(null);
      setUploadPct(0);
      try {
        await uploadDocument(file, setUploadPct);
        await load();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploadPct(null);
      }
    },
    [load, isViewer],
  );

  const removeDoc = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (isViewer) {
      alert("Viewers cannot delete documents");
      return;
    }
    if (!window.confirm("Delete this document and its analysis?")) return;
    try {
      await request(`/documents/${id}`, { method: "DELETE" });
      void load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete document");
    }
  };

  const filteredDocs = docs.filter((d) =>
    d.filename.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <div className="mx-auto max-w-5xl px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-neutral-500 uppercase tracking-wider mb-1">
            <Building2 className="h-3.5 w-3.5" />
            <span>{currentOrg?.name ?? "Legal Org"}</span>
            <span className="text-neutral-300">•</span>
            <FolderKanban className="h-3.5 w-3.5" />
            <span>{currentWorkspace?.name ?? "General Matters"}</span>
          </div>
          <h1 className="text-xl font-bold tracking-tight text-neutral-900">Matter Contracts</h1>
          <p className="mt-0.5 text-xs text-neutral-500">
            Sovereign legal intelligence repository for institutional playbooks, redlines, and cross-contract QA.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-neutral-200 bg-white px-3 py-1 text-xs font-mono text-neutral-600">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span>{filteredDocs.length} active agreements</span>
          </span>
        </div>
      </div>

      {/* Clean, Minimalist Dropzone */}
      {!isViewer ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragging(false);
            const file = e.dataTransfer.files?.[0];
            if (file) void upload(file);
          }}
          onClick={() => fileInput.current?.click()}
          className={`cursor-pointer rounded-xl border border-dashed p-7 text-center transition ${
            dragging
              ? "border-neutral-900 bg-neutral-100"
              : "border-neutral-300 bg-white hover:border-neutral-400 hover:bg-neutral-50/50"
          }`}
        >
          <input
            ref={fileInput}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) void upload(file);
              e.target.value = "";
            }}
          />

          {uploadPct !== null ? (
            <div className="py-2">
              <div className="text-xs font-medium text-neutral-800 flex items-center justify-center gap-2">
                <Loader2 className="h-3.5 w-3.5 animate-spin text-neutral-600" />
                <span>Uploading to {currentWorkspace?.name ?? "Matter"}… {uploadPct}%</span>
              </div>
              <div className="mx-auto mt-3 h-1 w-52 overflow-hidden rounded-full bg-neutral-100">
                <div
                  className="h-full bg-neutral-900 transition-all duration-200"
                  style={{ width: `${uploadPct}%` }}
                />
              </div>
            </div>
          ) : (
            <div>
              <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-100 text-neutral-600">
                <Upload className="h-4 w-4" />
              </div>
              <div className="mt-3 text-xs font-medium text-neutral-800">
                Upload Agreement into <span className="font-semibold text-neutral-900">{currentWorkspace?.name ?? "Workspace"}</span>
              </div>
              <div className="mt-1 text-[11px] text-neutral-400">
                Drag and drop PDF, DOCX, TXT or Markdown contracts (up to 50 MB)
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-xl border border-neutral-200 bg-neutral-50 p-4 text-center text-xs text-neutral-500 flex items-center justify-center gap-2">
          <Lock className="h-3.5 w-3.5 text-neutral-400" />
          <span>Read-only Viewer Mode: document uploads are disabled for your role.</span>
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-xs text-red-700">
          {error}
        </div>
      )}

      {/* Search Filter Bar */}
      <div className="mt-6 flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            placeholder="Filter indexed contracts by name…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-neutral-200/80 bg-white pl-9 pr-3 py-1.5 text-xs placeholder:text-neutral-400 focus:border-neutral-900 focus:outline-none transition"
          />
        </div>
      </div>

      {/* Contract Table */}
      <div className="mt-3 rounded-xl border border-neutral-200/80 bg-white overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-8 text-center text-xs text-neutral-400">
            <Loader2 className="mx-auto h-5 w-5 animate-spin text-neutral-400 mb-2" />
            Loading organization contracts…
          </div>
        ) : filteredDocs.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-7 w-7 text-neutral-300" />
            <div className="mt-2 text-xs font-medium text-neutral-700">
              {searchQuery ? "No contracts match your query" : "No agreements in this matter yet"}
            </div>
            <div className="mt-0.5 text-[11px] text-neutral-400">
              {searchQuery
                ? "Try clearing your search keyword."
                : "Upload an NDA, Master Services Agreement, or Lease above to begin."}
            </div>
          </div>
        ) : (
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-neutral-100 bg-neutral-50/50 text-neutral-400 font-mono text-[11px]">
                <th className="py-2.5 px-4 font-normal">Agreement</th>
                <th className="py-2.5 px-3 font-normal">Status</th>
                <th className="py-2.5 px-3 font-normal">Pages</th>
                <th className="py-2.5 px-3 font-normal">Clauses</th>
                <th className="py-2.5 px-3 font-normal">Size</th>
                <th className="py-2.5 px-3 font-normal">Date</th>
                {!isViewer && <th className="py-2.5 px-3 text-right font-normal">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 text-neutral-700">
              {filteredDocs.map((doc) => {
                const isReady = doc.status === "ready";
                return (
                  <tr
                    key={doc.id}
                    onClick={() => isReady && navigate(`/documents/${doc.id}`)}
                    className={`transition ${
                      isReady ? "cursor-pointer hover:bg-neutral-50/80" : "opacity-75"
                    }`}
                  >
                    <td className="py-3 px-4 font-medium text-neutral-900">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 shrink-0 text-neutral-400" />
                        <span className="truncate max-w-md">{doc.filename}</span>
                      </div>
                    </td>
                    <td className="py-3 px-3">
                      <StatusBadge status={doc.status} />
                    </td>
                    <td className="py-3 px-3 font-mono text-neutral-500">
                      {doc.page_count ?? "—"}
                    </td>
                    <td className="py-3 px-3 font-mono text-neutral-500">
                      {doc.clause_count > 0 ? doc.clause_count : "—"}
                    </td>
                    <td className="py-3 px-3 font-mono text-neutral-500">
                      {formatBytes(doc.size_bytes)}
                    </td>
                    <td className="py-3 px-3 font-mono text-neutral-400 text-[11px]">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    {!isViewer && (
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={(e) => removeDoc(doc.id, e)}
                          className="rounded p-1 text-neutral-400 hover:text-rose-600 transition"
                          title="Delete Contract"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
