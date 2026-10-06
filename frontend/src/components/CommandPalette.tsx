import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  FileText,
  GitCompare,
  Settings,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { request } from "../lib/api";
import type { DocumentOut } from "../lib/types";

interface CommandPaletteProps {
  isOpen: boolean;
  onToggle: () => void;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onToggle, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState("");
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isOpen) {
      setQuery("");
      setSelectedIndex(0);
      return;
    }

    void (async () => {
      try {
        const list = await request<DocumentOut[]>("/documents");
        setDocs(list);
      } catch {
        /* ignore */
      }
    })();
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onToggle();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onToggle]);

  if (!isOpen) return null;

  const filteredDocs = docs.filter((d) =>
    d.filename.toLowerCase().includes(query.toLowerCase()),
  );

  const navigationActions = [
    {
      id: "nav-docs",
      label: "Documents Workspace",
      icon: <FileText className="h-4 w-4 text-neutral-500" />,
      action: () => {
        navigate("/");
        onClose();
      },
    },
    {
      id: "nav-compare",
      label: "Compare Documents",
      icon: <GitCompare className="h-4 w-4 text-neutral-500" />,
      action: () => {
        navigate("/compare");
        onClose();
      },
    },
    {
      id: "nav-landing",
      label: "Overview & 3D Architectural Scene",
      icon: <Sparkles className="h-4 w-4 text-neutral-500" />,
      action: () => {
        navigate("/landing");
        onClose();
      },
    },
    {
      id: "nav-settings",
      label: "Settings & AI Provider",
      icon: <Settings className="h-4 w-4 text-neutral-500" />,
      action: () => {
        navigate("/settings");
        onClose();
      },
    },
  ];

  const filteredNav = navigationActions.filter((a) =>
    a.label.toLowerCase().includes(query.toLowerCase()),
  );

  const totalItems = filteredDocs.length + filteredNav.length;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (totalItems || 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + (totalItems || 1)) % (totalItems || 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex < filteredDocs.length) {
        const doc = filteredDocs[selectedIndex];
        navigate(`/documents/${doc.id}`);
        onClose();
      } else {
        const navIdx = selectedIndex - filteredDocs.length;
        if (filteredNav[navIdx]) filteredNav[navIdx].action();
      }
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/30 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-xl border border-neutral-200 bg-white shadow-xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        onKeyDown={handleKeyDown}
      >
        <div className="flex items-center gap-2.5 border-b border-neutral-100 px-4 py-3 bg-neutral-50/50">
          <Search className="h-4 w-4 text-neutral-400" />
          <input
            autoFocus
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            placeholder="Search documents or jump to page... (Esc to close)"
            className="flex-1 bg-transparent text-xs text-neutral-900 placeholder-neutral-400 outline-none"
          />
        </div>

        <div className="max-h-72 overflow-y-auto p-1.5 space-y-0.5">
          {filteredDocs.length > 0 && (
            <div>
              <div className="px-2.5 py-1 text-[10px] font-mono uppercase tracking-wider text-neutral-400">
                Documents
              </div>
              {filteredDocs.map((doc, idx) => {
                const isSelected = selectedIndex === idx;
                return (
                  <button
                    key={doc.id}
                    onClick={() => {
                      navigate(`/documents/${doc.id}`);
                      onClose();
                    }}
                    className={`flex items-center justify-between w-full rounded-lg px-2.5 py-1.5 text-left text-xs transition ${
                      isSelected
                        ? "bg-neutral-100 text-neutral-900 font-medium"
                        : "text-neutral-700 hover:bg-neutral-50"
                    }`}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="h-3.5 w-3.5 text-neutral-400 shrink-0" />
                      <span className="truncate">{doc.filename}</span>
                    </div>
                    <span className="text-[10px] font-mono text-neutral-400 shrink-0">
                      {doc.clause_count > 0 ? `${doc.clause_count} clauses` : ""}
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          {filteredNav.length > 0 && (
            <div className="pt-1">
              <div className="px-2.5 py-1 text-[10px] font-mono uppercase tracking-wider text-neutral-400">
                Navigation
              </div>
              {filteredNav.map((action, idx) => {
                const itemIdx = filteredDocs.length + idx;
                const isSelected = selectedIndex === itemIdx;
                return (
                  <button
                    key={action.id}
                    onClick={action.action}
                    className={`flex items-center justify-between w-full rounded-lg px-2.5 py-1.5 text-left text-xs transition ${
                      isSelected
                        ? "bg-neutral-100 text-neutral-900 font-medium"
                        : "text-neutral-700 hover:bg-neutral-50"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      {action.icon}
                      <span>{action.label}</span>
                    </div>
                    <ArrowRight className="h-3 w-3 text-neutral-400" />
                  </button>
                );
              })}
            </div>
          )}

          {totalItems === 0 && (
            <div className="py-6 text-center text-xs text-neutral-400">
              No results for "{query}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
