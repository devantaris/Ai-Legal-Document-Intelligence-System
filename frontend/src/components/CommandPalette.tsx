import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Search,
  FileText,
  Briefcase,
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
      id: "nav-vault",
      label: "Contract Vault & Due Diligence Matrix",
      icon: <Briefcase className="h-4 w-4 text-neutral-500" />,
      action: () => {
        navigate("/portfolio");
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
        const targetDoc = filteredDocs[selectedIndex];
        if (targetDoc) {
          navigate(`/documents/${targetDoc.id}`);
          onClose();
        }
      } else {
        const actionIdx = selectedIndex - filteredDocs.length;
        filteredNav[actionIdx]?.action();
      }
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 p-4 pt-20 backdrop-blur-xs"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl rounded-xl border border-neutral-200 bg-white shadow-2xl overflow-hidden font-sans"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div className="flex items-center border-b border-neutral-200/80 px-4 py-3 bg-white">
          <Search className="h-4 w-4 text-neutral-400 mr-2.5 shrink-0" />
          <input
            type="text"
            autoFocus
            placeholder="Type a document name, section, or action…"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            className="w-full bg-transparent text-sm text-neutral-900 placeholder-neutral-400 focus:outline-none"
          />
          <kbd className="rounded bg-neutral-100 border border-neutral-200 px-1.5 py-0.5 text-[10px] font-mono text-neutral-400">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2 space-y-1">
          {filteredDocs.length > 0 && (
            <div className="px-2.5 py-1 text-[10px] font-semibold tracking-wider text-neutral-400 uppercase">
              Documents
            </div>
          )}
          {filteredDocs.map((doc, idx) => {
            const isSelected = idx === selectedIndex;
            return (
              <div
                key={doc.id}
                onClick={() => {
                  navigate(`/documents/${doc.id}`);
                  onClose();
                }}
                className={`flex items-center justify-between rounded-lg px-2.5 py-2 text-xs cursor-pointer transition ${
                  isSelected
                    ? "bg-neutral-100 text-neutral-900 font-semibold"
                    : "text-neutral-700 hover:bg-neutral-50"
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <FileText className="h-4 w-4 text-neutral-400 shrink-0" />
                  <span className="truncate">{doc.filename}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0 text-neutral-400 text-[11px]">
                  <span>{doc.page_count ? `${doc.page_count}p` : ""}</span>
                  {isSelected && <ArrowRight className="h-3.5 w-3.5 text-neutral-900" />}
                </div>
              </div>
            );
          })}

          {filteredNav.length > 0 && (
            <div className="px-2.5 pt-2 pb-1 text-[10px] font-semibold tracking-wider text-neutral-400 uppercase">
              Navigation & Actions
            </div>
          )}
          {filteredNav.map((action, idx) => {
            const itemIndex = filteredDocs.length + idx;
            const isSelected = itemIndex === selectedIndex;
            return (
              <div
                key={action.id}
                onClick={action.action}
                className={`flex items-center justify-between rounded-lg px-2.5 py-2 text-xs cursor-pointer transition ${
                  isSelected
                    ? "bg-neutral-100 text-neutral-900 font-semibold"
                    : "text-neutral-700 hover:bg-neutral-50"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  {action.icon}
                  <span>{action.label}</span>
                </div>
                {isSelected && <ArrowRight className="h-3.5 w-3.5 text-neutral-900" />}
              </div>
            );
          })}

          {totalItems === 0 && (
            <div className="p-6 text-center text-xs text-neutral-400">
              No results found for "{query}".
            </div>
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="flex items-center justify-between border-t border-neutral-100 bg-neutral-50/60 px-3.5 py-2 text-[10px] text-neutral-400 font-mono">
          <div className="flex items-center gap-3">
            <span>↑↓ to navigate</span>
            <span>↵ to select</span>
          </div>
          <span>LegalIQ Command Center</span>
        </div>
      </div>
    </div>
  );
}
