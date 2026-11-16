import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Signaux précoces · YGO Meta. Vues hebdomadaires et co-occurrences en decks de tournoi.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Boutique · Cartes récentes",
    title: "Signaux précoces",
    footer: sourceLine("Vues hebdomadaires et co-occurrences en decks de tournoi"),
  });
}
