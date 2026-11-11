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
    <div className="relative flex h-full flex-col bg-[#fbfbfa] border border-neutral-200/80 rounded-xl overflow-hidden shadow-sm">
      {/* Document Reader Top Bar */}
      <div className="flex items-center justify-between border-b border-neutral-200/80 bg-white px-4 py-2.5 text-xs">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-neutral-500" />
          <span className="font-semibold text-neutral-900 truncate max-w-[220px]">
            {doc.filename}
          </span>
          <span className="rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-mono text-neutral-600">
            {doc.page_count ? `${doc.page_count} Pages` : `${content.chunks.length} Chunks`}
          </span>
          {terms.length > 0 && (
            <span className="rounded bg-amber-50 border border-amber-200/60 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">
              {terms.length} Defined Terms
            </span>
          )}
        </div>

        {/* In-doc Search */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2 top-1.5 h-3.5 w-3.5 text-neutral-400" />
            <input
              type="text"
              placeholder="Find in contract…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-7 w-36 sm:w-44 rounded-md border border-neutral-200 bg-neutral-50 pl-7 pr-2 text-[11px] text-neutral-800 focus:bg-white focus:border-neutral-400 focus:outline-none"
            />
          </div>

          {highlight && (
            <button
              onClick={onClearHighlight}
              className="rounded bg-amber-100 border border-amber-300 px-2 py-1 text-[10px] font-medium text-amber-900 hover:bg-amber-200 transition"
              title="Clear active citation focus"
            >
              Clear Focus
            </button>
          )}
        </div>
      </div>

      {/* Pages Canvas */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-8 select-text">
        {sortedPages.map(([pageNum, pageChunks]) => (
          <div
            key={`page-${pageNum}`}
            className="mx-auto max-w-2xl rounded-lg border border-neutral-200/90 bg-white p-7 shadow-xs font-serif text-neutral-800 text-xs leading-relaxed"
          >
            {/* Page Header Stamp */}
            <div className="mb-4 flex items-center justify-between border-b border-neutral-100 pb-2 text-[10px] font-mono uppercase tracking-wider text-neutral-400 select-none">
              <span>{doc.filename}</span>
              <span>Page {pageNum}</span>
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
                    className={`rounded p-2 transition-all duration-300 ${
                      isDirectlyHighlighted
                        ? "bg-amber-50 ring-2 ring-amber-400/80 shadow-xs"
                        : matchesQuery
                        ? "bg-yellow-50/80 ring-1 ring-yellow-300"
                        : ""
                    }`}
                  >
                    {chunk.section_path && (
                      <div className="mb-1 font-sans text-[11px] font-bold text-neutral-900 tracking-tight">
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
          className="w-72 rounded-lg border border-neutral-200 bg-white p-3.5 shadow-xl text-xs font-sans text-neutral-900 pointer-events-none animate-in fade-in duration-150"
        >
          <div className="flex items-center justify-between border-b border-neutral-100 pb-1.5 mb-1.5">
            <span className="font-semibold text-neutral-900 flex items-center gap-1">
              <Sparkles className="h-3 w-3 text-amber-600" />
              {activeTooltipTerm.term.term}
            </span>
            <span className="text-[10px] font-mono text-neutral-400">
              Used {activeTooltipTerm.term.frequency}x
            </span>
          </div>
          <p className="font-serif text-[11px] text-neutral-700 italic leading-snug line-clamp-4">
            "{activeTooltipTerm.term.definition}"
          </p>
          <div className="mt-2 pt-1 border-t border-neutral-100 flex items-center justify-between text-[10px] text-neutral-400">
            <span>{activeTooltipTerm.term.section_defined || "Defined in text"}</span>
            {activeTooltipTerm.term.page_defined && <span>Page {activeTooltipTerm.term.page_defined}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
