import { fmtNum } from "@/lib/format";
import { OG_CONTENT_TYPE, OG_SIZE, ogImage } from "@/lib/og";
import { SITE_FACTS } from "@/lib/site-facts";
import { DECK_SOURCE } from "@/lib/site";

// Image de partage de l'accueil, et image par défaut de toute route qui n'a pas la sienne.
// Chiffres de lib/site-facts.ts, avec leur période et leur source (comme sur l'accueil).
const R = fmtNum(SITE_FACTS.ocgTcgCorrelation, 2);
const CI = `${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[0], 2)} à ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[1], 2)}`;
const LEGEND = [
  `Corrélation OCG, TCG ${SITE_FACTS.ocgTcgLagRange} plus tard`,
  `IC 95 % : ${CI} · ${SITE_FACTS.ocgTcgArchetypes} archétypes`,
];
const FOOTER = [
  `${fmtNum(SITE_FACTS.decklists)} decklists de tournoi, mai 2023 à novembre 2026`,
  `Source : ${DECK_SOURCE}`,
];

export const alt = `YGO Meta. La méta OCG précède la méta TCG de ${SITE_FACTS.ocgTcgLagRange} : r = ${R}, ${LEGEND[1]}. ${FOOTER[0]}, ${DECK_SOURCE}.`;
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default function Image() {
  return ogImage({
    eyebrow: "Méta Yu-Gi-Oh! · TCG et OCG",
    title: `La méta OCG précède la méta TCG de ${SITE_FACTS.ocgTcgLagRange}`,
    emphasis: SITE_FACTS.ocgTcgLagRange,
    figure: { value: `r = ${R}`, legend: LEGEND },
    footer: FOOTER,
  });
}
