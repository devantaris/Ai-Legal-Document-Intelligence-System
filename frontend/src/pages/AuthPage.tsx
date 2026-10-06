import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Scale } from "lucide-react";
import { useAuth } from "../stores/auth";

export function AuthPage({ mode }: { mode: "login" | "register" }) {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setBusy(false);
    }
  };

  const handleDemoFill = () => {
    setEmail("demo@legaliq.dev");
    setPassword("demo12345");
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#f8f8f7] px-4 py-12">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="text-center mb-6">
          <div className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-neutral-900 text-white mb-2.5">
            <Scale className="h-4 w-4" />
          </div>
          <h1 className="text-lg font-semibold tracking-tight text-neutral-900">LegalIQ</h1>
          <p className="mt-0.5 text-xs text-neutral-500">
            {mode === "login" ? "Sign in to your workspace" : "Create a new local account"}
          </p>
        </div>

        {/* Card */}
        <div className="rounded-xl border border-neutral-200 bg-white p-6 shadow-xs">
          {error && (
            <div className="mb-4 rounded-lg bg-rose-50 border border-rose-200 p-2.5 text-xs text-rose-700">
              {error}
            </div>
          )}

          <form onSubmit={submit} className="space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-neutral-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="counsel@firm.com"
                className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs text-neutral-900 outline-none focus:border-neutral-400"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-neutral-700 mb-1">Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs text-neutral-900 outline-none focus:border-neutral-400"
              />
            </div>

            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-lg bg-neutral-900 py-2.5 text-xs font-medium text-white hover:bg-neutral-800 transition active:scale-[0.98] disabled:opacity-50"
            >
              {busy ? "Authenticating…" : mode === "login" ? "Sign In" : "Register"}
            </button>
          </form>

          {/* Quick Demo */}
          <div className="mt-4 pt-3.5 border-t border-neutral-100">
            <button
              type="button"
              onClick={handleDemoFill}
              className="w-full rounded-lg border border-neutral-200 bg-neutral-50 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-100 transition"
            >
              Fill Demo Credentials
            </button>
          </div>

          <div className="mt-4 text-center text-xs text-neutral-500">
            {mode === "login" ? (
              <span>
                Need an account?{" "}
                <Link to="/register" className="font-medium text-neutral-900 hover:underline">
                  Register
                </Link>
              </span>
            ) : (
              <span>
                Already have an account?{" "}
                <Link to="/login" className="font-medium text-neutral-900 hover:underline">
                  Sign in
                </Link>
              </span>
            )}
          </div>
        </div>

        <div className="mt-4 text-center">
          <Link to="/landing" className="text-xs text-neutral-500 hover:text-neutral-800">
            ← Overview &amp; 3D Showcase
          </Link>
        </div>
      </div>
    </div>
  );
}
