import { api } from "@/lib/api";
import { CardChip } from "@/components/card-chip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";

function ScoreRing({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const radius = 22;
  const circ = 2 * Math.PI * radius;
  const dash = (pct / 100) * circ;
  const color = pct >= 80 ? "#22c55e" : pct >= 60 ? "#eab308" : "#64748b";

  return (
    <div className="relative w-14 h-14 flex items-center justify-center">
      <svg width="56" height="56" className="-rotate-90">
        <circle cx="28" cy="28" r={radius} fill="none" stroke="#1e293b" strokeWidth="4" />
        <circle
          cx="28" cy="28" r={radius} fill="none"
          stroke={color} strokeWidth="4"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
        />
      </svg>
      <span className="absolute text-xs font-bold tabular-nums" style={{ color }}>
        {pct}
      </span>
    </div>
  );
}

export default async function EarlySignalsPage() {
  const { data } = await api.earlySignals();

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <main className="max-w-4xl mx-auto px-6 py-10 w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Early Signals</h1>
        <p className="text-slate-400 mt-1 text-sm">
          Nouvelles cartes entrant dans la méta · Score basé sur views, co-occurrence et tier
        </p>
      </div>

      <div className="grid gap-4">
        {data.map((signal) => (
          <div
            key={signal.card_name}
            className="flex items-center gap-5 rounded-lg border border-slate-800 bg-slate-900 px-5 py-4"
          >
            <ScoreRing value={signal.early_score} />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-base">
                <CardChip name={signal.card_name} subtitle={signal.archetype} />
              </p>
              <p className="text-slate-400 text-sm mt-1">{signal.archetype}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="text-sm text-slate-400">Views / semaine</p>
              <p className="font-bold tabular-nums text-indigo-400">
                {signal.views_week.toLocaleString("fr-FR")}
              </p>
            </div>
          </div>
        ))}
      </div>
      </main>
    </HoverPreviewProvider>
  );
}
