import { useEffect, useState } from "react";
import {
  BookOpen,
  Plus,
  Check,
  Star,
  Trash2,
  Edit3,
  X,
  RefreshCw,
  Search,
} from "lucide-react";
import { request } from "../lib/api";
import { useTenant } from "../stores/tenant";
import type { Playbook, PlaybookCreateIn, PlaybookRule, PlaybookUpdateIn } from "../lib/types";

const STANDARD_CLAUSE_TYPES = [
  { type: "limitation_of_liability", label: "Limitation of Liability" },
  { type: "indemnification", label: "Indemnification" },
  { type: "governing_law", label: "Governing Law & Jurisdiction" },
  { type: "termination", label: "Termination & Survival" },
  { type: "intellectual_property", label: "IP Ownership & Licensing" },
  { type: "confidentiality", label: "Confidentiality & Non-Disclosure" },
  { type: "non_solicitation", label: "Non-Solicitation & Restrictive Covenants" },
  { type: "payment_terms", label: "Payment Terms & Late Fees" },
  { type: "warranty", label: "Representations & Warranties" },
  { type: "data_privacy", label: "Data Privacy & Security Standard" },
];

export function PlaybooksPage() {
  const { currentOrg } = useTenant();
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPlaybook, setEditingPlaybook] = useState<Playbook | null>(null);
  const [formName, setFormName] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formIsDefault, setFormIsDefault] = useState(false);
  const [formRules, setFormRules] = useState<Record<string, PlaybookRule>>({});
  const [activeClauseType, setActiveClauseType] = useState<string>("limitation_of_liability");
  const [saving, setSaving] = useState(false);

  const loadPlaybooks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await request<Playbook[]>("/playbooks");
      setPlaybooks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load playbooks");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPlaybooks();
  }, [currentOrg?.id]);

  const handleOpenCreate = () => {
    setEditingPlaybook(null);
    setFormName("");
    setFormDesc("");
    setFormIsDefault(false);

    // Seed default baseline rules
    const defaultRules: Record<string, PlaybookRule> = {};
    for (const c of STANDARD_CLAUSE_TYPES) {
      defaultRules[c.type] = {
        clause_type: c.type,
        name: c.label,
        preferred_position: `Standard institutional standard for ${c.label}.`,
        unacceptable_triggers: ["unlimited liability", "sole discretion"],
        guidance: `Ensure balanced risk allocation adhering to Delaware/New York commercial law standards.`,
      };
    }
    setFormRules(defaultRules);
    setActiveClauseType("limitation_of_liability");
    setIsModalOpen(true);
  };

  const handleOpenEdit = (pb: Playbook) => {
    setEditingPlaybook(pb);
    setFormName(pb.name);
    setFormDesc(pb.description || "");
    setFormIsDefault(pb.is_default);

    const rulesCopy: Record<string, PlaybookRule> = {};
    for (const [k, v] of Object.entries(pb.rules || {})) {
      rulesCopy[k] = { ...v, unacceptable_triggers: [...(v.unacceptable_triggers || [])] };
    }
    setFormRules(rulesCopy);
    const firstKey = Object.keys(rulesCopy)[0] || "limitation_of_liability";
    setActiveClauseType(firstKey);
    setIsModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formName.trim()) return;

    setSaving(true);
    try {
      if (editingPlaybook) {
        const payload: PlaybookUpdateIn = {
          name: formName.trim(),
          description: formDesc.trim() || undefined,
          is_default: formIsDefault,
          rules: formRules,
        };
        await request<Playbook>(`/playbooks/${editingPlaybook.id}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        const payload: PlaybookCreateIn = {
          name: formName.trim(),
          description: formDesc.trim() || undefined,
          is_default: formIsDefault,
          rules: formRules,
        };
        await request<Playbook>("/playbooks", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      setIsModalOpen(false);
      await loadPlaybooks();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to save playbook");
    } finally {
      setSaving(false);
    }
  };

  const handleSetDefault = async (pb: Playbook) => {
    try {
      await request<Playbook>(`/playbooks/${pb.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_default: true }),
      });
      await loadPlaybooks();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to set default playbook");
    }
  };

  const handleDelete = async (pb: Playbook) => {
    if (!confirm(`Are you sure you want to delete playbook "${pb.name}"?`)) return;
    try {
      await request(`/playbooks/${pb.id}`, { method: "DELETE" });
      await loadPlaybooks();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete playbook");
    }
  };

  const filteredPlaybooks = playbooks.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-200/80 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-neutral-900">Contract Playbooks</h1>
            <span className="rounded-full bg-neutral-100 px-2.5 py-0.5 text-[11px] font-semibold text-neutral-600">
              Institutional Standards
            </span>
          </div>
          <p className="mt-1 text-xs text-neutral-500">
            Customize corporate legal positions, trigger phrases, and fallback drafts used for automated contract reviews.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={loadPlaybooks}
            className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={handleOpenCreate}
            className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-neutral-800 transition shadow-sm"
          >
            <Plus className="h-3.5 w-3.5" />
            <span>New Playbook</span>
          </button>
        </div>
      </div>

      {/* Filter / Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-neutral-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search playbooks by name or standard..."
            className="w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 py-1.5 text-xs text-neutral-900 placeholder-neutral-400 focus:border-neutral-900 focus:outline-none"
          />
        </div>
        <div className="text-xs text-neutral-400">
          Active Org: <strong className="text-neutral-700">{currentOrg?.name ?? "Default"}</strong>
        </div>
      </div>

      {/* Playbooks Grid */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
          <RefreshCw className="h-5 w-5 animate-spin mb-2" />
          <span className="text-xs">Loading institutional playbooks…</span>
        </div>
      ) : error ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
          {error}
        </div>
      ) : filteredPlaybooks.length === 0 ? (
        <div className="rounded-xl border border-neutral-200 bg-white p-12 text-center text-xs text-neutral-500">
          No playbooks found matching your search.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredPlaybooks.map((pb) => (
            <div
              key={pb.id}
              className={`flex flex-col justify-between rounded-xl border bg-white p-5 shadow-sm transition hover:shadow-md ${
                pb.is_default ? "border-emerald-300/80 ring-1 ring-emerald-500/20" : "border-neutral-200/90"
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-neutral-100 text-neutral-700">
                      <BookOpen className="h-4 w-4" />
                    </div>
                    <div>
                      <h3 className="text-xs font-semibold text-neutral-900">{pb.name}</h3>
                      <span className="text-[10px] text-neutral-400 font-mono">
                        {pb.rule_count} configured rules
                      </span>
                    </div>
                  </div>

                  {pb.is_default && (
                    <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
                      <Star className="h-3 w-3 fill-emerald-600 text-emerald-600" />
                      <span>Default</span>
                    </span>
                  )}
                </div>

                <p className="text-xs text-neutral-600 line-clamp-2 mb-4">
                  {pb.description || "Standard baseline corporate contract guidelines."}
                </p>

                {/* Sample rules badge tags */}
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {Object.keys(pb.rules || {})
                    .slice(0, 4)
                    .map((rk) => (
                      <span
                        key={rk}
                        className="rounded bg-neutral-100 px-2 py-0.5 text-[10px] font-medium text-neutral-600"
                      >
                        {rk.replace(/_/g, " ")}
                      </span>
                    ))}
                  {Object.keys(pb.rules || {}).length > 4 && (
                    <span className="rounded bg-neutral-50 border border-neutral-200 px-1.5 py-0.5 text-[10px] text-neutral-400">
                      +{Object.keys(pb.rules || {}).length - 4} more
                    </span>
                  )}
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="flex items-center justify-between border-t border-neutral-100 pt-3 text-xs">
                <div className="flex items-center gap-1">
                  {!pb.is_default && (
                    <button
                      onClick={() => handleSetDefault(pb)}
                      className="inline-flex items-center gap-1 rounded px-2 py-1 text-[11px] font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition"
                      title="Set as organization default standard"
                    >
                      <Check className="h-3 w-3" />
                      <span>Set Default</span>
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleOpenEdit(pb)}
                    className="inline-flex items-center gap-1 rounded px-2 py-1 text-[11px] font-medium text-neutral-700 hover:bg-neutral-100 transition"
                  >
                    <Edit3 className="h-3 w-3" />
                    <span>Edit Rules</span>
                  </button>
                  {!pb.is_default && (
                    <button
                      onClick={() => handleDelete(pb)}
                      className="inline-flex items-center rounded p-1 text-neutral-400 hover:text-rose-600 hover:bg-rose-50 transition"
                      title="Delete custom playbook"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Playbook Editor Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="relative flex flex-col w-full max-w-4xl max-h-[90vh] rounded-2xl bg-white shadow-2xl border border-neutral-200 overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-neutral-200 px-6 py-4 bg-neutral-50/80">
              <div>
                <h2 className="text-sm font-bold text-neutral-900">
                  {editingPlaybook ? `Edit Playbook: ${editingPlaybook.name}` : "Create Negotiation Playbook"}
                </h2>
                <p className="text-xs text-neutral-500">
                  Define acceptable liability limits, governing jurisdiction, and forbidden trigger words.
                </p>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="rounded-lg p-1 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Basic Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-neutral-800 mb-1">
                    Playbook Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={formName}
                    onChange={(e) => setFormName(e.target.value)}
                    placeholder="e.g. Aggressive Vendor Procurement Standard"
                    className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-neutral-800 mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    value={formDesc}
                    onChange={(e) => setFormDesc(e.target.value)}
                    placeholder="e.g. Applied to all supplier Master Services Agreements"
                    className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_default"
                  checked={formIsDefault}
                  onChange={(e) => setFormIsDefault(e.target.checked)}
                  className="rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900"
                />
                <label htmlFor="is_default" className="text-xs text-neutral-700 font-medium">
                  Set as active default standard for automated contract audits in this organization
                </label>
              </div>

              {/* Clause Rules Builder */}
              <div className="border-t border-neutral-200 pt-5">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-xs font-bold text-neutral-900">Clause Standards & Rules</h3>
                    <p className="text-[11px] text-neutral-500">
                      Configure evaluation criteria for each contractual provision.
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                  {/* Left Column: Clause Types Navigation */}
                  <div className="space-y-1 max-h-96 overflow-y-auto pr-1">
                    {STANDARD_CLAUSE_TYPES.map((c) => {
                      const isActive = activeClauseType === c.type;
                      const hasRule = Boolean(formRules[c.type]);
                      return (
                        <button
                          key={c.type}
                          type="button"
                          onClick={() => {
                            if (!formRules[c.type]) {
                              setFormRules((prev) => ({
                                ...prev,
                                [c.type]: {
                                  clause_type: c.type,
                                  name: c.label,
                                  preferred_position: "",
                                  unacceptable_triggers: [],
                                  guidance: "",
                                },
                              }));
                            }
                            setActiveClauseType(c.type);
                          }}
                          className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition text-left ${
                            isActive
                              ? "bg-neutral-900 text-white"
                              : "text-neutral-700 hover:bg-neutral-100"
                          }`}
                        >
                          <span>{c.label}</span>
                          {hasRule && (
                            <span
                              className={`h-1.5 w-1.5 rounded-full ${
                                isActive ? "bg-emerald-400" : "bg-emerald-600"
                              }`}
                            />
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Right Column: Active Rule Editor */}
                  <div className="md:col-span-2 rounded-xl border border-neutral-200 bg-neutral-50/50 p-4 space-y-4">
                    {activeClauseType && formRules[activeClauseType] ? (
                      <>
                        <div className="flex items-center justify-between border-b border-neutral-200 pb-2">
                          <span className="text-xs font-semibold text-neutral-900">
                            {formRules[activeClauseType].name}
                          </span>
                          <span className="font-mono text-[10px] text-neutral-400">
                            {activeClauseType}
                          </span>
                        </div>

                        <div>
                          <label className="block text-[11px] font-semibold text-neutral-700 mb-1">
                            Preferred Corporate Position
                          </label>
                          <textarea
                            rows={3}
                            value={formRules[activeClauseType].preferred_position}
                            onChange={(e) => {
                              const val = e.target.value;
                              setFormRules((prev) => ({
                                ...prev,
                                [activeClauseType]: {
                                  ...prev[activeClauseType],
                                  preferred_position: val,
                                },
                              }));
                            }}
                            placeholder="e.g. Liability capped at 12 months fees; mutual waiver of consequential damages."
                            className="w-full rounded-lg border border-neutral-200 bg-white p-2.5 text-xs focus:border-neutral-900 focus:outline-none"
                          />
                        </div>

                        <div>
                          <label className="block text-[11px] font-semibold text-neutral-700 mb-1">
                            Unacceptable Trigger Phrases (Comma-separated)
                          </label>
                          <input
                            type="text"
                            value={formRules[activeClauseType].unacceptable_triggers.join(", ")}
                            onChange={(e) => {
                              const arr = e.target.value
                                .split(",")
                                .map((s) => s.trim())
                                .filter(Boolean);
                              setFormRules((prev) => ({
                                ...prev,
                                [activeClauseType]: {
                                  ...prev[activeClauseType],
                                  unacceptable_triggers: arr,
                                },
                              }));
                            }}
                            placeholder="e.g. unlimited liability, uncapped, sole discretion"
                            className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
                          />
                          <p className="mt-1 text-[10px] text-neutral-400">
                            Any contract containing these trigger phrases will be flagged as RED violation.
                          </p>
                        </div>

                        <div>
                          <label className="block text-[11px] font-semibold text-neutral-700 mb-1">
                            Review Guidance & Strategic Rationale
                          </label>
                          <textarea
                            rows={2}
                            value={formRules[activeClauseType].guidance}
                            onChange={(e) => {
                              const val = e.target.value;
                              setFormRules((prev) => ({
                                ...prev,
                                [activeClauseType]: {
                                  ...prev[activeClauseType],
                                  guidance: val,
                                },
                              }));
                            }}
                            placeholder="Guidance for junior attorneys or AI automated evaluator on standard deviations."
                            className="w-full rounded-lg border border-neutral-200 bg-white p-2.5 text-xs focus:border-neutral-900 focus:outline-none"
                          />
                        </div>
                      </>
                    ) : (
                      <div className="py-12 text-center text-xs text-neutral-400">
                        Select a clause type to configure standards.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-end gap-2 border-t border-neutral-200 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="rounded-lg border border-neutral-200 px-4 py-2 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-neutral-900 px-4 py-2 text-xs font-medium text-white hover:bg-neutral-800 disabled:opacity-50 transition"
                >
                  {saving && <RefreshCw className="h-3.5 w-3.5 animate-spin" />}
                  <span>{editingPlaybook ? "Save Changes" : "Create Playbook"}</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
