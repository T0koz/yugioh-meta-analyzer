"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SmartSearch } from "@/components/smart-search";

const NAV_ITEMS = [
  { href: "/tier-list", label: "Tier List" },
  { href: "/evolution", label: "Évolution" },
  { href: "/predictions", label: "Prédictions" },
  { href: "/boutique", label: "Signaux Boutique" },
  { href: "/early-signals", label: "Early Signals" },
  { href: "/graph", label: "Graphe" },
  { href: "/ban-simulator", label: "Simulateur Ban" },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <nav className="border-b border-slate-800 bg-slate-950 px-6 py-3">
      <div className="max-w-6xl mx-auto flex flex-wrap items-center gap-x-6 gap-y-2">
        <span className="text-indigo-400 font-bold text-sm shrink-0">⚔ YGO Meta</span>
        <div className="flex items-center gap-6 overflow-x-auto">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`text-sm shrink-0 transition-colors ${
                pathname === item.href
                  ? "text-white font-semibold"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
        <SmartSearch />
      </div>
    </nav>
  );
}
