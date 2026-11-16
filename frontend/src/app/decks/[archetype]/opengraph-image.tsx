import { api } from "@/lib/api";
import { fmtNum, fmtWindow } from "@/lib/format";
import { OG_CONTENT_TYPE, OG_SIZE, type OgSpec, ogImage, sourceLine } from "@/lib/og";

// Image de partage d'une fiche de deck : nom, nombre de listes avec sa fenêtre.
// Mêmes chiffres que la page (GET /decks/{slug}) ; aucune illustration de carte.
export const alt = "Deck Yu-Gi-Oh! TCG : nombre de listes de tournoi relevées, fenêtre de mesure et source.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default async function Image({ params }: { params: Promise<{ archetype: string }> }) {
  const { archetype } = await params;
  const d = await api.deck(archetype);
  if (!d) {
    return ogImage({ eyebrow: "Deck", title: "Deck introuvable", footer: sourceLine("Decklists de tournoi TCG") });
  }
  const spec: OgSpec = {
    eyebrow: d.tier ? `Deck · TCG · tier ${d.tier}` : "Deck · TCG",
    title: d.archetype,
    figure: {
      value: fmtNum(d.decks),
      legend: [
        d.decks > 1 ? "listes de tournoi TCG" : "liste de tournoi TCG",
        `sur ${fmtNum(d.window.n_decks)} decks · ${fmtWindow(d.window)}`,
      ],
    },
    footer: sourceLine(
      d.has_profile
        ? "Part des listes qui jouent chaque carte, exemplaires médians"
        : `Moins de ${d.rule.min_decks} listes : contenu des listes relevées`
    ),
  };
  return ogImage(spec);
}
