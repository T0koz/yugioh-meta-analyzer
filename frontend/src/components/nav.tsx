"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { SmartSearch } from "@/components/smart-search";

type NavLink = { href: string; label: string };
type NavEntry =
  | ({ kind: "link" } & NavLink)
  | { kind: "group"; label: string; items: NavLink[] };

// Groupé par audience plutôt que par thème : Boutique reste à part de Méta
// même si Early Signals et Signaux Boutique parlent tous les deux de
// "cartes qui montent" — un tiers du score d'Early Signals est littéralement
// le même alert_score que Boutique (voir notebooks/11_early_card_signal.ipynb).
const NAV_ENTRIES: NavEntry[] = [
  {
    kind: "group",
    label: "Méta",
    items: [
      { href: "/tier-list", label: "Tier List" },
      { href: "/evolution", label: "Évolution" },
      { href: "/predictions", label: "Prédictions" },
    ],
  },
  { kind: "link", href: "/ban", label: "Ban Center" },
  {
    kind: "group",
    label: "Boutique",
    items: [
      { href: "/boutique", label: "Signaux Boutique" },
      { href: "/early-signals", label: "Early Signals" },
    ],
  },
  { kind: "link", href: "/graph", label: "Graphe" },
];

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      viewBox="0 0 12 12"
      className={`h-3 w-3 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
      fill="none"
    >
      <path
        d="M2.5 4.5L6 8l3.5-3.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function NavDropdown({
  label,
  items,
  pathname,
  isOpen,
  onToggle,
  onSelect,
}: {
  label: string;
  items: NavLink[];
  pathname: string;
  isOpen: boolean;
  onToggle: () => void;
  onSelect: () => void;
}) {
  const active = items.some((item) => item.href === pathname);

  return (
    <div className="relative shrink-0">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        className={`flex items-center gap-1 text-sm transition-colors ${
          active ? "text-white font-semibold" : "text-slate-400 hover:text-slate-200"
        }`}
      >
        {label}
        <ChevronIcon open={isOpen} />
      </button>
      {isOpen && (
        <div className="absolute left-0 top-full z-50 mt-2 min-w-[11rem] rounded-md border border-slate-700 bg-slate-900 py-1 shadow-xl">
          {items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onSelect}
              className={`block px-3 py-1.5 text-sm transition-colors ${
                pathname === item.href
                  ? "bg-slate-800 font-semibold text-white"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export function Nav() {
  const pathname = usePathname();
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const navRef = useRef<HTMLDivElement>(null);

  // Ferme le menu ouvert au clic en dehors — un vrai abonnement à un
  // événement DOM externe, pas une resynchronisation d'état dérivé.
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setOpenGroup(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <nav className="border-b border-slate-800 bg-slate-950 px-6 py-3">
      <div ref={navRef} className="max-w-6xl mx-auto flex flex-wrap items-center gap-x-6 gap-y-2">
        <span className="text-indigo-400 font-bold text-sm shrink-0">⚔ YGO Meta</span>
        {/* Pas d'overflow-x-auto ici : `overflow-x` sans `overflow-y` explicite
            fait passer ce dernier à `auto`, ce qui coupe verticalement les
            menus déroulants (même piège que InfoTooltip, voir context.md).
            flex-wrap sur le conteneur parent suffit à gérer l'étroit. */}
        <div className="flex items-center gap-6">
          {NAV_ENTRIES.map((entry) =>
            entry.kind === "link" ? (
              <Link
                key={entry.href}
                href={entry.href}
                className={`text-sm shrink-0 transition-colors ${
                  pathname === entry.href
                    ? "text-white font-semibold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {entry.label}
              </Link>
            ) : (
              <NavDropdown
                key={entry.label}
                label={entry.label}
                items={entry.items}
                pathname={pathname}
                isOpen={openGroup === entry.label}
                onToggle={() => setOpenGroup(openGroup === entry.label ? null : entry.label)}
                onSelect={() => setOpenGroup(null)}
              />
            )
          )}
        </div>
        <SmartSearch />
      </div>
    </nav>
  );
}
