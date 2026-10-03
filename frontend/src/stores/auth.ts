import { create } from "zustand";
import { request, setTokens, clearTokens, getAccessToken } from "../lib/api";
import type { User } from "../lib/types";

interface AuthState {
  user: User | null;
  initialized: boolean;
  init: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  initialized: false,

  init: async () => {
    window.addEventListener("lda:logout", () => set({ user: null }));
    if (!getAccessToken()) {
      set({ initialized: true });
      return;
    }
    try {
      const user = await request<User>("/auth/me");
      set({ user, initialized: true });
    } catch {
      set({ user: null, initialized: true });
    }
  },

  login: async (email, password) => {
    const tokens = await request<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setTokens(tokens.access_token, tokens.refresh_token);
    const user = await request<User>("/auth/me");
    set({ user });
  },

  register: async (email, password) => {
    const tokens = await request<{ access_token: string; refresh_token: string }>(
      "/auth/register",
      { method: "POST", body: JSON.stringify({ email, password }) },
    );
    setTokens(tokens.access_token, tokens.refresh_token);
    const user = await request<User>("/auth/me");
    set({ user });
  },

  logout: () => {
    clearTokens();
    set({ user: null });
  },
}));
