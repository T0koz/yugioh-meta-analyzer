import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { artCropUrl } from "@/lib/card-images";
import { fmtCopies, fmtDate, fmtNum, fmtPct, fmtPlacement, fmtWindow } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { CardArt, CardImage } from "@/components/card-art";
import { CardChip } from "@/components/card-chip";
import { ButtonLink, controlClass } from "@/components/ds/control";
import { DataFooter, Eyebrow, Meter, Page, StatBand } from "@/components/ds/page";
import { Tag, TierTag } from "@/components/ds/tags";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Reveal } from "@/components/reveal";
import { PageTransition } from "@/components/view-transitions";
import type { CardRole, DeckCardStat, DeckProfileRule, DeckResponse, RecentDeck, Zone } from "@/types";

const SOURCE = "decklists de tournoi TCG légales à la date du tournoi, yugiohmeta.com";
const H2 = "text-[clamp(22px,2.6vw,30px)] leading-tight font-medium tracking-[-0.03em]";
const MONO_LABEL = "font-mono text-[12px] uppercase tracking-[0.08em] text-muted-text";

// Une ligne de définition par zone : la page se lit sans connaître le jeu.
const ZONES: Record<Zone, { title: string; rule: string }> = {
  main: { title: "Main deck", rule: "40 à 60 cartes, la pioche" },
  extra: { title: "Extra deck", rule: "15 cartes au plus, tenues à part et posées en cours de partie" },
  side: { title: "Side deck", rule: "15 cartes au plus, échangées entre deux manches" },
};

type Params = { params: Promise<{ archetype: string }> };

// Construites d'avance : les archétypes à fiche. Les autres (listes seules) sont rendues
// à la première visite ; un slug sans liste dans la fenêtre donne une vraie 404.
export async function generateStaticParams() {
  const { data } = await api.decks();
  return data.filter((d) => d.has_profile).map((d) => ({ archetype: d.slug }));
}

const pct = (share: number) => fmtPct(share * 100, 0);
const byRole = (cards: DeckCardStat[], role: CardRole | null) => cards.filter((c) => c.role === role);
const copies = (cards: DeckCardStat[]) => cards.reduce((sum, c) => sum + c.median_copies, 0);

function describe(d: DeckResponse): string {
  const period = fmtWindow(d.window);
  if (!d.has_profile) {
    return `${d.archetype} : ${fmtNum(d.decks)} ${d.decks > 1 ? "listes" : "liste"} de tournoi TCG sur ${fmtNum(d.window.n_decks)} decks, ${period}. Sous ${d.rule.min_decks} listes, aucune part calculée : contenu des listes relevées.`;
  }
  const base = byRole(d.zones.find((z) => z.zone === "main")?.cards ?? [], "base");
  return `${d.archetype} : composition relevée sur ${fmtNum(d.decks)} listes de tournoi TCG, ${period}. ${base.length} cartes de base au main deck (au moins ${pct(d.rule.base_min_share)} des listes), ${fmtCopies(copies(base))} exemplaires.`;
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { archetype } = await params;
  const deck = await api.deck(archetype);
  if (!deck) return { title: "Deck introuvable", robots: { index: false, follow: false } };
  // Toute variante de casse rend la même page : l'adresse canonique est le slug servi par l'API.
  return pageMetadata({
    title: `Deck ${deck.archetype} : composition`,
    description: describe(deck),
    path: `/decks/${deck.slug}`,
  });
}

function CardRows({ cards, nDecks, tone }: { cards: DeckCardStat[]; nDecks: number; tone: "signal" | "soft" }) {
  return cards.map((card) => (
    <tr key={card.card_name} className="border-t border-line transition-colors duration-200 hover:bg-ink-3">
      <td className="py-2 pr-3 pl-3 min-[760px]:pl-4">
        <span className="flex items-center gap-3">
          <CardArt src={card.image_url} name={card.card_name} />
          <CardChip
            name={card.card_name}
            variant="plain"
            className="min-w-0 text-[14px] leading-snug font-medium tracking-[-0.01em] break-words"
          />
        </span>
      </td>
      <td className="py-2 text-right whitespace-nowrap min-[760px]:px-3">
        <span className="flex items-center justify-end gap-6">
          {/* La barre vit dans la cellule de la part : une colonne masquée décale un tableau à largeurs fixes. */}
          <span className="hidden min-w-0 flex-1 min-[760px]:block">
            <Meter value={card.share} max={1} tone={tone} />
          </span>
          <span className="w-[98px] shrink-0">
            <span className="block font-mono text-[15px] font-medium tabular-nums">{pct(card.share)}</span>
            <span className="block font-mono text-[12px] text-muted-text tabular-nums">
              {fmtNum(card.n_lists)} sur {fmtNum(nDecks)}
            </span>
          </span>
        </span>
      </td>
      <td className="py-2 pr-3 text-right font-mono text-[15px] font-medium tabular-nums min-[760px]:pr-4">
        ×{fmtCopies(card.median_copies)}
      </td>
    </tr>
  ));
}

