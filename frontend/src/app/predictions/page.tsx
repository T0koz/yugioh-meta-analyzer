import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtDate, fmtMonthShort, fmtNum, fmtSigned } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { controlClass } from "@/components/ds/control";
import { Em } from "@/components/ds/em";
import { DataFooter, Page, PageHero } from "@/components/ds/page";
import { MethodNote } from "@/components/ds/explain";
import { TrendLabel } from "@/components/ds/tags";
import { PredictionsChart } from "./PredictionsChart";

// TOK-131 : intervalles de prévision par archétype, prêts mais non dessinés tant que Thomas n'a pas rendu le
// formulaire (docs/planning/2026-11-18/decisions-prises.md, Jalon 2). Option de build : NEXT_PUBLIC_PREDICTION_INTERVALS=1.
const INTERVALS_ENABLED = process.env.NEXT_PUBLIC_PREDICTION_INTERVALS === "1";
// Couverture observée en validation (scripts/build_prediction_intervals.py, 2026-11-18) : 75,7 % sur 507 prévisions,
// 68,3 % sur les 5 premiers archétypes du mois. À recalculer avant toute mise en ligne.
const INTERVAL_COVERAGE_NOTE =
  "fourchette visée à 80 % ; rejouée sur 24 mois (507 prévisions, novembre 2024 à octobre 2026), elle a contenu la valeur réalisée 3 fois sur 4, 2 fois sur 3 pour les 5 premiers archétypes du mois";

/** « 2026-10 » → « 2026-11 ». */
function nextMonth(yearMonth: string): string {
  const [year, month] = yearMonth.split("-").map(Number);
  return month === 12 ? `${year + 1}-01` : `${year}-${String(month + 1).padStart(2, "0")}`;
}

export async function generateMetadata(): Promise<Metadata> {
  const { data, data_month, computed_at } = await api.predictions();
  const target = data_month ? ` pour ${fmtMonthShort(nextMonth(data_month))}` : "";
  const computed = computed_at ? `, calcul du ${fmtDate(computed_at)}` : "";
  return pageMetadata({
    title: "Prédictions de méta",
    description: `Score méta prévu${target} sur ${data.length} archétypes Yu-Gi-Oh! TCG${computed}. Données : decklists de tournoi, ${DECK_SOURCE}.`,
    path: "/predictions",
  });
}

export default async function PredictionsPage() {
  const { data, data_month, computed_at, direction_threshold, interval_level } = await api.predictions();
  // TOK-131 : intervalles dessinés seulement si l'option est posée ET servis par l'API (formulaire de Thomas).
  const intervalLevel = INTERVALS_ENABLED ? (interval_level ?? null) : null;
  const rows = [...data].sort((a, b) => b.predicted - a.predicted);
  const observed = data_month ? fmtMonthShort(data_month) : "dernier mois";
  const target = data_month ? fmtMonthShort(nextMonth(data_month)) : "mois suivant";
  // Audit de rigueur, A6 : le mois prévu est en général le mois en cours au calcul, déjà en partie relevé
  // (ses decks ne servent pas à la prévision). On le dit quand la date de calcul tombe dans ce mois.
  const partial = Boolean(data_month && computed_at && computed_at.slice(0, 7) === nextMonth(data_month));
  const targetNote = partial ? ", mois en cours au calcul, déjà en partie relevé mais non utilisé" : "";

  return (
    <Page>
      <PageHero
        eyebrow="Méta · Prédictions"
        title={
          <>
            Le score de chaque archétype, <Em>prévu</Em> pour {partial ? "le mois en cours" : "le mois suivant"}.
          </>
        }
        intro={
          <>
            Score méta ×100 de {rows.length} archétypes TCG : observé en {observed}, prévu
            <InfoTooltip
              term="Prévision"
              text="Valeur attendue si la situation récente se prolonge, en ramenant les écarts vers la moyenne."
            />{" "}
            pour {target}
            {targetNote}. Le modèle n’anticipe ni les ruptures ni l’arrivée d’un nouvel archétype.
          </>
        }
      />

      <PredictionsChart rows={rows} observedLabel={observed} targetLabel={target} intervalLevel={intervalLevel} />
      <DataFooter
        source="decklists de tournoi TCG, yugiohmeta.com"
        date={`observé ${observed}, prévu ${target}${partial ? " (mois en cours, partiel)" : ""}, calcul du ${computed_at ? fmtDate(computed_at) : "date inconnue"}`}
        sample={`${rows.length} archétypes`}
        uncertainty={intervalLevel != null ? INTERVAL_COVERAGE_NOTE : "aucun intervalle par archétype : le modèle ne produit qu’une valeur ; son erreur moyenne est mesurée sur l’historique (page Méthode)"}
      >
        anneau : observé ; point plein : prévu
        {direction_threshold != null &&
          ` ; direction : hausse ou baisse quand l’écart dessiné dépasse ${fmtNum(direction_threshold * 100, 1)} point, stable sinon (seuil fixé à la main)`}
      </DataFooter>
      <MethodNote anchor="predictions">
        <p>Prévision : surtout la valeur du mois observé, corrigée d’une part de retour à la moyenne.</p>
        <p>Rejouée mois par mois sur 24 mois, elle se trompe d’environ 6 % de moins que « rien ne change » sur la variation du score. Sur les seuls decks TCG, elle ne classe pas les archétypes mieux que la valeur du mois observé.</p>
      </MethodNote>

      <details className="group mt-5">
        <summary className={controlClass({ size: "sm" })}>
          Tableau des valeurs
          <span aria-hidden className="font-mono text-muted-text transition-transform group-open:rotate-45">
            +
          </span>
        </summary>
        <div className="mt-3 overflow-hidden rounded-[6px] border border-line">
          <Table>
            <caption className="sr-only">
              Score méta ×100 observé en {observed} et prévu pour {target}, par archétype
            </caption>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Archétype</TableHead>
                <TableHead className="text-right">Observé {observed}</TableHead>
                <TableHead className="text-right">Prévu {target}</TableHead>
                <TableHead className="text-right">Écart</TableHead>
                <TableHead className="text-right">Direction</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map((entry) => (
                <TableRow key={entry.archetype}>
                  <TableCell className="font-medium tracking-[-0.01em]">{entry.archetype}</TableCell>
                  <TableCell className="text-right font-mono text-[13px] tabular-nums">{fmtNum(entry.current * 100, 2)}</TableCell>
                  <TableCell className="text-right font-mono text-[13px] tabular-nums">{fmtNum(entry.predicted * 100, 2)}</TableCell>
                  <TableCell className="text-right font-mono text-[13px] tabular-nums">
                    {fmtSigned((entry.predicted - entry.current) * 100, 2)}
                  </TableCell>
                  <TableCell className="text-right">
                    <TrendLabel trend={entry.direction} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </details>
    </Page>
  );
}
