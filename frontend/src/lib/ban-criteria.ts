import type { BanRadarCriteria } from "@/types";

// Ordre et libellés de la barre de décomposition, alignés sur WEIGHTS côté API.
// Une teinte de la palette catégorielle par critère (design system §4 bis) : ordre fixe,
// « restriction » porte l'or, voisin du jaune des statuts de banlist.
export const CRITERIA: { key: keyof BanRadarCriteria; label: string; color: string; help: string }[] = [
  { key: "ubiquity", label: "Ubiquité", color: "var(--cat-1)", help: "Part des decks du format qui jouent la carte." },
  { key: "carrier", label: "Porteur", color: "var(--cat-2)", help: "La carte est indispensable à un archétype qui pèse dans la méta." },
  { key: "copies", label: "Copies", color: "var(--cat-3)", help: "Nombre moyen d'exemplaires joués : une carte jouée à 3 peut être limitée, une carte déjà à 1 beaucoup moins." },
  { key: "restriction", label: "Restriction", color: "var(--cat-4)", help: "La carte est déjà limitée ou semi-limitée : Konami y revient souvent." },
  { key: "momentum", label: "Élan", color: "var(--cat-5)", help: "Usage des 3 derniers mois comparé aux 3 précédents." },
  { key: "bridge", label: "Pont", color: "var(--cat-6)", help: "Centralité de type pont : la carte relie des paquets de cartes autrement séparés." },
];
