import { api } from "@/lib/api";
import { fmtNum, fmtSigned } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { Em } from "@/components/ds/em";
import { Meter, Page, PageHero } from "@/components/ds/page";
import { TrendLabel } from "@/components/ds/tags";

// Une hausse en --good, une baisse en gris : le rouge reste réservé à l'accent.
function Delta({ current, predicted }: { current: number; predicted: number }) {
  const delta = (predicted - current) * 100;
  const tone = delta > 0 ? "text-good" : "text-muted-text";
  return <span className={`font-mono text-[13px] font-medium tabular-nums ${tone}`}>{fmtSigned(delta)}</span>;
}

function ScoreCell({ value, max, tone }: { value: number; max: number; tone: "signal" | "soft" }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-24">
        <Meter value={value} max={max} tone={tone} />
      </div>
      <span className="w-9 text-right font-mono text-[13px] tabular-nums">{fmtNum(value * 100, 1)}</span>
    </div>
  );
}

export default async function PredictionsPage() {
  const { data } = await api.predictions();

  // Même échelle réduite que meta_score en tier-list : normalisation relative au max affiché.
  const maxScore = Math.max(...data.flatMap((d) => [d.current, d.predicted]), 0);
  const rows = [...data].sort((a, b) => b.predicted - a.predicted);

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
            Score méta actuel et prévu pour chaque archétype (×100). Modèle : blend 70 % naïf + 30 % Ridge. Il prolonge surtout la tendance et ramène vers la moyenne : il n’anticipe ni les ruptures ni l’arrivée d’un nouvel archétype.
            <InfoTooltip text="Blend 70 % naïf (pas de changement) + 30 % Ridge (α = 50, delta mensuel). Validation walk-forward : l’erreur sur la variation mensuelle baisse d’environ 5 % par rapport à « rien ne change », autant qu’une régression à une variable (retour à la moyenne)." />
          </>
        }
      />

      <div className="overflow-hidden rounded-[6px] border border-line">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Archétype</TableHead>
              <TableHead>Actuel</TableHead>
              <TableHead>Prévu</TableHead>
              <TableHead className="text-right">Δ</TableHead>
              <TableHead className="text-right">Direction</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((entry) => (
              <TableRow key={entry.archetype}>
                <TableCell className="font-medium tracking-[-0.01em]">{entry.archetype}</TableCell>
                <TableCell>
                  <ScoreCell value={entry.current} max={maxScore} tone="soft" />
                </TableCell>
                <TableCell>
                  <ScoreCell value={entry.predicted} max={maxScore} tone="signal" />
                </TableCell>
                <TableCell className="text-right">
                  <Delta current={entry.current} predicted={entry.predicted} />
                </TableCell>
                <TableCell className="text-right">
                  <TrendLabel trend={entry.direction} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Page>
  );
}
