"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { max, nice, ticks } from "d3-array";
import { ArtDot } from "@/components/card-art";
import { Pill, controlClass } from "@/components/ds/control";
import { BAND_OPACITY, ChartLegend, MethodNote, WEAK_FILL_OPACITY, WEAK_STROKE, bandPath, isWeakMonth } from "@/components/ds/explain";
import { DataFooter, Toolbar } from "@/components/ds/page";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import { wilsonInterval } from "@/lib/wilson";
import type { EvolutionResponse } from "@/types";

// Graphique SVG maison (TOK-99) : D3 calcule les échelles et les tracés, React
// rend le SVG. Le premier rendu (serveur) contient déjà les courbes, les axes et
// les étiquettes ; le survol, le clavier et l'ajustement à la largeur réelle
// s'ajoutent une fois le JavaScript chargé. Côté navigateur, seuls d3-array et
// d3-shape sont chargés : d3-scale (≈ 20 ko) ferait dépasser le budget de 200 ko,
// et une échelle linéaire tient en une ligne.
//
// Mesure tracée (lot 15) : la part des decks du mois, et non plus le score méta,
// pour pouvoir dessiner son incertitude : bande de Wilson à 95 % (lib/wilson.ts),
// mois de moins de 100 decks et mois en cours en pointillé et plus pâles. Le score
// reste dans l'infobulle de survol et le tableau. Segments droits entre deux mois :
// une courbe lissée inventerait des valeurs entre deux relevés.

// Palette catégorielle, ordre fixe (docs/design-system.md §4 bis). Une série garde
// sa teinte tant qu'elle est affichée : en retirer une ne repeint pas les autres.
const SERIES_COLORS = ["var(--cat-1)", "var(--cat-2)", "var(--cat-3)", "var(--cat-4)"];
const MAX_SERIES = SERIES_COLORS.length;

const AXIS = "font-mono text-[12px]";
const STRIP_H = 22; // bande « decks par mois » sous l'axe du temps

type Selection = { arch: string; slot: number };
/** value = part en % ; lo / hi = intervalle à 95 % en % ; k decks de l'archétype sur n. */
type Point = { month: string; value: number; score: number; k: number; n: number; lo: number; hi: number; weak: boolean };

/** Tous les mois de `first` à `last` inclus (« AAAA-MM »), sans trou. */
function monthSpan(first: string, last: string): string[] {
  const out: string[] = [];
  let [y, m] = first.split("-").map(Number);
  while (out.length < 240) {
    const label = `${y}-${String(m).padStart(2, "0")}`;
    out.push(label);
    if (label >= last) break;
    m += 1;
    if (m > 12) {
      m = 1;
      y += 1;
    }
  }
  return out;
}

const short = (name: string, n: number) => (name.length > n ? `${name.slice(0, n - 1)}…` : name);