function GroupHeader({ label, rule, cards }: { label: string; rule: string; cards: DeckCardStat[] }) {
  return (
    <tr className="border-t border-line bg-ink-3">
      <th colSpan={3} scope="colgroup" className="px-3 py-2.5 text-left font-normal min-[760px]:px-4">
        <span className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
          <Tag tone={label === "DE BASE" ? "strong" : "outline"}>{label}</Tag>
          <span className="font-mono text-[12px] text-soft">{rule}</span>
          <span className="ml-auto font-mono text-[12px] text-muted-text tabular-nums">
            {fmtNum(cards.length)} {cards.length > 1 ? "cartes" : "carte"} · {fmtCopies(copies(cards))} exemplaires
          </span>
        </span>
      </th>
    </tr>
  );
}

function ZoneSection({
  zone,
  cards,
  deck,
  rule,
  footDate,
}: {
  zone: Zone;
  cards: DeckCardStat[];
  deck: DeckResponse;
  rule: DeckProfileRule;
  footDate: string;
}) {
  const base = byRole(cards, "base");
  const flex = byRole(cards, "appoint");
  const rare = byRole(cards, null);
  const basePct = pct(rule.base_min_share);
  const flexPct = pct(rule.flex_min_share);
  const { title, rule: zoneRule } = ZONES[zone];

  return (
    <section aria-labelledby={`h-${zone}`} className="mt-14 scroll-mt-24" id={zone}>
      <div className="flex flex-wrap items-baseline justify-between gap-x-5 gap-y-1">
        <h2 id={`h-${zone}`} className={H2}>
          {title}
        </h2>
        <p className={MONO_LABEL}>{zoneRule}</p>
      </div>

      {base.length + flex.length === 0 ? (
        <p className="mt-5 rounded-[6px] border border-line bg-ink-2 px-4 py-5 text-[14px] text-soft">
          Aucune carte dans {flexPct} des {fmtNum(deck.decks)} listes ou plus.
        </p>
      ) : (
        <div className="mt-5 overflow-hidden rounded-[6px] border border-line bg-ink-2">
          <table className="w-full table-fixed border-collapse text-left">
            {/* Largeurs fixes : sans elles, la colonne du nom se réduit à un mot par ligne à 375 px. */}
            <colgroup>
              <col />
              <col className="w-[98px] min-[760px]:w-[44%]" />
              <col className="w-[58px] min-[760px]:w-[130px]" />
            </colgroup>
            <caption className="sr-only">
              {title} de {deck.archetype} : part des {fmtNum(deck.decks)} listes qui jouent chaque carte et nombre
              d’exemplaires médian
            </caption>
            <thead>
              <tr className="font-mono text-[11px] uppercase tracking-[0.08em] text-muted-text">
                <th scope="col" className="px-3 py-2.5 font-normal min-[760px]:px-4">
                  Carte
                </th>
                <th scope="col" className="py-2.5 text-right font-normal min-[760px]:px-3">
                  Part des listes
                </th>
                <th scope="col" className="py-2.5 pr-3 text-right font-normal min-[760px]:pr-4">
                  <abbr title="Exemplaires" className="no-underline min-[760px]:hidden">
                    Ex.
                  </abbr>
                  <span className="hidden min-[760px]:inline">Exemplaires</span>
                </th>
              </tr>
            </thead>
            {base.length > 0 && (
              <tbody>
                <GroupHeader label="DE BASE" rule={`au moins ${basePct} des listes`} cards={base} />
                <CardRows cards={base} nDecks={deck.decks} tone="signal" />
              </tbody>
            )}
            {flex.length > 0 && (
              <tbody>
                <GroupHeader label="D’APPOINT" rule={`de ${flexPct} à moins de ${basePct} des listes`} cards={flex} />
                <CardRows cards={flex} nDecks={deck.decks} tone="soft" />
              </tbody>
            )}
          </table>
        </div>
      )}
      <DataFooter source={SOURCE} date={footDate} sample={`${fmtNum(deck.decks)} listes ${deck.archetype}`} uncertainty={"pas d’intervalle : à 8 listes il serait trop large pour être lu ; chaque pourcentage est donné avec son effectif"}>
        part : listes qui jouent la carte sur {fmtNum(deck.decks)} ; exemplaires : médiane parmi ces listes
      </DataFooter>

      {rare.length > 0 && (
        <details className="group mt-4">
          <summary className={controlClass({ size: "sm" })}>
            {fmtNum(rare.length)} autres cartes, moins de {flexPct} des listes
            <span aria-hidden className="font-mono text-muted-text transition-transform group-open:rotate-45">
              +
            </span>
          </summary>
          <ul className="mt-3 gap-x-8 [column-width:260px]">
            {rare.map((card) => (
              <li
                key={card.card_name}
                className="flex break-inside-avoid items-baseline justify-between gap-3 border-b border-line py-1.5 text-[14px] text-soft"
              >
                <span className="min-w-0 [overflow-wrap:anywhere]">{card.card_name}</span>
                <span className="shrink-0 font-mono text-[12px] text-muted-text tabular-nums">
                  {fmtNum(card.n_lists)} sur {fmtNum(deck.decks)} · ×{fmtCopies(card.median_copies)}
                </span>
              </li>
            ))}
          </ul>
        </details>
      )}
    </section>
  );
}

