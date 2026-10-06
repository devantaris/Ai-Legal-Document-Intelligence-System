import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./stores/auth";
import { Layout } from "./components/Layout";
import { AuthPage } from "./pages/AuthPage";
import { DashboardPage } from "./pages/DashboardPage";
import { DocumentPage } from "./pages/DocumentPage";
import { ComparePage } from "./pages/ComparePage";
import { SettingsPage } from "./pages/SettingsPage";
import { LandingPage } from "./pages/LandingPage";

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, initialized } = useAuth();
  if (!initialized) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#f8f8f7] text-neutral-500">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-neutral-900 border-t-transparent" />
          <span className="text-xs font-mono">Preparing your workspace…</span>
        </div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

export default function App() {
  const init = useAuth((s) => s.init);
  const user = useAuth((s) => s.user);
  const initialized = useAuth((s) => s.initialized);
  const location = useLocation();

  useEffect(() => {
    void init();
  }, [init]);

  // Auth pages
  if (location.pathname === "/login" || location.pathname === "/register") {
    return (
      <Routes>
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
      </Routes>
    );
  }

  // Standalone 3D landing page / showcase accessible to anyone
  if (location.pathname === "/landing") {
    return (
      <Routes>
        <Route path="/landing" element={<LandingPage />} />
      </Routes>
    );
  }

  // Root route: If not authenticated, display the 3D Landing Page; if logged in, display Dashboard
  return (
    <Routes>
      <Route
        path="/"
        element={
          !initialized ? (
            <div className="flex h-screen items-center justify-center bg-[#f8f8f7] text-neutral-500">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-neutral-900 border-t-transparent" />
            </div>
          ) : user ? (
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          ) : (
            <LandingPage />
          )
        }
      />
      <Route
        path="/documents/:id"
        element={
          <RequireAuth>
            <DocumentPage />
          </RequireAuth>
        }
      />
      <Route
        path="/compare"
        element={
          <RequireAuth>
            <ComparePage />
          </RequireAuth>
        }
      />
      <Route
        path="/settings"
        element={
          <RequireAuth>
            <SettingsPage />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
