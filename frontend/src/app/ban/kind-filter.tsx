import { PillLink } from "@/components/ds/control";
import { Toolbar } from "@/components/ds/page";
import type { BanRadarKind } from "@/types";

/** Vue du filtre : un `kind` de l'API, ou `all` (aucun filtre). */
export type KindView = BanRadarKind | "all";

// Partagé entre BanRadarView et CardDiffusionView : les deux notent les cartes
// sur les mêmes critères et proposent le même filtre archétype/générique.
const KIND_FILTERS: Record<KindView, { label: string; hint: string }> = {
  archetype: { label: "Pièces d'archétype", hint: "Au moins la moitié des decks qui la jouent sont d’un même archétype" },
  generic: { label: "Staples génériques", hint: "Moins de la moitié des decks qui la jouent sont d’un même archétype" },
  all: { label: "Tout", hint: "Toutes les cartes notées" },
};

/**
 * Vue par défaut de chaque onglet, placée en premier dans la barre.
 * Radar : les pièces d'archétype (décision 4 de l'audit front). Konami frappe
 * les pièces de moteur, pas les staples jouées partout ; ouvrir sur « Tout »
 * mettait Ash Blossom à 100/100 en tête de page.
 * Diffusion : tout, puisque la mesure compte justement les archétypes qui jouent la carte.
 */
export const KIND_ORDER = {
  radar: ["archetype", "generic", "all"],
  diffusion: ["all", "archetype", "generic"],
} as const satisfies Record<string, readonly KindView[]>;

export type KindTab = keyof typeof KIND_ORDER;

export function parseKind(raw: string | string[] | undefined, tab: KindTab): KindView {
  return typeof raw === "string" && raw in KIND_FILTERS ? (raw as KindView) : KIND_ORDER[tab][0];
}

/** Paramètre `kind` attendu par l'API : absent pour la vue « Tout ». */
export function apiKind(view: KindView): BanRadarKind | undefined {
  return view === "all" ? undefined : view;
}

export function KindFilterTabs({ tab, active, count }: { tab: KindTab; active: KindView; count?: string }) {
  const basePath = `/ban?tab=${tab}`;
  const [defaultView] = KIND_ORDER[tab];
  return (
    <Toolbar count={count}>
      {KIND_ORDER[tab].map((view) => {
        const { label, hint } = KIND_FILTERS[view];
        const selected = view === active;
        return (
          <PillLink
            key={view}
            // La vue par défaut garde l'URL courte : une seule adresse par contenu.
            href={view === defaultView ? basePath : `${basePath}&kind=${view}`}
            title={hint}
            current={selected}
          >
            {label}
          </PillLink>
        );
      })}
    </Toolbar>
  );
}
