import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Graphe de synergies · YGO Meta. Cartes jouées dans les mêmes decks, indice de Jaccard.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Graphe · Co-occurrence",
    title: "Graphe de synergies",
    footer: sourceLine("Cartes jouées dans les mêmes decks, indice de Jaccard"),
  });
}
