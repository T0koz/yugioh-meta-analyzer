import type { Metadata } from "next";
import Link from "next/link";
import { api } from "@/lib/api";
import { fmtDate, fmtMonthRange, fmtNum, fmtRank } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { SITE_FACTS } from "@/lib/site-facts";
import { CardArt } from "@/components/card-art";
import { CardChip } from "@/components/card-chip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { DataFooter, Page, PageHero, StatBand } from "@/components/ds/page";
import { BanStatus, Tag } from "@/components/ds/tags";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BoutiqueSignal, CardPriceHistory, PriceHistoryResponse } from "@/types";
import { ArrivalTimeline, LABEL_TONE, type ArchetypeRow } from "./ArrivalTimeline";
import { PriceChart, SnapshotStrip, fmtDayShort, fmtEuro } from "./PriceChart";

const SIGNAL_SOURCE = "decklists OCG (yugiohmeta.com), vues Cardmarket (YGOPRODeck)";
const MONO = "font-mono text-[12px] leading-[1.6] text-muted-text tabular-nums";
const SUMMARY =
  "cursor-pointer font-mono text-[12px] tracking-[0.06em] text-muted-text uppercase transition-colors duration-200 hover:text-text";

export async function generateMetadata(): Promise<Metadata> {
  const { data, label_rule, computed_at } = await api.boutiqueSignals();
  const archetypes = new Set(data.map((s) => s.archetype)).size;
  const cards = new Set(data.map((s) => s.card_name)).size;
  const computed = computed_at ? `, calcul du ${fmtDate(computed_at)}` : "";
  const rule = label_rule
    ? ` Libellé : rang parmi ${label_rule.population} archétypes OCG${label_rule.provisional ? ", seuils provisoires, non validés hors échantillon" : ""}.`
    : "";
  return pageMetadata({
    title: "Signaux boutique",
    description: `${archetypes} archétypes joués en OCG, pas encore arrivés en TCG, et le prix Cardmarket de ${cards} cartes de leurs decks${computed}.${rule}`,
    path: "/boutique",
  });
}

interface ArchetypeGroup extends ArchetypeRow {
  signals: BoutiqueSignal[];
}

/** Un groupe par archétype, dans l'ordre du rang OCG (sans rang : à la fin). Cartes dans l'ordre de l'API. */
function groupByArchetype(data: BoutiqueSignal[]): ArchetypeGroup[] {
  const groups = new Map<string, ArchetypeGroup>();
  for (const s of data) {
    const group = groups.get(s.archetype) ?? {
      archetype: s.archetype,
      slug: s.archetype_slug,
      label: s.signal_label,
      rank: s.archetype_rank,
      windowStart: s.tcg_window_start,
      windowEnd: s.tcg_window_end,
      cards: 0,
      signals: [],
    };
    group.signals.push(s);
    group.cards = group.signals.length;
    groups.set(s.archetype, group);
  }
  return [...groups.values()].sort((a, b) => (a.rank ?? Infinity) - (b.rank ?? Infinity));
}

function priceSummary(history: CardPriceHistory): string {
  const first = history.points[0];
  const last = history.points[history.points.length - 1];
  const n = history.points.length;
  return `${n} relevé${n > 1 ? "s" : ""}, ${fmtDayShort(first.date)} → ${fmtDate(last.date)} · premier : ${fmtEuro(first.price)}`;
}

