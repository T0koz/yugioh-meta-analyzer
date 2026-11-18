import { fmtDate, fmtNum } from "@/lib/format";
import type { EarlySignalsResponse } from "@/types";

// Phrase sur le terme « proximité de texte » des signaux précoces (audit de rigueur, A1), construite
// à partir de la réponse de l'API : au lot 20, ce terme vaut 0 pour toutes les cartes retenues.
export function earlyTextNote(r: EarlySignalsResponse): string | null {
  if (r.text_signal_cards == null || r.cards_scored == null) return null;
  const lead = r.as_of ? `Avec les decks relevés jusqu’au ${fmtDate(r.as_of)}, la` : "La";
  return r.text_signal_cards === 0
    ? `${lead} proximité de texte vaut 0 pour les ${fmtNum(r.cards_scored)} cartes notées : aucune n’atteint le seuil de similarité avec les cartes des archétypes de la méta. La note ne repose alors que sur les vues et le poids de l’archétype en OCG.`
    : `${lead} proximité de texte est positive pour ${fmtNum(r.text_signal_cards)} cartes sur ${fmtNum(r.cards_scored)}.`;
}
