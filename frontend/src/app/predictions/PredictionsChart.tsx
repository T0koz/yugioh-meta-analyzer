import { max } from "d3-array";
import { scaleLinear } from "d3-scale";
import { CardArt } from "@/components/card-art";
import { TrendLabel } from "@/components/ds/tags";
import { fmtNum, fmtSigned } from "@/lib/format";
import type { PredictionEntry } from "@/types";

// Haltères (TOK-99) : un anneau pour le score observé, un point plein pour le
// score prévu, reliés par un trait. L'écart, souvent plus petit qu'un point de
// score, a sa propre colonne et sa propre échelle. Rendu côté serveur, sans
// JavaScript : D3 ne calcule que des positions en pourcentage de la largeur.

// Colonnes : archétype · haltère · écart · direction. Sous 1000 px, l'haltère passe
// sous le nom, l'écart reste à droite.
const GRID =
  "grid grid-cols-[minmax(0,1fr)_112px] items-center gap-x-3 px-3 min-[1000px]:grid-cols-[minmax(0,230px)_minmax(0,1fr)_150px_92px] min-[1000px]:gap-x-5 min-[1000px]:px-4";
const HEAD = "font-mono text-[11px] tracking-[0.08em] text-muted-text uppercase";
const pct = (value: number) => `${value.toFixed(2)}%`;

export function PredictionsChart({
  rows,
  observedLabel,
  targetLabel,
}: {
  rows: PredictionEntry[];
  observedLabel: string;
  targetLabel: string;
}) {
  // meta_score plafonne vers 0,15 : l'échelle part de zéro et s'arrête au maximum affiché.
  const top = (max(rows, (r) => Math.max(r.current, r.predicted)) ?? 0) * 100;
  const x = scaleLinear().domain([0, top || 1]).nice(4).range([1.5, 98.5]);
  const ticks = x.ticks(4);
  const topDelta = (max(rows, (r) => Math.abs(r.predicted - r.current)) ?? 0) * 100;
  // Écart : zéro au milieu, baisses à gauche, hausses à droite.
  const dx = scaleLinear().domain([-(topDelta || 1), topDelta || 1]).range([2, 98]);

  return (
    <div className="overflow-hidden rounded-[6px] border border-line">
      <p className="flex flex-wrap items-center gap-x-5 gap-y-1 border-b border-line px-3 py-2.5 font-mono text-[12px] text-muted-text min-[1000px]:px-4">
        <span className="inline-flex items-center gap-1.5">
          <svg aria-hidden width="10" height="10" className="shrink-0">
            <circle cx="5" cy="5" r="3.5" fill="var(--ink)" stroke="var(--soft)" strokeWidth="1.5" />
          </svg>
          observé {observedLabel}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <svg aria-hidden width="10" height="10" className="shrink-0">
            <circle cx="5" cy="5" r="4.5" fill="var(--text)" />
          </svg>
          prévu {targetLabel}
        </span>
      </p>
      <div className={`${GRID} border-b border-line py-2.5 ${HEAD}`}>
        <span>Archétype</span>
        <span className="hidden min-[1000px]:block">Score méta ×100</span>
        <span className="text-right">Écart (points)</span>
        <span className="hidden text-right min-[1000px]:block">Direction</span>
      </div>

      {/* Graduation commune à toutes les lignes. */}
      <div className={`${GRID} py-1`} aria-hidden>
        <span className="font-mono text-[12px] text-muted-text min-[1000px]:invisible">score ×100</span>
        <svg width="100%" height="14" className="col-span-2 row-start-2 min-[1000px]:col-span-1 min-[1000px]:row-start-auto">
          {ticks.map((tick) => (
            <text
              key={tick}
              x={pct(x(tick))}
              y="11"
              textAnchor={tick === 0 ? "start" : tick === ticks[ticks.length - 1] ? "end" : "middle"}
              fill="var(--muted-text)"
              className="font-mono text-[12px]"
            >
              {tick}
            </text>
          ))}
        </svg>
        <span className="flex gap-2.5 font-mono text-[12px] text-muted-text">
          <span className="flex-1 text-center">− 0 +</span>
          <span className="w-11 shrink-0" />
        </span>
      </div>

      <ol>
        {rows.map((row, index) => {
          const current = row.current * 100;
          const predicted = row.predicted * 100;
          const delta = predicted - current;
          const up = delta > 0;
          const tone = up ? "var(--good)" : "var(--muted-text)";
          const zero = dx(0);
          const end = dx(delta);
          return (
            <li
              key={row.archetype}
              className={`${GRID} border-t border-line py-2.5 transition-colors duration-200 hover:bg-ink-3`}
              title={`${row.archetype} : ${fmtNum(current, 1)} observé en ${observedLabel}, ${fmtNum(predicted, 1)} prévu pour ${targetLabel}`}
            >
              <span className="flex min-w-0 items-center gap-3 font-medium tracking-[-0.01em]">
                <CardArt src={row.image_url} name={row.archetype} eager={index < 8} />
                <span className="min-w-0">
                  <span className="block truncate">{row.archetype}</span>
                  <span className="block font-mono text-[12px] font-normal text-muted-text tabular-nums">
                    {fmtNum(current, 1)} → {fmtNum(predicted, 1)}
                  </span>
                  <span className="block min-[1000px]:hidden">
                    <TrendLabel trend={row.direction} />
                  </span>
                </span>
              </span>

              <svg
                width="100%"
                height="24"
                role="img"
                aria-label={`${row.archetype} : ${fmtNum(current, 1)} observé, ${fmtNum(predicted, 1)} prévu`}
                className="col-span-2 row-start-2 mt-1.5 min-[1000px]:col-span-1 min-[1000px]:row-start-auto min-[1000px]:mt-0"
              >
                {ticks.map((tick) => (
                  <line key={tick} x1={pct(x(tick))} x2={pct(x(tick))} y1="0" y2="24" stroke="var(--line)" />
                ))}
                <line x1={pct(x(current))} x2={pct(x(predicted))} y1="12" y2="12" stroke={tone} strokeWidth="2" />
                <circle cx={pct(x(current))} cy="12" r="4" fill="var(--ink)" stroke="var(--soft)" strokeWidth="1.5" />
                <circle cx={pct(x(predicted))} cy="12" r="4.5" fill="var(--text)" stroke="var(--ink)" strokeWidth="1" />
              </svg>

              <span className="flex items-center justify-end gap-2.5">
                <svg aria-hidden width="100%" height="24" className="min-w-0 flex-1">
                  <line x1={pct(zero)} x2={pct(zero)} y1="3" y2="21" stroke="var(--line-2)" />
                  <rect
                    x={pct(Math.min(zero, end))}
                    width={pct(Math.max(Math.abs(end - zero), 0.8))}
                    y="9"
                    height="6"
                    rx="1"
                    fill={tone}
                  />
                </svg>
                <span
                  className={`w-11 shrink-0 text-right font-mono text-[13px] font-medium tabular-nums ${up ? "text-good" : "text-muted-text"}`}
                >
                  {fmtSigned(delta)}
                </span>
              </span>

              <span className="hidden text-right min-[1000px]:block">
                <TrendLabel trend={row.direction} />
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
