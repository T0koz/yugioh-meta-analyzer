import Link from "next/link";
import type { BanRadarKind } from "@/types";

// Partagé entre BanRadarView et CardImpactView : les deux notent les cartes
// sur les mêmes critères et proposent le même filtre archétype/générique.
export const KIND_FILTERS: { kind?: BanRadarKind; label: string; hint: string }[] = [
  { label: "Tout", hint: "Toutes les cartes notées" },
  { kind: "archetype", label: "Pièces d'archétype", hint: "Cartes rattachées à un deck précis" },
  { kind: "generic", label: "Staples génériques", hint: "Cartes jouées un peu partout" },
];

export function parseKind(raw: string | string[] | undefined): BanRadarKind | undefined {
  return KIND_FILTERS.some((f) => f.kind === raw) ? (raw as BanRadarKind) : undefined;
}

export function KindFilterTabs({ basePath, active }: { basePath: string; active?: BanRadarKind }) {
  return (
    <div className="mb-6 flex flex-wrap gap-2">
      {KIND_FILTERS.map(({ kind, label, hint }) => {
        const selected = kind === active;
        return (
          <Link
            key={label}
            href={kind ? `${basePath}&kind=${kind}` : basePath}
            title={hint}
            aria-current={selected ? "page" : undefined}
            className={`rounded-md border px-3 py-1.5 text-sm transition-colors ${
              selected
                ? "border-indigo-500 bg-indigo-600/20 font-semibold text-indigo-300"
                : "border-slate-700 text-slate-400 hover:border-slate-600 hover:text-slate-200"
            }`}
          >
            {label}
          </Link>
        );
      })}
    </div>
  );
}
