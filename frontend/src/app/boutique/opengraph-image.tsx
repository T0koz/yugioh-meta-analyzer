import { OG_CONTENT_TYPE, OG_SIZE, ogImage, sourceLine } from "@/lib/og";

export const alt = "Signaux boutique · YGO Meta. Archétypes joués en OCG, pas encore sortis en TCG.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Boutique · OCG vers TCG",
    title: "Signaux boutique",
    footer: sourceLine("Archétypes joués en OCG, pas encore sortis en TCG"),
  });
}
