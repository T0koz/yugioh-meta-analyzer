import { api } from "@/lib/api";
import { fmtDate, fmtMonthShort, fmtNum } from "@/lib/format";
import { CardArt } from "@/components/card-art";
import { CardChip } from "@/components/card-chip";
import { PillLink } from "@/components/ds/control";
import { Em } from "@/components/ds/em";
import { DataFooter, PageHero } from "@/components/ds/page";
import { banStatusLabel } from "@/components/ds/tags";
import type { BanHistoryCard, BanHistoryList } from "@/types";

// TOK-55 — le Ban Radar rejoué la veille de chaque banlist, face à ce que Konami a fait.
// Tout est calculé par scripts/build_ban_history.py (mêmes chiffres que
// `build_ban_radar.py --backtest`) ; la page ne fait que des sommes et des positions.
// Rendu côté serveur, sans JavaScript : positions en pourcentage, textes en HTML.

const SOURCE = "decklists de tournoi TCG et OCG (yugiohmeta.com), banlists (Yugipedia)";
const LABEL = "font-mono text-[12px] leading-none text-muted-text tabular-nums";
const HEAD = "font-mono text-[11px] tracking-[0.08em] text-muted-text uppercase";

/** Clé d'adresse d'une liste : « tcg-2026-10-19 ». */
export function listKey(list: Pick<BanHistoryList, "format" | "effective_date">): string {
  return `${list.format.toLowerCase()}-${list.effective_date}`;
}

const CELL_LABEL = "col-start-1 row-start-1";
const CELL_RESULT = "col-start-2 row-start-1 text-right min-[760px]:col-start-3";
const CELL_TRACK = "col-span-2 col-start-1 row-start-2 min-[760px]:col-span-1 min-[760px]:col-start-2 min-[760px]:row-start-1";

const pos = (rank: number, n: number) => `${((rank - 0.5) / n) * 100}%`;

type Retained = BanHistoryList & {
  n_cards: number;
  median_rank: number;
  random_low: number;
  random_high: number;
  random_rank: number;
  baseline_median_rank: number;
  top_n_hits: number;
  baseline_top_n_hits: number;
  n_hits_ranked: number;
};

const isRetained = (list: BanHistoryList): list is Retained => list.retained && list.n_cards !== null;
const beatsChance = (l: Retained) => l.median_rank < l.random_low;
const beatsStaples = (l: Retained) => l.median_rank < l.baseline_median_rank;

// Colonnes : liste · piste · résultat. Sous 760 px, la piste passe sous le libellé.
const ROW =
  "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-4 gap-y-2 border-t border-line px-3 py-3 min-[760px]:grid-cols-[150px_minmax(0,1fr)_132px] min-[760px]:gap-x-5 min-[760px]:px-4";

function Track({ list, annotate }: { list: Retained; annotate: boolean }) {
  const n = list.n_cards;
  const hits = list.cards.filter((c): c is BanHistoryCard & { rank: number } => c.hit && c.rank !== null);
  return (
    <div
      className={`relative h-7 ${CELL_TRACK} ${annotate ? "mt-6 mb-5 min-[760px]:my-0" : ""}`}
      role="img"
      aria-label={`Liste ${list.format} du ${fmtDate(list.effective_date)} : rang médian des cartes touchées ${fmtNum(list.median_rank)} sur ${fmtNum(n)} ; hasard entre ${fmtNum(list.random_low)} et ${fmtNum(list.random_high)} ; staples les plus jouées ${fmtNum(list.baseline_median_rank)}.`}
    >
      {/* Piste complète : du 1er au dernier du classement de la veille. */}
      <span aria-hidden className="absolute inset-x-0 top-1/2 h-px bg-line-2" />
      {/* Bande du hasard : 90 % des tirages au sort tombent dedans. */}
      <span
        aria-hidden
        className="absolute inset-y-0.5 rounded-[2px] border-x border-soft/40 bg-soft/12"
        style={{ left: pos(list.random_low, n), width: `${((list.random_high - list.random_low) / n) * 100}%` }}
      />
      {annotate && (
        <span
          aria-hidden
          className={`absolute -top-5 -translate-x-1/2 whitespace-nowrap ${LABEL}`}
          style={{ left: pos(list.random_rank, n) }}
        >
          hasard
        </span>
      )}
      {/* Une graduation par carte touchée classée. */}
      {hits.map((card) => (
        <span
          key={card.card_name}
          aria-hidden
          className="absolute top-1/2 h-3 w-px -translate-y-1/2 bg-soft/70"
          style={{ left: pos(card.rank, n) }}
        />
      ))}
      <span
        aria-hidden
        className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-cat-2 bg-ink"
        style={{ left: pos(list.baseline_median_rank, n) }}
      />
      <span
        aria-hidden
        className="absolute top-1/2 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cat-1 ring-2 ring-ink"
        style={{ left: pos(list.median_rank, n) }}
      />
      {annotate && (
        <span
          aria-hidden
          className={`absolute top-8 whitespace-nowrap text-text ${LABEL}`}
          style={{ left: pos(list.median_rank, n) }}
        >
          ↑ rang médian
        </span>
      )}
    </div>
  );
}

