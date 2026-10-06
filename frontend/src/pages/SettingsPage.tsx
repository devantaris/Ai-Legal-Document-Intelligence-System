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
      <div className="mb-6">
        <h1 className="text-xl font-semibold tracking-tight text-neutral-900">Settings</h1>
        <p className="mt-0.5 text-xs text-neutral-500">
          AI engine configuration managed via backend <code>.env</code> file.
        </p>
      </div>

      <div className="rounded-xl border border-neutral-200 bg-white p-5 space-y-4">
        <div className="text-xs font-semibold text-neutral-900">Active AI Configuration</div>

        {info ? (
          <div className="grid grid-cols-2 gap-x-4 gap-y-3 text-xs">
            <div className="text-neutral-500">Provider</div>
            <div className="font-medium text-neutral-900 capitalize">{info.provider}</div>

            <div className="text-neutral-500">Chat model</div>
            <div className="font-mono text-neutral-800">{info.llm_model ?? "—"}</div>

            <div className="text-neutral-500">Embedding model</div>
            <div className="font-mono text-neutral-800">{info.embed_model ?? "—"}</div>

            <div className="text-neutral-500">Embedding dimension</div>
            <div className="font-mono text-neutral-800">{info.embedding_dim}</div>
          </div>
        ) : (
          <div className="text-xs text-neutral-400">Loading provider configuration…</div>
        )}
      </div>

      <div className="mt-4 rounded-xl border border-neutral-200 bg-white p-5 text-xs text-neutral-600 space-y-2">
        <div className="font-semibold text-neutral-900">Provider Setup</div>
        <ul className="list-disc pl-4 space-y-1 text-neutral-600">
          <li>
            <strong>Ollama (Local default):</strong> Set <code>LLM_PROVIDER=ollama</code> and{" "}
            <code>EMBEDDING_DIM=768</code> in <code>.env</code>.
          </li>
          <li>
            <strong>Z.ai GLM (Cloud):</strong> Set <code>LLM_PROVIDER=zai</code>,{" "}
            <code>ZAI_API_KEY=...</code>, and <code>EMBEDDING_DIM=1024</code>.
          </li>
        </ul>
      </div>
    </div>
  );
}
