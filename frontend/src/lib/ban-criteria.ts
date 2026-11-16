import type { BanRadarCriteria } from "@/types";

// Ordre et libellés de la barre de décomposition, alignés sur WEIGHTS côté API.
// Une seule teinte : l'opacité décroît avec le poids du critère (design system §4).
export const CRITERIA: { key: keyof BanRadarCriteria; label: string; opacity: number; help: string }[] = [
  { key: "ubiquity", label: "Ubiquité", opacity: 0.9, help: "Part des decks du format qui jouent la carte." },
  { key: "carrier", label: "Porteur", opacity: 0.75, help: "La carte est indispensable à un archétype qui pèse dans la méta." },
  { key: "copies", label: "Copies", opacity: 0.6, help: "Nombre moyen d'exemplaires joués : une carte jouée à 3 peut être limitée, une carte déjà à 1 beaucoup moins." },
  { key: "restriction", label: "Restriction", opacity: 0.45, help: "La carte est déjà limitée ou semi-limitée : Konami y revient souvent." },
  { key: "momentum", label: "Élan", opacity: 0.3, help: "Usage des 3 derniers mois comparé aux 3 précédents." },
  { key: "bridge", label: "Pont", opacity: 0.18, help: "Centralité de type pont : la carte relie des paquets de cartes autrement séparés." },
];
