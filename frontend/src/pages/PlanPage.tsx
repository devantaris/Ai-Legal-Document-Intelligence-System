import { useEffect, useState } from "react";
import {
  Sparkles,
  Check,
  HardDrive,
  FileText,
  Users,
  Clock,
  Scale,
} from "lucide-react";
import { useTenant } from "../stores/tenant";

const TIERS = [
  {
    name: "Starter Counsel",
    price: "$99",
    cadence: "/ month",
    badge: "Coming Soon",
    desc: "For solo transactional attorneys and boutique practices requiring sovereign citation-backed analysis.",
    features: [
      "1 Active Attorney Seat",
      "Up to 50 contracts per month",
      "Standard 10-Clause Playbook Review",
      "Split-Screen Legal Reader Canvas",
      "Deterministic Citation Guard",
      "100% Local Sovereign Ollama Runner",
    ],
    highlighted: false,
  },
  {
    name: "Sovereign Enterprise Pro",
    price: "$299",
    cadence: "/ month",
    badge: "Current Active Tier",
    desc: "Engineered for corporate in-house legal departments and multi-attorney transactional teams.",
    features: [
      "5 Team Seats included",
      "Up to 300 contracts per month",
      "Multi-Workspace Matter Partitioning",
      "Cross-Repository Due Diligence Grid (CSV)",
      "Native Word (.docx) Redline Export with Track Changes",
      "Mathematical Sentence Entailment Auditing",
      "Role-Based Access Control (RBAC)",
      "Dedicated Private vLLM / Ollama Node",
    ],
    highlighted: true,
  },
  {
    name: "Institutional Sovereign",
    price: "Custom",
    cadence: "annual license",
    badge: "Coming Soon",
    desc: "Air-gapped on-premise infrastructure for investment banks, defense contractors, and AmLaw 100 firms.",
    features: [
      "Unlimited Attorney Seats",
      "Unlimited Contract Capacity",
      "Air-Gapped Sovereign Hardware Deployment",
      "SAML 2.0 / Okta Enterprise SSO",
      "Custom Institutional Playbook Creator",
      "Immutable Audit Log Export (SOC2 / ISO 27001)",
      "24/7 Dedicated Legal AI Solutions Engineer",
    ],
    highlighted: false,
  },
];

