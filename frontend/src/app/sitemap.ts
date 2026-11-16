import type { MetadataRoute } from "next";
import { api } from "@/lib/api";
import { absoluteUrl } from "@/lib/site";

// Adresses canoniques uniquement (les mêmes que `alternates.canonical` de chaque page).
// Les onglets du Ban Center ont un contenu propre : une entrée chacun.
const STATIC_PATHS = [
  "/",
  "/tier-list",
  "/decks",
  "/evolution",
  "/predictions",
  "/boutique",
  "/early-signals",
  "/graph",
  "/ban",
  "/ban?tab=historique",
  "/ban?tab=impact",
  "/ban?tab=simulateur",
];

// Pages d'archétype : celles de la tier list courante et des signaux boutique, avec le
// slug servi par l'API (même ensemble que `generateStaticParams`). Pas de `lastModified` :
// l'API ne sert pas de date commune à toutes les pages, et une date fausse vaut moins qu'aucune.
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [tierList, boutique, decks] = await Promise.all([api.tierList(), api.boutiqueSignals(), api.decks()]);
  const slugs = new Set([...tierList.data.map((e) => e.slug), ...boutique.data.map((s) => s.archetype_slug)]);
  return [
    ...STATIC_PATHS.map((path) => ({ url: absoluteUrl(path) })),
    ...[...slugs].sort().map((slug) => ({ url: absoluteUrl(`/archetype/${slug}`) })),
    // Fiches de composition : seulement les archétypes au-dessus de l'effectif minimal (TOK-114).
    ...decks.data
      .filter((d) => d.has_profile)
      .map((d) => d.slug)
      .sort()
      .map((slug) => ({ url: absoluteUrl(`/decks/${slug}`) })),
  ];
}
