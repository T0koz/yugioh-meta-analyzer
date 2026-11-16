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
  const { data, data_month, computed_at } = await api.predictions();
  const rows = [...data].sort((a, b) => b.predicted - a.predicted);
  const observed = data_month ? fmtMonthShort(data_month) : "dernier mois";
  const target = data_month ? fmtMonthShort(nextMonth(data_month)) : "mois suivant";

  return (
    <Page>
      <PageHero
        eyebrow="Méta · Prédictions"
        title={
          <>
            La méta du mois <Em>prochain</Em>.
          </>
        }
        intro={
          <>
            Score méta ×100 de {rows.length} archétypes TCG : observé en {observed}, prévu
            <InfoTooltip
              term="Prévision"
              text="Valeur attendue si la situation récente se prolonge, en ramenant les écarts vers la moyenne."
            />{" "}
            pour {target}. Le modèle n’anticipe ni les ruptures ni l’arrivée d’un nouvel archétype.
          </>
        }
      />

      <PredictionsChart rows={rows} observedLabel={observed} targetLabel={target} />
      <DataFooter
        source="decklists de tournoi TCG, yugiohmeta.com"
        date={`observé ${observed}, calcul du ${computed_at ? fmtDate(computed_at) : "date inconnue"}`}
        sample={`${rows.length} archétypes`}
        uncertainty="aucun intervalle par archétype : le modèle ne produit qu’une valeur ; son erreur moyenne est mesurée sur l’historique (page Méthode)"
      >
        anneau : observé ; point plein : prévu
      </DataFooter>
      <MethodNote anchor="predictions">
        <p>Prévision : surtout la valeur du mois observé, corrigée d’une part de retour à la moyenne.</p>
        <p>Rejouée mois par mois sur l’historique, elle se trompe d’environ 5 % de moins que « rien ne change ».</p>
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