export function PlanPage() {
  const { currentOrg, usage, loadUsage } = useTenant();
  const [inquirySent, setInquirySent] = useState(false);

  useEffect(() => {
    void loadUsage();
  }, [currentOrg?.id]);

  const storageMb = usage ? (usage.storage_bytes / (1024 * 1024)).toFixed(1) : "0.0";

  return (
    <div className="mx-auto max-w-5xl px-8 py-8 space-y-8">
      {/* Header */}
      <div className="border-b border-neutral-200/80 pb-6">
        <div className="flex items-center gap-2 text-xs font-mono text-neutral-500 uppercase tracking-wider">
          <Scale className="h-3.5 w-3.5" />
          <span>{currentOrg?.name ?? "Organization"} Plan & Usage</span>
        </div>
        <h1 className="mt-1 text-2xl font-bold tracking-tight text-neutral-900">
          SaaS Tiers & Sovereign Resource Metering
        </h1>
        <p className="mt-1 text-xs text-neutral-500">
          Transparent compute and storage accounting with strict on-premise attorney-client privilege.
        </p>
      </div>

      {/* Sovereign Assurance Card */}
      <div className="rounded-xl border border-neutral-200 bg-neutral-900 text-white p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[11px] font-mono uppercase tracking-wider text-emerald-400">
              100% Sovereign Guarantee
            </span>
          </div>
          <h2 className="text-base font-semibold">Zero-Cloud Retention Privacy Architecture</h2>
          <p className="text-xs text-neutral-400 leading-relaxed">
            Your legal agreements, defined-term graphs, and redline drafts execute entirely inside your sovereign local boundary. No data is transmitted to public cloud LLMs or used to train third-party models.
          </p>
        </div>

        <div className="rounded-lg border border-neutral-700 bg-neutral-800/80 px-4 py-3 text-center shrink-0">
          <div className="text-[11px] text-neutral-400 uppercase tracking-wider font-mono">Status</div>
          <div className="text-sm font-semibold text-emerald-400 mt-0.5">Sovereign Pro Active</div>
          <div className="text-[10px] text-neutral-500 mt-0.5">Commercial Gateway: Coming Soon</div>
        </div>
      </div>

      {/* Usage Metrics Grid */}
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-500 mb-3">
          Current Organization Resource Utilization
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="rounded-xl border border-neutral-200/80 bg-white p-4">
            <div className="flex items-center gap-2 text-xs text-neutral-500 mb-1">
              <FileText className="h-3.5 w-3.5 text-neutral-400" />
              <span>Contracts Indexed</span>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {usage?.documents_count ?? 0}
            </div>
            <div className="text-[10px] text-neutral-400 mt-1">Across all matters</div>
          </div>

          <div className="rounded-xl border border-neutral-200/80 bg-white p-4">
            <div className="flex items-center gap-2 text-xs text-neutral-500 mb-1">
              <Sparkles className="h-3.5 w-3.5 text-neutral-400" />
              <span>Pages Processed</span>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {usage?.pages_processed ?? 0}
            </div>
            <div className="text-[10px] text-neutral-400 mt-1">OCR & hybrid chunking</div>
          </div>

          <div className="rounded-xl border border-neutral-200/80 bg-white p-4">
            <div className="flex items-center gap-2 text-xs text-neutral-500 mb-1">
              <Users className="h-3.5 w-3.5 text-neutral-400" />
              <span>Active Counsel Seats</span>
            </div>
            <div className="text-2xl font-bold text-neutral-900">
              {usage?.members_count ?? 1}
            </div>
            <div className="text-[10px] text-neutral-400 mt-1">Assigned RBAC members</div>
          </div>

          <div className="rounded-xl border border-neutral-200/80 bg-white p-4">
            <div className="flex items-center gap-2 text-xs text-neutral-500 mb-1">
              <HardDrive className="h-3.5 w-3.5 text-neutral-400" />
              <span>Storage Used</span>
            </div>
            <div className="text-2xl font-bold text-neutral-900">{storageMb} MB</div>
            <div className="text-[10px] text-neutral-400 mt-1">Encrypted disk storage</div>
          </div>
        </div>
      </div>

      {/* Pricing & Tier Matrix */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
            Subscription Tiers & Feature Matrix
          </h2>
          <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-[11px] font-medium text-amber-700">
            <Clock className="h-3 w-3" />
            Billing Integration Coming Soon
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {TIERS.map((tier) => (
            <div
              key={tier.name}
              className={`rounded-xl p-5 flex flex-col justify-between transition ${
                tier.highlighted
                  ? "border-2 border-neutral-900 bg-white shadow-md relative"
                  : "border border-neutral-200/80 bg-white"
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                      tier.highlighted
                        ? "bg-neutral-900 text-white border-neutral-900"
                        : "bg-neutral-100 text-neutral-600 border-neutral-200"
                    }`}
                  >
                    {tier.badge}
                  </span>
                </div>

                <h3 className="mt-3 text-base font-bold text-neutral-900">{tier.name}</h3>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-2xl font-black text-neutral-900">{tier.price}</span>
                  <span className="text-xs text-neutral-500">{tier.cadence}</span>
                </div>
                <p className="mt-2 text-xs text-neutral-600 leading-relaxed">{tier.desc}</p>

                <div className="mt-4 pt-4 border-t border-neutral-100 space-y-2">
                  {tier.features.map((feat) => (
                    <div key={feat} className="flex items-start gap-2 text-xs text-neutral-700">
                      <Check className="h-3.5 w-3.5 shrink-0 text-emerald-600 mt-0.5" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-neutral-100">
                {tier.highlighted ? (
                  <button
                    disabled
                    className="w-full rounded-lg bg-neutral-900 py-2 text-xs font-medium text-white opacity-90 cursor-default"
                  >
                    Current Plan (Active)
                  </button>
                ) : (
                  <button
                    onClick={() => setInquirySent(true)}
                    className="w-full rounded-lg border border-neutral-200 bg-white py-2 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
                  >
                    {inquirySent ? "Notified When Available ✓" : "Notify When Available"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
