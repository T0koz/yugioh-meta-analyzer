import { max, min, nice } from "d3-array";
import { fmtDate, fmtNum } from "@/lib/format";
import type { CardPriceHistory, PriceGap } from "@/types";

// Courbe de prix Cardmarket d'une carte (TOK-103). Rendu serveur, sans JavaScript.
// Règle de la charte : on ne relie que deux relevés proches (l'API dit lesquels
// ne le sont pas, `gaps`). Une période sans relevé est une bande grise, sans
// trait ni pointillé à travers : rien n'est lissé, interpolé ou comblé.
// Même construction que ShareChart : tracé dans un SVG étiré, textes en HTML
// positionnés en pourcentage (12 px quelle que soit la largeur).

const DAY_MS = 86_400_000;
// Marge horizontale (en % de la largeur) : les points des deux extrémités restent entiers.
const PAD = 3;
const PLOT_H = 84;
const LABEL = "font-mono text-[12px] leading-none text-muted-text tabular-nums";
// Période sans relevé : hachures (lisibles sur toutes les surfaces sombres), jamais un trait.
export const GAP_FILL = "bg-ink-4 bg-[repeating-linear-gradient(135deg,var(--line-2)_0_1px,transparent_1px_6px)]";
const PLOT_BOX = "relative ml-14 mr-1";

export function fmtEuro(value: number): string {
  return `${fmtNum(value, 2)}\u00a0€`;
}

/** « 2026-11-16 » → « 16 nov. » (dates courtes des courbes). */
export function fmtDayShort(iso: string): string {
  const date = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
}

function dayNumber(iso: string): number {
  return Date.parse(`${iso}T00:00:00Z`) / DAY_MS;
}

/** Abscisse (0-100) d'une date sur la période commune à toutes les courbes. */
export function timeScale(periodStart: string, periodEnd: string) {
  const d0 = dayNumber(periodStart);
  const span = Math.max(dayNumber(periodEnd) - d0, 1);
  return (iso: string) => PAD + ((dayNumber(iso) - d0) / span) * (100 - 2 * PAD);
}

/** Premiers du mois compris dans la période, pour l'axe (« juil. », « août »…). */
export function monthTicks(periodStart: string, periodEnd: string): { iso: string; label: string }[] {
  const out = [];
  const [y, m] = periodStart.split("-").map(Number);
  const cursor = new Date(Date.UTC(y, m - 1, 1));
  while (true) {
    cursor.setUTCMonth(cursor.getUTCMonth() + 1);
    const iso = cursor.toISOString().slice(0, 10);
    if (iso > periodEnd) break;
    out.push({ iso, label: cursor.toLocaleDateString("fr-FR", { month: "short", timeZone: "UTC" }) });
  }
  return out;
}

export function MonthAxis({ periodStart, periodEnd, className = "" }: { periodStart: string; periodEnd: string; className?: string }) {
  const x = timeScale(periodStart, periodEnd);
  return (
    <div className={`relative h-4 ${className}`} aria-hidden>
      {monthTicks(periodStart, periodEnd).map((tick) => (
        <span key={tick.iso} className={`absolute top-0 -translate-x-1/2 whitespace-nowrap ${LABEL}`} style={{ left: `${x(tick.iso)}%` }}>
          {tick.label}
        </span>
      ))}
    </div>
  );
}

/** Découpe les relevés en suites reliables : une nouvelle suite commence après chaque trou. */
function runsOf<T extends { date: string }>(points: T[], gaps: PriceGap[]): T[][] {
  const breaks = new Set(gaps.map((g) => g.end));
  const runs: T[][] = [];
  for (const point of points) {
    if (!runs.length || breaks.has(point.date)) runs.push([]);
    runs[runs.length - 1].push(point);
  }
  return runs;
}

