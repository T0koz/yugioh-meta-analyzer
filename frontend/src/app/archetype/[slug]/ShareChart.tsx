import { max } from "d3-array";
import { scaleLinear } from "d3-scale";
import { fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import type { ArchetypeMonth, TierWindow } from "@/types";

// Part mensuelle de l'archétype dans les decks de tournoi TCG. Rendu côté serveur,
// sans JavaScript. Le tracé vit dans un SVG étiré (viewBox 0-100, trait à
// épaisseur constante) ; les textes sont du HTML positionné en pourcentage, donc
// toujours à 12 px quelle que soit la largeur. Sous le tracé, une bande donne le
// nombre de decks relevés chaque mois : une part sur 76 decks ne pèse pas comme
// une part sur 519.

const PLOT_H = 220;
const BOX = "relative ml-11 mr-1";
const LABEL = "font-mono text-[12px] leading-none text-muted-text tabular-nums";

export function ShareChart({
  archetype,
  history,
  window,
}: {
  archetype: string;
  history: ArchetypeMonth[];
  window: TierWindow | null;
}) {
  const n = history.length;
  // Chaque mois occupe une colonne de largeur égale ; le point est au milieu.
  const x = (index: number) => ((index + 0.5) / n) * 100;
  const top = (max(history, (h) => h.share) ?? 0) * 100;
  const y = scaleLinear().domain([0, top || 1]).nice(4).range([100, 0]);
  const ticks = y.ticks(4);
  const points = history.map((h, i) => ({ ...h, x: x(i), y: y(h.share * 100) }));
  const line = points.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(2)} ${p.y.toFixed(2)}`).join(" ");
  const area = `${line} L${points[n - 1].x.toFixed(2)} 100 L${points[0].x.toFixed(2)} 100 Z`;

  const peak = points.reduce((best, p) => (p.share > best.share ? p : best), points[0]);
  const last = points[n - 1];
  // Le dernier mois n'est annoté à part que s'il est loin du maximum (étiquettes lisibles).
  const labelled = last.x - peak.x > 18 ? [peak, last] : [peak];

  // Mois de la fenêtre de la tier list : c'est sur eux que portent part, tier et tendance.
  const inWindow = window ? points.filter((p) => p.month >= window.start && p.month <= window.end) : [];
  const band = inWindow.length
    ? { x: inWindow[0].x - 50 / n, width: (inWindow.length * 100) / n }
    : null;

  const maxDecks = max(history, (h) => h.total_decks) ?? 0;
  const barWidth = Math.min(60 / n, 4);
  // Une étiquette de mois tous les `step` mois, en partant du dernier.
  const step = Math.ceil(n / 8);
  const axisMonths = points.filter((_, i) => (n - 1 - i) % step === 0);

  return (
    <figure className="rounded-[6px] border border-line bg-ink-2 px-3 pt-4 pb-3 min-[760px]:px-5 min-[760px]:pt-5">
      <figcaption className={`mb-9 flex flex-wrap items-center gap-x-5 gap-y-1.5 ${LABEL}`}>
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden className="h-0.5 w-4 bg-cat-1" />
          part mensuelle des decks TCG
        </span>
        {band && window && (
          <span className="inline-flex items-center gap-1.5">
            <span aria-hidden className="h-3 w-3 border-x border-line-2 bg-ink-4" />
            fenêtre de la tier list ({fmtMonthShort(window.start)}
            {window.start !== window.end && ` à ${fmtMonthShort(window.end)}`})
          </span>
        )}
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden className="h-3 w-1 bg-faint" />
          decks relevés par mois (max. {fmtNum(maxDecks)})
        </span>
      </figcaption>

      <div className={BOX} style={{ height: PLOT_H }}>
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="absolute inset-0 h-full w-full"
          role="img"
          aria-label={`Part de ${archetype} dans les decks de tournoi TCG, par mois, de ${fmtMonthShort(points[0].month)} à ${fmtMonthShort(last.month)}. Maximum ${fmtPct(peak.share * 100)} en ${fmtMonthShort(peak.month)} (${fmtNum(peak.decks)} decks sur ${fmtNum(peak.total_decks)}). Dernier mois : ${fmtPct(last.share * 100)} (${fmtNum(last.decks)} decks sur ${fmtNum(last.total_decks)}).`}
        >
          {band && <rect x={band.x} y="0" width={band.width} height="100" fill="var(--ink-4)" />}
          {ticks.map((tick) => (
            <line
              key={tick}
              x1="0"
              x2="100"
              y1={y(tick)}
              y2={y(tick)}
              stroke={tick === 0 ? "var(--line-2)" : "var(--line)"}
              vectorEffect="non-scaling-stroke"
            />
          ))}
          <path d={area} fill="var(--cat-1)" fillOpacity="0.12" />
          <path
            d={line}
            fill="none"
            stroke="var(--cat-1)"
            strokeWidth="2"
            strokeLinejoin="round"
            strokeLinecap="round"
            vectorEffect="non-scaling-stroke"
          />
        </svg>
        {/* Points : SVG non étiré, pour des cercles ronds. */}
        <svg aria-hidden className="absolute inset-0 h-full w-full overflow-visible">
          {points.map((p) => {
            const marked = labelled.includes(p);
            return (
              <circle
                key={p.month}
                cx={`${p.x}%`}
                cy={`${p.y}%`}
                r={marked ? 4.5 : n > 24 ? 0 : 2.5}
                fill={marked ? "var(--cat-1)" : "var(--ink-2)"}
                stroke="var(--cat-1)"
                strokeWidth="1.5"
              >
                <title>{`${fmtMonthShort(p.month)} : ${fmtPct(p.share * 100)} (${fmtNum(p.decks)} decks sur ${fmtNum(p.total_decks)})`}</title>
              </circle>
            );
          })}
        </svg>
        {ticks.map((tick) => (
          <span key={tick} aria-hidden className={`absolute -left-11 w-9 -translate-y-1/2 text-right ${LABEL}`} style={{ top: `${y(tick)}%` }}>
            {tick} %
          </span>
        ))}
        {labelled.map((p) => (
          <span
            key={p.month}
            aria-hidden
            className={`absolute -mt-3 -translate-y-full font-mono text-[12px] leading-none font-medium whitespace-nowrap text-text tabular-nums ${
              p.x < 15 ? "" : p.x > 80 ? "-translate-x-full" : "-translate-x-1/2"
            }`}
            style={{ left: `${p.x < 15 ? p.x - 1 : p.x > 80 ? p.x + 1.5 : p.x}%`, top: `${p.y}%` }}
          >
            {fmtPct(p.share * 100)} · {fmtMonthShort(p.month)}
          </span>
        ))}
      </div>

      <div className={`${BOX} mt-2 h-[22px]`} aria-hidden>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
          {points.map((p) => {
            const height = maxDecks ? (p.total_decks / maxDecks) * 100 : 0;
            return <rect key={p.month} x={p.x - barWidth / 2} y={100 - height} width={barWidth} height={height} fill="var(--faint)" />;
          })}
        </svg>
        <span className={`absolute -left-11 bottom-0 w-9 text-right ${LABEL}`}>decks</span>
      </div>

      <div className={`${BOX} mt-2 h-4`} aria-hidden>
        {axisMonths.map((p, rank) => (
          <span
            key={p.month}
            // Sur mobile, une étiquette sur deux : huit dates de 56 px ne tiennent pas dans 300 px.
            className={`absolute top-0 whitespace-nowrap ${LABEL} ${p.x > 90 ? "-translate-x-full" : "-translate-x-1/2"} ${
              (axisMonths.length - 1 - rank) % 2 ? "max-[759px]:hidden" : ""
            }`}
            style={{ left: `${p.x > 90 ? 100 : p.x}%` }}
          >
            {fmtMonthShort(p.month)}
          </span>
        ))}
      </div>
    </figure>
  );
}
