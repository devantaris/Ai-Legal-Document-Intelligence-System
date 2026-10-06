import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import confetti from "canvas-confetti";
import {
  FileText,
  Upload,
  Search,
  Trash2,
  Loader2,
} from "lucide-react";
import { request, uploadDocument } from "../lib/api";
import type { DocumentOut } from "../lib/types";
import { StatusBadge } from "../components/StatusBadge";

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
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploadPct, setUploadPct] = useState<number | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  const prevStatuses = useRef<Map<string, string>>(new Map());
  const navigate = useNavigate();

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
  }, [load]);

  // Poll while any document is still processing
  useEffect(() => {
    if (!docs.some((d) => PROCESSING.has(d.status))) return;
    const t = setInterval(() => void load(), 2500);
    return () => clearInterval(t);
  }, [docs, load]);

  const upload = useCallback(
    async (file: File) => {
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
    [load],
  );

  const removeDoc = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
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
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-neutral-900">Documents</h1>
          <p className="mt-0.5 text-xs text-neutral-500">
            Upload legal agreements for executive summaries, structured terms, clause extraction, and Q&amp;A.
          </p>
        </div>
      </div>

      {/* Clean, Minimalist Dropzone */}
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
              <span>Uploading &amp; indexing… {uploadPct}%</span>
            </div>
            <div className="mx-auto mt-3 h-1 w-52 overflow-hidden rounded-full bg-neutral-100">
              <div
                className="h-full bg-neutral-900 transition-all duration-200"
                style={{ width: `${uploadPct}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-1.5">
            <Upload className="h-5 w-5 text-neutral-400" />
            <div className="text-xs font-medium text-neutral-800">
              Upload a document, or drag and drop
            </div>
            <div className="text-[11px] text-neutral-400">PDF, DOCX, TXT, MD up to 50 MB</div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-rose-50 border border-rose-200 p-3 text-xs text-rose-800">
          {error}
        </div>
      )}

      {/* Search & Document Count */}
      <div className="mt-8 flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-neutral-400" />
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documents..."
            className="w-full rounded-lg border border-neutral-200 bg-white pl-8 pr-3 py-1.5 text-xs text-neutral-900 placeholder-neutral-400 outline-none focus:border-neutral-400"
          />
        </div>
        <div className="text-xs text-neutral-400 font-mono">
          {filteredDocs.length} {filteredDocs.length === 1 ? "document" : "documents"}
        </div>
      </div>

      {/* Document List */}
      <div className="mt-3">
        {loading ? (
          <div className="py-12 text-center text-xs text-neutral-400">Loading documents…</div>
        ) : filteredDocs.length === 0 ? (
          <div className="rounded-xl border border-neutral-200 bg-white py-12 text-center text-xs text-neutral-500">
            {searchQuery
              ? `No documents matching "${searchQuery}"`
              : "No documents uploaded yet. Drop a file above to begin."}
          </div>
        ) : (
          <div className="overflow-hidden rounded-xl border border-neutral-200 bg-white">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-neutral-100 bg-neutral-50 text-neutral-500 font-medium">
                  <th className="py-2.5 px-4">Filename</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4">Pages</th>
                  <th className="py-2.5 px-4">Clauses</th>
                  <th className="py-2.5 px-4">Size</th>
                  <th className="py-2.5 px-4 text-right"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 text-neutral-700">
                {filteredDocs.map((doc) => (
                  <tr
                    key={doc.id}
                    onClick={() => navigate(`/documents/${doc.id}`)}
                    className="cursor-pointer hover:bg-neutral-50/80 transition"
                  >
                    <td className="py-3 px-4 font-medium text-neutral-900 max-w-sm truncate">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-neutral-400 shrink-0" />
                        <span className="truncate">{doc.filename}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={doc.status} />
                    </td>
                    <td className="py-3 px-4 font-mono text-neutral-500">
                      {doc.page_count ?? "—"}
                    </td>
                    <td className="py-3 px-4 font-mono text-neutral-500">
                      {doc.clause_count > 0 ? doc.clause_count : "—"}
                    </td>
                    <td className="py-3 px-4 font-mono text-neutral-400">
                      {formatBytes(doc.size_bytes)}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={(e) => void removeDoc(doc.id, e)}
                        className="rounded p-1 text-neutral-400 hover:text-rose-600 transition"
                        title="Delete document"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
