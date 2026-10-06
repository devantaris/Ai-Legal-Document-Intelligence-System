import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Scale,
  ShieldCheck,
  ChevronDown,
  ArrowRight,
  GitCompare,
  Layers,
  Database,
} from "lucide-react";
import { ThreeHeroScene } from "../components/ThreeHeroScene";

export function LandingPage() {
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const FAQS = [
    {
      q: "How is zero data egress guaranteed?",
      a: "LegalIQ runs the entire LLM and embedding pipeline locally on your machine via Ollama (Llama 3.2 3B and nomic-embed-text). Contracts and confidential terms never leave your hardware.",
    },
    {
      q: "Why hybrid retrieval (pgvector + BM25 FTS)?",
      a: "Legal agreements rely on exact clause numbers, parties, and specific words that vector search alone can overlook. Fusing vector similarity with BM25 full-text keyword search via Reciprocal Rank Fusion ensures verified citation grounding.",
    },
    {
      q: "Can it handle long-form 30+ page contracts?",
      a: "Yes. Long-form agreements are chunked by legal heading hierarchy and summarized via recursive map-reduce, preserving page coordinates for every claim.",
    },
    {
      q: "What file formats are supported?",
      a: "PDF, DOCX, TXT, and Markdown files are supported natively with page-level mapping.",
    },
  ];

  return (
    <div className="min-h-screen bg-[#f8f8f7] text-neutral-900 selection:bg-neutral-900 selection:text-white">
      {/* Clean Single-Line Header */}
      <header className="sticky top-0 z-40 border-b border-neutral-200/80 bg-[#f8f8f7]/90 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-neutral-900 text-white">
              <Scale className="h-4 w-4" />
            </div>
            <span className="font-semibold text-base tracking-tight text-neutral-900">
              LegalIQ
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-neutral-600">
            <a href="#capabilities" className="hover:text-neutral-900 transition">
              Capabilities
            </a>
            <a href="#pipeline" className="hover:text-neutral-900 transition">
              Pipeline
            </a>
            <a href="#faq" className="hover:text-neutral-900 transition">
              FAQ
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg px-3 py-1.5 text-xs font-medium text-neutral-600 hover:text-neutral-900 transition"
            >
              Sign in
            </Link>
            <Link
              to="/login"
              className="rounded-lg bg-neutral-900 px-3.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-neutral-800 transition active:scale-[0.98]"
            >
              Open Workspace
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section: Understated, Disciplined, Balanced */}
      <section className="mx-auto max-w-6xl px-6 pt-16 pb-20 md:pt-20 md:pb-24">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-6 space-y-5">
            <div className="inline-flex items-center gap-1.5 rounded-full border border-neutral-200 bg-white px-2.5 py-0.5 text-[11px] font-medium text-neutral-600 shadow-xs">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              <span>100% On-Premise · Air-Gapped Privacy</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-neutral-950 leading-[1.12]">
              Autonomous Legal Document Intelligence. Completely Local.
            </h1>

            <p className="text-sm sm:text-base text-neutral-600 leading-relaxed max-w-lg">
              Audit contracts, extract structured terms, compare versions, and query clauses with
              verifiable page-level citations on your private machine.
            </p>

            <div className="flex items-center gap-3 pt-2">
              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-lg bg-neutral-900 px-5 py-2.5 text-xs font-medium text-white shadow-sm hover:bg-neutral-800 transition"
              >
                <span>Launch Workspace</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
              <a
                href="#capabilities"
                className="rounded-lg border border-neutral-200 bg-white px-4 py-2.5 text-xs font-medium text-neutral-700 hover:bg-neutral-50 transition"
              >
                Learn more
              </a>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-6 border-t border-neutral-200/80 text-xs text-neutral-500">
              <div>
                <span className="font-semibold text-neutral-900 block font-mono text-sm">Zero</span>
                <span>Cloud Data Egress</span>
              </div>
              <div>
                <span className="font-semibold text-neutral-900 block font-mono text-sm">K=60</span>
                <span>Hybrid RRF Retrieval</span>
              </div>
              <div>
                <span className="font-semibold text-neutral-900 block font-mono text-sm">20+</span>
                <span>Clause Taxonomies</span>
              </div>
            </div>
          </div>

          {/* 3D Architectural Canvas */}
          <div className="lg:col-span-6 h-[380px] sm:h-[440px]">
            <ThreeHeroScene />
          </div>
        </div>
      </section>

      {/* Capabilities Section */}
      <section id="capabilities" className="border-t border-neutral-200/80 py-20 bg-white">
        <div className="mx-auto max-w-6xl px-6">
          <div className="max-w-xl mb-12">
            <h2 className="text-2xl font-semibold tracking-tight text-neutral-900">
              Contract Intelligence Without Cloud Compromise
            </h2>
            <p className="mt-2 text-xs sm:text-sm text-neutral-600">
              Engineered for legal operations, in-house counsel, and sensitive transaction diligence.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="rounded-xl border border-neutral-200/80 p-6 bg-[#f8f8f7]/50">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-100 text-neutral-800 border border-neutral-200">
                <Database className="h-4 w-4" />
              </div>
              <h3 className="mt-4 text-sm font-semibold text-neutral-900">Hybrid RRF Grounding</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-neutral-600">
                Fuses pgvector cosine similarity with Postgres BM25 full-text indexing via
                Reciprocal Rank Fusion. Every assertion cites physical page numbers.
              </p>
            </div>

            <div className="rounded-xl border border-neutral-200/80 p-6 bg-[#f8f8f7]/50">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-100 text-neutral-800 border border-neutral-200">
                <Layers className="h-4 w-4" />
              </div>
              <h3 className="mt-4 text-sm font-semibold text-neutral-900">Clause Taxonomy</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-neutral-600">
                Classifies contract text into 20 standard commercial legal types (indemnity,
                termination, governing law) with page-mapped references.
              </p>
            </div>

            <div className="rounded-xl border border-neutral-200/80 p-6 bg-[#f8f8f7]/50">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-100 text-neutral-800 border border-neutral-200">
                <GitCompare className="h-4 w-4" />
              </div>
              <h3 className="mt-4 text-sm font-semibold text-neutral-900">Semantic Redline Diff</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-neutral-600">
                Aligns clauses across two versions to pinpoint modified, added, and removed
                obligations categorized by impact severity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Technical Pipeline */}
      <section id="pipeline" className="border-t border-neutral-200/80 py-20 bg-[#f8f8f7]">
        <div className="mx-auto max-w-6xl px-6">
          <div className="max-w-xl mb-12">
            <h2 className="text-2xl font-semibold tracking-tight text-neutral-900">
              The Ingestion &amp; Retrieval Pipeline
            </h2>
            <p className="mt-2 text-xs sm:text-sm text-neutral-600">
              Deterministic, memory-safe, and verifiable at every step.
            </p>
          </div>

          <div className="rounded-xl border border-neutral-200/80 bg-white p-6 divide-y divide-neutral-100">
            <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <span className="font-mono text-neutral-500 w-12">01</span>
              <span className="font-semibold text-neutral-900 w-48">Page-Mapped Ingestion</span>
              <span className="text-neutral-600 flex-1">
                PyMuPDF &amp; python-docx extract raw text preserving exact 1-based page bounds.
              </span>
            </div>
            <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <span className="font-mono text-neutral-500 w-12">02</span>
              <span className="font-semibold text-neutral-900 w-48">Structure-Aware Chunking</span>
              <span className="text-neutral-600 flex-1">
                Preserves heading hierarchy (Article $\rightarrow$ Section) in ~700-token windows.
              </span>
            </div>
            <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <span className="font-mono text-neutral-500 w-12">03</span>
              <span className="font-semibold text-neutral-900 w-48">Hybrid Vector + FTS</span>
              <span className="text-neutral-600 flex-1">
                Dual storage in pgvector (cosine) and Postgres tsvector (BM25).
              </span>
            </div>
            <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <span className="font-mono text-neutral-500 w-12">04</span>
              <span className="font-semibold text-neutral-900 w-48">Reciprocal Rank Fusion</span>
              <span className="text-neutral-600 flex-1">
                Merges rankings via RRF (K=60) to eliminate legal hallucinations.
              </span>
            </div>
            <div className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
              <span className="font-mono text-neutral-500 w-12">05</span>
              <span className="font-semibold text-neutral-900 w-48">Grounded Local Streaming</span>
              <span className="text-neutral-600 flex-1">
                Ollama Llama 3.2 3B streams cited answers via SSE with verified brackets.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="border-t border-neutral-200/80 py-20 bg-white">
        <div className="mx-auto max-w-4xl px-6">
          <h2 className="text-2xl font-semibold tracking-tight text-neutral-900 text-center mb-10">
            Frequently Asked Questions
          </h2>

          <div className="space-y-3">
            {FAQS.map((faq, idx) => (
              <div
                key={idx}
                className="rounded-xl border border-neutral-200/80 bg-[#f8f8f7]/40 overflow-hidden"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                  className="flex w-full items-center justify-between p-4 text-left text-xs sm:text-sm font-medium text-neutral-900"
                >
                  <span>{faq.q}</span>
                  <ChevronDown
                    className={`h-4 w-4 text-neutral-400 transition-transform ${
                      openFaq === idx ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {openFaq === idx && (
                  <div className="px-4 pb-4 text-xs sm:text-sm text-neutral-600 leading-relaxed border-t border-neutral-100 pt-3">
                    {faq.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Minimal Footer */}
      <footer className="border-t border-neutral-200/80 bg-[#f8f8f7] py-10 text-xs text-neutral-500">
        <div className="mx-auto max-w-6xl px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Scale className="h-4 w-4 text-neutral-700" />
            <span>LegalIQ · Local Document Intelligence</span>
          </div>
          <div className="flex items-center gap-6">
            <Link to="/login" className="hover:text-neutral-900">
              Sign In
            </Link>
            <Link to="/" className="hover:text-neutral-900">
              Workspace
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
