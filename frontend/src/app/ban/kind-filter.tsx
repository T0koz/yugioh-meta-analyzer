import Link from "next/link";
import { Toolbar, pillClass } from "@/components/ds/page";
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

export function KindFilterTabs({
  basePath,
  active,
  count,
}: {
  basePath: string;
  active?: BanRadarKind;
  count?: string;
}) {
  return (
    <Toolbar count={count}>
      {KIND_FILTERS.map(({ kind, label, hint }) => {
        const selected = kind === active;
        return (
          <Link
            key={label}
            href={kind ? `${basePath}&kind=${kind}` : basePath}
            title={hint}
            aria-current={selected ? "page" : undefined}
            className={pillClass(selected)}
          >
            {label}
          </Link>
        );
      })}
    </Toolbar>
  );
}
