"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useState } from "react";
import { ArtDot } from "@/components/card-art";
import { Toolbar, pillClass } from "@/components/ds/page";
import { fmtMonthShort } from "@/lib/format";
import type { EvolutionResponse } from "@/types";

// Série principale (la première sélectionnée) en accent, les autres en gris
// décroissants (docs/design-system.md §4) : au plus quatre séries lisibles.
const SERIES_COLORS = ["var(--signal)", "var(--soft)", "var(--muted-text)", "var(--faint)"];
const MAX_SERIES = SERIES_COLORS.length;

const AXIS_TICK = { fill: "var(--muted-text)", fontSize: 11, fontFamily: "var(--font-jetbrains-mono)" };

export function EvolutionChart({ data, images }: Pick<EvolutionResponse, "data" | "images">) {
  const archetypes = Object.keys(data);
  // Ordre de sélection = ordre des couleurs : la première série choisie porte l'accent.
  const [selected, setSelected] = useState<string[]>(archetypes.slice(0, 3));

  function toggle(arch: string) {
    setSelected((prev) => {
      if (prev.includes(arch)) return prev.filter((a) => a !== arch);
      // Au-delà de quatre séries, la plus ancienne sélection cède sa place.
      return [...prev, arch].slice(-MAX_SERIES);
    });
  }

  const months = Array.from(new Set(archetypes.flatMap((a) => data[a].map((p) => p.month)))).sort();
  const chartData = months.map((month) => {
    const row: Record<string, string | number | null> = { month };
    for (const arch of archetypes) {
      const point = data[arch].find((p) => p.month === month);
      // null (pas absence de clé) pour que `connectNulls` relie les mois sans données.
      row[arch] = point ? Math.round(point.meta_score * 100) : null;
    }
    return row;
  });

  // L'axe du temps commence au premier mois où une série affichée a une valeur :
  // sinon les courbes sont tassées à droite d'un graphique vide.
  const firstIndex = chartData.findIndex((row) => selected.some((arch) => row[arch] !== null));
  const visibleData = firstIndex > 0 ? chartData.slice(firstIndex) : chartData;

  const main = selected[0];
  const mainLastIndex = main ? visibleData.findLastIndex((row) => row[main] !== null) : -1;

  return (
    <>
      <Toolbar count={`${selected.length} / ${MAX_SERIES} séries`}>
        {archetypes.map((arch) => {
          const slot = selected.indexOf(arch);
          return (
            <button
              key={arch}
              type="button"
              aria-pressed={slot >= 0}
              onClick={() => toggle(arch)}
              className={`${pillClass(slot >= 0)} inline-flex items-center gap-2`}
            >
              {slot >= 0 && (
                <span aria-hidden className="h-2 w-2 rounded-full" style={{ backgroundColor: SERIES_COLORS[slot] }} />
              )}
              {images[arch] && <ArtDot src={images[arch]} />}
              {arch}
            </button>
          );
        })}
      </Toolbar>

      <div className="rounded-[8px] border border-line-2 bg-ink-2 p-4 min-[760px]:p-6">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={visibleData} margin={{ top: 8, right: 28, bottom: 0, left: -12 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
            <XAxis
              dataKey="month"
              tickFormatter={fmtMonthShort}
              stroke="var(--line)"
              tick={AXIS_TICK}
              tickLine={false}
            />
            {/* Le score méta dépasse rarement 20 : l'axe part de zéro (pour ne pas
                exagérer les écarts) et s'arrête au maximum des séries affichées. */}
            <YAxis domain={[0, "auto"]} allowDecimals={false} stroke="var(--line)" tick={AXIS_TICK} tickLine={false} />
            <Tooltip
              labelFormatter={(m) => fmtMonthShort(String(m))}
              contentStyle={{
                backgroundColor: "var(--ink-3)",
                border: "1px solid var(--line-2)",
                borderRadius: 4,
                fontFamily: "var(--font-jetbrains-mono)",
                fontSize: 12,
              }}
              labelStyle={{ color: "var(--muted-text)" }}
              itemStyle={{ color: "var(--text)" }}
              cursor={{ stroke: "var(--line-2)" }}
            />
            {selected.map((arch, slot) => (
              <Line
                key={arch}
                type="monotone"
                dataKey={arch}
                stroke={SERIES_COLORS[slot]}
                strokeWidth={2}
                // Seul le dernier point de la série principale est mis en évidence.
                dot={(props: { cx?: number; cy?: number; index?: number; key?: React.Key | null }) =>
                  slot === 0 && props.index === mainLastIndex ? (
                    <circle key={props.key ?? undefined} cx={props.cx} cy={props.cy} r={4.5} fill="var(--signal)" />
                  ) : null
                }
                activeDot={{ r: 4, strokeWidth: 0, fill: SERIES_COLORS[slot] }}
                connectNulls
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
