import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Prédictions de méta · YGO Meta. Score méta prévu à un mois, modèle 70 % naïf + 30 % Ridge.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Méta · TCG",
    title: "Prédictions de méta",
    footer: sourceLine("Score méta prévu à un mois, modèle 70 % naïf + 30 % Ridge"),
  });
}
