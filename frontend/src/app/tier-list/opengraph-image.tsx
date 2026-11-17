import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Tier list TCG · YGO Meta. Part de decks par archétype, decklists de tournoi TCG.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Méta · TCG",
    title: "Tier list TCG",
    footer: sourceLine("Part de decks par archétype, decklists de tournoi TCG"),
  });
}
