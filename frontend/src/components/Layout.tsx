import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../stores/auth";

const navItems = [
  { to: "/", label: "Documents", icon: "📄" },
  { to: "/compare", label: "Compare", icon: "⇄" },
  { to: "/settings", label: "Settings", icon: "⚙" },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex h-full">
      <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="px-5 py-5">
          <div className="text-lg font-semibold tracking-tight text-slate-900">
            ⚖ Legal<span className="text-indigo-600">IQ</span>
          </div>
          <div className="mt-0.5 text-xs text-slate-400">Document Intelligence</div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`
              }
            >
              <span className="w-5 text-center">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-200 p-3">
          <div className="mb-2 truncate px-2 text-xs text-slate-500" title={user?.email}>
            {user?.email}
          </div>
          <button
            onClick={() => {
              logout();
              navigate("/login");
            }}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-600 hover:bg-slate-100"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="min-w-0 flex-1 overflow-y-auto">{children}</main>
    </div>
  );
}
