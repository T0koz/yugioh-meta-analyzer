import type { BanRadarCriteria } from "@/types";

// Ordre et libellés de la barre de décomposition, alignés sur WEIGHTS côté API.
// Une teinte de la palette catégorielle par critère (design system §4 bis) : ordre fixe,
// « restriction » porte l'or, voisin du jaune des statuts de banlist.
export const CRITERIA: { key: keyof BanRadarCriteria; label: string; color: string; help: string }[] = [
  { key: "ubiquity", label: "Part des decks", color: "var(--cat-1)", help: "Part des decks du format qui jouent la carte." },
  { key: "carrier", label: "Porteur", color: "var(--cat-2)", help: "La carte est jouée par la plupart des decks d’un archétype qui pèse dans la méta." },
  { key: "copies", label: "Exemplaires", color: "var(--cat-3)", help: "Nombre moyen d’exemplaires joués par deck (1 à 3)." },
  { key: "restriction", label: "Restriction", color: "var(--cat-4)", help: "La carte est déjà limitée ou semi-limitée." },
  { key: "momentum", label: "Élan", color: "var(--cat-5)", help: "Usage des 3 derniers mois comparé aux 3 précédents." },
  { key: "bridge", label: "Pont", color: "var(--cat-6)", help: "La carte relie des groupes de cartes qui, sans elle, se jouent rarement ensemble." },
];