// Repliées : cinq listes ouvertes ajoutent 15 000 px à la page mobile.
function RecentList({ deck }: { deck: RecentDeck }) {
  return (
    <details className="group border-t border-line first:border-t-0">
      <summary className="flex cursor-pointer list-none flex-wrap items-center gap-x-4 gap-y-1.5 px-3 py-3.5 transition-colors duration-200 hover:bg-ink-3 min-[760px]:px-4 [&::-webkit-details-marker]:hidden">
        <Tag tone={deck.placement <= 1 ? "strong" : deck.placement <= 4 ? "outline" : "neutral"}>
          {fmtPlacement(deck.placement).toUpperCase()}
        </Tag>
        <span className="text-[15px] font-medium tracking-[-0.01em]">{deck.tournament_type ?? "Tournoi non précisé"}</span>
        <span className="font-mono text-[12px] text-muted-text tabular-nums">
          {fmtDate(deck.date)}
          {deck.author && deck.author !== "Player" ? ` · ${deck.author}` : ""}
        </span>
        <span aria-hidden className="ml-auto font-mono text-muted-text transition-transform group-open:rotate-45">
          +
        </span>
      </summary>
      <div className="grid gap-6 px-3 pt-1 pb-5 min-[760px]:grid-cols-[minmax(0,2fr)_minmax(0,1fr)_minmax(0,1fr)] min-[760px]:px-4">
        {deck.zones.map(({ zone, n_cards, cards }) => (
          <div key={zone}>
            <h3 className={MONO_LABEL}>
              {ZONES[zone].title} · {fmtNum(n_cards)} cartes
            </h3>
            <ul className={`mt-2.5 gap-x-6 ${zone === "main" ? "min-[520px]:columns-2" : ""}`}>
              {cards.map((card) => (
                <li key={card.card_name} className="flex break-inside-avoid items-center gap-2.5 py-1 text-[14px]">
                  <span className="w-5 shrink-0 text-right font-mono text-[13px] text-muted-text tabular-nums">
                    {card.amount}×
                  </span>
                  <CardArt src={card.image_url} name={card.card_name} />
                  <span className="min-w-0 leading-snug [overflow-wrap:anywhere]">{card.card_name}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </details>
  );
}

export default async function DeckPage({ params }: Params) {
  const { archetype } = await params;
  const d = await api.deck(archetype);
  if (!d) notFound();

  const period = fmtWindow(d.window);
  const footDate = `${period}, calcul du ${fmtDate(d.computed_at)}`;
  const main = d.zones.find((z) => z.zone === "main")?.cards ?? [];
  const mainBase = byRole(main, "base");
  const mainFlex = byRole(main, "appoint");
  const basePct = pct(d.rule.base_min_share);
  const first = d.recent_decks[0];
  const last = d.recent_decks[d.recent_decks.length - 1];

  const stats = [
    { value: fmtNum(d.decks), label: `${d.decks > 1 ? "Listes" : "Liste"} sur ${fmtNum(d.window.n_decks)} decks` },
    { value: fmtPct(d.share * 100), label: "Part des decks TCG" },
  ];
  if (d.has_profile) {
    stats.push(
      { value: fmtNum(mainBase.length), label: "Cartes de base au main deck" },
      { value: fmtCopies(copies(mainBase)), label: "Exemplaires de base, sur 40 à 60" }
    );
  }

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <PageTransition id={`deck-${d.slug}`}>
        <Page>
          <header className="relative isolate pt-8 pb-4">
            {d.image_url && (
              <span
                aria-hidden
                className="pointer-events-none absolute inset-x-[calc(var(--gutter)*-1)] top-0 -z-10 hidden h-[320px] [mask-image:linear-gradient(180deg,rgb(0_0_0/0.3),transparent)] min-[760px]:block"
              >
                <CardImage
                  src={artCropUrl(d.image_url)}
                  alt=""
                  fill
                  sizes="(min-width: 1200px) 1200px, 100vw"
                  className="object-cover object-[center_28%] [mask-image:linear-gradient(90deg,transparent,rgb(0_0_0/0.5)_45%,black)]"
                />
              </span>
            )}

            <Link
              href="/decks"
              className="inline-flex items-center gap-2 font-mono text-[12px] uppercase tracking-[0.1em] text-muted-text transition-colors duration-200 hover:text-text"
            >
              <span aria-hidden>←</span> Decks
            </Link>

            <div className="mt-8">
              <Eyebrow className="enter">
                Composition · TCG · {period} · {fmtNum(d.decks)} {d.decks > 1 ? "listes" : "liste"}
              </Eyebrow>
              <h1 className="enter mt-[18px] text-[clamp(34px,6.2vw,80px)] leading-[0.98] font-medium tracking-[-0.045em] text-balance [--i:1] [overflow-wrap:anywhere]">
                {d.archetype}
              </h1>
              <div className="enter mt-5 flex flex-wrap items-center gap-x-4 gap-y-3 [--i:2]">
                {d.tier && <TierTag tier={d.tier} />}
                <ButtonLink href={`/archetype/${d.slug}`} size="sm">
                  Part de méta par mois
                </ButtonLink>
                {d.has_profile && (
                  <nav aria-label="Zones du deck" className="flex flex-wrap gap-2">
                    {d.zones.map(({ zone }) => (
                      <a key={zone} href={`#${zone}`} className={controlClass({ variant: "ghost", size: "sm" })}>
                        {ZONES[zone].title}
                      </a>
                    ))}
                    <a href="#listes" className={controlClass({ variant: "ghost", size: "sm" })}>
                      Listes récentes
                    </a>
                  </nav>
                )}
              </div>
            </div>

            <StatBand stats={stats} />
            <DataFooter
              source={SOURCE}
              date={footDate}
              sample={`${fmtNum(d.window.n_decks)} decks`}
              uncertainty={
                d.has_profile
                  ? "pas d’intervalle : à 8 listes il serait trop large pour être lu ; chaque pourcentage est donné avec son effectif"
                  : "sous 8 listes, aucune part n’est calculée : seules les listes sont montrées"
              }
            >
              {d.has_profile ? (
                <>
                  de base : dans au moins {basePct} des listes ; d’appoint : de {pct(d.rule.flex_min_share)} à moins de{" "}
                  {basePct} ({fmtNum(mainFlex.length)} cartes au main deck) ; exemplaires de base : somme des médianes
                </>
              ) : (
                <>
                  sous {d.rule.min_decks} listes, aucune part n’est calculée : seules les listes relevées sont affichées
                </>
              )}
            </DataFooter>
          </header>

          {d.zones.map(({ zone, cards }) => (
            <ZoneSection key={zone} zone={zone} cards={cards} deck={d} rule={d.rule} footDate={footDate} />
          ))}

          {d.recent_decks.length > 0 && (
            <Reveal className="mt-16">
              <section aria-labelledby="h-listes" id="listes" className="scroll-mt-24">
                <h2 id="h-listes" className={H2}>
                  Listes récentes
                </h2>
                <div className="mt-5 overflow-hidden rounded-[6px] border border-line bg-ink-2">
                  {d.recent_decks.map((deck) => (
                    <RecentList key={deck.deck_id} deck={deck} />
                  ))}
                </div>
                <DataFooter
                  source={SOURCE}
                  date={first.date === last.date ? `tournoi du ${fmtDate(first.date)}` : `tournois du ${fmtDate(last.date)} au ${fmtDate(first.date)}`}
                  sample={`${fmtNum(d.recent_decks.length)} ${d.recent_decks.length > 1 ? "listes les plus récentes" : "liste"} sur ${fmtNum(d.decks)}`}
                  uncertainty="aucune : listes et résultats relevés tels quels"
                >
                  résultat : place finale du joueur dans le tournoi ; ordre : date du tournoi, puis meilleur résultat
                </DataFooter>
              </section>
            </Reveal>
          )}
        </Page>
      </PageTransition>
    </HoverPreviewProvider>
  );
}
