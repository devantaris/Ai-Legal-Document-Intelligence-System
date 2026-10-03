import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { request, uploadDocument } from "../lib/api";
import type { DocumentOut } from "../lib/types";
import { StatusBadge } from "../components/StatusBadge";

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

const PROCESSING = new Set(["uploaded", "parsing", "embedding"]);

export function DashboardPage() {
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [uploadPct, setUploadPct] = useState<number | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    try {
      setDocs(await request<DocumentOut[]>("/documents"));
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

  // poll while any document is still processing
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

  const remove = async (id: string) => {
    if (!confirm("Delete this document and all its analysis?")) return;
    await request(`/documents/${id}`, { method: "DELETE" });
    void load();
  };

  return (
    <div className="mx-auto max-w-5xl px-8 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Documents</h1>
          <p className="mt-1 text-sm text-slate-500">
            Upload contracts &amp; agreements — get summaries, key terms, a clause library and Q&amp;A.
          </p>
        </div>
      </div>

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
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
          dragging
            ? "border-indigo-400 bg-indigo-50"
            : "border-slate-300 bg-white hover:border-indigo-300 hover:bg-indigo-50/40"
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
          <div>
            <div className="text-sm font-medium text-indigo-600">Uploading… {uploadPct}%</div>
            <div className="mx-auto mt-3 h-1.5 w-56 overflow-hidden rounded-full bg-slate-200">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all"
                style={{ width: `${uploadPct}%` }}
              />
            </div>
          </div>
        ) : (
          <>
            <div className="text-3xl">📤</div>
            <p className="mt-2 text-sm font-medium text-slate-700">
              Drop a document here, or click to browse
            </p>
            <p className="mt-1 text-xs text-slate-400">PDF, DOCX, TXT or MD · up to 50 MB</p>
          </>
        )}
      </div>

      {error && (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="mt-8">
        {loading ? (
          <div className="py-10 text-center text-sm text-slate-400">Loading documents…</div>
        ) : docs.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white py-12 text-center text-sm text-slate-500">
            No documents yet — upload your first contract above.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {docs.map((doc) => (
              <div
                key={doc.id}
                className="group relative rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-indigo-300 hover:shadow"
              >
                <div className="flex items-start justify-between gap-3">
                  <Link to={`/documents/${doc.id}`} className="min-w-0 flex-1">
                    <div className="truncate font-medium text-slate-900 group-hover:text-indigo-700">
                      {doc.filename}
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
                      <StatusBadge status={doc.status} />
                      {doc.page_count !== null && <span>{doc.page_count} pages</span>}
                      <span>{formatBytes(doc.size_bytes)}</span>
                      {doc.status === "ready" && (
                        <>
                          <span>{doc.chunk_count} chunks</span>
                          {doc.clause_count > 0 && <span>{doc.clause_count} clauses</span>}
                        </>
                      )}
                    </div>
                    {doc.error && (
                      <div className="mt-2 line-clamp-2 text-xs text-red-600" title={doc.error}>
                        {doc.error}
                      </div>
                    )}
                  </Link>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      void remove(doc.id);
                    }}
                    className="rounded p-1 text-slate-300 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                    title="Delete document"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
