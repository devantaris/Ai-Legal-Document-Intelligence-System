import { useEffect, useState } from "react";
import {
  FolderKanban,
  Plus,
  FolderOpen,
  FileText,
  Check,
  AlertCircle,
  Building2,
  Trash2,
} from "lucide-react";
import { useTenant } from "../stores/tenant";
import { ApiError, request } from "../lib/api";

export function WorkspacesPage() {
  const { currentOrg, workspaces, currentWorkspace, selectWorkspace, loadWorkspaces, createWorkspace } =
    useTenant();
  const [createOpen, setCreateOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isOwnerOrAdmin = currentOrg?.role === "owner" || currentOrg?.role === "admin";

  useEffect(() => {
    if (currentOrg) {
      void loadWorkspaces(currentOrg.id);
    }
  }, [currentOrg?.id]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await createWorkspace(name.trim(), description.trim() || undefined);
      setName("");
      setDescription("");
      setCreateOpen(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create workspace");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (workspaceId: string, wsName: string) => {
    if (!currentOrg) return;
    if (workspaces.length <= 1) {
      alert("Cannot delete the only workspace in an organization.");
      return;
    }
    if (!confirm(`Are you sure you want to delete workspace "${wsName}"?`)) return;

    setError(null);
    try {
      await request(`/organizations/${currentOrg.id}/workspaces/${workspaceId}`, {
        method: "DELETE",
      });
      await loadWorkspaces(currentOrg.id);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete workspace");
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-neutral-200/80 pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-neutral-500 uppercase tracking-wider">
            <Building2 className="h-3.5 w-3.5" />
            <span>{currentOrg?.name ?? "Organization"}</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-neutral-900">
            Workspaces & Legal Matters
          </h1>
          <p className="mt-1 text-xs text-neutral-500">
            Organize agreements by transaction, corporate acquisition, or client matter with partitioned repositories.
          </p>
        </div>

        {currentOrg?.role !== "viewer" && (
          <button
            onClick={() => setCreateOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-neutral-900 px-3.5 py-2 text-xs font-medium text-white shadow-sm hover:bg-neutral-800 transition"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Workspace</span>
          </button>
        )}
      </div>

      {/* Notifications */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-700">
          <AlertCircle className="h-4 w-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Create Modal / Form */}
      {createOpen && (
        <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-neutral-900">Create New Matter Workspace</h2>
            <button
              onClick={() => setCreateOpen(false)}
              className="text-xs text-neutral-400 hover:text-neutral-600"
            >
              Cancel
            </button>
          </div>
          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="block text-[11px] font-medium text-neutral-600 mb-1">
                Workspace Name
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Project Apollo M&A Acquisition, Vendor MSAs 2026..."
                className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-neutral-600 mb-1">
                Matter Scope / Description (Optional)
              </label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Briefly describe the legal engagement, counterparties, or review guidelines..."
                className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
              />
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setCreateOpen(false)}
                className="rounded-lg border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="rounded-lg bg-neutral-900 px-4 py-1.5 text-xs font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
              >
                {submitting ? "Creating…" : "Create Workspace"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Workspaces Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {workspaces.map((ws) => {
          const isActive = ws.id === currentWorkspace?.id;

          return (
            <div
              key={ws.id}
              className={`rounded-xl border p-5 transition flex flex-col justify-between ${
                isActive
                  ? "border-neutral-900 bg-white ring-1 ring-neutral-900 shadow-sm"
                  : "border-neutral-200/80 bg-white hover:border-neutral-300"
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <div
                      className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                        isActive ? "bg-neutral-900 text-white" : "bg-neutral-100 text-neutral-600"
                      }`}
                    >
                      <FolderKanban className="h-4 w-4" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-neutral-900">{ws.name}</h3>
                      <div className="text-[11px] text-neutral-400">
                        Created {new Date(ws.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  {isActive && (
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 text-[10px] font-medium text-emerald-700">
                      <Check className="h-3 w-3" />
                      Active
                    </span>
                  )}
                </div>

                <p className="mt-3 text-xs text-neutral-600 line-clamp-2">
                  {ws.description || "No specific matter description provided."}
                </p>
              </div>

              <div className="mt-5 pt-4 border-t border-neutral-100 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs text-neutral-500">
                  <FileText className="h-3.5 w-3.5" />
                  <span>{ws.document_count} contracts indexed</span>
                </div>

                <div className="flex items-center gap-2">
                  {!isActive && (
                    <button
                      onClick={() => selectWorkspace(ws.id)}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 hover:border-neutral-300 transition"
                    >
                      <FolderOpen className="h-3.5 w-3.5" />
                      <span>Switch</span>
                    </button>
                  )}

                  {isOwnerOrAdmin && workspaces.length > 1 && (
                    <button
                      onClick={() => handleDelete(ws.id, ws.name)}
                      className="rounded p-1 text-neutral-400 hover:text-rose-600 transition"
                      title="Delete Workspace"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
