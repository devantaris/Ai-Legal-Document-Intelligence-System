import { useEffect, useState } from "react";
import { request } from "../lib/api";
import type { LlmInfo } from "../lib/types";

export function SettingsPage() {
  const [info, setInfo] = useState<LlmInfo | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setInfo(await request<LlmInfo>("/settings/llm"));
      } catch {
        setInfo(null);
      }
    })();
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-8 py-8">
      <h1 className="text-2xl font-bold tracking-tight text-slate-900">Settings</h1>
      <p className="mt-1 text-sm text-slate-500">
        The AI engine is configured in the backend <code>.env</code> file.
      </p>

      <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-900">AI provider</h2>
        {info ? (
          <>
            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
              <div className="text-slate-500">Provider</div>
              <div className="font-medium capitalize text-slate-800">{info.provider}</div>
              <div className="text-slate-500">Chat model</div>
              <div className="font-mono text-xs text-slate-800">{info.llm_model ?? "—"}</div>
              <div className="text-slate-500">Embedding model</div>
              <div className="font-mono text-xs text-slate-800">{info.embed_model ?? "—"}</div>
              <div className="text-slate-500">Embedding dimension</div>
              <div className="font-mono text-xs text-slate-800">{info.embedding_dim}</div>
            </div>
            {info.error && (
              <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">
                {info.error}
              </div>
            )}
          </>
        ) : (
          <div className="mt-3 text-sm text-slate-400">Could not load provider info.</div>
        )}
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        <h2 className="text-sm font-semibold text-slate-900">Switching providers</h2>
        <ul className="mt-3 list-disc space-y-1.5 pl-5">
          <li>
            <span className="font-medium">Z.ai GLM</span> — set <code>ZAI_API_KEY</code> and{" "}
            <code>LLM_PROVIDER=zai</code>.
          </li>
          <li>
            <span className="font-medium">Ollama (local)</span> — install Ollama, pull a model
            (e.g. <code>ollama pull llama3.1</code> and <code>ollama pull nomic-embed-text</code>),
            then set <code>LLM_PROVIDER=ollama</code> and <code>EMBEDDING_DIM=768</code>.
          </li>
          <li>
            Changing the embedding provider/dimension requires re-ingesting existing documents
            (delete and re-upload, or re-run ingestion).
          </li>
        </ul>
      </div>
    </div>
  );
}
