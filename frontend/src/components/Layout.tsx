import { useState, useEffect } from "react";
import { NavLink, useNavigate, useLocation } from "react-router-dom";
import {
  FileText,
  Briefcase,
  GitCompare,
  Settings,
  Sparkles,
  LogOut,
  Scale,
  Search,
  Menu,
  X,
  Users,
  FolderKanban,
  CreditCard,
  Building2,
  ChevronDown,
  Plus,
} from "lucide-react";
import { useAuth } from "../stores/auth";
import { useTenant } from "../stores/tenant";
import { CommandPalette } from "./CommandPalette";
import { request } from "../lib/api";
import type { LlmInfo } from "../lib/types";

const navItems = [
  { to: "/", label: "Documents", icon: FileText },
  { to: "/portfolio", label: "Contract Vault", icon: Briefcase },
  { to: "/compare", label: "Compare", icon: GitCompare },
  { to: "/workspaces", label: "Workspaces", icon: FolderKanban },
  { to: "/team", label: "Team & RBAC", icon: Users },
  { to: "/plan", label: "Plan & Usage", icon: CreditCard },
  { to: "/landing", label: "Overview & 3D", icon: Sparkles },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const {
    currentOrg,
    organizations,
    selectOrganization,
    currentWorkspace,
    workspaces,
    selectWorkspace,
    loadOrganizations,
    createOrganization,
  } = useTenant();
  const navigate = useNavigate();
  const location = useLocation();
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [orgDropdownOpen, setOrgDropdownOpen] = useState(false);
  const [newOrgPromptOpen, setNewOrgPromptOpen] = useState(false);
  const [newOrgName, setNewOrgName] = useState("");
  const [llmInfo, setLlmInfo] = useState<LlmInfo | null>(null);

  useEffect(() => {
    void loadOrganizations();
  }, [loadOrganizations]);

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

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName.trim()) return;
    try {
      await createOrganization(newOrgName.trim());
      setNewOrgName("");
      setNewOrgPromptOpen(false);
    } catch {
      alert("Failed to create organization");
    }
  };

  return (
    <div className="flex h-screen bg-[#f8f8f7] text-neutral-900 overflow-hidden font-sans">
      <CommandPalette
        isOpen={commandPaletteOpen}
        onToggle={() => setCommandPaletteOpen((o) => !o)}
        onClose={() => setCommandPaletteOpen(false)}
      />

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-60 shrink-0 flex-col border-r border-neutral-200/80 bg-white">
        {/* Brand & Org Switcher */}
        <div className="p-3 border-b border-neutral-100">
          <div className="flex items-center gap-2 mb-2 px-1">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-neutral-900 text-white">
              <Scale className="h-3.5 w-3.5" />
            </div>
            <div className="text-xs font-bold tracking-tight text-neutral-900">LegalIQ SaaS</div>
          </div>

          {/* Org Selector Dropdown */}
          <div className="relative">
            <button
              onClick={() => setOrgDropdownOpen(!orgDropdownOpen)}
              className="flex w-full items-center justify-between rounded-lg border border-neutral-200/80 bg-neutral-50 px-2.5 py-1.5 text-xs text-neutral-800 hover:bg-neutral-100 transition"
            >
              <div className="flex items-center gap-2 truncate">
                <Building2 className="h-3.5 w-3.5 text-neutral-500 shrink-0" />
                <span className="font-medium truncate">{currentOrg?.name ?? "Select Org"}</span>
              </div>
              <ChevronDown className="h-3 w-3 text-neutral-400 shrink-0 ml-1" />
            </button>

            {orgDropdownOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 z-50 rounded-lg border border-neutral-200 bg-white shadow-lg py-1 text-xs">
                <div className="px-2.5 py-1 text-[10px] font-mono text-neutral-400 uppercase tracking-wider">
                  Organizations
                </div>
                {organizations.map((org) => (
                  <button
                    key={org.id}
                    onClick={() => {
                      void selectOrganization(org.id);
                      setOrgDropdownOpen(false);
                    }}
                    className={`flex w-full items-center justify-between px-3 py-1.5 text-left hover:bg-neutral-50 ${
                      org.id === currentOrg?.id ? "font-semibold text-neutral-900 bg-neutral-50" : "text-neutral-600"
                    }`}
                  >
                    <span className="truncate">{org.name}</span>
                    <span className="text-[10px] text-neutral-400 capitalize">{org.role}</span>
                  </button>
                ))}
                <div className="border-t border-neutral-100 mt-1 pt-1">
                  <button
                    onClick={() => {
                      setOrgDropdownOpen(false);
                      setNewOrgPromptOpen(true);
                    }}
                    className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-neutral-700 hover:bg-neutral-50 font-medium"
                  >
                    <Plus className="h-3 w-3" />
                    <span>New Organization</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Workspace Switcher Selector */}
          {workspaces.length > 0 && (
            <div className="mt-2">
              <label className="block text-[10px] font-mono uppercase tracking-wider text-neutral-400 px-1 mb-0.5">
                Active Matter
              </label>
              <select
                value={currentWorkspace?.id ?? ""}
                onChange={(e) => selectWorkspace(e.target.value)}
                className="w-full rounded-md border border-neutral-200/80 bg-neutral-50 px-2 py-1 text-[11px] font-medium text-neutral-700 focus:border-neutral-900 focus:outline-none"
              >
                {workspaces.map((ws) => (
                  <option key={ws.id} value={ws.id}>
                    📁 {ws.name} ({ws.document_count})
                  </option>
                ))}
              </select>
            </div>
          )}
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
        <nav className="flex-1 space-y-0.5 px-2.5 py-1 overflow-y-auto">
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
                {item.to === "/plan" && (
                  <span className="rounded bg-neutral-100 border border-neutral-200 px-1.5 py-0.2 text-[9px] font-mono text-neutral-500">
                    Pro
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Engine status indicator */}
        <div className="px-3 py-2 border-t border-neutral-100">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-neutral-500">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            <span>{llmInfo?.provider === "zai" ? "Z.ai GLM" : "Ollama Sovereign"}</span>
          </div>
        </div>

        {/* User Card */}
        <div className="border-t border-neutral-100 p-3">
          <div className="flex items-center justify-between">
            <div className="min-w-0 pr-2">
              <div className="truncate text-xs font-medium text-neutral-800" title={user?.email}>
                {user?.email}
              </div>
              <div className="text-[10px] text-neutral-400 capitalize">
                Role: {currentOrg?.role ?? "counsel"}
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
            <span className="text-[10px] font-mono bg-neutral-100 px-1.5 py-0.5 rounded text-neutral-600">
              {currentOrg?.name}
            </span>
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

      {/* New Organization Modal */}
      {newOrgPromptOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-xl border border-neutral-200 bg-white p-5 shadow-xl">
            <h3 className="text-sm font-semibold text-neutral-900">Create New Legal Organization</h3>
            <p className="mt-1 text-xs text-neutral-500">
              Organizations provide isolated tenant boundaries for matters, agreements, and members.
            </p>
            <form onSubmit={handleCreateOrg} className="mt-4 space-y-3">
              <input
                type="text"
                required
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder="e.g. Acme Legal Corp, Wilson & Associates"
                className="w-full rounded-lg border border-neutral-200 px-3 py-2 text-xs focus:border-neutral-900 focus:outline-none"
              />
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setNewOrgPromptOpen(false)}
                  className="rounded-lg border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-neutral-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-neutral-900 px-3.5 py-1.5 text-xs font-medium text-white hover:bg-neutral-800"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
