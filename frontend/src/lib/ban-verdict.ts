import { SITE_FACTS } from "@/lib/site-facts";

// Verdict du Ban Radar contre l'historique (diagnostic TOK-115, formulaire validé par Thomas le
// 17/11, point 5), écrit avec les chiffres figés de SITE_FACTS.banTop25 (backtest du 16/11/2026).
// Une phrase qualitative (« plus », « moins bien ») ne se recalcule pas seule : si les listes
// servies ne donnent plus les mêmes sommes, `verdictMatches` est faux et le verdict n'est pas
// affiché (onglet Historique) ; il faut alors relancer le diagnostic et réécrire ce texte.
const [TCG, OCG] = SITE_FACTS.banTop25;

export const BAN_VERDICT = {
  measures: `Sur les ${TCG.lists} banlists TCG ${TCG.periodFrom}, le Ban Radar place plus de cartes touchées dans son top 25 que le classement par part des decks (${TCG.radar} contre ${TCG.staples}), mais situe moins bien l’ensemble des cartes touchées (rang médian meilleur sur ${TCG.medianBetter} listes sur ${TCG.lists}). En OCG, il fait mieux sur les deux mesures (${OCG.radar} contre ${OCG.staples} ; ${OCG.medianBetter} listes sur ${OCG.lists}).`,
  significance: `Avec ${TCG.lists} listes par format, seul l’écart de top 25 en OCG dépasse ce que le hasard produit couramment.`,
};

/** Sommes par format calculées sur les listes servies, comparées aux chiffres figés du verdict. */
export function verdictMatches(
  rows: { format: string; n: number; staples: number; topHits: number; baselineTopHits: number }[],
): boolean {
  return SITE_FACTS.banTop25.every((fact) => {
    const row = rows.find((r) => r.format === fact.format);
    return (
      row !== undefined &&
      row.n === fact.lists &&
      row.staples === fact.medianBetter &&
      row.topHits === fact.radar &&
      row.baselineTopHits === fact.staples
    );
  });
}
