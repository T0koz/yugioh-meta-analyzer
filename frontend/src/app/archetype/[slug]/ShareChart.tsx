import { max } from "d3-array";
import { scaleLinear } from "d3-scale";
import { BAND_OPACITY, ChartAnnotation, ChartLegend, WEAK_STROKE, bandPath, isWeakMonth } from "@/components/ds/explain";
import { fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import { wilsonInterval } from "@/lib/wilson";
import type { ArchetypeMonth, TierWindow } from "@/types";

// Part mensuelle de l'archétype dans les decks de tournoi TCG. Rendu côté serveur,
// sans JavaScript. Le tracé vit dans un SVG étiré (viewBox 0-100, trait à
// épaisseur constante) ; les textes sont du HTML positionné en pourcentage, donc
// toujours à 12 px quelle que soit la largeur. Sous le tracé, une bande donne le
// nombre de decks relevés chaque mois : une part sur 76 decks ne pèse pas comme
// une part sur 519.
//
// Incertitude (lot 15, charte §3) : bande de Wilson à 95 % autour de chaque part
// (lib/wilson.ts) ; mois de moins de 100 decks et dernier mois (en cours) tracés
// en pointillé et plus pâles. L'axe s'arrête au plus haut point des bandes des
// mois pleins : la bande d'un mois à 1 deck irait jusqu'à 100 % et écraserait le
// reste ; elle est coupée au bord du cadre.

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
  const withBand = history.map((h, i) => {
    const [lo, hi] = wilsonInterval(h.decks, h.total_decks);
    // Le dernier mois est en cours de relevé (job hebdomadaire) : même convention
    // que le reste de la page.
    const small = isWeakMonth(h.total_decks);
    return { ...h, lo: lo * 100, hi: hi * 100, small, weak: small || i === n - 1 };
  });
  // Un mois à 1 deck peut valoir 100 % : seuls les mois d'au moins 100 decks
  // fixent l'échelle ; un point plus haut est posé au bord du cadre.
  const full = withBand.filter((h) => !h.small);
  const top = Math.max(max(full, (h) => h.share * 100) ?? 0, max(full, (h) => h.hi) ?? 0);
  const y = scaleLinear().domain([0, top || 1]).nice(4).range([100, 0]);
  const yTop = y.domain()[1];
  const ticks = y.ticks(4);
  const points = withBand.map((h, i) => ({ ...h, x: x(i), y: y(Math.min(h.share * 100, yTop)) }));
  const band = bandPath(points.map((p) => ({ x: p.x, lo: y(p.lo), hi: y(Math.min(p.hi, yTop)) })));
  // Un segment est atténué si l'un de ses deux mois l'est.
  const segments = points.slice(1).map((p, i) => ({ from: points[i], to: p, weak: p.weak || points[i].weak }));
  const weakMonths = points.filter((p) => p.weak && p !== points[n - 1]).length;

  const candidates = points.filter((p) => !p.small);
  const peak = (candidates.length ? candidates : points).reduce((best, p) => (p.share > best.share ? p : best));
  const last = points[n - 1];
  // Le dernier mois (en cours) est toujours annoté ; proche du maximum, son
  // étiquette passe sous le point pour ne pas chevaucher celle du pic.
  const labelled = peak === last ? [peak] : [peak, last];
  const crowded = last.x - peak.x <= 18;

  // Mois de la fenêtre de la tier list : c'est sur eux que portent part, tier et tendance.
  const inWindow = window ? points.filter((p) => p.month >= window.start && p.month <= window.end) : [];
  const zone = inWindow.length
    ? { x: inWindow[0].x - 50 / n, width: (inWindow.length * 100) / n }
    : null;

  const maxDecks = max(history, (h) => h.total_decks) ?? 0;
  const barWidth = Math.min(60 / n, 4);
  // Une étiquette de mois tous les `step` mois, en partant du dernier.
  const step = Math.ceil(n / 8);
  const axisMonths = points.filter((_, i) => (n - 1 - i) % step === 0);

  return (
    <figure className="rounded-[6px] border border-line bg-ink-2 px-3 pt-4 pb-3 min-[760px]:px-5 min-[760px]:pt-5">
      <ChartLegend
        as="figcaption"
        className="mb-9"
        items={[
          { swatch: "line", color: "var(--cat-1)", label: "part mensuelle des decks TCG" },
          { swatch: "band", color: "var(--cat-1)", label: "intervalle à 95 %" },
          {
            swatch: "dashed",
            color: "var(--cat-1)",
            label: weakMonths ? "mois de moins de 100 decks, mois en cours" : "mois en cours",
          },
          ...(zone && window
            ? [
                {
                  swatch: "zone" as const,
                  label: `fenêtre de la tier list (${fmtMonthShort(window.start)}${
                    window.start !== window.end ? ` à ${fmtMonthShort(window.end)}` : ""
                  })`,
                },
              ]
            : []),
          { swatch: "bar", color: "var(--faint)", label: `decks relevés par mois (max. ${fmtNum(maxDecks)})` },
        ]}
      />

      <div className={BOX} style={{ height: PLOT_H }}>
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="absolute inset-0 h-full w-full"
          role="img"
          aria-label={`Part de ${archetype} dans les decks de tournoi TCG, par mois, de ${fmtMonthShort(points[0].month)} à ${fmtMonthShort(last.month)}. Maximum ${fmtPct(peak.share * 100)} en ${fmtMonthShort(peak.month)} (${fmtNum(peak.decks)} decks sur ${fmtNum(peak.total_decks)}). Dernier mois : ${fmtPct(last.share * 100)} (${fmtNum(last.decks)} decks sur ${fmtNum(last.total_decks)}).`}
        >
          {zone && <rect x={zone.x} y="0" width={zone.width} height="100" fill="var(--ink-4)" />}
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
          <path d={band} fill="var(--cat-1)" fillOpacity={BAND_OPACITY} />
          {segments.map((s) => (
            <line
              key={s.to.month}
              x1={s.from.x}
              y1={s.from.y}
              x2={s.to.x}
              y2={s.to.y}
              stroke="var(--cat-1)"
              strokeWidth="2"
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
              {...(s.weak ? WEAK_STROKE : {})}
            />
          ))}
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
                {...(p.weak && !marked ? { strokeOpacity: WEAK_STROKE.strokeOpacity } : {})}
              >
                <title>{`${fmtMonthShort(p.month)} : ${fmtPct(p.share * 100)} (${fmtNum(p.decks)} decks sur ${fmtNum(p.total_decks)}), intervalle à 95 % de ${fmtPct(p.lo)} à ${fmtPct(p.hi)}`}</title>
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
          <ChartAnnotation key={p.month} x={p.x} y={p.y} decorative below={p === last && peak !== last && crowded}>
            {fmtPct(p.share * 100)} · {fmtMonthShort(p.month)}
            {p === last && `, en cours, n = ${fmtNum(p.total_decks)}`}
          </ChartAnnotation>
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
