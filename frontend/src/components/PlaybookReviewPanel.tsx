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
  BookOpen,
  CheckCircle2,
  Flag,
  XCircle,
  MessageSquare,
} from "lucide-react";
import { request } from "../lib/api";
import type {
  ClauseDecision,
  DocumentOut,
  Playbook,
  PlaybookFinding,
  PlaybookReviewOut,
  RiskLevel,
} from "../lib/types";

interface Props {
  doc: DocumentOut;
  onSelectClause?: (finding: PlaybookFinding) => void;
}

export function PlaybookReviewPanel({ doc, onSelectClause }: Props) {
  const [review, setReview] = useState<PlaybookReviewOut | null>(null);
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [selectedPlaybookId, setSelectedPlaybookId] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"ALL" | RiskLevel>("ALL");
  const [activeFallbackTab, setActiveFallbackTab] = useState<
    Record<string, "conservative" | "compromise" | "aggressive">
  >({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [expandedDetails, setExpandedDetails] = useState<Record<string, boolean>>({});
  const [decisionNotes, setDecisionNotes] = useState<Record<string, string>>({});
  const [savingDecision, setSavingDecision] = useState<Record<string, boolean>>({});

  useEffect(() => {
    void (async () => {
      try {
        const pbList = await request<Playbook[]>("/playbooks");
        setPlaybooks(pbList);
      } catch {
        /* fallback to default */
      }
    })();
  }, []);

  const loadReview = async (refresh = false, pbId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const activePb = pbId !== undefined ? pbId : selectedPlaybookId;
      const queryParts: string[] = [];
      if (refresh) queryParts.push("refresh=true");
      if (activePb) queryParts.push(`playbook_id=${activePb}`);
      const qs = queryParts.length ? `?${queryParts.join("&")}` : "";

      const data = await request<PlaybookReviewOut>(
        `/documents/${doc.id}/playbook-review${qs}`
      );
      setReview(data);

      const notesMap: Record<string, string> = {};
      for (const f of data.findings) {
        if (f.decision_notes) {
          notesMap[f.clause_type] = f.decision_notes;
        }
      }
      setDecisionNotes((prev) => ({ ...notesMap, ...prev }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load playbook audit");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadReview();
  }, [doc.id]);

  const handlePlaybookChange = (pbId: string) => {
    setSelectedPlaybookId(pbId);
    void loadReview(false, pbId);
  };

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const toggleExpand = (id: string) => {
    setExpandedDetails((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleRecordDecision = async (
    clauseType: string,
    decision: "accepted" | "flagged" | "rejected" | "pending"
  ) => {
    setSavingDecision((prev) => ({ ...prev, [clauseType]: true }));
    try {
      const notes = decisionNotes[clauseType] || "";
      await request<ClauseDecision>(`/playbooks/documents/${doc.id}/decisions`, {
        method: "POST",
        body: JSON.stringify({
          clause_type: clauseType,
          decision,
          notes: notes.trim() || undefined,
        }),
      });

      setReview((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          findings: prev.findings.map((f) =>
            f.clause_type === clauseType
              ? { ...f, decision, decision_notes: notes.trim() || null }
              : f
          ),
        };
      });
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to record decision");
    } finally {
      setSavingDecision((prev) => ({ ...prev, [clauseType]: false }));
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <RefreshCw className="h-6 w-6 animate-spin text-amber-600 mb-3" />
        <div className="text-xs font-bold text-[#0F172A] font-serif-legal">
          Auditing Contract Against Institutional Playbook…
        </div>
        <p className="mt-1 text-[11px] text-neutral-400 font-mono">
          Evaluating liability caps, indemnification, termination, IP, and governing law
        </p>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50/60 p-6 text-xs text-rose-800">
        <div className="font-bold text-sm mb-1 font-serif-legal">Playbook Evaluation Failed</div>
        <div>{error ?? "Unable to analyze document"}</div>
        <button
          onClick={() => loadReview(true)}
          className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-rose-300 bg-white px-3 py-1.5 text-xs font-semibold text-rose-800 hover:bg-rose-50 transition"
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
          <span className="inline-flex items-center gap-1 rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-800">
            <ShieldAlert className="h-3 w-3 text-rose-600" />
            <span>High Risk / Violation</span>
          </span>
        );
      case "AMBER":
        return (
          <span className="inline-flex items-center gap-1 rounded-md border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
            <AlertTriangle className="h-3 w-3 text-amber-600" />
            <span>Moderate Deviation</span>
          </span>
        );
      case "GREEN":
        return (
          <span className="inline-flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
            <ShieldCheck className="h-3 w-3 text-emerald-600" />
            <span>Market Compliant</span>
          </span>
        );
    }
  };

  const getDecisionBadge = (decision?: string) => {
    switch (decision) {
      case "accepted":
        return (
          <span className="inline-flex items-center gap-1 rounded-md border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-800">
            <CheckCircle2 className="h-3 w-3 text-emerald-600" />
            <span>Risk Accepted</span>
          </span>
        );
      case "flagged":
        return (
          <span className="inline-flex items-center gap-1 rounded-md border border-amber-200 bg-amber-50 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
            <Flag className="h-3 w-3 text-amber-600" />
            <span>Escalated to Partner</span>
          </span>
        );
      case "rejected":
        return (
          <span className="inline-flex items-center gap-1 rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-[10px] font-semibold text-rose-800">
            <XCircle className="h-3 w-3 text-rose-600" />
            <span>Remediation Required</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center rounded-md border border-neutral-200 bg-neutral-100 px-2 py-0.5 text-[10px] font-medium text-neutral-600">
            Decision Pending
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Executive Scorecard */}
      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-2xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#F1F5F9] pb-5">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 shrink-0 flex-col items-center justify-center rounded-2xl border border-[#E2E8F0] bg-[#F8F9FA] shadow-2xs">
              <span className={`text-2xl font-bold tracking-tight font-serif-legal ${getScoreColor(review.compliance_score)}`}>
                {review.compliance_score}%
              </span>
              <span className="text-[9px] uppercase tracking-wider text-neutral-400 font-mono font-bold">Score</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-[#0F172A] font-serif-legal">
                  {review.playbook_name || "Institutional Commercial Standard"}
                </h3>
                <span className="rounded-md border border-[#E2E8F0] bg-[#F8F9FA] px-2 py-0.5 text-[10px] font-semibold text-neutral-700">
                  {review.overall_risk}
                </span>
              </div>
              <p className="mt-1 text-xs text-neutral-600 max-w-2xl leading-relaxed">{review.summary}</p>
            </div>
          </div>

          {/* Standard Selector & Re-evaluate */}
          <div className="flex items-center gap-2.5 self-start md:self-auto">
            {playbooks.length > 0 && (
              <div className="flex items-center gap-1.5">
                <BookOpen className="h-3.5 w-3.5 text-neutral-400" />
                <select
                  value={selectedPlaybookId}
                  onChange={(e) => handlePlaybookChange(e.target.value)}
                  className="rounded-lg border border-[#E2E8F0] bg-white px-2.5 py-1.5 text-xs text-[#0F172A] font-medium focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
                >
                  <option value="">Default Institutional Standard</option>
                  {playbooks.map((pb) => (
                    <option key={pb.id} value={pb.id}>
                      {pb.name} {pb.is_default ? "(Default)" : ""}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <button
              onClick={() => loadReview(true)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-1.5 text-xs font-semibold text-neutral-700 hover:bg-[#F8F9FA] transition shadow-2xs"
              title="Re-run compliance evaluation"
            >
              <RefreshCw className="h-3.5 w-3.5 text-neutral-500" />
              <span>Re-evaluate</span>
            </button>
          </div>
        </div>

        {/* Counter Pills & Risk Filters */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-neutral-400 text-[11px] font-mono mr-1 flex items-center gap-1">
              <SlidersHorizontal className="h-3 w-3" /> Filter:
            </span>
            <button
              onClick={() => setFilter("ALL")}
              className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                filter === "ALL"
                  ? "bg-[#0F172A] text-white"
                  : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
              }`}
            >
              All Provisions ({review.total_evaluated})
            </button>
            <button
              onClick={() => setFilter("RED")}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
                filter === "RED"
                  ? "bg-rose-800 text-white"
                  : "bg-rose-50 text-rose-800 border border-rose-200 hover:bg-rose-100"
              }`}
            >
              Red Violations ({review.red_count})
            </button>
            <button
              onClick={() => setFilter("AMBER")}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
                filter === "AMBER"
                  ? "bg-amber-800 text-white"
                  : "bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100"
              }`}
            >
              Amber Deviations ({review.amber_count})
            </button>
            <button
              onClick={() => setFilter("GREEN")}
              className={`rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
                filter === "GREEN"
                  ? "bg-emerald-800 text-white"
                  : "bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100"
              }`}
            >
              Compliant ({review.green_count})
            </button>
          </div>

          <div className="text-[11px] text-neutral-400 font-mono">
            Standard: {review.playbook_name || "Institutional Commercial Standard"}
          </div>
        </div>
      </div>

      {/* Findings Inventory */}
      <div className="space-y-4">
        {filteredFindings.length === 0 ? (
          <div className="rounded-2xl border border-[#E2E8F0] bg-white p-12 text-center text-xs text-neutral-500 font-serif-legal">
            No contract provisions match the selected risk filter.
          </div>
        ) : (
          filteredFindings.map((finding, idx) => {
            const cardKey = finding.clause_id ?? `omitted-${idx}`;
            const activeTab = activeFallbackTab[cardKey] || "conservative";
            const isExpanded = expandedDetails[cardKey] ?? true;
            const currentDecision = finding.decision || "pending";
            const isSaving = savingDecision[finding.clause_type];

            return (
              <div
                key={cardKey}
                className="overflow-hidden rounded-2xl border border-[#E2E8F0] bg-white shadow-2xs transition hover:border-[#CBD5E1]"
              >
                {/* Finding Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 bg-[#F8F9FA] px-5 py-3.5 border-b border-[#E2E8F0]">
                  <div className="flex items-center gap-2.5">
                    {getRiskBadge(finding.risk_level)}
                    <h4 className="text-xs font-bold text-[#0F172A] font-serif-legal">{finding.title}</h4>
                    {finding.page_start && (
                      <span className="text-[10px] text-neutral-400 font-mono">Page {finding.page_start}</span>
                    )}
                    {getDecisionBadge(finding.decision)}
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-mono text-neutral-500">
                      Score: <strong className={getScoreColor(finding.score)}>{finding.score}/100</strong>
                    </span>
                    {onSelectClause && (
                      <button
                        onClick={() => onSelectClause(finding)}
                        className="text-[11px] text-neutral-700 hover:text-[#0F172A] underline font-semibold transition"
                      >
                        Inspect in Canvas
                      </button>
                    )}
                    <button
                      onClick={() => toggleExpand(cardKey)}
                      className="text-neutral-400 hover:text-neutral-700 p-0.5 rounded"
                    >
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Finding Body */}
                {isExpanded && (
                  <div className="p-5 space-y-4">
                    {/* Contract Clause vs Playbook Standard */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                      {/* Original Clause Text */}
                      <div className="rounded-xl border border-[#E2E8F0] bg-[#FAF9F6] p-4">
                        <div className="flex items-center justify-between text-[10px] font-mono font-semibold uppercase tracking-wider text-neutral-400 mb-2">
                          <span>Contract Provision</span>
                          <span>{finding.section_path}</span>
                        </div>
                        <p className="font-serif-legal text-neutral-900 leading-relaxed text-xs italic">
                          "{finding.clause_text}"
                        </p>
                      </div>

                      {/* Institutional Standard & Deviation */}
                      <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 flex flex-col justify-between">
                        <div>
                          <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-neutral-400 mb-2">
                            Playbook Standard & Deviation Analysis
                          </div>
                          <p className="text-[#0F172A] font-medium mb-2 leading-relaxed">{finding.standard_rule}</p>
                          <div className="rounded-lg border border-amber-200/70 bg-amber-50/50 p-2.5 text-[11px] text-amber-900">
                            <strong>Deviation:</strong> {finding.deviation_reason}
                          </div>
                        </div>

                        <div className="mt-3 pt-2.5 border-t border-[#F1F5F9] text-[11px] text-neutral-600">
                          <strong className="text-neutral-900">Recommended Action:</strong> {finding.action_required}
                        </div>
                      </div>
                    </div>

                    {/* Fallback Remediation Clauses */}
                    <div className="rounded-xl border border-[#E2E8F0] bg-[#F8F9FA] p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-[#0F172A] font-serif-legal">
                            Remediation Fallback Counter-Proposals
                          </span>
                          <span className="text-[10px] text-neutral-400 font-mono">Pre-approved counsel drafts</span>
                        </div>

                        {/* Fallback Tabs */}
                        <div className="flex rounded-lg border border-[#E2E8F0] bg-white p-0.5 text-[11px]">
                          <button
                            onClick={() =>
                              setActiveFallbackTab((prev) => ({ ...prev, [cardKey]: "conservative" }))
                            }
                            className={`rounded-md px-2.5 py-1 font-medium transition ${
                              activeTab === "conservative"
                                ? "bg-[#0F172A] text-white shadow-2xs font-semibold"
                                : "text-neutral-600 hover:text-[#0F172A]"
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
                                ? "bg-[#0F172A] text-white shadow-2xs font-semibold"
                                : "text-neutral-600 hover:text-[#0F172A]"
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
                                ? "bg-[#0F172A] text-white shadow-2xs font-semibold"
                                : "text-neutral-600 hover:text-[#0F172A]"
                            }`}
                          >
                            ⚡ Aggressive Counter
                          </button>
                        </div>
                      </div>

                      {/* Active Fallback Text & Copy Action */}
                      <div className="relative rounded-xl border border-[#E2E8F0] bg-white p-4">
                        <p className="font-mono-legal text-xs text-neutral-900 leading-relaxed pr-16 select-all">
                          {finding.fallbacks[activeTab]}
                        </p>
                        <button
                          onClick={() =>
                            handleCopy(finding.fallbacks[activeTab], `${cardKey}-${activeTab}`)
                          }
                          className="absolute right-3.5 top-3.5 inline-flex items-center gap-1 rounded-lg border border-[#E2E8F0] bg-[#F8F9FA] px-2.5 py-1 text-[11px] font-semibold text-neutral-700 hover:bg-[#F1F5F9] transition shadow-2xs"
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

                    {/* Attorney Review Decision Bar */}
                    <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-[#0F172A] font-serif-legal">
                            Attorney Negotiation Decision
                          </span>
                          <span className="text-[10px] text-neutral-400 font-mono">
                            Record risk acceptance or remediation posture
                          </span>
                        </div>

                        {/* Decision Buttons */}
                        <div className="flex items-center gap-1.5">
                          <button
                            type="button"
                            disabled={isSaving}
                            onClick={() => handleRecordDecision(finding.clause_type, "accepted")}
                            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                              currentDecision === "accepted"
                                ? "bg-emerald-700 text-white shadow-sm"
                                : "border border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
                            }`}
                          >
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            <span>Accept Risk</span>
                          </button>

                          <button
                            type="button"
                            disabled={isSaving}
                            onClick={() => handleRecordDecision(finding.clause_type, "flagged")}
                            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                              currentDecision === "flagged"
                                ? "bg-amber-700 text-white shadow-sm"
                                : "border border-amber-200 bg-amber-50 text-amber-800 hover:bg-amber-100"
                            }`}
                          >
                            <Flag className="h-3.5 w-3.5" />
                            <span>Flag for Partner</span>
                          </button>

                          <button
                            type="button"
                            disabled={isSaving}
                            onClick={() => handleRecordDecision(finding.clause_type, "rejected")}
                            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                              currentDecision === "rejected"
                                ? "bg-rose-700 text-white shadow-sm"
                                : "border border-rose-200 bg-rose-50 text-rose-800 hover:bg-rose-100"
                            }`}
                          >
                            <XCircle className="h-3.5 w-3.5" />
                            <span>Reject & Apply Fallback</span>
                          </button>
                        </div>
                      </div>

                      {/* Rationale / Notes input */}
                      <div className="flex items-center gap-2.5">
                        <MessageSquare className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                        <input
                          type="text"
                          value={decisionNotes[finding.clause_type] ?? ""}
                          onChange={(e) => {
                            const val = e.target.value;
                            setDecisionNotes((prev) => ({ ...prev, [finding.clause_type]: val }));
                          }}
                          onBlur={() => {
                            if (currentDecision !== "pending") {
                              void handleRecordDecision(
                                finding.clause_type,
                                currentDecision as "accepted" | "flagged" | "rejected"
                              );
                            }
                          }}
                          placeholder="Attorney rationale (e.g. Approved by CFO due to critical enterprise deployment timeline)..."
                          className="flex-1 rounded-lg border border-[#E2E8F0] bg-[#F8F9FA] px-3 py-1.5 text-xs text-[#0F172A] placeholder-neutral-400 focus:bg-white focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
                        />
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
