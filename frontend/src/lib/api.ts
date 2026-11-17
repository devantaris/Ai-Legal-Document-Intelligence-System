const BASE = "/api";

const ACCESS_KEY = "lda_access_token";
const REFRESH_KEY = "lda_refresh_token";
const ORG_KEY = "lda_active_org_id";
const WORKSPACE_KEY = "lda_active_workspace_id";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function getActiveOrgId(): string | null {
  return localStorage.getItem(ORG_KEY);
}

export function setActiveOrgId(id: string | null): void {
  if (id) localStorage.setItem(ORG_KEY, id);
  else localStorage.removeItem(ORG_KEY);
}

export function getActiveWorkspaceId(): string | null {
  return localStorage.getItem(WORKSPACE_KEY);
}

export function setActiveWorkspaceId(id: string | null): void {
  if (id) localStorage.setItem(WORKSPACE_KEY, id);
  else localStorage.removeItem(WORKSPACE_KEY);
}

function detailOf(body: unknown, fallback: string): string {
  if (typeof body === "string") return body;
  if (body && typeof body === "object" && "detail" in body) {
    const d = (body as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d)) {
      return d
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : String(item),
        )
        .join("; ");
    }
    return JSON.stringify(d);
  }
  return fallback;
}

async function refreshAccessToken(): Promise<boolean> {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = (await res.json()) as { access_token: string; refresh_token: string };
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function request<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  
  const orgId = getActiveOrgId();
  if (orgId) headers["X-Organization-Id"] = orgId;
  const wsId = getActiveWorkspaceId();
  if (wsId) headers["X-Workspace-Id"] = wsId;

  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && retry && localStorage.getItem(REFRESH_KEY)) {
    if (await refreshAccessToken()) {
      return request<T>(path, options, false);
    }
    clearTokens();
    window.dispatchEvent(new Event("lda:logout"));
  }
  if (res.status === 204) return undefined as T;
  const body: unknown = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(detailOf(body, res.statusText), res.status);
  }
  return body as T;
}

export function uploadDocument(file: File, onProgress?: (pct: number) => void): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append("file", file);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${BASE}/documents`);
    const token = getAccessToken();
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    const orgId = getActiveOrgId();
    if (orgId) xhr.setRequestHeader("X-Organization-Id", orgId);
    const wsId = getActiveWorkspaceId();
    if (wsId) xhr.setRequestHeader("X-Workspace-Id", wsId);

    xhr.upload.addEventListener("progress", (e) => {
      if (e.lengthComputable && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
    });
    xhr.addEventListener("load", () => {
      if (xhr.status === 401) {
        void refreshAccessToken().then((ok) => (ok ? resolve(uploadDocument(file, onProgress)) : reject(new ApiError("Session expired", 401))));
        return;
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        let detail = xhr.statusText;
        try {
          detail = detailOf(JSON.parse(xhr.responseText), detail);
        } catch {
          /* keep statusText */
        }
        reject(new ApiError(detail, xhr.status));
      }
    });
    xhr.addEventListener("error", () => reject(new ApiError("Upload failed", 0)));
    xhr.send(form);
  });
}

/** POST an SSE endpoint and yield parsed `data:` payloads. */
export async function* streamSSE<T>(path: string, body: unknown): AsyncGenerator<T> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const orgId = getActiveOrgId();
  if (orgId) headers["X-Organization-Id"] = orgId;
  const wsId = getActiveWorkspaceId();
  if (wsId) headers["X-Workspace-Id"] = wsId;

  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errBody = await res.json().catch(() => ({}));
    throw new ApiError(detailOf(errBody, res.statusText), res.status);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new ApiError("No response body", 0);

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() ?? "";
    for (const chunk of lines) {
      const match = chunk.match(/^data:\s*(.*)$/m);
      if (match) {
        try {
          yield JSON.parse(match[1]) as T;
        } catch {
          /* skip malformed chunk */
        }
      }
    }
  }
}