export function EvolutionChart({ data, images, decks_by_month }: EvolutionResponse) {
  const archetypes = useMemo(() => Object.keys(data), [data]);
  const [selected, setSelected] = useState<Selection[]>(() =>
    archetypes.slice(0, 3).map((arch, slot) => ({ arch, slot }))
  );
  const [size, setSize] = useState({ w: 1100, h: 400 });
  const [active, setActive] = useState<number | null>(null);
  const frame = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = frame.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      if (width > 0 && height > 0) setSize({ w: Math.round(width), h: Math.round(height) });
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  function toggle(arch: string) {
    setActive(null);
    setSelected((prev) => {
      if (prev.some((s) => s.arch === arch)) return prev.filter((s) => s.arch !== arch);
      // Au-delà de quatre séries, la plus ancienne cède sa place (et sa teinte).
      const kept = prev.length >= MAX_SERIES ? prev.slice(1) : prev;
      const slot = SERIES_COLORS.findIndex((_, i) => !kept.some((s) => s.slot === i));
      return [...kept, { arch, slot }];
    });
  }

  // Dernier mois relevé, tous archétypes : il est en cours (job hebdomadaire).
  const currentMonth = useMemo(
    () => archetypes.flatMap((a) => data[a].map((p) => p.month)).sort().at(-1) ?? "",
    [archetypes, data]
  );

  const series = useMemo(
    () =>
      selected.map(({ arch, slot }) => ({
        arch,
        color: SERIES_COLORS[slot],
        points: data[arch].map<Point>((p) => {
          const n = decks_by_month[p.month] ?? 0;
          // `decks` est servi depuis le lot 15 ; à défaut (ancien instantané), la part
          // vaut exactement decks / n et se retourne.
          const k = p.decks ?? Math.round(p.share * n);
          const [lo, hi] = wilsonInterval(k, n);
          return {
            month: p.month,
            value: p.share * 100,
            score: p.meta_score * 100,
            k,
            n,
            lo: lo * 100,
            hi: hi * 100,
            weak: isWeakMonth(n) || p.month === currentMonth,
          };
        }),
      })),
    [selected, data, decks_by_month, currentMonth]
  );

  // L'axe du temps commence au premier mois où une série affichée a une valeur
  // (TOK-96) : sinon les courbes sont tassées à droite d'un graphique vide.
  const months = useMemo(() => {
    const all = archetypes.flatMap((a) => data[a].map((p) => p.month)).sort();
    if (all.length === 0) return [];
    const shown = series.flatMap((s) => s.points.map((p) => p.month)).sort();
    return monthSpan(shown[0] ?? all[0], all[all.length - 1]);
  }, [archetypes, data, series]);

  const { w, h } = size;
  const compact = w < 620;
  const margin = { top: 26, right: compact ? 60 : 172, bottom: 30 + STRIP_H + 14, left: 38 };
  const plotBottom = h - margin.bottom;

  const step = months.length > 1 ? (w - margin.left - margin.right) / (months.length - 1) : 0;
  const px = (month: string) => margin.left + Math.max(0, months.indexOf(month)) * step;
  // L'axe part de zéro (pour ne pas exagérer les écarts) et s'arrête au plus haut
  // point affiché, bande comprise (TOK-96). Un mois de moins de 100 decks ne fixe
  // pas l'échelle (à 1 deck, sa part peut valoir 100 %) : il est posé au bord.
  const scaled = series.flatMap((s) => s.points.filter((p) => months.includes(p.month) && !isWeakMonth(p.n)));
  const yMax = Math.max(max(scaled, (p) => p.value) ?? 0, max(scaled, (p) => p.hi) ?? 0) || 1;
  const [, yTop] = nice(0, yMax, 4);
  const y = (value: number) => plotBottom - (Math.min(value, yTop) / yTop) * (plotBottom - margin.top);
  const yTicks = ticks(0, yTop, 4);
  // Un mois sans deck de l'archétype n'a pas de ligne dans la source : la courbe
  // relie les mois mesurés, chacun marqué d'un point. Un segment est atténué si
  // l'un de ses deux mois l'est.
  const segmentsOf = (points: Point[]) =>
    points.slice(1).map((p, i) => ({ from: points[i], to: p, weak: p.weak || points[i].weak }));

  const tickEvery = step > 0 ? Math.max(1, Math.ceil((compact ? 92 : 58) / step)) : 1;
  const lastIndex = months.length - 1;

  const maxDecks = max(months, (m) => decks_by_month[m] ?? 0) ?? 0;
  const stripTop = plotBottom + 30;
  const barW = Math.max(2, Math.min(18, (step || 18) * 0.6));

  // Étiquettes directes en bout de courbe, écartées de 15 px quand elles se chevauchent.
  const labels = series
    .map((s) => {
      const last = s.points[s.points.length - 1];
      return { ...s, last, lx: px(last.month), ly: y(last.value) };
    })
    .sort((a, b) => a.ly - b.ly);
  for (let i = 1; i < labels.length; i++) {
    if (labels[i].ly - labels[i - 1].ly < 15) labels[i].ly = labels[i - 1].ly + 15;
  }

  const activeMonth = active === null ? null : months[active];
  const activeRows =
    activeMonth === null
      ? []
      : series.map((s) => ({ ...s, point: s.points.find((p) => p.month === activeMonth) ?? null }));

  function monthAt(clientX: number, target: SVGSVGElement) {
    const box = target.getBoundingClientRect();
    const svgX = ((clientX - box.left) / box.width) * w;
    return Math.max(0, Math.min(lastIndex, (step > 0 ? Math.round((svgX - margin.left) / step) : 0)));
  }

  function onKeyDown(event: React.KeyboardEvent) {
    const moves: Record<string, number> = { ArrowLeft: -1, ArrowRight: 1, Home: -lastIndex, End: lastIndex };
    if (event.key === "Escape") return setActive(null);
    if (!(event.key in moves)) return;
    event.preventDefault();
    setActive((current) => Math.max(0, Math.min(lastIndex, (current ?? lastIndex + 1) + moves[event.key])));
  }

  const period = months.length ? `${fmtMonthShort(months[0])} à ${fmtMonthShort(months[lastIndex])}` : "";
  const summary = series
    .map((s) => {
      const last = s.points[s.points.length - 1];
      return `${s.arch} ${fmtPct(last.value)} en ${fmtMonthShort(last.month)} (${fmtNum(last.k)} decks sur ${fmtNum(last.n)})`;
    })
    .join(" ; ");
  const readout =
    activeMonth === null
      ? ""
      : `${fmtMonthShort(activeMonth)} : ${activeRows
          .map((r) =>
            r.point
              ? `${r.arch} ${fmtPct(r.point.value)}, ${fmtNum(r.point.k)} decks, intervalle à 95 % de ${fmtPct(r.point.lo)} à ${fmtPct(r.point.hi)}`
              : `${r.arch} aucun deck`
          )
          .join(", ")}. ${fmtNum(decks_by_month[activeMonth] ?? 0)} decks.`;
  const tipLeft = activeMonth !== null && px(activeMonth) > w / 2;

  return (
    <>
      <Toolbar count={`${selected.length} / ${MAX_SERIES} séries`}>
        {archetypes.map((arch) => {
          const slot = selected.find((s) => s.arch === arch)?.slot ?? -1;
          return (
            <Pill key={arch} pressed={slot >= 0} onClick={() => toggle(arch)}>
              {slot >= 0 && (
                <span aria-hidden className="h-2 w-2 rounded-full" style={{ backgroundColor: SERIES_COLORS[slot] }} />
              )}
              {images[arch] && <ArtDot src={images[arch]} />}
              {arch}
            </Pill>
          );
        })}
      </Toolbar>

      <div className="rounded-[8px] border border-line-2 bg-ink-2 p-3 min-[760px]:p-6">
        <ChartLegend
          className="mb-4"
          items={[
            { swatch: "line", label: "part des decks du mois" },
            { swatch: "band", label: "intervalle à 95 %" },
            { swatch: "dashed", label: "mois de moins de 100 decks, mois en cours" },
            { swatch: "bar", color: "var(--line-2)", label: "decks relevés par mois" },
          ]}
        />
        <div
          ref={frame}
          tabIndex={0}
          role="group"
          aria-label={`Graphique interactif, ${period}. Flèches gauche et droite : changer de mois. Échap : quitter.`}
          onKeyDown={onKeyDown}
          onBlur={() => setActive(null)}
          className="relative h-[320px] rounded-[4px] min-[760px]:h-[400px]"
        >
          <svg
            viewBox={`0 0 ${w} ${h}`}
            width="100%"
            height="100%"
            role="img"
            aria-label={
              series.length
                ? `Part mensuelle des decks de tournoi TCG, ${period}, avec intervalle à 95 %. Dernière valeur : ${summary}.`
                : "Aucune série sélectionnée."
            }
            className="block touch-pan-y"
            onPointerMove={(e) => setActive(monthAt(e.clientX, e.currentTarget))}
            onPointerDown={(e) => setActive(monthAt(e.clientX, e.currentTarget))}
            onPointerLeave={(e) => e.pointerType === "mouse" && setActive(null)}
          >
            <text x={0} y={11} fill="var(--muted-text)" className={AXIS}>
              part des decks
            </text>
            {yTicks.map((tick) => (
              <g key={tick}>
                <line
                  x1={margin.left}
                  x2={w - margin.right}
                  y1={y(tick)}
                  y2={y(tick)}
                  stroke="var(--line)"
                  strokeDasharray={tick === 0 ? undefined : "3 5"}
                />
                <text x={margin.left - 8} y={y(tick) + 4} textAnchor="end" fill="var(--muted-text)" className={AXIS}>
                  {tick} %
                </text>
              </g>
            ))}
            {months.map((month, i) =>
              (lastIndex - i) % tickEvery === 0 ? (
                <text
                  key={month}
                  x={px(month)}
                  y={plotBottom + 18}
                  textAnchor={i === lastIndex && compact ? "end" : "middle"}
                  fill="var(--muted-text)"
                  className={AXIS}
                >
                  {fmtMonthShort(month)}
                </text>
              ) : null
            )}

            {/* Taille d'échantillon : decks de tournoi comptés chaque mois. */}
            {months.map((month) => {
              const n = decks_by_month[month] ?? 0;
              const barH = maxDecks ? Math.max(1, (n / maxDecks) * STRIP_H) : 0;
              return (
                <rect
                  key={month}
                  x={px(month) - barW / 2}
                  y={stripTop + STRIP_H - barH}
                  width={barW}
                  height={barH}
                  rx={1}
                  fill={month === activeMonth ? "var(--soft)" : "var(--line-2)"}
                />
              );
            })}
            {months.length > 0 && (
              <text
                x={w - margin.right + barW / 2 + 8}
                y={stripTop + STRIP_H}
                fill="var(--muted-text)"
                className={AXIS}
              >
                {compact
                  ? fmtNum(decks_by_month[months[lastIndex]] ?? 0)
                  : `en cours, ${fmtNum(decks_by_month[months[lastIndex]] ?? 0)} decks`}
              </text>
            )}

            {activeMonth !== null && (
              <line
                x1={px(activeMonth)}
                x2={px(activeMonth)}
                y1={margin.top}
                y2={stripTop + STRIP_H}
                stroke="var(--line-2)"
              />
            )}

            {series.map((s) => {
              const shown = s.points.filter((p) => months.includes(p.month));
              return (
                <g key={s.arch}>
                  <path
                    d={bandPath(shown.map((p) => ({ x: px(p.month), lo: y(p.lo), hi: y(p.hi) })))}
                    fill={s.color}
                    fillOpacity={BAND_OPACITY}
                  />
                  {segmentsOf(shown).map((seg) => (
                    <line
                      key={seg.to.month}
                      x1={px(seg.from.month)}
                      y1={y(seg.from.value)}
                      x2={px(seg.to.month)}
                      y2={y(seg.to.value)}
                      stroke={s.color}
                      strokeWidth={2}
                      strokeLinecap="round"
                      {...(seg.weak ? WEAK_STROKE : {})}
                    />
                  ))}
                  {shown.map((p) => (
                    <circle
                      key={p.month}
                      cx={px(p.month)}
                      cy={y(p.value)}
                      r={p.month === activeMonth ? 4.5 : 2}
                      fill={s.color}
                      fillOpacity={p.weak && p.month !== activeMonth ? WEAK_FILL_OPACITY : 1}
                      stroke="var(--ink-2)"
                      strokeWidth={p.month === activeMonth ? 2 : 0}
                    />
                  ))}
                </g>
              );
            })}

            {labels.map((l) => (
              <g key={l.arch}>
                <circle cx={l.lx} cy={y(l.last.value)} r={4.5} fill={l.color} stroke="var(--ink-2)" strokeWidth={2} />
                <text x={l.lx + 10} y={l.ly + 4} className={AXIS}>
                  <tspan fill="var(--text)" fontWeight={500}>
                    {fmtPct(l.last.value)}
                  </tspan>
                  {!compact && (
                    <tspan fill="var(--soft)" dx={6}>
                      {short(l.arch, 16)}
                    </tspan>
                  )}
                </text>
              </g>
            ))}
          </svg>

          {activeMonth !== null && (
            <div
              className="pointer-events-none absolute top-2 z-10 min-w-[168px] rounded-[4px] border border-line-2 bg-ink-3 px-3 py-2.5 font-mono text-[12px]"
              style={
                tipLeft
                  ? { right: `${((w - px(activeMonth)) / w) * 100}%`, marginRight: 12 }
                  : { left: `${(px(activeMonth) / w) * 100}%`, marginLeft: 12 }
              }
            >
              <p className="text-muted-text">
                {fmtMonthShort(activeMonth)} · {fmtNum(decks_by_month[activeMonth] ?? 0)} decks
              </p>
              <p className="mt-0.5 text-muted-text">part · intervalle à 95 %</p>
              {activeRows.map((r) => (
                <p key={r.arch} className="mt-1 flex items-center gap-2">
                  <span aria-hidden className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: r.color }} />
                  <span className="min-w-0 flex-1 truncate text-soft">{short(r.arch, 22)}</span>
                  <span className="font-medium text-text tabular-nums">{r.point ? fmtPct(r.point.value) : "—"}</span>
                  <span className="w-[84px] text-right text-muted-text tabular-nums">
                    {r.point ? `${fmtNum(r.point.lo, 1)}–${fmtNum(r.point.hi, 1)}` : ""}
                  </span>
                </p>
              ))}
            </div>
          )}
          <p aria-live="polite" className="sr-only">
            {readout}
          </p>
        </div>
      </div>

      <DataFooter
        source="decklists de tournoi TCG, yugiohmeta.com"
        date={period}
        sample={`${fmtNum(months.reduce((sum, m) => sum + (decks_by_month[m] ?? 0), 0))} decks`}
        uncertainty="bande : intervalle à 95 % de chaque part mensuelle ; pointillé : mois de moins de 100 decks et mois en cours"
      >
        un mois sans deck de l’archétype n’a pas de point
      </DataFooter>
      <MethodNote anchor="evolution">
        <p>Part du mois : decks de l’archétype divisés par tous les decks de tournoi TCG relevés ce mois-là.</p>
        <p>Archétypes proposés : les premiers au score méta du dernier mois, qui combine la part et le classement en tournoi.</p>
        <p>L’intervalle suppose des decks indépendants ; plusieurs listes d’un même joueur ou d’un même tournoi le rendent trop étroit.</p>
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
              Part mensuelle des decks (decks de l’archétype entre parenthèses) et score méta des séries affichées, {period}
            </caption>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Mois</TableHead>
                {series.map((s) => (
                  <TableHead key={s.arch} className="text-right">
                    {s.arch}
                  </TableHead>
                ))}
                <TableHead className="text-right">Decks</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...months].reverse().map((month) => (
                <TableRow key={month}>
                  <TableCell className="font-mono text-[13px] text-soft">{fmtMonthShort(month)}</TableCell>
                  {series.map((s) => {
                    const point = s.points.find((p) => p.month === month);
                    return (
                      <TableCell key={s.arch} className="text-right font-mono text-[13px] tabular-nums">
                        {point ? (
                          <>
                            {fmtPct(point.value)} <span className="text-muted-text">({fmtNum(point.k)})</span>
                          </>
                        ) : (
                          "—"
                        )}
                      </TableCell>
                    );
                  })}
                  <TableCell className="text-right font-mono text-[13px] text-muted-text tabular-nums">
                    {fmtNum(decks_by_month[month] ?? 0)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </details>
    </>
  );
}
