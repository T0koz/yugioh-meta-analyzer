import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Decks TCG · YGO Meta. Composition par archétype : part des listes de tournoi qui jouent chaque carte.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Decks · TCG",
    title: "Composition des decks",
    footer: sourceLine("Part des listes de tournoi TCG qui jouent chaque carte, par archétype"),
  });
}
