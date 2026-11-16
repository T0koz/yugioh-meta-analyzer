"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { controlClass } from "@/components/ds/control";
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
      { href: "/tier-list", label: "Tier list" },
      { href: "/evolution", label: "Évolution" },
      { href: "/predictions", label: "Prédictions" },
    ],
  },
  { kind: "link", href: "/ban", label: "Ban Center" },
  {
    kind: "group",
    label: "Boutique",
    items: [
      { href: "/boutique", label: "Signaux boutique" },
      { href: "/early-signals", label: "Signaux précoces" },
    ],
  },
  { kind: "link", href: "/graph", label: "Graphe" },
];

// Lien de premier niveau : un onglet du composant source (actif = en relief sur --ink-4).
function linkClass(active: boolean, className?: string) {
  return controlClass({ variant: "tab", active, className });
}

// Même surface que la nav pour les sous-menus et le menu mobile.
const PANEL = "rounded-[8px] border border-line-2 bg-ink-2/95 backdrop-blur p-1";

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

function PanelLink({ item, pathname, onSelect }: { item: NavLink; pathname: string; onSelect: () => void }) {
  return (
    <Link href={item.href} onClick={onSelect} className={linkClass(pathname === item.href, "w-full justify-start")}>
      {item.label}
    </Link>
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
      <button type="button" onClick={onToggle} aria-expanded={isOpen} className={linkClass(active)}>
        {label}
        <ChevronIcon open={isOpen} />
      </button>
      {isOpen && (
        <div className={`absolute left-0 top-full z-50 mt-2 min-w-[11rem] ${PANEL}`}>
          {items.map((item) => (
            <PanelLink key={item.href} item={item} pathname={pathname} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
}

export function Nav() {
  const pathname = usePathname();
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const navRef = useRef<HTMLDivElement>(null);

  // Ferme le menu ouvert au clic en dehors — un vrai abonnement à un
  // événement DOM externe, pas une resynchronisation d'état dérivé.
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setOpenGroup(null);
        setMobileOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const closeAll = () => {
    setOpenGroup(null);
    setMobileOpen(false);
  };

  return (
    <div className="sticky top-3 z-40 mt-3 px-[var(--gutter)]">
      <nav
        ref={navRef}
        className="relative mx-auto flex max-w-[var(--maxw)] items-center gap-2 rounded-[10px] min-[760px]:gap-4 border border-line-2 bg-ink-2/85 p-2 pl-4 backdrop-blur"
      >
        <Link
          href="/"
          className="flex shrink-0 items-center gap-2 font-mono text-[14px] font-semibold tracking-[0.08em] text-text"
        >
          <span
            aria-hidden
            className="h-3.5 w-3.5 bg-signal [clip-path:polygon(0_100%,30%_0,50%_60%,70%_0,100%_100%,80%_100%,70%_45%,50%_100%,30%_45%,20%_100%)]"
          />
          YGO META
        </Link>

        {/* Pas d'overflow-x-auto ici : `overflow-x` sans `overflow-y` explicite
            fait passer ce dernier à `auto`, ce qui coupe verticalement les
            menus déroulants (même piège que InfoTooltip, voir context.md). */}
        <div className="hidden items-center gap-1 min-[760px]:flex">
          {NAV_ENTRIES.map((entry) =>
            entry.kind === "link" ? (
              <Link
                key={entry.href}
                href={entry.href}
                onClick={closeAll}
                className={linkClass(pathname === entry.href, "shrink-0")}
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
                onSelect={closeAll}
              />
            )
          )}
        </div>

        <SmartSearch />

        {/* Sous 760 px, les liens passent dans un menu : la spec les masque
            sans alternative, ce qui rendrait la navigation impossible. */}
        <button
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-expanded={mobileOpen}
          className={controlClass({ size: "sm", className: "shrink-0 font-mono text-[12px] min-[760px]:hidden" })}
        >
          Menu
        </button>
        {mobileOpen && (
          <div className={`absolute inset-x-0 top-full mt-2 min-[760px]:hidden ${PANEL}`}>
            {NAV_ENTRIES.flatMap((entry) => (entry.kind === "link" ? [entry] : entry.items)).map((item) => (
              <PanelLink key={item.href} item={item} pathname={pathname} onSelect={closeAll} />
            ))}
          </div>
        )}
      </nav>
    </div>
  );
}
