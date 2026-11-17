import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Ban Center · YGO Meta. Risque de restriction, cartes à impact, simulateur.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Bans · TCG",
    title: "Ban Center",
    footer: sourceLine("Risque de restriction, cartes à impact, simulateur"),
  });
}