// Libellé court de la place d'une liste par rapport au calage des poids ; rien pour les listes
// rejouées après coup, qui sont la majorité.
const SAMPLE_LABEL: Record<BanHistoryList["sample"], string | null> = {
  calage: "liste de calage",
  validation: "vue au calage",
  prospective: "après calage",
  retrospective: null,
};

function ListLabel({ list }: { list: BanHistoryList }) {
  const sample = list.retained ? SAMPLE_LABEL[list.sample] : null;
  return (
    <span className={`min-w-0 ${CELL_LABEL}`}>
      <span className="block font-medium tracking-[-0.01em] tabular-nums">{fmtDate(list.effective_date)}</span>
      <span className={`mt-1 block ${LABEL}`}>
        {list.format} · {fmtNum(list.n_hits)} touchées
      </span>
      {sample && (
        <span
          className={`mt-1.5 inline-block whitespace-nowrap rounded-[3px] border px-1.5 py-[3px] font-mono text-[11px] leading-none ${
            list.sample === "prospective" ? "border-line-2 text-text" : "border-line text-muted-text"
          }`}
        >
          {sample}
        </span>
      )}
    </span>
  );
}

function RetainedRow({ list, annotate }: { list: Retained; annotate: boolean }) {
  return (
    <li className={`${ROW} ${annotate ? "min-[760px]:pt-9 min-[760px]:pb-9" : ""}`}>
      <ListLabel list={list} />
      <Track list={list} annotate={annotate} />
      <span className={CELL_RESULT}>
        <span className="block font-mono text-[14px] font-medium tabular-nums">
          {fmtNum(list.median_rank)}
          <span className="font-normal text-muted-text"> / {fmtNum(list.n_cards)}</span>
        </span>
        <span className={`mt-1 block ${LABEL}`}>staples : {fmtNum(list.baseline_median_rank)}</span>
      </span>
    </li>
  );
}

function SkippedRow({ list, minDecks, minHits }: { list: BanHistoryList; minDecks: number; minHits: number }) {
  const reason =
    list.skip_reason === "decks"
      ? `écartée : ${fmtNum(list.n_decks)} decks dans la fenêtre, seuil ${fmtNum(minDecks)}`
      : `écartée : ${fmtNum(list.n_hits)} cartes touchées, seuil ${fmtNum(minHits)}`;
  return (
    <li className={ROW}>
      <ListLabel list={list} />
      <span className={`rounded-[2px] border border-dashed border-line-2 px-2.5 py-1.5 font-mono text-[12px] text-muted-text ${CELL_TRACK}`}>
        {reason}
      </span>
      <span className={`${CELL_RESULT} ${LABEL}`}>non classée</span>
    </li>
  );
}

