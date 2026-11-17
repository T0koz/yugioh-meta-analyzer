import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Évolution de la méta · YGO Meta. Part mensuelle des decks par archétype, decklists de tournoi TCG.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Méta · TCG",
    title: "Évolution de la méta",
    footer: sourceLine("Part mensuelle des decks par archétype, decklists de tournoi TCG"),
  });
}
