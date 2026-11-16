import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import { artCropUrl } from "@/lib/card-images";
import { fmtDate, fmtMonthRange, fmtMonthShort, fmtNum, fmtPct, fmtRank } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { CardArt, CardImage } from "@/components/card-art";
import { CardChip } from "@/components/card-chip";
import { ButtonLink, controlClass } from "@/components/ds/control";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { DataFooter, Eyebrow, Page, StatBand } from "@/components/ds/page";
import { MethodNote } from "@/components/ds/explain";
import { BanStatus, Tag, TierTag, TrendLabel } from "@/components/ds/tags";
import { Reveal } from "@/components/reveal";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  NAV_BACK,
  PageTransition,
  SharedElement,
  archetypeArtName,
  archetypeTitleName,
} from "@/components/view-transitions";
import type { ArchetypeResponse, BuyLabel, TierWindow } from "@/types";
import { ShareChart } from "./ShareChart";

const TCG_SOURCE = "decklists de tournoi TCG, yugiohmeta.com";
const PROVISIONAL = "seuils provisoires, non validés hors échantillon";
const H2 = "text-[clamp(22px,2.6vw,30px)] leading-tight font-medium tracking-[-0.03em]";
const SUB = "mt-2 max-w-[68ch] text-[14px] text-soft";
const LABEL_TONE: Record<BuyLabel, "strong" | "outline" | "neutral"> = {
  Fort: "strong",
  Modéré: "outline",
  Faible: "neutral",
};

type Params = { params: Promise<{ slug: string }> };

// Pages construites d'avance : les archétypes de la tier list et ceux d'un signal
// boutique. Les autres (archétypes anciens) sont rendues à la première visite puis
// mises en cache ; un slug inconnu donne une vraie 404.
export async function generateStaticParams() {
  const [tierList, boutique] = await Promise.all([api.tierList(), api.boutiqueSignals()]);
  const slugs = new Set([...tierList.data.map((e) => e.slug), ...boutique.data.map((s) => s.archetype_slug)]);
  return [...slugs].map((slug) => ({ slug }));
}

function windowLabel(window: TierWindow): string {
  return window.start === window.end
    ? fmtMonthShort(window.end)
    : `${fmtMonthShort(window.start)} à ${fmtMonthShort(window.end)}`;
}

function describe(a: ArchetypeResponse): string {
  if (a.tcg && a.tcg_window) {
    return `${a.archetype} : ${fmtPct(a.tcg.share * 100)} des decks de tournoi TCG (${fmtNum(a.tcg.decks)} sur ${fmtNum(a.tcg_window.n_decks)}, ${windowLabel(a.tcg_window)}), tier ${a.tcg.tier}. Part mensuelle et cartes clés.`;
  }
  if (a.ocg) {
    return `${a.archetype} : ${fmtPct(a.ocg.share * 100)} des decks de tournoi OCG (${fmtNum(a.ocg.decks)} decks${a.ocg.computed_at ? `, calcul du ${fmtDate(a.ocg.computed_at)}` : ""}), aucun deck TCG dans la fenêtre courante.`;
  }
  const lastPlayed = [...a.history].reverse().find((h) => h.decks > 0);
  return `${a.archetype} : aucun deck de tournoi TCG dans la fenêtre courante${lastPlayed ? `, dernier relevé en ${fmtMonthShort(lastPlayed.month)}` : ""}. Part mensuelle depuis ${a.history[0] ? fmtMonthShort(a.history[0].month) : "le début des relevés"}.`;
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { slug } = await params;
  const archetype = await api.archetype(slug);
  if (!archetype) return { title: "Archétype introuvable", robots: { index: false, follow: false } };
  // Toute variante de casse rend la même page : l'adresse canonique est le slug servi par l'API.
  return pageMetadata({
    title: archetype.archetype,
    description: describe(archetype),
    path: `/archetype/${archetype.slug}`,
  });
}