function PriceTable({ group, prices }: { group: ArchetypeGroup; prices: Map<string, CardPriceHistory> }) {
  const cards = group.signals.map((s) => s.card_name);
  const dates = [...new Set(cards.flatMap((c) => prices.get(c)?.points.map((p) => p.date) ?? []))].sort();
  if (!dates.length) return null;
  const value = (card: string, date: string) => prices.get(card)?.points.find((p) => p.date === date)?.price;
  return (
    <details className="mt-4">
      <summary className={SUMMARY}>Relevés de prix en tableau</summary>
      <div className="mt-3 overflow-x-auto rounded-[6px] border border-line">
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead>Date du relevé</TableHead>
              {cards.map((c) => (
                <TableHead key={`${group.archetype}-${c}`} className="text-right">
                  {c}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {dates.map((date) => (
              <TableRow key={date}>
                <TableCell className="font-mono text-[12px] whitespace-nowrap">{fmtDate(date)}</TableCell>
                {cards.map((c) => {
                  const price = value(c, date);
                  return (
                    <TableCell key={`${group.archetype}-${c}`} className="text-right font-mono text-[12px] tabular-nums">
                      {price != null ? fmtEuro(price) : "—"}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </details>
  );
}

function ArchetypeSection({
  group,
  prices,
  response,
  population,
}: {
  group: ArchetypeGroup;
  prices: Map<string, CardPriceHistory>;
  response: PriceHistoryResponse;
  population: number | null;
}) {
  const window = fmtMonthRange(group.windowStart, group.windowEnd);
  const { period_start: start, period_end: end } = response;
  return (
    <section id={group.slug} className="mt-14 scroll-mt-24" aria-labelledby={`titre-${group.slug}`}>
      <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-3 border-b border-line pb-4">
        <div className="flex flex-wrap items-center gap-3">
          <h2 id={`titre-${group.slug}`} className="text-[clamp(24px,3vw,32px)] leading-none font-medium tracking-[-0.03em]">
            {group.archetype}
          </h2>
          {group.label && <Tag tone={LABEL_TONE[group.label]}>{group.label.toUpperCase()}</Tag>}
        </div>
        <p className={MONO}>
          {group.rank != null && population != null && `${fmtRank(group.rank)} sur ${population} archétypes OCG · `}
          {window ? `arrivée en TCG : ${window}, 8 fois sur 10` : "fenêtre d’arrivée indisponible"} ·{" "}
          <Link
            href={`/archetype/${group.slug}`}
            className="text-soft underline decoration-line-2 underline-offset-4 transition-colors duration-200 hover:text-text hover:decoration-signal-hi"
          >
            page de l’archétype
          </Link>
        </p>
      </header>

      <ul className="mt-5 grid gap-4 min-[760px]:grid-cols-2 min-[1100px]:grid-cols-3">
        {group.signals.map((s) => {
          const history = prices.get(s.card_name);
          const last = history?.points.at(-1);
          return (
            <li key={`${s.archetype}-${s.card_name}`} className="flex flex-col rounded-[6px] border border-line bg-ink-3 p-4">
              <div className="mb-4 flex items-start gap-3">
                <CardArt src={s.image_url} name={s.card_name} />
                <div className="flex min-w-0 flex-col items-start gap-1.5">
                  <CardChip name={s.card_name} subtitle={s.archetype} variant="plain" className="font-medium tracking-[-0.01em]" />
                  {s.ban_tcg && <BanStatus status={s.ban_tcg} />}
                </div>
                {last && (
                  <p className="ml-auto shrink-0 text-right">
                    <span className="block text-[20px] leading-none font-medium tracking-[-0.02em] tabular-nums">{fmtEuro(last.price)}</span>
                    <span className={`mt-1 block ${MONO}`}>{fmtDayShort(last.date)}</span>
                  </p>
                )}
              </div>
              {history && start && end ? (
                <PriceChart history={history} periodStart={start} periodEnd={end} maxStepDays={response.max_step_days} />
              ) : (
                <p className={`${MONO} grow`}>
                  Aucun relevé de prix pour cette carte. Prix du calcul du signal : {fmtEuro(s.cm_price)}.
                </p>
              )}
              <p className={`mt-3 border-t border-line pt-2 ${MONO}`}>
                Cardmarket via YGOPRODeck · {history ? priceSummary(history) : "aucun relevé"}
              </p>
            </li>
          );
        })}
      </ul>

      <PriceTable group={group} prices={prices} />
      <DataFooter
        source={`${response.source} ; signal : ${SIGNAL_SOURCE}`}
        date={start && end ? `relevés du ${fmtDate(start)} au ${fmtDate(end)}` : "aucun relevé de prix servi"}
        sample={`${fmtNum(group.signals.length)} carte${group.signals.length > 1 ? "s" : ""}`}
      >
        bandes grises : plus de {response.max_step_days} jours sans relevé, rien n’y est tracé
      </DataFooter>
    </section>
  );
}

export default async function BoutiquePage() {
  const [{ data, label_rule, computed_at }, prices] = await Promise.all([api.boutiqueSignals(), api.boutiquePrices()]);
  const groups = groupByArchetype(data);
  const cardCount = new Set(data.map((s) => s.card_name)).size;
  const priceByCard = new Map(prices.cards.map((c) => [c.card_name, c]));
  const snapshotDates = [...new Set(prices.cards.flatMap((c) => c.points.map((p) => p.date)))].sort();
  const computed = computed_at ? `au ${fmtDate(computed_at)}` : "à une date de calcul inconnue";

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          eyebrow="Boutique · OCG → TCG"
          title={
            <>
              Archétypes joués en OCG, <Em>pas encore</Em> arrivés en TCG.
            </>
          }
          intro={`${groups.length} archétypes joués en OCG ${computed}, dont au moins 3 cartes clés ne sont pas sorties en TCG, et le prix Cardmarket de ${cardCount} cartes de leurs decks${prices.snapshot_count ? ` (${prices.snapshot_count} relevés, ${prices.period_start ? fmtDayShort(prices.period_start) : ""} → ${prices.period_end ? fmtDate(prices.period_end) : ""})` : ""}.${label_rule ? ` Libellé : rang de l’archétype parmi les ${label_rule.population} archétypes OCG${label_rule.provisional ? ", seuils provisoires, non validés hors échantillon" : ""}.` : ""}`}
        >
          <StatBand
            stats={[
              { value: fmtNum(groups.length), label: "Archétypes" },
              { value: fmtNum(cardCount), label: "Cartes" },
              { value: fmtNum(prices.snapshot_count), label: "Relevés de prix" },
              {
                value: fmtNum(SITE_FACTS.ocgTcgCorrelation, 2),
                label: `Corrélation OCG → TCG, IC 95 % ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[0], 2)} à ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[1], 2)}`,
              },
            ]}
          />
          <p className={`mt-4 max-w-[80ch] ${MONO}`}>
            {`Corrélation entre le score d’un archétype en OCG et son score en TCG ${SITE_FACTS.ocgTcgLagRange} plus tard, sur ${SITE_FACTS.ocgTcgArchetypes} archétypes. Signal de juin 2026 : ses cartes ont baissé de 35 % contre 1 % pour le marché.`}
          </p>
        </PageHero>

        <h2 className="mb-4 text-[20px] font-medium tracking-[-0.02em]">Rang en OCG et arrivée en TCG</h2>
        <ArrivalTimeline rows={groups} rule={label_rule} computedAt={computed_at} />
        <DataFooter
          source={SIGNAL_SOURCE}
          date={computed_at ? `calcul du ${fmtDate(computed_at)}` : "date de calcul inconnue"}
          sample={label_rule ? `${fmtNum(groups.length)} archétypes sur ${label_rule.population} suivis en OCG` : `${fmtNum(groups.length)} archétypes`}
        >
          fenêtre d’arrivée : délai mesuré sur 1 897 cartes, 2022 à 2025, non vérifié sur des cas nouveaux
        </DataFooter>

        {snapshotDates.length > 0 && prices.period_start && prices.period_end && (
          <>
            <h2 className="mt-14 mb-4 text-[20px] font-medium tracking-[-0.02em]">Dates des relevés de prix</h2>
            <SnapshotStrip
              dates={snapshotDates}
              periodStart={prices.period_start}
              periodEnd={prices.period_end}
              maxStepDays={prices.max_step_days}
            />
            <DataFooter
              source={prices.source}
              date={`du ${fmtDate(prices.period_start)} au ${fmtDate(prices.period_end)}`}
              sample={`${fmtNum(snapshotDates.length)} dates`}
            >
              relevés pris à la main avant novembre 2026
            </DataFooter>
          </>
        )}

        {groups.map((group) => (
          <ArchetypeSection
            key={group.archetype}
            group={group}
            prices={priceByCard}
            response={prices}
            population={label_rule?.population ?? null}
          />
        ))}

        <details className="mt-14">
          <summary className={SUMMARY}>Tous les signaux en tableau</summary>
          <div className="mt-3 overflow-x-auto rounded-[6px] border border-line">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Archétype</TableHead>
                  <TableHead>Signal</TableHead>
                  <TableHead className="text-right">Arrivée TCG (8 fois sur 10)</TableHead>
                  <TableHead>Carte</TableHead>
                  <TableHead className="text-right">Dernier prix Cardmarket</TableHead>
                  <TableHead>Banlist TCG</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {groups.flatMap((g) =>
                  g.signals.map((s) => {
                    const last = priceByCard.get(s.card_name)?.points.at(-1);
                    return (
                      <TableRow key={`${s.archetype}-${s.card_name}`}>
                        <TableCell className="text-[14px]">{s.archetype}</TableCell>
                        <TableCell className="font-mono text-[12px] whitespace-nowrap">
                          {s.signal_label ?? "—"}
                          {s.archetype_rank != null && label_rule && ` · ${fmtRank(s.archetype_rank)} sur ${label_rule.population}`}
                        </TableCell>
                        <TableCell className="text-right font-mono text-[12px] whitespace-nowrap">
                          {fmtMonthRange(s.tcg_window_start, s.tcg_window_end) ?? "—"}
                        </TableCell>
                        <TableCell className="text-[14px]">{s.card_name}</TableCell>
                        <TableCell className="text-right font-mono text-[12px] whitespace-nowrap tabular-nums">
                          {last ? `${fmtEuro(last.price)} (${fmtDayShort(last.date)})` : `${fmtEuro(s.cm_price)} (calcul)`}
                        </TableCell>
                        <TableCell>{s.ban_tcg ? <BanStatus status={s.ban_tcg} /> : <span className="font-mono text-[12px] text-faint">—</span>}</TableCell>
                      </TableRow>
                    );
                  }),
                )}
              </TableBody>
            </Table>
          </div>
        </details>
      </Page>
    </HoverPreviewProvider>
  );
}
