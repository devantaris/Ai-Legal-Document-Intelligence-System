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
  BookOpen,
  ShieldCheck,
  Shield,
} from "lucide-react";
import { useAuth } from "../stores/auth";
import { useTenant } from "../stores/tenant";
import { CommandPalette } from "./CommandPalette";
import { request } from "../lib/api";
import type { LlmInfo } from "../lib/types";

interface NavCategory {
  title: string;
  items: {
    to: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: string;
  }[];
}

const navCategories: NavCategory[] = [
  {
    title: "Matter Dossier",
    items: [
      { to: "/", label: "Agreements Docket", icon: FileText },
      { to: "/portfolio", label: "Contract Vault & Diligence", icon: Briefcase },
      { to: "/compare", label: "Bilateral Redline Compare", icon: GitCompare },
    ],
  },
  {
    title: "Institutional Governance",
    items: [
      { to: "/playbooks", label: "Negotiation Playbooks", icon: BookOpen },
      { to: "/workspaces", label: "Matter Workspaces", icon: FolderKanban },
      { to: "/audit-logs", label: "Compliance Audit Trail", icon: ShieldCheck },
    ],
  },
  {
    title: "Practice Management",
    items: [
      { to: "/team", label: "Firm Roster & RBAC", icon: Users },
      { to: "/plan", label: "Sovereign Quotas", icon: CreditCard, badge: "Pro" },
      { to: "/landing", label: "Architectural Overview", icon: Sparkles },
      { to: "/settings", label: "Inference Engine", icon: Settings },
    ],
  },
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

  const userInitials = user?.email
    ? user.email.slice(0, 2).toUpperCase()
    : "AT";

  return (
    <div className="flex h-screen bg-[#F8F9FA] text-[#0F172A] overflow-hidden font-sans-legal">
      <CommandPalette
        isOpen={commandPaletteOpen}
        onToggle={() => setCommandPaletteOpen((o) => !o)}
        onClose={() => setCommandPaletteOpen(false)}
      />

      {/* Desktop Sovereign Sidebar */}
      <aside className="hidden md:flex w-64 shrink-0 flex-col border-r border-[#E2E8F0] bg-white shadow-[1px_0_3px_0_rgba(15,23,42,0.03)] z-20">
        {/* Brand & Crest Header */}
        <div className="p-4 border-b border-[#F1F5F9]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#0F172A] text-amber-400 shadow-sm border border-neutral-800">
                <Scale className="h-4 w-4" />
              </div>
              <div>
                <span className="text-xs font-bold tracking-tight text-[#0F172A] uppercase font-mono-legal">
                  LegalIQ
                </span>
                <span className="block text-[9px] font-semibold text-amber-700 uppercase tracking-widest">
                  Sovereign SaaS
                </span>
              </div>
            </div>

            <span className="inline-flex items-center gap-1 rounded border border-emerald-200 bg-emerald-50 px-1.5 py-0.5 text-[9px] font-mono font-medium text-emerald-800">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Private
            </span>
          </div>

          {/* Institutional Organization Switcher */}
          <div className="relative">
            <button
              onClick={() => setOrgDropdownOpen(!orgDropdownOpen)}
              className="flex w-full items-center justify-between rounded-lg border border-[#E2E8F0] bg-[#F8F9FA] px-2.5 py-1.5 text-xs text-[#1E293B] hover:bg-[#F1F5F9] transition"
            >
              <div className="flex items-center gap-2 truncate">
                <Building2 className="h-3.5 w-3.5 text-neutral-500 shrink-0" />
                <span className="font-semibold truncate">{currentOrg?.name ?? "Select Firm Org"}</span>
              </div>
              <ChevronDown className="h-3 w-3 text-neutral-400 shrink-0 ml-1" />
            </button>

            {orgDropdownOpen && (
              <div className="absolute top-full left-0 right-0 mt-1 z-50 rounded-lg border border-[#E2E8F0] bg-white shadow-xl py-1 text-xs">
                <div className="px-3 py-1 text-[10px] font-mono text-neutral-400 uppercase tracking-wider border-b border-neutral-100">
                  Client Organizations
                </div>
                {organizations.map((org) => (
                  <button
                    key={org.id}
                    onClick={() => {
                      void selectOrganization(org.id);
                      setOrgDropdownOpen(false);
                    }}
                    className={`flex w-full items-center justify-between px-3 py-2 text-left hover:bg-[#F8F9FA] transition ${
                      org.id === currentOrg?.id ? "font-semibold text-[#0F172A] bg-[#F1F5F9]" : "text-neutral-600"
                    }`}
                  >
                    <span className="truncate">{org.name}</span>
                    <span className="text-[10px] text-neutral-400 font-mono capitalize">{org.role}</span>
                  </button>
                ))}
                <div className="border-t border-neutral-100 mt-1 pt-1">
                  <button
                    onClick={() => {
                      setOrgDropdownOpen(false);
                      setNewOrgPromptOpen(true);
                    }}
                    className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-neutral-700 hover:bg-[#F8F9FA] font-medium"
                  >
                    <Plus className="h-3 w-3" />
                    <span>Create Organization</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Active Matter Deal Room Selector */}
          {workspaces.length > 0 && (
            <div className="mt-2.5 pt-2 border-t border-neutral-100">
              <div className="flex items-center justify-between text-[10px] font-mono uppercase tracking-wider text-neutral-400 px-1 mb-1">
                <span>Active Matter</span>
                <span className="text-amber-700 font-semibold">{workspaces.length} Matters</span>
              </div>
              <select
                value={currentWorkspace?.id ?? ""}
                onChange={(e) => selectWorkspace(e.target.value)}
                className="w-full rounded-md border border-[#E2E8F0] bg-white px-2 py-1.5 text-[11px] font-medium text-[#1E293B] focus:border-[#0F172A] focus:outline-none transition shadow-2xs"
              >
                {workspaces.map((ws) => (
                  <option key={ws.id} value={ws.id}>
                    📁 {ws.name} ({ws.document_count} contracts)
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Global Quick Search Button */}
        <div className="px-3 pt-3 pb-1">
          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex w-full items-center justify-between rounded-lg border border-[#E2E8F0] bg-[#F8F9FA] px-2.5 py-1.5 text-xs text-neutral-500 hover:bg-[#F1F5F9] hover:text-[#0F172A] transition"
          >
            <div className="flex items-center gap-2">
              <Search className="h-3.5 w-3.5 text-neutral-400" />
              <span className="text-[11px]">Command Palette…</span>
            </div>
            <kbd className="rounded bg-white px-1.5 py-0.5 text-[10px] font-mono text-neutral-400 border border-[#E2E8F0] shadow-2xs">
              ⌘K
            </kbd>
          </button>
        </div>

        {/* Categorized Workstation Navigation */}
        <nav className="flex-1 px-3 py-2 space-y-4 overflow-y-auto">
          {navCategories.map((cat) => (
            <div key={cat.title}>
              <div className="px-2.5 mb-1 text-[10px] font-mono uppercase tracking-wider text-neutral-400 font-semibold">
                {cat.title}
              </div>
              <div className="space-y-0.5">
                {cat.items.map((item) => {
                  const Icon = item.icon;
                  const isActive =
                    item.to === "/" ? location.pathname === "/" : location.pathname.startsWith(item.to);
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.to === "/"}
                      className={`group flex items-center justify-between rounded-lg px-2.5 py-1.5 text-xs font-medium transition ${
                        isActive
                          ? "bg-[#0F172A] text-white shadow-sm font-semibold"
                          : "text-neutral-600 hover:bg-[#F1F5F9] hover:text-[#0F172A]"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 truncate">
                        <Icon
                          className={`h-3.5 w-3.5 shrink-0 transition ${
                            isActive ? "text-amber-400" : "text-neutral-400 group-hover:text-neutral-600"
                          }`}
                        />
                        <span className="truncate">{item.label}</span>
                      </div>
                      {item.badge && (
                        <span
                          className={`rounded px-1.5 py-0.2 text-[9px] font-mono ${
                            isActive
                              ? "bg-amber-400 text-neutral-900 font-bold"
                              : "bg-neutral-100 text-neutral-500 border border-neutral-200"
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Sovereign Inference Status Footer */}
        <div className="p-3 border-t border-[#F1F5F9] bg-[#FAFAFA]">
          <div className="flex items-center justify-between text-[10px] font-mono text-neutral-500 mb-2">
            <span className="flex items-center gap-1.5">
              <Shield className="h-3 w-3 text-emerald-600" />
              <span>Sovereign Local Inference</span>
            </span>
            <span className="text-emerald-700 font-semibold">Active</span>
          </div>
          <div className="flex items-center justify-between rounded-md bg-white border border-[#E2E8F0] px-2 py-1 text-[10px] font-mono text-neutral-600">
            <span className="truncate">{llmInfo?.llm_model ?? "llama3.2:3b"}</span>
            <span className="text-[9px] text-neutral-400">Ollama</span>
          </div>
        </div>

        {/* User Profile Card */}
        <div className="border-t border-[#E2E8F0] p-3 bg-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0 pr-2">
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[#0F172A] text-[10px] font-bold text-white font-mono">
                {userInitials}
              </div>
              <div className="min-w-0">
                <div className="truncate text-xs font-semibold text-[#0F172A]" title={user?.email}>
                  {user?.email}
                </div>
                <div className="text-[10px] text-neutral-400 font-mono capitalize">
                  {currentOrg?.role ?? "Attorney"} • {currentOrg?.plan_tier?.replace(/_/g, " ") ?? "Sovereign Pro"}
                </div>
              </div>
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="rounded p-1 text-neutral-400 hover:text-rose-600 hover:bg-rose-50 transition"
              title="Sign Out"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-[#F8F9FA]">
        {/* Top Desktop Breadcrumb & Action Banner */}
        <header className="hidden md:flex h-12 shrink-0 items-center justify-between border-b border-[#E2E8F0] bg-white px-6">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-neutral-900">{currentOrg?.name ?? "Legal Organization"}</span>
            <span className="text-neutral-300">/</span>
            <span className="font-medium text-neutral-600 flex items-center gap-1">
              📁 {currentWorkspace?.name ?? "General Matters"}
            </span>
            <span className="text-neutral-300">/</span>
            <span className="text-[11px] font-mono text-neutral-400 uppercase tracking-wider">
              {location.pathname === "/"
                ? "Agreements Docket"
                : location.pathname.slice(1).replace(/-/g, " ")}
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-[11px] text-neutral-500 font-mono bg-[#F8F9FA] px-2.5 py-1 rounded-md border border-[#E2E8F0]">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              <span>Privileged & Confidential • Zero Data Egress</span>
            </div>
          </div>
        </header>

        {/* Mobile Top Header */}
        <div className="flex md:hidden items-center justify-between border-b border-[#E2E8F0] bg-white px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#0F172A] text-amber-400">
              <Scale className="h-3.5 w-3.5" />
            </div>
            <span className="font-bold text-xs tracking-tight">LegalIQ</span>
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
          <div className="md:hidden border-b border-[#E2E8F0] bg-white p-4 space-y-3">
            {navCategories.map((cat) => (
              <div key={cat.title}>
                <div className="text-[10px] font-mono uppercase text-neutral-400 font-semibold mb-1">
                  {cat.title}
                </div>
                {cat.items.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium text-neutral-700 hover:bg-[#F8F9FA]"
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </NavLink>
                ))}
              </div>
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
        <main className="min-w-0 flex-1 overflow-y-auto bg-[#F8F9FA]">
          {children}
        </main>
      </div>

      {/* New Organization Modal */}
      {newOrgPromptOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
          <div className="w-full max-w-sm rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-2xl">
            <h3 className="text-sm font-bold text-[#0F172A]">Create Legal Organization</h3>
            <p className="mt-1 text-xs text-neutral-500">
              Each organization maintains isolated matter vaults, custom playbooks, and strict attorney-client privilege boundaries.
            </p>
            <form onSubmit={handleCreateOrg} className="mt-4 space-y-3">
              <input
                type="text"
                required
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder="e.g. Cravath & Swaine LLP, Acme Enterprise Counsel"
                className="w-full rounded-lg border border-[#E2E8F0] px-3 py-2 text-xs focus:border-[#0F172A] focus:outline-none"
              />
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setNewOrgPromptOpen(false)}
                  className="rounded-lg border border-[#E2E8F0] px-3 py-1.5 text-xs font-medium text-neutral-600 hover:bg-[#F8F9FA]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-[#0F172A] px-4 py-1.5 text-xs font-semibold text-white hover:bg-neutral-800 transition"
                >
                  Create Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