export default async function ArchetypePage({ params }: Params) {
  const { slug } = await params;
  const a = await api.archetype(slug);
  if (!a) notFound();

  const { tcg, tcg_window: window, ocg, boutique, key_cards: keyCards, history } = a;
  const period = window ? windowLabel(window) : null;
  const lastPlayed = [...history].reverse().find((h) => h.decks > 0);
  const rule = boutique?.label_rule ?? null;

  const stats: { value: React.ReactNode; label: string }[] = [];
  if (tcg && window) {
    stats.push(
      { value: fmtPct(tcg.share * 100), label: "Part de méta TCG" },
      { value: fmtNum(tcg.decks), label: `Decks sur ${fmtNum(window.n_decks)}` },
      { value: fmtRank(tcg.rank), label: `Rang sur ${fmtNum(tcg.n_archetypes)} archétypes` }
    );
  } else if (window) {
    stats.push({ value: "0", label: `Deck TCG sur ${fmtNum(window.n_decks)}` });
    if (lastPlayed) stats.push({ value: fmtMonthShort(lastPlayed.month), label: "Dernier mois joué en TCG" });
  }
  if (ocg) {
    stats.push({ value: fmtPct(ocg.share * 100), label: "Part de méta OCG" });
    if (!tcg) stats.push({ value: fmtNum(ocg.decks), label: "Decks OCG" });
  } else if (tcg) {
    stats.push({ value: fmtNum(tcg.meta_score * 100, 1), label: "Score méta ×100" });
  }
  if (boutique?.archetype_rank != null && rule && stats.length < 4) {
    stats.push({ value: fmtRank(boutique.archetype_rank), label: `Rang OCG sur ${rule.population}` });
  }

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <PageTransition id={`archetype-${a.slug}`}>
        <Page>
          <header className="relative isolate pt-8 pb-10">
            {a.image_url && (
              // Illustration recadrée en fond d'en-tête, très assombrie par le masque :
              // même traitement que les bandeaux de la tier list. Écran large seulement.
              <span
                aria-hidden
                className="pointer-events-none absolute inset-x-[calc(var(--gutter)*-1)] top-0 -z-10 hidden h-[360px] [mask-image:linear-gradient(180deg,rgb(0_0_0/0.3),transparent)] min-[760px]:block"
              >
                <CardImage
                  src={artCropUrl(a.image_url)}
                  alt=""
                  fill
                  sizes="(min-width: 1200px) 1200px, 100vw"
                  className="object-cover object-[center_28%] [mask-image:linear-gradient(90deg,transparent,rgb(0_0_0/0.5)_45%,black)]"
                />
              </span>
            )}

            <Link
              href="/tier-list"
              transitionTypes={NAV_BACK}
              className="inline-flex items-center gap-2 font-mono text-[12px] uppercase tracking-[0.1em] text-muted-text transition-colors duration-200 hover:text-text"
            >
              <span aria-hidden>←</span> Tier list
            </Link>

            <div className="mt-8 grid grid-cols-[minmax(0,1fr)_auto] items-end gap-x-5 gap-y-6 min-[760px]:gap-x-10">
              <div className="min-w-0">
                <Eyebrow className="enter">
                  {period && window
                    ? `Archétype · TCG · ${period} · ${fmtNum(window.n_decks)} decks`
                    : "Archétype"}
                </Eyebrow>
                <h1 className="enter mt-[18px] text-[clamp(34px,6.2vw,80px)] leading-[0.98] font-medium tracking-[-0.045em] text-balance [--i:1] [overflow-wrap:anywhere]">
                  <SharedElement name={archetypeTitleName(a.slug)}>
                    <span className="inline-block">{a.archetype}</span>
                  </SharedElement>
                </h1>
                <div className="enter mt-5 flex flex-wrap items-center gap-x-4 gap-y-2 [--i:2]">
                  {tcg ? (
                    <>
                      <TierTag tier={tcg.tier} />
                      <TrendLabel trend={tcg.trend} />
                      {tcg.share_prev != null && (
                        <span className="font-mono text-[12px] text-muted-text tabular-nums">
                          fenêtre précédente : {fmtPct(tcg.share_prev * 100)} ({fmtNum(tcg.decks_prev)} decks sur{" "}
                          {fmtNum(tcg.n_decks_prev)})
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="font-mono text-[12px] text-muted-text">
                      Hors tier list : aucun deck TCG relevé{period ? ` de ${period}` : ""}.
                    </span>
                  )}
                  {/* Un archétype de la tier list a au moins une liste dans la fenêtre : sa page Decks existe (TOK-114). */}
                  {tcg && (
                    <ButtonLink href={`/decks/${a.slug}`} size="sm">
                      Composition du deck
                    </ButtonLink>
                  )}
                  {boutique?.signal_label && (
                    <a href="#signal-boutique" className="inline-flex items-center gap-2 text-[13px] text-soft hover:text-text">
                      <Tag tone={LABEL_TONE[boutique.signal_label]}>SIGNAL {boutique.signal_label.toUpperCase()}</Tag>
                    </a>
                  )}
                </div>
              </div>

              <SharedElement name={archetypeArtName(a.slug)}>
                <CardArt
                  src={a.image_url}
                  name={a.archetype}
                  size="lg"
                  eager
                  className="shadow-[var(--shadow-card)] max-[759px]:h-32 max-[759px]:w-[88px] max-[759px]:rounded-[6px] min-[760px]:rotate-2"
                />
              </SharedElement>
            </div>

            {stats.length > 0 && <StatBand stats={stats} />}
            <DataFooter
              source={TCG_SOURCE}
              date={period ?? "fenêtre inconnue"}
              sample={window ? `${fmtNum(window.n_decks)} decks` : undefined}
              uncertainty={
                tcg
                  ? `part calculée sur ${fmtNum(tcg.decks)} decks ; la tendance n’est affichée que si l’écart avec la fenêtre précédente dépasse le bruit d’échantillonnage`
                  : "aucun deck TCG dans la fenêtre, pas de part calculée"
              }
            >
              {ocg && (
                <>
                  OCG : {fmtNum(ocg.decks)} decks, {ocg.computed_at ? `calcul du ${fmtDate(ocg.computed_at)}` : "date de calcul inconnue"}
                </>
              )}
            </DataFooter>
            {tcg && (
              <MethodNote anchor="tier-list">
                <p>Tier : T0 à partir de 40 % des decks de la fenêtre, T1 à partir de 15 %, T2 à partir de 7 %, T3 à partir de 3 %.</p>
                <p>Tendance : comparaison avec la fenêtre précédente, affichée seulement si l’écart dépasse le bruit d’échantillonnage.</p>
              </MethodNote>
            )}
          </header>

          {history.length > 0 && (
            <section aria-labelledby="h-part" className="mt-6">
              <h2 id="h-part" className={H2}>
                Part de méta par mois
              </h2>
              <div className="mt-5">
                <ShareChart archetype={a.archetype} history={history} window={window} />
              </div>
              <DataFooter
                source={TCG_SOURCE}
                date={fmtMonthRange(history[0].month, history[history.length - 1].month) ?? ""}
                sample={`${fmtNum(history.reduce((sum, h) => sum + h.decks, 0))} decks ${a.archetype} sur ${fmtNum(history.reduce((sum, h) => sum + h.total_decks, 0))}`}
                uncertainty="bande : intervalle à 95 % de chaque part mensuelle ; pointillé : mois de moins de 100 decks et mois en cours"
              />
              <MethodNote anchor="part-mensuelle">
                <p>Part du mois : decks de l’archétype divisés par tous les decks de tournoi TCG relevés ce mois-là.</p>
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
                    <caption className="sr-only">Part mensuelle de {a.archetype} dans les decks de tournoi TCG</caption>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent">
                        <TableHead>Mois</TableHead>
                        <TableHead className="text-right">Part</TableHead>
                        <TableHead className="text-right">Decks {a.archetype}</TableHead>
                        <TableHead className="text-right">Decks relevés</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {[...history].reverse().map((h) => (
                        <TableRow key={h.month}>
                          <TableCell className="font-mono text-[13px] text-soft">{fmtMonthShort(h.month)}</TableCell>
                          <TableCell className="text-right font-mono text-[13px] tabular-nums">{fmtPct(h.share * 100)}</TableCell>
                          <TableCell className="text-right font-mono text-[13px] tabular-nums">{fmtNum(h.decks)}</TableCell>
                          <TableCell className="text-right font-mono text-[13px] text-muted-text tabular-nums">
                            {fmtNum(h.total_decks)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </details>
            </section>
          )}

          {keyCards && (
            <Reveal className="mt-16">
              <section aria-labelledby="h-cartes">
                <h2 id="h-cartes" className={H2}>
                  Cartes clés
                </h2>
                <p className={SUB}>
                  Les {fmtNum(keyCards.data.length)} cartes les plus jouées dont {a.archetype} est le deck d’attache, sur{" "}
                  {fmtNum(keyCards.n_decks_window)} decks TCG au {fmtDate(keyCards.as_of)} : decks qui la jouent, part
                  de tous les decks, exemplaires moyens par deck.
                </p>
                <ol className="mt-6 grid grid-cols-2 gap-x-4 gap-y-7 min-[560px]:grid-cols-3 min-[760px]:grid-cols-4 min-[1000px]:grid-cols-6">
                  {keyCards.data.map((card) => (
                    <li key={card.card_name} className="grid content-start justify-items-start gap-2.5">
                      <CardArt
                        src={card.image_url}
                        name={card.card_name}
                        size="lg"
                        className="transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-1"
                      />
                      <CardChip
                        name={card.card_name}
                        subtitle={a.archetype}
                        variant="plain"
                        className="text-[14px] leading-snug font-medium tracking-[-0.01em] [overflow-wrap:anywhere]"
                      />
                      <span className="font-mono text-[12px] leading-[1.6] text-muted-text tabular-nums">
                        {fmtNum(card.decks)} decks · {fmtPct(card.deck_share)}
                        <br />
                        {fmtNum(card.mean_copies, 1)} ex. par deck
                      </span>
                      {card.current_status !== "Unlimited" && <BanStatus status={card.current_status} />}
                    </li>
                  ))}
                </ol>
                <DataFooter
                  source={TCG_SOURCE}
                  date={`au ${fmtDate(keyCards.as_of)}`}
                  sample={`${fmtNum(keyCards.n_decks_window)} decks`}
                  uncertainty="comptes exacts sur la fenêtre, pas d’intervalle : la liste ordonne les cartes, elle n’estime rien"
                >
                  deck d’attache : au moins la moitié des decks qui jouent la carte sont de cet archétype ; statut :
                  banlist TCG en vigueur
                </DataFooter>
              </section>
            </Reveal>
          )}

          {boutique && (
            <Reveal className="mt-16">
              <section id="signal-boutique" aria-labelledby="h-boutique" className="scroll-mt-24">
                <h2 id="h-boutique" className={H2}>
                  Signal boutique
                </h2>
                <dl className="mt-5 grid gap-px overflow-hidden rounded-[6px] border border-line bg-line min-[760px]:grid-cols-3">
                  <div className="grid content-start gap-2 bg-ink-2 px-4 py-4">
                    <dt className="font-mono text-[11px] uppercase tracking-[0.08em] text-muted-text">Libellé</dt>
                    <dd className="flex flex-wrap items-center gap-2.5">
                      {boutique.signal_label ? (
                        <Tag tone={LABEL_TONE[boutique.signal_label]}>{boutique.signal_label.toUpperCase()}</Tag>
                      ) : (
                        <span className="font-mono text-[12px] text-faint">indisponible</span>
                      )}
                      <span className="font-mono text-[12px] text-muted-text">{PROVISIONAL}</span>
                    </dd>
                  </div>
                  <div className="grid content-start gap-2 bg-ink-2 px-4 py-4">
                    <dt className="font-mono text-[11px] uppercase tracking-[0.08em] text-muted-text">
                      Rang parmi les archétypes OCG
                    </dt>
                    <dd className="text-[22px] leading-none font-medium tracking-[-0.02em] tabular-nums">
                      {boutique.archetype_rank != null && rule
                        ? `${fmtRank(boutique.archetype_rank)} sur ${rule.population}`
                        : "—"}
                      {rule && (
                        <span className="mt-2 block font-mono text-[12px] leading-[1.6] font-normal tracking-normal text-muted-text">
                          Fort : rang {rule.strong_max_rank} ou mieux · Modéré : rang {rule.moderate_max_rank} ou mieux
                        </span>
                      )}
                    </dd>
                  </div>
                  <div className="grid content-start gap-2 bg-ink-2 px-4 py-4">
                    <dt className="font-mono text-[11px] uppercase tracking-[0.08em] text-muted-text">
                      Arrivée en TCG, intervalle à 80 %
                    </dt>
                    <dd className="text-[22px] leading-none font-medium tracking-[-0.02em]">
                      {fmtMonthRange(boutique.tcg_window_start, boutique.tcg_window_end) ?? "—"}
                      <span className="mt-2 block font-mono text-[12px] leading-[1.6] font-normal tracking-normal text-muted-text">
                        75 à 202 jours après le premier deck OCG, délai mesuré sur 1 897 cartes sorties de 2022 à 2025 ;
                        non vérifié sur des cas nouveaux
                      </span>
                    </dd>
                  </div>
                </dl>

                <div className="mt-4 overflow-hidden rounded-[6px] border border-line">
                  <Table>
                    <caption className="sr-only">Cartes du signal boutique de {a.archetype}</caption>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent">
                        <TableHead>Carte</TableHead>
                        <TableHead className="text-right">Ordre dans le lot</TableHead>
                        <TableHead className="text-right">Prix CM</TableHead>
                        <TableHead>Banlist TCG</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {boutique.signals.map((signal) => (
                        <TableRow key={`${signal.archetype}-${signal.card_name}`}>
                          <TableCell>
                            <span className="flex items-center gap-3">
                              <CardArt src={signal.image_url} name={signal.card_name} />
                              <CardChip
                                name={signal.card_name}
                                subtitle={signal.archetype}
                                variant="plain"
                                className="font-medium tracking-[-0.01em]"
                              />
                            </span>
                          </TableCell>
                          <TableCell className="text-right font-mono text-[13px] font-medium tabular-nums">
                            {fmtNum(signal.buy_score, 1)}
                          </TableCell>
                          <TableCell className="text-right font-mono text-[13px] tabular-nums">
                            {fmtNum(signal.cm_price, 2)} €
                          </TableCell>
                          <TableCell>
                            {signal.ban_tcg ? (
                              <BanStatus status={signal.ban_tcg} />
                            ) : (
                              <span className="font-mono text-[12px] text-faint">—</span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                <DataFooter
                  source="decklists OCG (yugiohmeta.com), vues et prix Cardmarket (YGOPRODeck)"
                  date={boutique.computed_at ? `calcul du ${fmtDate(boutique.computed_at)}` : "date de calcul inconnue"}
                  sample={`${fmtNum(boutique.signals.length)} cartes`}
                  uncertainty="arrivée en TCG : intervalle à 80 % ; rang et libellé sans intervalle, seuils provisoires"
                >
                  ordre dans le lot : la première carte de tous les signaux affichés vaut 100, ce n’est pas une force de
                  signal ·{" "}
                  <Link href="/boutique" className="underline decoration-line-2 underline-offset-4 hover:text-text">
                    tous les signaux
                  </Link>
                </DataFooter>
              </section>
            </Reveal>
          )}
        </Page>
      </PageTransition>
    </HoverPreviewProvider>
  );
}
