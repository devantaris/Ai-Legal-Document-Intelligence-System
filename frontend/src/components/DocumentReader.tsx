import React, { useEffect, useRef, useState } from "react";
import { BookOpen, Search, Loader2, Sparkles } from "lucide-react";
import { request } from "../lib/api";
import type { ChunkLite, DefinedTermOut, DefinedTermsSummaryOut, DocumentContentOut, DocumentOut } from "../lib/types";

interface Props {
  doc: DocumentOut;
  highlight?: {
    chunk_id?: string;
    quote?: string;
    page?: number;
  } | null;
  onClearHighlight?: () => void;
}

export function DocumentReader({ doc, highlight, onClearHighlight }: Props) {
  const [content, setContent] = useState<DocumentContentOut | null>(null);
  const [terms, setTerms] = useState<DefinedTermOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTooltipTerm, setActiveTooltipTerm] = useState<{
    term: DefinedTermOut;
    x: number;
    y: number;
  } | null>(null);

  const chunkRefs = useRef<Record<string, HTMLDivElement | null>>({});

  useEffect(() => {
    let active = true;
    const fetchData = async () => {
      setLoading(true);
      try {
        const [contentData, termsData] = await Promise.all([
          request<DocumentContentOut>(`/documents/${doc.id}/content`),
          request<DefinedTermsSummaryOut>(`/documents/${doc.id}/defined-terms`).catch(() => null),
        ]);
        if (active) {
          setContent(contentData);
          if (termsData?.terms) setTerms(termsData.terms);
        }
      } catch (err) {
        console.error("Failed to fetch document content", err);
      } finally {
        if (active) setLoading(false);
      }
    };
    void fetchData();
    return () => {
      active = false;
    };
  }, [doc.id]);

  // Scroll to highlight when prop changes
  useEffect(() => {
    if (!highlight || !content) return;

    let targetEl: HTMLDivElement | null = null;
    if (highlight.chunk_id && chunkRefs.current[highlight.chunk_id]) {
      targetEl = chunkRefs.current[highlight.chunk_id];
    } else if (highlight.page) {
      // Find first chunk matching page
      const foundChunk = content.chunks.find((c) => c.page_start === highlight.page);
      if (foundChunk && chunkRefs.current[foundChunk.id]) {
        targetEl = chunkRefs.current[foundChunk.id];
      }
    }

    if (targetEl) {
      targetEl.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [highlight, content]);

  if (loading) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center text-xs text-neutral-500">
        <Loader2 className="h-5 w-5 animate-spin text-neutral-400 mb-2" />
        <span>Loading full contract text & definition index…</span>
      </div>
    );
  }

  if (!content || content.chunks.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center text-xs text-neutral-400">
        <span>No text content available for this document.</span>
      </div>
    );
  }

  // Group chunks by page_start
  const pagesMap = new Map<number, ChunkLite[]>();
  for (const chunk of content.chunks) {
    const pageNum = chunk.page_start ?? 1;
    if (!pagesMap.has(pageNum)) {
      pagesMap.set(pageNum, []);
    }
    pagesMap.get(pageNum)!.push(chunk);
  }
  const sortedPages = Array.from(pagesMap.entries()).sort(([a], [b]) => a - b);

  // Render text with defined terms highlighting and tooltips
  const renderTextWithDefinedTerms = (text: string) => {
    if (terms.length === 0) {
      return text;
    }

    // Sort terms by length descending to match longest terms first
    const sortedTerms = [...terms].sort((a, b) => b.term.length - a.term.length);
    const regexPattern = new RegExp(`\\b(${sortedTerms.map((t) => t.term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})\\b`, "g");

    const parts: (string | React.ReactNode)[] = [];
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regexPattern.exec(text)) !== null) {
      const matchStart = match.index;
      const matchEnd = regexPattern.lastIndex;
      const matchedTermStr = match[0];

      if (matchStart > lastIndex) {
        parts.push(text.slice(lastIndex, matchStart));
      }

      const termObj = terms.find((t) => t.term.toLowerCase() === matchedTermStr.toLowerCase());

      parts.push(
        <span
          key={`term-${matchStart}`}
          onMouseEnter={(e) => {
            if (termObj) {
              const rect = e.currentTarget.getBoundingClientRect();
              setActiveTooltipTerm({
                term: termObj,
                x: rect.left,
                y: rect.bottom + 6,
              });
            }
          }}
          onMouseLeave={() => setActiveTooltipTerm(null)}
          className="border-b border-dotted border-neutral-400 cursor-help hover:text-amber-900 hover:border-amber-700 font-medium transition"
        >
          {matchedTermStr}
        </span>
      );

      lastIndex = matchEnd;
    }

    if (lastIndex < text.length) {
      parts.push(text.slice(lastIndex));
    }

    return parts;
  };

  return (
    <div className="relative flex h-full flex-col bg-[#F8F9FA] border border-[#E2E8F0] rounded-2xl overflow-hidden shadow-2xs">
      {/* Document Reader Top Bar */}
      <div className="flex items-center justify-between border-b border-[#E2E8F0] bg-white px-4 py-2.5 text-xs shrink-0">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-amber-700" />
          <span className="font-bold text-[#0F172A] truncate max-w-[220px] font-serif-legal">
            {doc.filename}
          </span>
          <span className="rounded bg-[#F1F5F9] px-1.5 py-0.5 text-[10px] font-mono text-neutral-600">
            {doc.page_count ? `${doc.page_count} Pages` : `${content.chunks.length} Chunks`}
          </span>
          {terms.length > 0 && (
            <span className="rounded bg-amber-50 border border-amber-200/60 px-1.5 py-0.5 text-[10px] font-semibold text-amber-800">
              {terms.length} Definitions
            </span>
          )}
        </div>

        {/* In-doc Search */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1.5 h-3.5 w-3.5 text-neutral-400" />
            <input
              type="text"
              placeholder="Find in contract…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-7 w-36 sm:w-44 rounded-lg border border-[#E2E8F0] bg-[#F8F9FA] pl-7 pr-2 text-[11px] text-neutral-800 focus:bg-white focus:border-[#0F172A] focus:outline-none transition"
            />
          </div>

          {highlight && (
            <button
              onClick={onClearHighlight}
              className="rounded-lg bg-amber-100 border border-amber-300 px-2 py-1 text-[10px] font-semibold text-amber-900 hover:bg-amber-200 transition"
              title="Clear active citation focus"
            >
              Clear Focus
            </button>
          )}
        </div>
      </div>

      {/* Pages Canvas */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 select-text bg-[#F1F5F9]/50">
        {sortedPages.map(([pageNum, pageChunks]) => (
          <div
            key={`page-${pageNum}`}
            className="mx-auto max-w-2xl rounded-xl border border-[#E2E8F0] bg-white p-8 shadow-sm font-serif-legal text-neutral-900 text-xs leading-relaxed"
          >
            {/* Page Header Stamp */}
            <div className="mb-4 flex items-center justify-between border-b border-[#F1F5F9] pb-2 text-[10px] font-mono uppercase tracking-wider text-neutral-400 select-none">
              <span className="truncate max-w-sm">{doc.filename}</span>
              <span className="font-semibold text-neutral-500">Page {pageNum}</span>
            </div>

            {/* Chunks on this page */}
            <div className="space-y-4">
              {pageChunks.map((chunk) => {
                const isDirectlyHighlighted =
                  highlight?.chunk_id === chunk.id ||
                  (highlight?.quote && chunk.text.includes(highlight.quote.slice(0, 40)));

                const matchesQuery =
                  searchQuery.trim().length > 1 &&
                  chunk.text.toLowerCase().includes(searchQuery.toLowerCase());

                return (
                  <div
                    key={chunk.id}
                    ref={(el) => {
                      chunkRefs.current[chunk.id] = el;
                    }}
                    className={`rounded-lg p-2.5 transition-all duration-300 ${
                      isDirectlyHighlighted
                        ? "bg-amber-50 ring-2 ring-amber-400/90 shadow-sm"
                        : matchesQuery
                        ? "bg-yellow-50/80 ring-1 ring-yellow-300"
                        : "hover:bg-neutral-50/50"
                    }`}
                  >
                    {chunk.section_path && (
                      <div className="mb-1 font-sans-legal text-[11px] font-bold text-[#0F172A] tracking-tight">
                        {chunk.section_path}
                      </div>
                    )}
                    <p className="whitespace-pre-wrap leading-relaxed">
                      {renderTextWithDefinedTerms(chunk.text)}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Floating Definition Tooltip */}
      {activeTooltipTerm && (
        <div
          style={{
            position: "fixed",
            left: `${Math.min(window.innerWidth - 320, Math.max(16, activeTooltipTerm.x))}px`,
            top: `${Math.min(window.innerHeight - 200, activeTooltipTerm.y)}px`,
            zIndex: 9999,
          }}
          className="w-80 rounded-xl border border-[#CBD5E1] bg-white p-4 shadow-2xl text-xs font-sans-legal text-[#0F172A] pointer-events-none animate-in fade-in duration-150"
        >
          <div className="flex items-center justify-between border-b border-[#F1F5F9] pb-1.5 mb-1.5">
            <span className="font-bold text-[#0F172A] flex items-center gap-1.5 font-serif-legal">
              <Sparkles className="h-3.5 w-3.5 text-amber-600" />
              {activeTooltipTerm.term.term}
            </span>
            <span className="text-[10px] font-mono text-neutral-400 bg-neutral-100 px-1 rounded">
              Invoked {activeTooltipTerm.term.frequency}x
            </span>
          </div>
          <p className="font-serif-legal text-[11px] text-neutral-700 italic leading-relaxed line-clamp-4">
            "{activeTooltipTerm.term.definition}"
          </p>
          <div className="mt-2.5 pt-1.5 border-t border-[#F1F5F9] flex items-center justify-between text-[10px] font-mono text-neutral-400">
            <span>{activeTooltipTerm.term.section_defined || "Defined in body"}</span>
            {activeTooltipTerm.term.page_defined && <span>Page {activeTooltipTerm.term.page_defined}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