function Legend() {
  return (
    <figcaption className={`flex flex-wrap items-center gap-x-5 gap-y-2 border-b border-line px-3 py-3 min-[760px]:px-4 ${LABEL}`}>
      <span className="inline-flex items-center gap-1.5">
        <span aria-hidden className="h-3 w-3 rounded-full bg-cat-1" />
        Ban Radar
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span aria-hidden className="h-3 w-3 rounded-full border-2 border-cat-2" />
        staples les plus jouées
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span aria-hidden className="h-3 w-5 rounded-[2px] border-x border-soft/40 bg-soft/12" />
        hasard (90 % des tirages)
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span aria-hidden className="h-3 w-px bg-soft/70" />
        une carte touchée
      </span>
    </figcaption>
  );
}

function Axis() {
  const ticks = [
    { at: 0, label: "1er" },
    { at: 25, label: "25 %" },
    { at: 50, label: "50 %" },
    { at: 75, label: "75 %" },
    { at: 100, label: "dernier" },
  ];
  return (
    <div className={`${ROW} border-t-0 py-2`} aria-hidden>
      <span className={`${HEAD} ${CELL_LABEL}`}>Liste</span>
      <span className={`relative h-4 ${CELL_TRACK}`}>
        {ticks.map((t) => (
          <span
            key={t.at}
            className={`absolute top-0 ${LABEL} ${t.at === 0 ? "" : t.at === 100 ? "-translate-x-full" : "-translate-x-1/2"}`}
            style={{ left: `${t.at}%` }}
          >
            {t.label}
          </span>
        ))}
      </span>
      <span className={`${HEAD} ${CELL_RESULT}`}>Rang médian</span>
    </div>
  );
}

function FormatChart({
  format,
  lists,
  minDecks,
  minHits,
  annotateFirst,
}: {
  format: "TCG" | "OCG";
  lists: BanHistoryList[];
  minDecks: number;
  minHits: number;
  annotateFirst: boolean;
}) {
  const firstRetained = lists.find(isRetained);
  return (
    <section aria-labelledby={`frise-${format}`} className="mt-8">
      <h2 id={`frise-${format}`} className="mb-3 text-[20px] font-medium tracking-[-0.02em]">
        {format}
      </h2>
      <figure className="overflow-hidden rounded-[6px] border border-line bg-ink-2">
        <Legend />
        <Axis />
        <ol>
          {lists.map((list) =>
            isRetained(list) ? (
              <RetainedRow key={listKey(list)} list={list} annotate={annotateFirst && list === firstRetained} />
            ) : (
              <SkippedRow key={listKey(list)} list={list} minDecks={minDecks} minHits={minHits} />
            ),
          )}
        </ol>
      </figure>
    </section>
  );
}

