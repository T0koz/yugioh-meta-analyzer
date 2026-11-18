import type { Metadata } from "next";
import Link from "next/link";
import { api } from "@/lib/api";
import { CRITERIA } from "@/lib/ban-criteria";
import { fmtDate, fmtMonthRange, fmtNum } from "@/lib/format";
import { PROOF } from "@/lib/proof-data";
import { pageMetadata } from "@/lib/seo";
import { SITE_FACTS } from "@/lib/site-facts";
import { CardArt, CardArtFill } from "@/components/card-art";
import { ButtonLink, controlClass } from "@/components/ds/control";
import { Em } from "@/components/ds/em";
import { Eyebrow, StatBand } from "@/components/ds/page";
import { Tag, banStatusLabel } from "@/components/ds/tags";
import { Constellation } from "@/components/home/constellation";
import { CountUp, Embers, FanStage, GlowLink, ProofScroll } from "@/components/home/effects";
import { ProofChart } from "@/components/home/proof-chart";
import { Reveal } from "@/components/reveal";
import { SiteFooter } from "@/components/site-footer";
import type { BuyLabel } from "@/types";

// Accueil « Braise vivante » (TOK-106), portage de docs/audit-front/prototype :
// hero, preuve au défilement, outils, méthode, pied de page. Tout le contenu est
// rendu côté serveur ; les effets (components/home/effects.tsx) s'y ajoutent.

export const metadata: Metadata = pageMetadata({
  title: "Accueil",
  absoluteTitle: "YGO Meta · Méta Yu-Gi-Oh! TCG et OCG",
  description:
    "Méta Yu-Gi-Oh! TCG et OCG mesurée sur 23 948 decklists de tournoi : corrélation OCG → TCG de 0,53, signaux boutique, risque de ban, méthode et limites.",
  path: "/",
});

const WRAP = "mx-auto w-full max-w-[var(--maxw)] px-[var(--gutter)]";
const H2 = "text-[clamp(30px,4.2vw,56px)] leading-[1.02] font-medium tracking-[-0.04em] text-balance";
const H3 = "text-[clamp(22px,2.4vw,32px)] leading-[1.08] font-medium tracking-[-0.03em] text-balance";
const TILE = "grid min-w-0 gap-[18px] rounded-[14px] border border-line-2 bg-ink-3 p-[22px] min-[760px]:p-[26px] col-span-12";
/** Pied de données : source et date sous chaque visualisation. */
const SOURCE = "font-mono text-[12px] leading-[1.6] text-muted-text";
/** Étiquette de métadonnée, non interactive (les pills de filtre sont dans ds/control.tsx). */
const META_TAG = "rounded-[4px] border border-line-2 px-2 py-[5px] font-mono text-[11px] tracking-[0.06em] text-soft uppercase";

const LABEL_TONE: Record<BuyLabel, "strong" | "outline" | "neutral"> = { Fort: "strong", Modéré: "outline", Faible: "neutral" };

// Ton de la page (consigne du 2026-11-16) : sobre, factuel, statistique. Pas de
// formule publicitaire ni d'appel à l'action ; une phrase porte une mesure, une
// période et une source, sinon elle n'est pas écrite. Le graphique explique, le
// texte annote.

// Mots du titre, révélés un par un (CSS .home-word). Titre neutre (lot 16, décision de Thomas
// du 17/11) : il nomme ce que couvre le site ; le graphique OCG / TCG fait la démonstration.
const TITLE: { word: string; accent?: boolean }[] = [
  { word: "Méta" },
  { word: "Yu-Gi-Oh!" },
  { word: "TCG", accent: true },
  { word: "et", accent: true },
  { word: "OCG", accent: true },
];

// Éventail : [rang dans la tier list, position --k, profondeur --z, ordre de distribution --n].
const FAN_SLOTS = [
  [3, -2, 0, 0],
  [1, -1, 20, 1],
  [0, 0, 60, 4],
  [2, 1, 20, 3],
  [4, 2, 0, 2],
] as const;

