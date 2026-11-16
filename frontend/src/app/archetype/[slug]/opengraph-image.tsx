import { api } from "@/lib/api";
import { fmtDate, fmtMonthRange, fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import { OG_CONTENT_TYPE, OG_SIZE, type OgSpec, ogImage, sourceLine } from "@/lib/og";
import { DECK_SOURCE } from "@/lib/site";

// Image de partage d'un archétype : nom, part de decks avec sa fenêtre, part mensuelle.
// Mêmes chiffres que la page (GET /archetypes/{slug}) ; aucune illustration de carte.
export const alt = "Archétype Yu-Gi-Oh! : part des decks de tournoi, fenêtre de mesure et source.";
export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const a = await api.archetype(slug);
  if (!a) {
    return ogImage({ eyebrow: "Archétype", title: "Archétype introuvable", footer: sourceLine("Decklists de tournoi") });
  }

  const spec: OgSpec = { eyebrow: "Archétype", title: a.archetype, footer: sourceLine("Decklists de tournoi TCG") };
  if (a.tcg && a.tcg_window) {
    spec.eyebrow = `Archétype · TCG · tier ${a.tcg.tier}`;
    spec.figure = {
      value: fmtPct(a.tcg.share * 100),
      legend: [
        "des decks de tournoi TCG",
        `${fmtNum(a.tcg.decks)} sur ${fmtNum(a.tcg_window.n_decks)} · ${fmtMonthRange(a.tcg_window.start, a.tcg_window.end)}`,
      ],
    };
  } else if (a.ocg) {
    spec.eyebrow = "Archétype · OCG";
    spec.figure = {
      value: fmtPct(a.ocg.share * 100),
      legend: [
        "des decks de tournoi OCG",
        `${fmtNum(a.ocg.decks)} decks${a.ocg.computed_at ? ` · calcul du ${fmtDate(a.ocg.computed_at)}` : ""}`,
      ],
    };
    spec.footer = ["Aucun deck TCG dans la fenêtre courante", `Source : ${DECK_SOURCE}`];
  }
  const played = a.history.filter((h) => h.total_decks > 0);
  if (played.some((h) => h.decks > 0)) {
    spec.series = {
      values: played.map((h) => h.share),
      caption: `Part mensuelle TCG, ${fmtMonthShort(played[0].month)} à ${fmtMonthShort(played[played.length - 1].month)}`,
    };
  }
  return ogImage(spec);
}
