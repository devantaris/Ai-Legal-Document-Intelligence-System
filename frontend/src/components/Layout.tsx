import { useState, useEffect } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  FileText,
  GitCompare,
  Settings,
  Sparkles,
  LogOut,
  Scale,
  Search,
  Menu,
  X,
} from "lucide-react";
import { useAuth } from "../stores/auth";
import { CommandPalette } from "./CommandPalette";
import { request } from "../lib/api";
import type { LlmInfo } from "../lib/types";

const navItems = [
  { to: "/", label: "Documents", icon: FileText },
  { to: "/compare", label: "Compare", icon: GitCompare },
  { to: "/landing", label: "Overview & 3D", icon: Sparkles },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [llmInfo, setLlmInfo] = useState<LlmInfo | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const info = await request<LlmInfo>("/settings/llm");
        setLlmInfo(info);
      } catch {
        /* ignore */
      }
    })();
  }, []);

  return (
    <div className="flex h-screen bg-[#f8f8f7] text-neutral-900 overflow-hidden font-sans">
      <CommandPalette
        isOpen={commandPaletteOpen}
        onToggle={() => setCommandPaletteOpen((o) => !o)}
        onClose={() => setCommandPaletteOpen(false)}
      />

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-56 shrink-0 flex-col border-r border-neutral-200/80 bg-white">
        {/* Brand */}
        <div className="p-4 border-b border-neutral-100">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-neutral-900 text-white">
              <Scale className="h-3.5 w-3.5" />
            </div>
            <div className="text-sm font-semibold tracking-tight text-neutral-900">LegalIQ</div>
          </div>
        </div>

        {/* Quick Search */}
        <div className="p-2.5">
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex w-full items-center justify-between rounded-lg border border-neutral-200/80 bg-neutral-50 px-2.5 py-1.5 text-xs text-neutral-500 hover:bg-neutral-100 hover:text-neutral-900 transition"
          >
            <div className="flex items-center gap-2">
              <Search className="h-3.5 w-3.5" />
              <span>Search...</span>
            </div>
            <kbd className="rounded bg-white px-1.5 py-0.5 text-[10px] font-mono text-neutral-400 border border-neutral-200">
              ⌘K
            </kbd>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-0.5 px-2.5 py-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.to === "/" ? location.pathname === "/" : location.pathname.startsWith(item.to);
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-xs font-medium transition ${
                  isActive
                    ? "bg-neutral-100 text-neutral-900 font-semibold"
                    : "text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900"
                }`}
              >
                <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-neutral-900" : "text-neutral-400"}`} />
                <span className="flex-1">{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Engine status indicator */}
        <div className="px-3 py-2 border-t border-neutral-100">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-neutral-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            <span>{llmInfo?.provider === "zai" ? "Z.ai GLM" : "Ollama Local"}</span>
          </div>
        </div>

        {/* User Card */}
        <div className="border-t border-neutral-100 p-3">
          <div className="flex items-center justify-between">
            <div className="min-w-0 pr-2">
              <div className="truncate text-xs font-medium text-neutral-800" title={user?.email}>
                {user?.email}
              </div>
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="rounded p-1 text-neutral-400 hover:text-neutral-900 transition"
              title="Sign Out"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Mobile Top Header */}
        <div className="flex md:hidden items-center justify-between border-b border-neutral-200/80 bg-white px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-neutral-900 text-white">
              <Scale className="h-3.5 w-3.5" />
            </div>
            <span className="font-semibold text-sm">LegalIQ</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="rounded p-1 text-neutral-600"
            >
              <Search className="h-4 w-4" />
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="rounded p-1 text-neutral-600"
            >
              {mobileMenuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-b border-neutral-200 bg-white p-4 space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-neutral-700 hover:bg-neutral-100"
              >
                <item.icon className="h-4 w-4" />
                <span>{item.label}</span>
              </NavLink>
            ))}
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50"
            >
              <LogOut className="h-4 w-4" />
              <span>Sign Out</span>
            </button>
          </div>
        )}

        {/* Scrollable Work Area */}
        <main className="min-w-0 flex-1 overflow-y-auto bg-[#f8f8f7]">
          {children}
        </main>
      </div>
    </div>
  );
}