const fmtRank = (rank: number) => (rank === 1 ? "1er" : `${rank}ᵉ`);

const ALSO = [
  { href: "/tier-list", label: "Tier list" },
  { href: "/evolution", label: "Évolution" },
  { href: "/predictions", label: "Prédictions" },
  { href: "/early-signals", label: "Signaux précoces" },
];

const pct = (v: number) => `${fmtNum(v, 1)} %`;
/** « 2026-11 » → « novembre 2026 ». */
const fmtMonthYearLong = (yearMonth: string) =>
  new Date(`${yearMonth}-01T00:00:00`).toLocaleDateString("fr-FR", { month: "long", year: "numeric" });

export default async function Home() {
  const [boutique, radar, tierList, predictions, early] = await Promise.all([
    api.boutiqueSignals(),
    api.banRadar({ limit: 3, kind: "archetype" }),
    api.tierList(),
    api.predictions(),
    api.earlySignals(),
  ]);
  const topBuy = boutique.data[0];
  const rule = boutique.label_rule;
  const tcgWindow = topBuy ? fmtMonthRange(topBuy.tcg_window_start, topBuy.tcg_window_end) : null;
  const illustrated = tierList.data.filter((entry) => entry.image_url);
  const leader = tierList.data[0];
  const lag = PROOF.tcgPeak - PROOF.ocgPeak;
  const tierWindow = fmtMonthRange(`${tierList.window_start}-01`, `${tierList.window_end}-01`);
  const { ocg, tcg, ocgPeak, tcgPeak } = PROOF;
  const topEarly = early.data[0];
  // Une ligne chiffrée par lien, tirée de l'API ; sans donnée, le lien reste seul.
  const alsoText: Record<string, string | undefined> = {
    "/tier-list": leader && `${leader.archetype} : ${pct(leader.share * 100)} de ${fmtNum(tierList.n_decks)} decks TCG, ${tierWindow}.`,
    "/evolution": `Part mensuelle des archétypes TCG, mai 2023 à ${fmtMonthYearLong(tierList.window_end)}.`,
    "/predictions": `${predictions.data.length} archétypes, horizon d’un mois, sans intervalle par archétype.`,
    "/early-signals": topEarly && `${early.data.length} cartes classées, au ${fmtDate(radar.as_of)}. Première : ${topEarly.card_name}, score ${fmtNum(topEarly.early_score, 2)}.`,
  };

  return (
    <>
      <main>
        {/* ---------- 1. Hero : la promesse ---------- */}
        <section className="relative isolate grid min-h-[min(880px,100svh)] items-center overflow-x-clip pt-10 pb-10 min-[900px]:pt-14">
          <Embers className="absolute inset-0 -z-20 h-full w-full" />
          <div
            aria-hidden
            className="absolute top-[8%] right-[-6%] -z-10 aspect-square w-[70%] opacity-75 blur-[30px] [background:radial-gradient(closest-side,var(--glow),transparent_70%)]"
          />
          <div className={WRAP}>
            <div className="grid items-center gap-2 min-[900px]:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)] min-[900px]:gap-10">
              <div>
                <Eyebrow className="enter home-pulse">YGO Meta · données au {fmtDate(radar.as_of)}</Eyebrow>
                <h1 className="mt-5 text-[clamp(38px,5.6vw,80px)] leading-[0.98] font-medium tracking-[-0.05em] text-balance">
                  {TITLE.map(({ word, accent }, i) => (
                    <span key={i}>
                      <span className="home-word">
                        <span style={{ "--i": i } as React.CSSProperties}>
                          {accent ? <Em>{word}</Em> : word}
                          {i === TITLE.length - 1 && "."}
                        </span>
                      </span>{" "}
                    </span>
                  ))}
                </h1>
                <p className="enter mt-6 max-w-[50ch] text-[18px] text-soft [--i:2]">
                  {`Corrélation de ${fmtNum(SITE_FACTS.ocgTcgCorrelation, 2)} (IC 95 % : ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[0], 2)} à ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[1], 2)}) entre le score d’un archétype en OCG et son score en TCG ${SITE_FACTS.ocgTcgLagRange} plus tard, sur ${SITE_FACTS.ocgTcgArchetypes} archétypes et ${fmtNum(SITE_FACTS.decklists)} decklists de tournoi (yugiohmeta.com, mai 2023 à novembre 2026).`}
                </p>
                <div className="enter mt-[30px] flex flex-wrap gap-2.5 [--i:3]">
                  <ButtonLink href="/boutique" variant="primary" size="lg">
                    Signaux boutique
                  </ButtonLink>
                  <a href="#methode" className={controlClass({ size: "lg" })}>
                    Méthode et limites
                  </a>
                </div>
              </div>

              {illustrated.length >= FAN_SLOTS.length && (
                <FanStage className="home-stage max-[899px]:order-first max-[899px]:h-[320px]">
                  <div className="home-fan" aria-hidden>
                    {/* Images en chargement différé : sur mobile le LCP est le paragraphe, les
                        cartes ne doivent pas disputer la bande passante au CSS et aux polices. */}
                    {FAN_SLOTS.map(([rank, k, z, n]) => (
                      <div
                        key={rank}
                        className="home-fan-card"
                        data-hot={rank === 0 ? "" : undefined}
                        style={{ "--k": k, "--z": z, "--n": n } as React.CSSProperties}
                      >
                        <CardArtFill
                          src={illustrated[rank].image_url}
                          name={illustrated[rank].archetype}
                          sizes="(min-width: 900px) 230px, 128px"
                        />
                      </div>
                    ))}
                  </div>
                  <p className="enter absolute bottom-[2%] left-1/2 z-10 -translate-x-1/2 rounded-[6px] border border-line-2 bg-ink-2/85 px-3 py-2 font-mono text-[11px] font-medium tracking-[0.08em] uppercase backdrop-blur max-[599px]:w-max max-[599px]:max-w-[calc(100vw-2rem)] max-[599px]:text-center min-[600px]:whitespace-nowrap [--i:5]">
                    <b className="font-medium text-signal">{illustrated[0].archetype}</b> · {pct(illustrated[0].share * 100)} des
                    decks TCG · {tierWindow}
                  </p>
                </FanStage>
              )}
            </div>

            <div className="enter [--i:4]">
              <StatBand
                stats={[
                  { value: <CountUp value={SITE_FACTS.decklists} />, label: "Decklists analysées" },
                  { value: <CountUp value={SITE_FACTS.cardsTracked} />, label: "Cartes suivies" },
                  { value: <CountUp value={SITE_FACTS.ocgTcgCorrelation} digits={2} />, label: "Corrélation OCG → TCG (r)" },
                  { value: SITE_FACTS.ocgTcgLagRange, label: "Écart OCG → TCG" },
                ]}
              />
            </div>
          </div>
        </section>

        {/* ---------- 2. La preuve : graphique piloté par le défilement ---------- */}
        <ProofScroll id="preuve" aria-labelledby="h-preuve" className="scroll-mt-20">
          <div className="home-proof-sticky py-20">
            <div className={`${WRAP} grid items-center gap-10 min-[900px]:grid-cols-[minmax(0,0.8fr)_minmax(0,1.4fr)] min-[900px]:gap-12`}>
              <div>
                <Eyebrow>Exemple · un archétype, deux formats</Eyebrow>
                <h2 id="h-preuve" className={`mt-[18px] ${H2}`}>
                  {PROOF.archetype} : pic en OCG en avril 2026, en TCG <Em>{lag} mois</Em> plus tard.
                </h2>
                <ol className="mt-7 grid gap-1.5">
                  {[
                    ["1 · OCG", `${pct(ocg[ocgPeak - 3])} des decks en janvier 2026, ${pct(ocg[ocgPeak - 2])} en février, pic à ${pct(ocg[ocgPeak])} en avril.`],
                    ["2 · TCG", `${pct(tcg[tcgPeak - 3])} en avril 2026, ${pct(tcg[tcgPeak - 2])} en mai, pic à ${pct(tcg[tcgPeak])} en juillet.`],
                    [
                      "3 · Écart",
                      `Courbe OCG décalée de ${lag} mois. Un seul archétype : sur ${SITE_FACTS.ocgTcgArchetypes} archétypes, l’écart observé va de ${SITE_FACTS.ocgTcgLagRange}.`,
                    ],
                  ].map(([label, text]) => (
                    <li key={label} className="home-step px-4 py-3.5 text-[16px]">
                      <b className="mb-1 block font-mono text-[11px] font-medium tracking-[0.1em] uppercase">{label}</b>
                      {text}
                    </li>
                  ))}
                </ol>
              </div>

              <figure className="rounded-[14px] border border-line-2 bg-linear-to-b from-ink-3 to-ink-2 px-4 pt-5 pb-3.5 min-[760px]:px-[22px]">
                <div className="mb-2.5 flex flex-wrap gap-4 font-mono text-[12px] text-soft">
                  <span className="flex items-center gap-2">
                    <i className="h-[3px] w-[18px] rounded-[2px] bg-ocg" />
                    OCG (Japon, Asie)
                  </span>
                  <span className="flex items-center gap-2">
                    <i className="h-[3px] w-[18px] rounded-[2px] bg-signal" />
                    TCG (Europe, Amériques)
                  </span>
                </div>
                <ProofChart />
                <figcaption className={`mt-3 ${SOURCE}`}>
                  Part des decks de tournoi par mois, août 2025 à novembre 2026 (novembre incomplet). Source : decklists
                  yugiohmeta.com, relevé du {fmtDate(PROOF.asOf)}. Incertitude non dessinée : les effectifs mensuels
                  n’ont pas été relevés avec cette série figée.
                </figcaption>
              </figure>
            </div>
          </div>
        </ProofScroll>

        {/* ---------- 3. Les outils : bento avec de vraies cartes ---------- */}
        <section id="outils" aria-labelledby="h-outils" className={`${WRAP} scroll-mt-20 pt-24 min-[900px]:pt-[120px]`}>
          <Reveal>
            <Eyebrow>Outils</Eyebrow>
            <h2 id="h-outils" className={`mt-[18px] max-w-[18ch] ${H2}`}>
              {`Trois outils sur `}
              <Em>{fmtNum(SITE_FACTS.decklists)}</Em>
              {` decklists de tournoi, mai 2023 à novembre 2026.`}
            </h2>
          </Reveal>

          <div className="mt-10 grid grid-cols-12 gap-3.5">
            {topBuy && (
              <Reveal className="col-span-12 grid min-[900px]:col-span-5">
                <GlowLink href="/boutique" className={`${TILE} content-between min-[900px]:min-h-[340px]`}>
                  <Eyebrow>Signal boutique</Eyebrow>
                  <div className="grid grid-cols-[auto_minmax(0,1fr)] items-end gap-[22px]">
                    <div className="home-bigcard relative aspect-[59/86] w-[clamp(110px,13vw,160px)] overflow-hidden rounded-[8px] bg-ink-4">
                      <CardArtFill src={topBuy.image_url} name={topBuy.card_name} sizes="160px" />
                    </div>
                    {topBuy.archetype_rank != null && rule ? (
                      <p className="text-[clamp(64px,9vw,120px)] leading-[0.85] font-medium tracking-[-0.07em] tabular-nums">
                        {fmtRank(topBuy.archetype_rank)}
                        <span className="mt-3 block font-mono text-[12px] leading-[1.5] font-normal tracking-[0.04em] text-muted-text">
                          sur {rule.population} archétypes OCG
                        </span>
                      </p>
                    ) : (
                      <p className="text-[clamp(48px,7vw,88px)] leading-[0.85] font-medium tracking-[-0.06em] tabular-nums">
                        {fmtNum(topBuy.cm_price, 2)} €
                      </p>
                    )}
                  </div>
                  <div>
                    <h3 className={H3}>{topBuy.archetype}</h3>
                    <p className="mt-2 text-[15px] text-muted-text">Carte suivie : {topBuy.card_name}.</p>
                    <div className="mt-3 flex flex-wrap items-center gap-1.5">
                      {topBuy.signal_label && <Tag tone={LABEL_TONE[topBuy.signal_label]}>{topBuy.signal_label.toUpperCase()}</Tag>}
                      <span className={META_TAG}>Cardmarket {fmtNum(topBuy.cm_price, 2)} €</span>
                      {tcgWindow && <span className={META_TAG}>Arrivée TCG {tcgWindow}</span>}
                      {topBuy.ban_tcg && <span className={META_TAG}>{banStatusLabel(topBuy.ban_tcg)} en TCG</span>}
                    </div>
                    <p className={`mt-3.5 ${SOURCE}`}>
                      {topBuy.signal_label && "Libellé : rang de l’archétype en OCG, seuils provisoires, non validés hors échantillon. "}
                      {tcgWindow && "Fenêtre d’arrivée : intervalle à 80 %, non validé. "}
                      Source : decklists OCG et prix Cardmarket, au {fmtDate(radar.as_of)}.
                    </p>
                  </div>
                </GlowLink>
              </Reveal>
            )}

            <Reveal className={`col-span-12 grid ${topBuy ? "min-[900px]:col-span-7" : ""}`}>
              <GlowLink href="/ban" className={`${TILE} content-between`}>
                <div>
                  <Eyebrow>Ban Radar · pièces d’archétype</Eyebrow>
                  <h3 className={`mt-3.5 ${H3}`}>
                    Risque de restriction, <Em>score</Em> sur 100.
                  </h3>
                </div>
                <div>
                  {radar.data.map((entry) => (
                    <div key={entry.card_name} className="grid grid-cols-[44px_minmax(0,1fr)_auto] items-center gap-3.5 border-t border-line py-3">
                      <CardArt src={entry.image_url} name={entry.card_name} size="sm" />
                      <div className="min-w-0">
                        <strong className="block text-[16px] font-medium [overflow-wrap:anywhere]">{entry.card_name}</strong>
                        <small className="font-mono text-[12px] text-muted-text">
                          {fmtNum(entry.deck_share, 1)} % des decks · {fmtNum(entry.mean_copies, 2)} ex. en moyenne
                          {entry.current_status !== "Unlimited" && ` · ${banStatusLabel(entry.current_status)}`}
                        </small>
                        <div aria-hidden className="mt-2 flex h-2 gap-0.5 overflow-hidden rounded-[2px] bg-ink-4">
                          {CRITERIA.map(({ key, color }) =>
                            entry.criteria[key] > 0 ? (
                              <i key={key} className="fill-in block h-full" style={{ width: `${entry.criteria[key]}%`, backgroundColor: color }} />
                            ) : null
                          )}
                        </div>
                      </div>
                      <span className="text-[30px] font-medium tracking-[-0.03em] tabular-nums">
                        <CountUp value={entry.ban_risk_score} digits={1} />
                      </span>
                    </div>
                  ))}
                  <p className={`mt-1 ${SOURCE}`}>
                    Barre : {CRITERIA.map((c) => c.label.toLowerCase()).join(", ")}. Source :{" "}
                    {fmtNum(radar.n_decks_window)} decks de tournoi TCG, au {fmtDate(radar.as_of)}.
                  </p>
                </div>
              </GlowLink>
            </Reveal>

            <Reveal className="col-span-12 grid">
              <GlowLink href="/graph" className={TILE}>
                <div className="grid items-center gap-6 min-[900px]:grid-cols-[minmax(0,1fr)_minmax(0,1.6fr)]">
                  <div>
                    <Eyebrow>Graphe de synergies</Eyebrow>
                    <h3 className={`mt-3.5 ${H3}`}>
                      Cartes jouées <Em>ensemble</Em> dans les mêmes decks.
                    </h3>
                    <p className="mt-3 max-w-[46ch] text-[15px] text-muted-text">
                      {`${SITE_FACTS.graphCommunities} communautés de cartes détectées. En orange, les cartes « pont », qui en relient plusieurs.`}
                    </p>
                  </div>
                  <figure>
                    <Constellation names={tierList.data.slice(0, 3).map((entry) => entry.archetype)} />
                    <figcaption className={SOURCE}>
                      Schéma d’illustration : positions et liens ne sont pas des données. Graphe réel : cooccurrences
                      dans les decklists de tournoi.
                    </figcaption>
                  </figure>
                </div>
              </GlowLink>
            </Reveal>
          </div>

          <Reveal>
            <ul className="mt-3.5 grid gap-px overflow-hidden rounded-[14px] border border-line-2 bg-line min-[600px]:grid-cols-2 min-[900px]:grid-cols-4">
              {ALSO.map((item) => (
                <li key={item.href} className="grid bg-ink">
                  <Link href={item.href} className="group grid content-start gap-1.5 p-5 transition-colors duration-200 hover:bg-ink-3">
                    <span className="flex items-center justify-between font-medium">
                      {item.label}
                      <span aria-hidden className="text-muted-text transition-transform duration-200 motion-safe:group-hover:translate-x-1">
                        →
                      </span>
                    </span>
                    {alsoText[item.href] && <span className="text-[14px] text-muted-text">{alsoText[item.href]}</span>}
                  </Link>
                </li>
              ))}
            </ul>
          </Reveal>
        </section>

        {/* ---------- 4. La méthode : d'où viennent les chiffres, et ce qu'ils valent ---------- */}
        <section id="methode" aria-labelledby="h-methode" className={`${WRAP} scroll-mt-20 pt-24 min-[900px]:pt-[120px]`}>
          <Reveal>
            <Eyebrow>Méthode</Eyebrow>
            <h2 id="h-methode" className={`mt-[18px] max-w-[20ch] ${H2}`}>
              Méthode et <Em>limites</Em>.
            </h2>
          </Reveal>

          <div className="mt-10 grid gap-x-12 gap-y-10 min-[900px]:grid-cols-2">
            <Reveal className="min-w-0">
              <h3 className="font-mono text-[11px] tracking-[0.1em] text-signal uppercase">Les données</h3>
              <dl className="mt-4 grid gap-px border-y border-line bg-line">
                {[
                  [fmtNum(SITE_FACTS.decklists), `decklists de tournoi, mai 2023 à novembre 2026 : ${fmtNum(SITE_FACTS.decklistsTcg)} en TCG, ${fmtNum(SITE_FACTS.decklistsOcg)} en OCG, légales à la date du tournoi.`],
                  [fmtNum(SITE_FACTS.cardsTracked), "cartes suivies : prix Cardmarket et statut sur la banlist."],
                  ["Lundi", "mise à jour hebdomadaire. Prédictions datées et archivées depuis le 1ᵉʳ novembre 2026."],
                ].map(([value, text]) => (
                  <div key={value} className="grid grid-cols-[minmax(0,7.5rem)_minmax(0,1fr)] items-baseline gap-4 bg-ink py-4">
                    <dt className="text-[clamp(22px,2.6vw,30px)] leading-none font-medium tracking-[-0.03em] tabular-nums">{value}</dt>
                    <dd className="text-[15px] text-soft">{text}</dd>
                  </div>
                ))}
              </dl>
              <p className={`mt-3 ${SOURCE}`}>
                Sources : yugiohmeta.com (decklists), YGOPRODeck (cartes), Yugipedia (banlists), Cardmarket (prix).
                Décompte au {fmtDate(radar.as_of)}.
              </p>
            </Reveal>

            <Reveal className="min-w-0">
              <h3 className="font-mono text-[11px] tracking-[0.1em] text-signal uppercase">Le signal OCG → TCG</h3>
              <p className="mt-4 text-[clamp(22px,2.6vw,30px)] leading-[1.15] font-medium tracking-[-0.03em]">
                {fmtNum(SITE_FACTS.ocgTcgCorrelation, 2)}
                <span className="ml-3 font-mono text-[12px] font-normal tracking-normal text-muted-text">
                  IC 95 % : {fmtNum(SITE_FACTS.ocgTcgCorrelationCi[0], 2)} à {fmtNum(SITE_FACTS.ocgTcgCorrelationCi[1], 2)}
                </span>
              </p>
              {/* Intervalle de confiance sur l'axe 0 à 1 : la mesure se lit avant le texte. */}
              <svg
                viewBox="0 0 400 46"
                role="img"
                aria-label={`Corrélation de ${fmtNum(SITE_FACTS.ocgTcgCorrelation, 2)}, intervalle de confiance à 95 % de ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[0], 2)} à ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[1], 2)}, sur une échelle de 0 à 1.`}
                className="mt-4 block h-auto w-full max-w-[440px] overflow-visible"
              >
                <line x1="0" x2="400" y1="14" y2="14" stroke="var(--line-2)" />
                {[0, 0.25, 0.5, 0.75, 1].map((tick) => (
                  <g key={tick}>
                    <line x1={tick * 400} x2={tick * 400} y1="10" y2="18" stroke="var(--line-2)" />
                    <text
                      x={tick * 400}
                      y="38"
                      textAnchor={tick === 0 ? "start" : tick === 1 ? "end" : "middle"}
                      fill="var(--muted-text)"
                      className="font-mono text-[11px]"
                    >
                      {fmtNum(tick, 2)}
                    </text>
                  </g>
                ))}
                <line
                  x1={SITE_FACTS.ocgTcgCorrelationCi[0] * 400}
                  x2={SITE_FACTS.ocgTcgCorrelationCi[1] * 400}
                  y1="14"
                  y2="14"
                  stroke="var(--signal)"
                  strokeWidth="6"
                  strokeOpacity=".45"
                  strokeLinecap="round"
                />
                <circle cx={SITE_FACTS.ocgTcgCorrelation * 400} cy="14" r="5.5" fill="var(--signal)" />
              </svg>
              <p className="mt-3 max-w-[56ch] text-[15px] text-soft">
                {`Corrélation entre le score d’un archétype en OCG et son score en TCG ${SITE_FACTS.ocgTcgLagRange} plus tard, sur ${SITE_FACTS.ocgTcgArchetypes} archétypes.`}
              </p>
              <p className="mt-3 max-w-[56ch] text-[15px] text-soft">
                Libellés Fort, Modéré, Faible des signaux boutique : seuils provisoires, non validés hors échantillon.
                Premières prédictions datées à échéance en mars 2027.
              </p>
              <p className={`mt-3 ${SOURCE}`}>Source : méta TCG et OCG mensuelles, calcul du {fmtDate(SITE_FACTS.banBacktestDate)}.</p>
            </Reveal>

            <Reveal className="min-w-0 min-[900px]:col-span-2">
              <h3 className="font-mono text-[11px] tracking-[0.1em] text-signal uppercase">
                {`Ban Radar rejoué sur ${SITE_FACTS.banBacktestTotalLists} banlists passées`}
              </h3>
              <p className="mt-4 max-w-[70ch] text-[15px] text-soft">
                {`Cartes ensuite restreintes parmi les 25 premières du classement calculé la veille de chaque banlist, sur ${SITE_FACTS.banTop25[0].lists * 25} places par format (${SITE_FACTS.banTop25[0].lists} listes), comparées au classement par part des decks.`}
              </p>
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[520px] border-collapse text-left text-[15px]">
                  <caption className="sr-only">Cartes touchées dans le top 25 de la veille, Ban Radar et part des decks, par format</caption>
                  <thead>
                    <tr className="font-mono text-[11px] tracking-[0.08em] text-muted-text uppercase">
                      <th scope="col" className="border-b border-line-2 py-2.5 pr-4 font-normal">Format</th>
                      <th scope="col" className="border-b border-line-2 py-2.5 pr-4 font-normal">Cartes touchées dans le top 25</th>
                      <th scope="col" className="border-b border-line-2 py-2.5 text-right font-normal">Listes où le Ban Radar fait mieux</th>
                    </tr>
                  </thead>
                  <tbody className="tabular-nums">
                    {SITE_FACTS.banTop25.map((row) => {
                      // Barres recalibrées sur le maximum du tableau (charte : la barre se lit avant le chiffre).
                      const max = Math.max(...SITE_FACTS.banTop25.map((r) => r.radar));
                      const ties = row.lists - row.better - row.worse;
                      return (
                        <tr key={row.format}>
                          <th scope="row" className="border-b border-line py-3 pr-4 align-top font-normal whitespace-nowrap">
                            <span className="mr-2 font-mono text-[11px] text-muted-text">{row.format}</span>
                            <span className="block text-[13px] text-muted-text">{row.period}</span>
                          </th>
                          <td className="border-b border-line py-3 pr-4">
                            {[
                              { label: "Ban Radar", value: row.radar, tone: "bg-signal" },
                              { label: "Part des decks", value: row.staples, tone: "bg-muted-text" },
                            ].map((bar) => (
                              <span key={bar.label} className="flex items-center gap-3 py-0.5">
                                <span className="w-[14ch] shrink-0 text-[13px] text-muted-text">{bar.label}</span>
                                <b className="w-[3ch] text-right font-medium">{bar.value}</b>
                                <span aria-hidden className="relative h-1 max-w-[240px] flex-1 rounded-[2px] bg-ink-4">
                                  <span
                                    className={`fill-in absolute inset-y-0 left-0 rounded-[2px] ${bar.tone}`}
                                    style={{ width: `${(bar.value / max) * 100}%` }}
                                  />
                                </span>
                              </span>
                            ))}
                          </td>
                          <td className="border-b border-line py-3 text-right align-top text-muted-text">
                            {`${row.better} sur ${row.lists}`}
                            <span className="block text-[13px]">{`${row.worse} moins bien${ties ? `, ${ties} ${ties > 1 ? "égalités" : "égalité"}` : ""}`}</span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="mt-4 max-w-[70ch] text-[15px] text-soft">
                {`Rang médian de l’ensemble des cartes touchées meilleur que celui de la part des decks sur ${SITE_FACTS.banTop25[0].medianBetter} listes TCG sur ${SITE_FACTS.banTop25[0].lists}, ${SITE_FACTS.banTop25[1].medianBetter} listes OCG sur ${SITE_FACTS.banTop25[1].lists}. Avec ${SITE_FACTS.banTop25[0].lists} listes par format, seul l’écart de top 25 en OCG dépasse ce que le hasard produit couramment.`}
              </p>
              <p className={`mt-3 ${SOURCE}`}>
                {`Source : backtest du ${fmtDate(SITE_FACTS.banBacktestDate)}, ${SITE_FACTS.banBacktestTotalLists} listes rejouées (10 TCG, 10 OCG), banlists Yugipedia. Poids du score réglés sur la liste TCG de mai 2026. Liste par liste : `}
                <Link href="/ban?tab=historique" className="text-signal underline-offset-4 hover:underline">
                  historique du Ban Center
                </Link>
                .
              </p>
            </Reveal>
          </div>
        </section>
      </main>

      <SiteFooter asOf={radar.as_of} />
    </>
  );
}