export function PriceChart({
  history,
  periodStart,
  periodEnd,
  maxStepDays,
}: {
  history: CardPriceHistory;
  periodStart: string;
  periodEnd: string;
  maxStepDays: number;
}) {
  const { points, gaps, sparse } = history;
  const x = timeScale(periodStart, periodEnd);
  const top = nice(0, max(points, (p) => p.price) ?? 1, 3)[1] || 1;
  const y = (price: number) => 100 - (price / top) * 100;
  const placed = points.map((p) => ({ ...p, x: x(p.date), y: y(p.price) }));
  const runs = sparse ? [] : runsOf(placed, gaps).filter((run) => run.length > 1);
  const first = placed[0];
  const last = placed[placed.length - 1];
  const low = min(points, (p) => p.price) ?? 0;
  const high = max(points, (p) => p.price) ?? 0;

  const description = sparse
    ? `Prix Cardmarket de ${history.card_name} : ${points.length} relevé${points.length > 1 ? "s" : ""} seulement, trop peu pour une courbe. Dernier relevé : ${fmtEuro(last.price)} le ${fmtDate(last.date)}.`
    : `Prix Cardmarket de ${history.card_name} : ${points.length} relevés du ${fmtDate(first.date)} au ${fmtDate(last.date)}, de ${fmtEuro(low)} à ${fmtEuro(high)}. Premier relevé ${fmtEuro(first.price)}, dernier ${fmtEuro(last.price)}. ${gaps.length} période${gaps.length > 1 ? "s" : ""} de plus de ${maxStepDays} jours sans relevé, non reliée${gaps.length > 1 ? "s" : ""}.`;

  return (
    <div>
      <div className={PLOT_BOX} style={{ height: PLOT_H }}>
        {gaps.map((gap) => (
          <div
            key={gap.start}
            aria-hidden
            className={`absolute inset-y-0 ${GAP_FILL}`}
            style={{ left: `${x(gap.start)}%`, width: `${x(gap.end) - x(gap.start)}%` }}
            title={`${gap.days} jours sans relevé`}
          />
        ))}
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full" role="img" aria-label={description}>
          <line x1="0" x2="100" y1="0" y2="0" stroke="var(--line)" vectorEffect="non-scaling-stroke" />
          <line x1="0" x2="100" y1="100" y2="100" stroke="var(--line-2)" vectorEffect="non-scaling-stroke" />
          {runs.map((run) => (
            <path
              key={run[0].date}
              d={run.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(" ")}
              fill="none"
              stroke="var(--cat-2)"
              strokeWidth="2"
              strokeLinejoin="round"
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
            />
          ))}
        </svg>
        {/* Points : SVG non étiré, pour des cercles ronds. Chaque relevé a le sien, isolé ou non. */}
        <svg aria-hidden className="absolute inset-0 h-full w-full overflow-visible">
          {placed.map((p) => (
            <circle key={p.date} cx={`${p.x}%`} cy={`${p.y}%`} r="3" fill="var(--ink-3)" stroke="var(--cat-2)" strokeWidth="1.75">
              <title>{`${fmtDate(p.date)} : ${fmtEuro(p.price)}`}</title>
            </circle>
          ))}
        </svg>
        <span aria-hidden className={`absolute -left-14 top-0 w-12 -translate-y-1/2 text-right whitespace-nowrap ${LABEL}`}>
          {fmtNum(top, top < 1 ? 2 : 0)} €
        </span>
        <span aria-hidden className={`absolute -left-14 bottom-0 w-12 translate-y-1/2 text-right whitespace-nowrap ${LABEL}`}>
          0 €
        </span>
        {sparse && (
          <span className={`absolute inset-x-0 top-1/2 -translate-y-1/2 text-center ${LABEL}`}>
            {points.length} relevé{points.length > 1 ? "s" : ""} : trop peu pour une courbe
          </span>
        )}
      </div>
      <MonthAxis periodStart={periodStart} periodEnd={periodEnd} className="mt-2 ml-14 mr-1" />
    </div>
  );
}

/**
 * Calendrier des relevés, commun à toutes les courbes : un trait par date de relevé,
 * une bande grise et sa durée pour chaque période de plus de `maxStepDays` jours sans relevé.
 */
export function SnapshotStrip({
  dates,
  periodStart,
  periodEnd,
  maxStepDays,
}: {
  dates: string[];
  periodStart: string;
  periodEnd: string;
  maxStepDays: number;
}) {
  const x = timeScale(periodStart, periodEnd);
  const gaps = dates.slice(1).flatMap((date, i) => {
    const days = Math.round(dayNumber(date) - dayNumber(dates[i]));
    return days > maxStepDays ? [{ start: dates[i], end: date, days }] : [];
  });
  return (
    <figure className="rounded-[6px] border border-line bg-ink-2 px-4 pt-4 pb-3 min-[760px]:px-5">
      <figcaption className={`mb-4 flex flex-wrap items-center gap-x-5 gap-y-2 ${LABEL}`}>
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden className="h-3 w-0.5 bg-cat-2" />
          date de relevé ({dates.length})
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden className={`h-3 w-4 ${GAP_FILL}`} />
          plus de {maxStepDays} jours sans relevé : rien n’est tracé
        </span>
      </figcaption>
      <div className="relative ml-14 mr-1 h-9" role="img" aria-label={`${dates.length} dates de relevé de prix du ${fmtDate(periodStart)} au ${fmtDate(periodEnd)}. Périodes sans relevé : ${gaps.map((g) => `${g.days} jours du ${fmtDate(g.start)} au ${fmtDate(g.end)}`).join(", ")}.`}>
        {gaps.map((gap) => (
          <div
            key={gap.start}
            className={`absolute inset-y-0 flex items-center justify-center ${GAP_FILL}`}
            style={{ left: `${x(gap.start)}%`, width: `${x(gap.end) - x(gap.start)}%` }}
          >
            {/* Sur mobile, une bande de moins de 12 % de large n'a pas la place de son étiquette (l'aria-label la donne). */}
            <span className={`whitespace-nowrap rounded-[2px] bg-ink-2 px-1 ${LABEL} text-soft ${x(gap.end) - x(gap.start) < 12 ? "max-[759px]:hidden" : ""}`}>
              {gap.days} j
            </span>
          </div>
        ))}
        {dates.map((date) => (
          <div key={date} className="absolute inset-y-1 w-0.5 -translate-x-1/2 bg-cat-2" style={{ left: `${x(date)}%` }} title={fmtDate(date)} />
        ))}
      </div>
      <MonthAxis periodStart={periodStart} periodEnd={periodEnd} className="mt-2 ml-14 mr-1" />
    </figure>
  );
}
