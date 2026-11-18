import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Signaux précoces · YGO Meta. Vues hebdomadaires, proximité de texte et poids de l’archétype en OCG.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Boutique · Cartes récentes",
    title: "Signaux précoces",
    footer: sourceLine("Vues hebdomadaires, proximité de texte, poids de l’archétype en OCG"),
  });
}
