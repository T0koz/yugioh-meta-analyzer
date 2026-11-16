import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Méthode · YGO Meta. Sources, seuils et résultats des validations de chaque outil, échecs compris.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Méthode",
    title: "Sources, seuils et validations",
    footer: sourceLine("Résultats des validations de chaque outil, échecs compris"),
  });
}
