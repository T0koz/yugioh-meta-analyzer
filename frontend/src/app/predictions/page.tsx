import { api } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import type { Trend } from "@/types";

const TREND_ICON: Record<Trend, string> = { Rising: "↑", Stable: "→", Declining: "↓" };
const TREND_COLOR: Record<Trend, string> = {
  Rising: "text-green-500",
  Stable: "text-slate-400",
  Declining: "text-red-400",
};

function Delta({ current, predicted }: { current: number; predicted: number }) {
  const delta = predicted - current;
  const sign = delta > 0 ? "+" : "";
  const color = delta > 0 ? "text-green-500" : delta < 0 ? "text-red-400" : "text-slate-400";
  return (
    <span className={`tabular-nums text-sm font-semibold ${color}`}>
      {sign}{(delta * 100).toFixed(1)}
    </span>
  );
}

function ScoreCell({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="tabular-nums text-sm">{(value * 100).toFixed(1)}</span>
    </div>
  );
}

export default async function PredictionsPage() {
  const { data, model } = await api.predictions();

  // Même échelle réduite que meta_score en tier-list : normalisation relative au max affiché.
  const maxScore = Math.max(...data.flatMap((d) => [d.current, d.predicted]), 0);

  return (
    <main className="max-w-4xl mx-auto px-6 py-10 w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Prédictions</h1>
        <p className="text-slate-400 mt-1 text-sm">Modèle : {model}</p>
      </div>

      <div className="rounded-lg border border-slate-800 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-slate-400 w-[200px]">Archétype</TableHead>
              <TableHead className="text-slate-400">Score actuel</TableHead>
              <TableHead className="text-slate-400">
                Score prédit
                <InfoTooltip text="Blend 70% naïf (pas de changement) + 30% Ridge(α=50, delta mensuel). Walk-forward CV, Spearman ρ≈+0.65 sur la méta 2026 (très 'sticky')." />
              </TableHead>
              <TableHead className="text-slate-400">Δ</TableHead>
              <TableHead className="text-slate-400">Direction</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data
              .sort((a, b) => b.predicted - a.predicted)
              .map((entry) => (
                <TableRow key={entry.archetype} className="border-slate-800 hover:bg-slate-900">
                  <TableCell className="font-medium">{entry.archetype}</TableCell>
                  <TableCell><ScoreCell value={entry.current} max={maxScore} /></TableCell>
                  <TableCell><ScoreCell value={entry.predicted} max={maxScore} /></TableCell>
                  <TableCell><Delta current={entry.current} predicted={entry.predicted} /></TableCell>
                  <TableCell>
                    <span className={`font-semibold ${TREND_COLOR[entry.direction]}`}>
                      {TREND_ICON[entry.direction]} {entry.direction}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </div>
    </main>
  );
}
