import Link from "next/link";
import { fmtDate, fmtMonthRange, fmtRank } from "@/lib/format";
import { Tag } from "@/components/ds/tags";
import type { BuyLabel, SignalLabelRule } from "@/types";

// Vue d'ensemble des archétypes du signal (TOK-103) : rang parmi les archétypes
// OCG (jauge à deux graduations, charte §6 ex. 5) et fenêtre d'arrivée en TCG
// (segment sur une échelle de mois commune, charte §6 ex. 4). Rendu serveur.

export interface ArchetypeRow {
  archetype: string;
  slug: string;
  label: BuyLabel | null;
  rank: number | null;
  windowStart: string | null;
  windowEnd: string | null;
  cards: number;
}

export const LABEL_TONE: Record<BuyLabel, "strong" | "outline" | "neutral"> = {
  Fort: "strong",
  Modéré: "outline",
  Faible: "neutral",
};

const LABEL = "font-mono text-[12px] leading-none text-muted-text tabular-nums";

function monthStart(iso: string): Date {
  const [y, m] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, 1));
}

export function RankGauge({ rank, rule }: { rank: number; rule: SignalLabelRule }) {
  const pos = (r: number) => ((r - 0.5) / rule.population) * 100;
  return (
    <div className="relative h-3 w-full max-w-[180px]" aria-hidden>
      <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-line-2" />
      {[rule.strong_max_rank, rule.moderate_max_rank].map((cut) => (
        <div key={cut} className="absolute top-0 h-3 w-px bg-muted-text" style={{ left: `${(cut / rule.population) * 100}%` }} />
      ))}
      <div className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-signal" style={{ left: `${pos(rank)}%` }} />
    </div>
  );
}

export function ArrivalTimeline({
  rows,
  rule,
  computedAt,
}: {
  rows: ArchetypeRow[];
  rule: SignalLabelRule | null;
  computedAt: string | null;
}) {
  const ends = rows.flatMap((r) => (r.windowEnd ? [r.windowEnd] : []));
  const starts = rows.flatMap((r) => (r.windowStart ? [r.windowStart] : []));
  if (!ends.length) return null;
  const firstIso = [computedAt, ...starts].filter(Boolean).sort()[0] as string;
  const lastIso = ends.sort().at(-1) as string;
  const t0 = monthStart(firstIso).getTime();
  const endMonth = monthStart(lastIso);
  endMonth.setUTCMonth(endMonth.getUTCMonth() + 1);
  const t1 = endMonth.getTime();
  const x = (iso: string) => ((Date.parse(`${iso}T00:00:00Z`) - t0) / (t1 - t0)) * 100;

  const months: { iso: string; label: string }[] = [];
  for (const cursor = new Date(t0); cursor.getTime() < t1; cursor.setUTCMonth(cursor.getUTCMonth() + 1)) {
    months.push({
      iso: cursor.toISOString().slice(0, 10),
      label: cursor.toLocaleDateString("fr-FR", { month: "short", year: "2-digit", timeZone: "UTC" }),
    });
  }

  return (
    <figure className="rounded-[6px] border border-line bg-ink-2 px-4 pt-4 pb-3 min-[760px]:px-5 min-[760px]:pt-5">
      <figcaption className={`mb-5 flex flex-wrap items-center gap-x-5 gap-y-2 ${LABEL}`}>
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-signal" />
          rang parmi les {rule?.population ?? "—"} archétypes OCG (graduations : {rule ? `${fmtRank(rule.strong_max_rank)} et ${fmtRank(rule.moderate_max_rank)}` : "—"})
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span aria-hidden className="h-2 w-5 rounded-[2px] bg-cat-2/60" />
          arrivée en TCG, 8 fois sur 10 par le passé
        </span>
        {computedAt && (
          <span className="inline-flex items-center gap-1.5">
            <span aria-hidden className="h-3 w-px bg-text" />
            calcul du {fmtDate(computedAt)}
          </span>
        )}
      </figcaption>

      <ul className="grid gap-4">
        {rows.map((row) => (
          <li
            key={row.archetype}
            className="grid gap-x-6 gap-y-2 min-[760px]:grid-cols-[minmax(0,15rem)_minmax(0,11rem)_minmax(0,1fr)] min-[760px]:items-center"
          >
            <div className="flex flex-wrap items-center gap-2.5">
              {row.label && <Tag tone={LABEL_TONE[row.label]}>{row.label.toUpperCase()}</Tag>}
              <Link
                href={`#${row.slug}`}
                className="font-medium tracking-[-0.01em] underline decoration-line-2 underline-offset-4 transition-colors duration-200 hover:decoration-signal-hi"
              >
                {row.archetype}
              </Link>
            </div>
            <div className="flex items-center gap-3">
              {row.rank != null && rule ? (
                <>
                  <RankGauge rank={row.rank} rule={rule} />
                  <span className={`shrink-0 ${LABEL}`}>
                    {fmtRank(row.rank)} sur {rule.population}
                  </span>
                </>
              ) : (
                <span className={LABEL}>rang indisponible</span>
              )}
            </div>
            <div className="relative h-6">
              {months.map((m) => (
                <div key={m.iso} aria-hidden className="absolute inset-y-0 w-px bg-line" style={{ left: `${x(m.iso)}%` }} />
              ))}
              {computedAt && <div aria-hidden className="absolute -inset-y-1 w-px bg-text" style={{ left: `${x(computedAt)}%` }} />}
              {row.windowStart && row.windowEnd ? (
                <div
                  className="absolute top-1/2 flex h-4 -translate-y-1/2 items-center justify-center rounded-[3px] bg-cat-2/60"
                  style={{ left: `${x(row.windowStart)}%`, width: `${x(row.windowEnd) - x(row.windowStart)}%` }}
                  title={`Arrivée en TCG estimée : ${fmtMonthRange(row.windowStart, row.windowEnd)}, 8 fois sur 10 par le passé`}
                >
                  <span className="sr-only">
                    Arrivée en TCG estimée de {fmtDate(row.windowStart)} à {fmtDate(row.windowEnd)}, 8 fois sur 10 par le passé
                  </span>
                </div>
              ) : (
                <span className={`absolute top-1/2 -translate-y-1/2 ${LABEL}`}>fenêtre indisponible</span>
              )}
            </div>
          </li>
        ))}
      </ul>

      <div className="mt-3 grid min-[760px]:grid-cols-[minmax(0,15rem)_minmax(0,11rem)_minmax(0,1fr)] min-[760px]:gap-x-6" aria-hidden>
        <div className="max-[759px]:hidden" />
        <div className="max-[759px]:hidden" />
        <div className="relative h-4">
          {months.map((m, i) => (
            <span
              key={m.iso}
              className={`absolute top-0 whitespace-nowrap ${LABEL} ${i % 2 ? "max-[759px]:hidden" : ""}`}
              style={{ left: `${x(m.iso)}%` }}
            >
              {m.label}
            </span>
          ))}
        </div>
      </div>
    </figure>
  );
}
