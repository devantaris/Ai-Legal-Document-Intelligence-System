import { useEffect, useState } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  RefreshCw,
  Copy,
  Check,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { request } from "../lib/api";
import type { DocumentOut, PlaybookFinding, PlaybookReviewOut, RiskLevel } from "../lib/types";

interface Props {
  doc: DocumentOut;
  onSelectClause?: (finding: PlaybookFinding) => void;
}

export function PlaybookReviewPanel({ doc, onSelectClause }: Props) {
  const [review, setReview] = useState<PlaybookReviewOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"ALL" | RiskLevel>("ALL");
  const [activeFallbackTab, setActiveFallbackTab] = useState<
    Record<string, "conservative" | "compromise" | "aggressive">
  >({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [expandedDetails, setExpandedDetails] = useState<Record<string, boolean>>({});

  const loadReview = async (refresh = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = await request<PlaybookReviewOut>(
        `/documents/${doc.id}/playbook-review${refresh ? "?refresh=true" : ""}`
      );
      setReview(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load playbook audit");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadReview();
  }, [doc.id]);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const toggleExpand = (id: string) => {
    setExpandedDetails((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <RefreshCw className="h-5 w-5 animate-spin text-neutral-400" />
        <div className="mt-3 text-xs font-medium text-neutral-700">
          Auditing contract against Institutional Playbook…
        </div>
        <div className="mt-1 text-[11px] text-neutral-400">
          Evaluating liability caps, indemnification, termination, and governance rules
        </div>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="rounded-xl border border-rose-200 bg-rose-50/60 p-5 text-xs text-rose-800">
        <div className="font-semibold mb-1">Playbook Audit Failed</div>
        <div>{error ?? "Unable to analyze document"}</div>
        <button
          onClick={() => loadReview(true)}
          className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-rose-300 bg-white px-2.5 py-1 text-[11px] font-medium text-rose-800 hover:bg-rose-50"
        >
          <RefreshCw className="h-3 w-3" />
          <span>Retry Audit</span>
        </button>
      </div>
    );
  }

  const filteredFindings = review.findings.filter((f) => {
    if (filter === "ALL") return true;
    return f.risk_level === filter;
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-700";
    if (score >= 60) return "text-amber-700";
    return "text-rose-700";
  };

  const getRiskBadge = (level: RiskLevel) => {
    switch (level) {
      case "RED":
        return (
          <span className="inline-flex items-center gap-1 rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-800">
            <ShieldAlert className="h-3 w-3 text-rose-600" />
            <span>High Risk / Violation</span>
          </span>
        );
      case "AMBER":
        return (
          <span className="inline-flex items-center gap-1 rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
            <AlertTriangle className="h-3 w-3 text-amber-600" />
            <span>Moderate Deviation</span>
          </span>
        );
      case "GREEN":
        return (
          <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
            <ShieldCheck className="h-3 w-3 text-emerald-600" />
            <span>Market Compliant</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Executive Scorecard */}
      <div className="rounded-xl border border-neutral-200/90 bg-white p-5 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-neutral-100 pb-4">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 shrink-0 flex-col items-center justify-center rounded-xl border border-neutral-200 bg-neutral-50/80">
              <span className={`text-xl font-bold tracking-tight ${getScoreColor(review.compliance_score)}`}>
                {review.compliance_score}%
              </span>
              <span className="text-[9px] uppercase tracking-wider text-neutral-400 font-medium">Score</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-neutral-900">Institutional Playbook Audit</h3>
                <span className="rounded-md border border-neutral-200 bg-neutral-100 px-2 py-0.5 text-[10px] font-medium text-neutral-700">
                  {review.overall_risk}
                </span>
              </div>
              <p className="mt-1 text-xs text-neutral-600 max-w-2xl">{review.summary}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <button
              onClick={() => loadReview(true)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-neutral-200 bg-white px-3 py-1.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
              title="Re-run compliance evaluation"
            >
              <RefreshCw className="h-3.5 w-3.5 text-neutral-500" />
              <span>Re-evaluate</span>
            </button>
          </div>
        </div>

        {/* Counter Pills & Filters */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-neutral-400 text-[11px] font-medium mr-1 flex items-center gap-1">
              <SlidersHorizontal className="h-3 w-3" /> Filter:
            </span>
            <button
              onClick={() => setFilter("ALL")}
              className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                filter === "ALL"
                  ? "bg-neutral-900 text-white"
                  : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200/80"
              }`}
            >
              All ({review.total_evaluated})
            </button>
            <button
              onClick={() => setFilter("RED")}
              className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                filter === "RED"
                  ? "bg-rose-800 text-white"
                  : "bg-rose-50 text-rose-800 border border-rose-200/70 hover:bg-rose-100"
              }`}
            >
              Red Violations ({review.red_count})
            </button>
            <button
              onClick={() => setFilter("AMBER")}
              className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                filter === "AMBER"
                  ? "bg-amber-800 text-white"
                  : "bg-amber-50 text-amber-800 border border-amber-200/70 hover:bg-amber-100"
              }`}
            >
              Amber Deviations ({review.amber_count})
            </button>
            <button
              onClick={() => setFilter("GREEN")}
              className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                filter === "GREEN"
                  ? "bg-emerald-800 text-white"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200/70 hover:bg-emerald-100"
              }`}
            >
              Compliant ({review.green_count})
            </button>
          </div>

          <div className="text-[11px] text-neutral-400">
            Standard: Corporate Tech B2B Baseline (Delaware/NY Law, 12M Cap)
          </div>
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {filteredFindings.length === 0 ? (
          <div className="rounded-xl border border-neutral-200 bg-white p-8 text-center text-xs text-neutral-500">
            No provisions match the selected filter.
          </div>
        ) : (
          filteredFindings.map((finding, idx) => {
            const cardKey = finding.clause_id ?? `omitted-${idx}`;
            const activeTab = activeFallbackTab[cardKey] || "conservative";
            const isExpanded = expandedDetails[cardKey] ?? true;

            return (
              <div
                key={cardKey}
                className="overflow-hidden rounded-xl border border-neutral-200/90 bg-white shadow-sm transition hover:border-neutral-300"
              >
                {/* Finding Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 bg-neutral-50/70 px-5 py-3 border-b border-neutral-200/70">
                  <div className="flex items-center gap-2.5">
                    {getRiskBadge(finding.risk_level)}
                    <h4 className="text-xs font-semibold text-neutral-900">{finding.title}</h4>
                    {finding.page_start && (
                      <span className="text-[10px] text-neutral-400 font-mono">Page {finding.page_start}</span>
                    )}
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-medium text-neutral-500">
                      Score: <strong className={getScoreColor(finding.score)}>{finding.score}/100</strong>
                    </span>
                    {onSelectClause && (
                      <button
                        onClick={() => onSelectClause(finding)}
                        className="text-[11px] text-neutral-600 hover:text-neutral-900 underline font-medium"
                      >
                        Inspect in Canvas
                      </button>
                    )}
                    <button
                      onClick={() => toggleExpand(cardKey)}
                      className="text-neutral-400 hover:text-neutral-700"
                    >
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Finding Body */}
                {isExpanded && (
                  <div className="p-5 space-y-4">
                    {/* Contract Clause vs Playbook Rule Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      {/* Original Clause Text */}
                      <div className="rounded-lg border border-neutral-200 bg-neutral-50/40 p-3.5">
                        <div className="flex items-center justify-between text-[10px] font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                          <span>Contract Provision</span>
                          <span className="font-mono">{finding.section_path}</span>
                        </div>
                        <p className="font-serif text-neutral-800 leading-relaxed text-xs italic">
                          "{finding.clause_text}"
                        </p>
                      </div>

                      {/* Institutional Standard Rule & Deviation */}
                      <div className="rounded-lg border border-neutral-200 bg-white p-3.5 flex flex-col justify-between">
                        <div>
                          <div className="text-[10px] font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                            Playbook Standard & Deviation Analysis
                          </div>
                          <p className="text-neutral-700 font-medium mb-2">{finding.standard_rule}</p>
                          <div className="rounded border border-amber-200/60 bg-amber-50/40 p-2 text-[11px] text-amber-900">
                            <strong>Deviation:</strong> {finding.deviation_reason}
                          </div>
                        </div>

                        <div className="mt-3 pt-2 border-t border-neutral-100 text-[11px] text-neutral-600">
                          <strong>Recommended Action:</strong> {finding.action_required}
                        </div>
                      </div>
                    </div>

                    {/* Fallback Remediation Clauses */}
                    <div className="rounded-lg border border-neutral-200/90 bg-neutral-50/30 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-neutral-900">Remediation Fallback Drafts</span>
                          <span className="text-[10px] text-neutral-400">Pre-approved counter-proposals</span>
                        </div>

                        {/* Fallback Tabs */}
                        <div className="flex rounded-lg border border-neutral-200 bg-white p-0.5 text-[11px]">
                          <button
                            onClick={() =>
                              setActiveFallbackTab((prev) => ({ ...prev, [cardKey]: "conservative" }))
                            }
                            className={`rounded-md px-2.5 py-1 font-medium transition ${
                              activeTab === "conservative"
                                ? "bg-neutral-900 text-white"
                                : "text-neutral-600 hover:text-neutral-900"
                            }`}
                          >
                            🛡️ Conservative (Market Standard)
                          </button>
                          <button
                            onClick={() =>
                              setActiveFallbackTab((prev) => ({ ...prev, [cardKey]: "compromise" }))
                            }
                            className={`rounded-md px-2.5 py-1 font-medium transition ${
                              activeTab === "compromise"
                                ? "bg-neutral-900 text-white"
                                : "text-neutral-600 hover:text-neutral-900"
                            }`}
                          >
                            ⚖️ Balanced Compromise
                          </button>
                          <button
                            onClick={() =>
                              setActiveFallbackTab((prev) => ({ ...prev, [cardKey]: "aggressive" }))
                            }
                            className={`rounded-md px-2.5 py-1 font-medium transition ${
                              activeTab === "aggressive"
                                ? "bg-neutral-900 text-white"
                                : "text-neutral-600 hover:text-neutral-900"
                            }`}
                          >
                            ⚡ Aggressive Counter
                          </button>
                        </div>
                      </div>

                      {/* Active Fallback Text & Copy Action */}
                      <div className="relative rounded-lg border border-neutral-200 bg-white p-3.5">
                        <p className="font-mono text-xs text-neutral-800 leading-relaxed pr-16 select-all">
                          {finding.fallbacks[activeTab]}
                        </p>
                        <button
                          onClick={() =>
                            handleCopy(finding.fallbacks[activeTab], `${cardKey}-${activeTab}`)
                          }
                          className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-md border border-neutral-200 bg-neutral-50 px-2 py-1 text-[11px] font-medium text-neutral-700 hover:bg-neutral-100 transition"
                          title="Copy revision to clipboard"
                        >
                          {copiedKey === `${cardKey}-${activeTab}` ? (
                            <>
                              <Check className="h-3 w-3 text-emerald-600" />
                              <span className="text-emerald-700">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3 w-3 text-neutral-500" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