function Summary({ lists, topN }: { lists: BanHistoryList[]; topN: number }) {
  const rows = (["TCG", "OCG"] as const).map((format) => {
    const retained = lists.filter(isRetained).filter((l) => l.format === format);
    return {
      format,
      n: retained.length,
      chance: retained.filter(beatsChance).length,
      staples: retained.filter(beatsStaples).length,
      places: retained.length * topN,
      topHits: retained.reduce((sum, l) => sum + l.top_n_hits, 0),
      baselineTopHits: retained.reduce((sum, l) => sum + l.baseline_top_n_hits, 0),
    };
  });
  const cell = "border-t border-line px-3 py-3 text-right tabular-nums min-[760px]:px-4";
  return (
    <div className="mt-2 overflow-x-auto rounded-[6px] border border-line">
      <table className="w-full min-w-[560px] border-collapse text-[14px]">
        <caption className="sr-only">Bilan des banlists rejouées, par format</caption>
        <thead>
          <tr className={HEAD}>
            <th scope="col" className="px-3 py-2.5 text-left font-normal min-[760px]:px-4">Format</th>
            <th scope="col" className="px-3 py-2.5 text-right font-normal min-[760px]:px-4">Rang médian meilleur que le hasard</th>
            <th scope="col" className="px-3 py-2.5 text-right font-normal min-[760px]:px-4">Meilleur que les staples</th>
            <th scope="col" className="px-3 py-2.5 text-right font-normal min-[760px]:px-4">Top {topN} touché, Ban Radar</th>
            <th scope="col" className="px-3 py-2.5 text-right font-normal min-[760px]:px-4">Top {topN} touché, staples</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.format}>
              <th scope="row" className="border-t border-line px-3 py-3 text-left font-medium min-[760px]:px-4">
                {r.format}
              </th>
              <td className={cell}>
                {fmtNum(r.chance)} <span className="text-muted-text">listes sur {fmtNum(r.n)}</span>
              </td>
              <td className={cell}>
                {fmtNum(r.staples)} <span className="text-muted-text">sur {fmtNum(r.n)}</span>
              </td>
              <td className={cell}>
                {fmtNum(r.topHits)} <span className="text-muted-text">places sur {fmtNum(r.places)}</span>
              </td>
              <td className={cell}>
                {fmtNum(r.baselineTopHits)} <span className="text-muted-text">sur {fmtNum(r.places)}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StatusChange({ card }: { card: BanHistoryCard }) {
  if (!card.hit) return <span className="font-mono text-[12px] text-muted-text">non touchée</span>;
  return (
    <span className="font-mono text-[12px] whitespace-nowrap text-warn">
      {banStatusLabel(card.status_before)} → {banStatusLabel(card.status_after)}
    </span>
  );
}

function CardRow({ card, n, eager }: { card: BanHistoryCard; n: number; eager: boolean }) {
  const origin = card.rank === null ? null : (card.top_archetype ?? "Générique");
  return (
    <li className="grid grid-cols-[34px_minmax(0,1fr)_auto] items-center gap-x-3 border-t border-line px-3 py-2.5 min-[760px]:px-4">
      <CardArt src={card.image_url} name={card.card_name} eager={eager} />
      <span className="min-w-0">
        <span className="block truncate font-medium tracking-[-0.01em]">
          <CardChip name={card.card_name} subtitle={origin ?? undefined} variant="plain" />
        </span>
        <span className={`mt-1 block ${LABEL}`}>
          {card.rank === null ? "hors classement (moins de 5 decks)" : `${fmtNum(card.rank)}ᵉ sur ${fmtNum(n)}`}
          {origin && ` · ${origin}`}
        </span>
      </span>
      <StatusChange card={card} />
    </li>
  );
}

function ListDetail({ list, topN }: { list: Retained; topN: number }) {
  const top = list.cards.filter((c) => c.in_top);
  const hits = list.cards.filter((c) => c.hit);
  return (
    <section aria-labelledby="detail-liste" className="mt-6">
      <h3 id="detail-liste" className="text-[20px] font-medium tracking-[-0.02em]">
        {list.format}, liste du {fmtDate(list.effective_date)}
      </h3>
      <p className={`mt-2 ${LABEL}`}>
        classement du {fmtDate(list.as_of)} · {fmtNum(list.n_cards)} cartes · {fmtNum(list.n_decks)} decks sur 6 mois
      </p>
      <div className="mt-4 grid gap-5 min-[960px]:grid-cols-2">
        <div className="overflow-hidden rounded-[6px] border border-line bg-ink-2">
          <p className={`flex justify-between gap-3 px-3 py-2.5 min-[760px]:px-4 ${HEAD}`}>
            <span>Top {topN} de la veille</span>
            <span>{fmtNum(list.top_n_hits)} touchées</span>
          </p>
          <ol>
            {top.map((card) => (
              <CardRow key={card.card_name} card={card} n={list.n_cards} eager={false} />
            ))}
          </ol>
        </div>
        <div className="overflow-hidden rounded-[6px] border border-line bg-ink-2">
          <p className={`flex justify-between gap-3 px-3 py-2.5 min-[760px]:px-4 ${HEAD}`}>
            <span>Cartes touchées</span>
            <span>{fmtNum(hits.length)}</span>
          </p>
          <ol>
            {hits.map((card) => (
              <CardRow key={card.card_name} card={card} n={list.n_cards} eager={false} />
            ))}
          </ol>
        </div>
      </div>
      <DataFooter
        source={SOURCE}
        date={`classement reconstitué au ${fmtDate(list.as_of)}, decks des 6 mois précédents`}
        sample={`${fmtNum(list.n_decks)} decks, ${fmtNum(list.n_cards)} cartes classées, ${fmtNum(list.n_hits_ranked)} touchées classées sur ${fmtNum(list.n_hits)}`}
      />
    </section>
  );
}

function DataTable({ lists, topN }: { lists: BanHistoryList[]; topN: number }) {
  const td = "border-t border-line px-2.5 py-2 text-right tabular-nums";
  return (
    <details className="mt-4">
      <summary className="cursor-pointer font-mono text-[12px] text-muted-text">Tableau des données (toutes les listes)</summary>
      <div className="mt-3 overflow-x-auto rounded-[6px] border border-line">
        <table className="w-full min-w-[1040px] border-collapse font-mono text-[12px]">
          <thead>
            <tr className="text-muted-text">
              {["Liste", "Format", "Decks", "Cartes classées", "Touchées", "dont classées", "Rang médian", "Hasard (90 %)", "Staples", `Top ${topN}`, `Top ${topN}, staples`, "Top 10 %", "Top 25 %", "Calage"].map((h, i) => (
                <th key={h} scope="col" className={`px-2.5 py-2 font-normal ${i < 2 ? "text-left" : "text-right"}`}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {lists.map((l) => (
              <tr key={listKey(l)}>
                <th scope="row" className="border-t border-line px-2.5 py-2 text-left font-normal">
                  {l.effective_date}
                </th>
                <td className="border-t border-line px-2.5 py-2">{l.format}</td>
                <td className={td}>{fmtNum(l.n_decks)}</td>
                {isRetained(l) ? (
                  <>
                    <td className={td}>{fmtNum(l.n_cards)}</td>
                    <td className={td}>{fmtNum(l.n_hits)}</td>
                    <td className={td}>{fmtNum(l.n_hits_ranked)}</td>
                    <td className={td}>{fmtNum(l.median_rank)}</td>
                    <td className={td}>
                      {fmtNum(l.random_low)} à {fmtNum(l.random_high)}
                    </td>
                    <td className={td}>{fmtNum(l.baseline_median_rank)}</td>
                    <td className={td}>{fmtNum(l.top_n_hits)}</td>
                    <td className={td}>{fmtNum(l.baseline_top_n_hits)}</td>
                    <td className={td}>{fmtNum(l.top10pct_hits ?? 0)}</td>
                    <td className={td}>{fmtNum(l.top25pct_hits ?? 0)}</td>
                    <td className="border-t border-line px-2.5 py-2 text-right">{SAMPLE_LABEL[l.sample] ?? "rejouée après coup"}</td>
                  </>
                ) : (
                  <>
                    <td className={td}>—</td>
                    <td className={td}>{fmtNum(l.n_hits)}</td>
                    <td colSpan={9} className="border-t border-line px-2.5 py-2 text-left text-muted-text">
                      écartée ({l.skip_reason === "decks" ? "moins de 600 decks" : "moins de 5 cartes touchées"})
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}

export async function BanHistoryView({ selected, tabs }: { selected: string | undefined; tabs: React.ReactNode }) {
  const { lists, computed_at, top_n, min_decks, min_hits } = await api.banHistory();
  const retained = lists.filter(isRetained);

  const hero = (
    <PageHero
      eyebrow="Ban Center · Historique"
      title={
        <>
          Le classement de la veille, face aux <Em>banlists</Em> réelles.
        </>
      }
      aside={
        computed_at ? (
          <>
            Calcul du {fmtDate(computed_at)}
            <br />
            {fmtNum(retained.length)} listes rejouées · {fmtNum(lists.length - retained.length)} écartées
          </>
        ) : undefined
      }
      intro={
        retained.length
          ? `Ban Radar recalculé la veille de ${fmtNum(retained.length)} banlists TCG et OCG, de ${fmtMonthShort(retained[retained.length - 1].effective_date.slice(0, 7))} à ${fmtMonthShort(retained[0].effective_date.slice(0, 7))}, avec les seuls decks des 6 mois précédant l’entrée en vigueur, puis comparé aux cartes réellement restreintes.`
          : undefined
      }
    >
      {tabs}
    </PageHero>
  );

  if (!retained.length) {
    return (
      <>
        {hero}
        <p className="text-soft">Historique non calculé sur cette base.</p>
      </>
    );
  }

  const current = retained.find((l) => listKey(l) === selected) ?? retained[0];
  const firstDate = lists[lists.length - 1].effective_date;
  const lastDate = lists[0].effective_date;

  return (
    <>
      {hero}

      <h2 className="text-[20px] font-medium tracking-[-0.02em]">Bilan par format</h2>
      <Summary lists={lists} topN={top_n} />
      <DataFooter
        source={SOURCE}
        date={`calcul du ${fmtDate(computed_at)}, listes du ${fmtDate(firstDate)} au ${fmtDate(lastDate)}`}
        sample={`${fmtNum(retained.length)} listes retenues ; le seuil de ${fmtNum(min_decks)} decks et ${fmtNum(min_hits)} cartes touchées en écarte ${fmtNum(lists.length - retained.length)}`}
      />

      {(["TCG", "OCG"] as const).map((format) => (
        <FormatChart
          key={format}
          format={format}
          lists={lists.filter((l) => l.format === format)}
          minDecks={min_decks}
          minHits={min_hits}
          annotateFirst={format === "TCG"}
        />
      ))}
      <DataFooter
        source={SOURCE}
        date={`classements reconstitués la veille de chaque liste, calcul du ${fmtDate(computed_at)}`}
        sample={`${fmtNum(retained.length)} listes, 700 à 1 250 cartes classées par liste`}
      >
        position de gauche à droite : du premier au dernier du classement
      </DataFooter>
      <DataTable lists={lists} topN={top_n} />

      <section aria-labelledby="detail-titre" className="mt-14">
        <h2 id="detail-titre" className="text-[clamp(24px,3vw,32px)] font-medium tracking-[-0.03em]">
          Top {top_n} prévu et cartes touchées, liste par liste
        </h2>
        {(["TCG", "OCG"] as const).map((format) => (
          <nav key={format} aria-label={`Listes ${format}`} className="mt-4 flex flex-wrap items-center gap-2">
            <span className={`w-10 ${HEAD}`}>{format}</span>
            {retained
              .filter((l) => l.format === format)
              .map((l) => (
                <PillLink
                  key={listKey(l)}
                  href={
                    l === retained[0] ? "/ban?tab=historique#detail-titre" : `/ban?tab=historique&liste=${listKey(l)}#detail-titre`
                  }
                  current={l === current}
                  scroll={false}
                >
                  {fmtMonthShort(l.effective_date.slice(0, 7))}
                </PillLink>
              ))}
          </nav>
        ))}
        <ListDetail list={current} topN={top_n} />
      </section>

      <details className="mt-10 max-w-[72ch]">
        <summary className="cursor-pointer font-mono text-[12px] text-muted-text">Méthode</summary>
        <div className="mt-3 grid gap-2 text-[14px] text-soft">
          <p>
            Pour chaque liste, le score est recalculé avec les seules decklists des 6 mois qui précèdent son entrée en
            vigueur. Une carte compte comme touchée quand son statut se durcit (illimitée vers semi-limitée, limitée
            ou interdite, et ainsi de suite).
          </p>
          <p>
            Une liste est écartée sous {fmtNum(min_decks)} decks dans la fenêtre ou sous {fmtNum(min_hits)} cartes
            touchées : en dessous, le classement ne se distingue pas du hasard.
          </p>
          <p>
            Les poids du score ont été choisis en août 2026 sur la liste TCG du 18 mai 2026. Seules les listes
            marquées « après calage » ({fmtNum(retained.filter((l) => l.sample === "prospective").length)} sur{" "}
            {fmtNum(retained.length)}) sont postérieures à ce choix ; les autres sont rejouées après coup.
          </p>
          <p>
            Le classement est celui de la veille de l’entrée en vigueur, qui suit l’annonce de une à trois semaines :
            les decks joués entre les deux sont dans la fenêtre. Les fenêtres de 6 mois de deux listes voisines se
            chevauchent : les listes ne sont pas des essais indépendants.
          </p>
        </div>
      </details>
    </>
  );
}
