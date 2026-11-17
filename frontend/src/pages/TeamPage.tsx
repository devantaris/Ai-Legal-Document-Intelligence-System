import { useEffect, useState } from "react";
import {
  Users,
  UserPlus,
  ShieldCheck,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Lock,
} from "lucide-react";
import { useTenant } from "../stores/tenant";
import { useAuth } from "../stores/auth";
import { request, ApiError } from "../lib/api";
import type { OrganizationMember, OrgRole } from "../lib/types";

const ROLE_DESCRIPTIONS: Record<OrgRole, { label: string; desc: string; badge: string }> = {
  owner: {
    label: "Owner",
    desc: "Full administrative ownership, billing, member invites, and workspace management.",
    badge: "bg-purple-50 text-purple-700 border-purple-200",
  },
  admin: {
    label: "Admin",
    desc: "Can manage team members, configure workspaces, and delete documents.",
    badge: "bg-blue-50 text-blue-700 border-blue-200",
  },
  counsel: {
    label: "Legal Counsel",
    desc: "Can upload contracts, run playbook risk scoring, chat, and export redlines.",
    badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  reviewer: {
    label: "Reviewer",
    desc: "Can review analysis findings and chat, but cannot delete documents.",
    badge: "bg-amber-50 text-amber-700 border-amber-200",
  },
  viewer: {
    label: "Viewer",
    desc: "Read-only access to contracts, summaries, and playbooks.",
    badge: "bg-neutral-100 text-neutral-600 border-neutral-200",
  },
};

export function TeamPage() {
  const { currentOrg } = useTenant();
  const { user } = useAuth();
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<OrgRole>("counsel");
  const [inviteSubmitting, setInviteSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const isOwnerOrAdmin = currentOrg?.role === "owner" || currentOrg?.role === "admin";

  const fetchMembers = async () => {
    if (!currentOrg) return;
    setLoading(true);
    setError(null);
    try {
      const data = await request<OrganizationMember[]>(`/organizations/${currentOrg.id}/members`);
      setMembers(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load team members");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchMembers();
  }, [currentOrg?.id]);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentOrg || !inviteEmail.trim()) return;

    setInviteSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      await request<OrganizationMember>(`/organizations/${currentOrg.id}/members`, {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail.trim(), role: inviteRole }),
      });
      setSuccess(`Invited ${inviteEmail} as ${ROLE_DESCRIPTIONS[inviteRole].label}`);
      setInviteEmail("");
      setInviteOpen(false);
      await fetchMembers();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to invite member");
    } finally {
      setInviteSubmitting(false);
    }
  };

  const handleRoleChange = async (targetUserId: string, newRole: OrgRole) => {
    if (!currentOrg) return;
    setError(null);
    try {
      await request<OrganizationMember>(
        `/organizations/${currentOrg.id}/members/${targetUserId}`,
        {
          method: "PATCH",
          body: JSON.stringify({ role: newRole }),
        }
      );
      setSuccess("Role updated successfully");
      await fetchMembers();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to update role");
    }
  };

  const handleRemoveMember = async (targetUserId: string, email: string) => {
    if (!currentOrg) return;
    if (!confirm(`Are you sure you want to remove ${email} from ${currentOrg.name}?`)) return;

    setError(null);
    try {
      await request(`/organizations/${currentOrg.id}/members/${targetUserId}`, {
        method: "DELETE",
      });
      setSuccess(`Removed ${email}`);
      await fetchMembers();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to remove member");
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#E2E8F0] pb-6">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono text-neutral-400 uppercase tracking-wider mb-1.5">
            <span className="font-semibold text-neutral-700">{currentOrg?.name ?? "Firm Organization"}</span>
            <span>•</span>
            <span className="text-amber-700 font-semibold font-mono">RBAC Security Boundary</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#0F172A] font-serif-legal">
            Practice Team & Role-Based Access Control
          </h1>
          <p className="mt-1 text-xs text-neutral-500 max-w-2xl leading-relaxed">
            Manage partners, senior counsel, junior reviewers, and external auditors with strictly partitioned tenant permissions.
          </p>
        </div>

        {isOwnerOrAdmin && (
          <button
            onClick={() => setInviteOpen(true)}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[#0F172A] px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-neutral-800 transition"
          >
            <UserPlus className="h-3.5 w-3.5 text-amber-400" />
            <span>Invite Colleague</span>
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
      {success && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-xs text-emerald-700">
          <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
          <span>{success}</span>
        </div>
      )}

      {/* Invite Modal / Box */}
      {inviteOpen && (
        <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-neutral-900">Invite New Team Member</h2>
            <button
              onClick={() => setInviteOpen(false)}
              className="text-xs text-neutral-400 hover:text-neutral-600"
            >
              Cancel
            </button>
          </div>
          <form onSubmit={handleInvite} className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="md:col-span-2">
              <label className="block text-[11px] font-medium text-neutral-600 mb-1">
                Corporate Email Address
              </label>
              <input
                type="email"
                required
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="colleague@firm.com"
                className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-neutral-600 mb-1">
                Assigned Role
              </label>
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as OrgRole)}
                className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
              >
                <option value="counsel">Legal Counsel</option>
                <option value="admin">Admin</option>
                <option value="reviewer">Reviewer</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <div className="md:col-span-3 flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setInviteOpen(false)}
                className="rounded-lg border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={inviteSubmitting}
                className="rounded-lg bg-neutral-900 px-4 py-1.5 text-xs font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
              >
                {inviteSubmitting ? "Inviting…" : "Send Access Invitation"}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Member Table */}
      <div className="rounded-xl border border-neutral-200/80 bg-white overflow-hidden shadow-sm">
        <div className="border-b border-neutral-100 bg-neutral-50/50 px-5 py-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-neutral-900">
            <Users className="h-4 w-4 text-neutral-500" />
            <span>Active Team Roster ({members.length})</span>
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-neutral-400">Loading team members…</div>
        ) : members.length === 0 ? (
          <div className="p-8 text-center text-xs text-neutral-500">No members found.</div>
        ) : (
          <div className="divide-y divide-neutral-100">
            {members.map((m) => {
              const roleMeta = ROLE_DESCRIPTIONS[m.role as OrgRole] || ROLE_DESCRIPTIONS.counsel;
              const isCurrentUser = m.user_id === user?.id;

              return (
                <div
                  key={m.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-3 hover:bg-neutral-50/50 transition"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-neutral-100 text-xs font-semibold text-neutral-700 uppercase">
                      {m.email.slice(0, 2)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-neutral-900">{m.email}</span>
                        {isCurrentUser && (
                          <span className="rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-mono text-neutral-500">
                            You
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-neutral-400">
                        Joined {new Date(m.joined_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center">
                    {isOwnerOrAdmin && !isCurrentUser && m.role !== "owner" ? (
                      <select
                        value={m.role}
                        onChange={(e) => handleRoleChange(m.user_id, e.target.value as OrgRole)}
                        className="rounded-lg border border-neutral-200 bg-white px-2.5 py-1 text-xs font-medium text-neutral-700 focus:border-neutral-900 focus:outline-none"
                      >
                        <option value="owner">Owner</option>
                        <option value="admin">Admin</option>
                        <option value="counsel">Legal Counsel</option>
                        <option value="reviewer">Reviewer</option>
                        <option value="viewer">Viewer</option>
                      </select>
                    ) : (
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${roleMeta.badge}`}
                      >
                        {roleMeta.label}
                      </span>
                    )}

                    {isOwnerOrAdmin && !isCurrentUser && m.role !== "owner" && (
                      <button
                        onClick={() => handleRemoveMember(m.user_id, m.email)}
                        className="rounded p-1 text-neutral-400 hover:text-rose-600 transition"
                        title="Remove Member"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Role Definitions Guide */}
      <div className="rounded-xl border border-neutral-200/80 bg-white p-5 space-y-3 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-semibold text-neutral-900">
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          <span>Role Permissions Architecture</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {(Object.keys(ROLE_DESCRIPTIONS) as OrgRole[]).map((r) => {
            const meta = ROLE_DESCRIPTIONS[r];
            return (
              <div key={r} className="rounded-lg border border-neutral-100 bg-neutral-50/50 p-3">
                <div className="font-semibold text-neutral-900 flex items-center justify-between">
                  <span>{meta.label}</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${meta.badge}`}>
                    {r}
                  </span>
                </div>
                <p className="mt-1 text-[11px] text-neutral-600">{meta.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Sovereign Privacy Banner */}
      <div className="rounded-xl border border-neutral-200 bg-neutral-900 text-white p-5 flex items-start gap-4">
        <div className="rounded-lg bg-neutral-800 p-2 text-emerald-400">
          <Lock className="h-5 w-5" />
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
            Sovereign Tenant Isolation
          </div>
          <div className="mt-0.5 text-sm font-medium">Zero Data Leakage Guarantee</div>
          <p className="mt-1 text-xs text-neutral-400 leading-relaxed">
            All team contract queries and citations execute through your organization's local Ollama/vLLM inference runner. Opposing counsel redlines and defined-term graphs are isolated per tenant database schema.
          </p>
        </div>
      </div>
    </div>
  );
}
