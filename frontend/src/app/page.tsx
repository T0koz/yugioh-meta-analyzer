import Link from "next/link";
import { api } from "@/lib/api";
import { fmtMonthYear, fmtNum, fmtPct } from "@/lib/format";
import { SITE_FACTS } from "@/lib/site-facts";
import { Em } from "@/components/ds/em";
import { Eyebrow, Page } from "@/components/ds/page";
import type { PredictionEntry } from "@/types";

// Home en bento (docs/design-system.md §4, maquette B) : une tuile par usage,
// pensée pour le pitch boutiques. Une seule tuile accent, un seul bouton plein.

const TILE =
  "grid min-w-0 content-between gap-3.5 rounded-[8px] border p-[22px] transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-px col-span-12";

function TileTag({ letter, children, className = "" }: { letter: string; children: React.ReactNode; className?: string }) {
  return (
    <p className={`flex items-center gap-2.5 font-mono text-[11px] uppercase tracking-[0.1em] ${className}`}>
      <b className="rounded-[3px] border border-current px-[5px] font-medium">{letter}</b>
      {children}
    </p>
  );
}

const H3 = "text-[clamp(22px,2.6vw,30px)] leading-[1.08] font-medium tracking-[-0.03em] text-balance";

/** Plus forte hausse prévue : c'est elle qui « vend » la prédiction. */
function biggestRise(predictions: PredictionEntry[]): PredictionEntry | undefined {
  return [...predictions].sort((a, b) => b.predicted - b.current - (a.predicted - a.current))[0];
}

function PredictionSpark({ current, predicted }: { current: number; predicted: number }) {
  // Deux points honnêtes (actuel, prévu) sur une échelle commune, pas de courbe inventée.
  const max = Math.max(current, predicted) || 1;
  const y = (v: number) => 56 - (v / max) * 40;
  return (
    <svg viewBox="0 0 200 70" width="100%" role="img" aria-label={`Actuel ${fmtNum(current * 100, 1)}, prévu ${fmtNum(predicted * 100, 1)}`}>
      <line x1="12" y1="58" x2="188" y2="58" stroke="var(--on-signal)" strokeOpacity=".25" />
      <line x1="40" y1={y(current)} x2="172" y2={y(predicted)} stroke="var(--on-signal)" strokeWidth="2.5" strokeDasharray="3 5" strokeLinecap="round" />
      <circle cx="40" cy={y(current)} r="4.5" fill="var(--on-signal)" />
      <circle cx="172" cy={y(predicted)} r="4.5" fill="var(--signal)" stroke="var(--on-signal)" strokeWidth="2.5" />
      <text x="40" y="68" textAnchor="middle" fontFamily="var(--font-jetbrains-mono)" fontSize="9" fill="var(--on-signal)">ACTUEL</text>
      <text x="172" y="68" textAnchor="middle" fontFamily="var(--font-jetbrains-mono)" fontSize="9" fill="var(--on-signal)">PRÉVU</text>
    </svg>
  );
}

function GraphSketch() {
  return (
    <svg viewBox="0 0 240 150" width="100%" role="img" aria-label="Aperçu stylisé du graphe : une carte pont relie plusieurs paquets">
      <g stroke="var(--line-2)" strokeWidth="1">
        <line x1="40" y1="40" x2="110" y2="75" /><line x1="40" y1="110" x2="110" y2="75" />
        <line x1="110" y1="75" x2="180" y2="40" /><line x1="110" y1="75" x2="190" y2="115" />
        <line x1="180" y1="40" x2="215" y2="70" /><line x1="40" y1="40" x2="22" y2="80" />
        <line x1="190" y1="115" x2="215" y2="70" />
      </g>
      <g fill="var(--ink-4)" stroke="var(--line-2)">
        <circle cx="40" cy="40" r="9" /><circle cx="40" cy="110" r="7" /><circle cx="180" cy="40" r="10" />
        <circle cx="190" cy="115" r="8" /><circle cx="215" cy="70" r="6" /><circle cx="22" cy="80" r="5" />
      </g>
      <circle cx="110" cy="75" r="17" fill="var(--signal)" />
      <circle cx="110" cy="75" r="27" fill="none" stroke="var(--signal)" strokeOpacity=".35" />
      <text x="110" y="79" textAnchor="middle" fontFamily="var(--font-jetbrains-mono)" fontSize="9" fontWeight="500" fill="var(--on-signal)">PONT</text>
    </svg>
  );
}

export default async function Home() {
  const [boutique, radar, predictions] = await Promise.all([
    api.boutiqueSignals(),
    api.banRadar({ limit: 3 }),
    api.predictions(),
  ]);
  const topBuy = boutique.data[0];
  const topRisk = radar.data[0];
  const rise = biggestRise(predictions.data);

  return (
    <Page>
      <header className="relative isolate pt-14 pb-10">
        {/* Les points sont sur un calque à part : un mask-image sur le header
            estomperait aussi le texte et les boutons. */}
        <div
          aria-hidden
          className="bg-dots absolute inset-y-0 -inset-x-[var(--gutter)] -z-10 [mask-image:linear-gradient(to_bottom,black_55%,transparent)]"
        />
        <div>
          <Eyebrow>Analyse de méta · Yu-Gi-Oh! TCG &amp; OCG</Eyebrow>
          <h1 className="mt-[18px] max-w-[16ch] text-[clamp(36px,6vw,72px)] leading-[0.98] font-medium tracking-[-0.045em] text-balance">
            Le TCG suit l’OCG, <Em>avec quelques mois</Em> de retard.
          </h1>
        </div>
        <p className="mt-[22px] max-w-[52ch] text-soft">
          {`Corrélation d’environ ${fmtNum(SITE_FACTS.ocgTcgCorrelation, 2)} entre la méta OCG et la méta TCG ${SITE_FACTS.ocgTcgLagRange} plus tard (IC 95 % : ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[0], 2)} à ${fmtNum(SITE_FACTS.ocgTcgCorrelationCi[1], 2)}, ${SITE_FACTS.ocgTcgArchetypes} archétypes), sur ${fmtNum(SITE_FACTS.decklists)} decklists de tournoi. Un signal réel mais modéré : une aide à la décision, pas une garantie.`}
        </p>
        <div className="mt-7 flex flex-wrap gap-2.5">
          <Link
            href="/boutique"
            className="rounded-[4px] border border-signal bg-signal px-[18px] py-[11px] text-[14px] font-medium text-on-signal transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-px"
          >
            Voir les signaux boutique →
          </Link>
          <Link
            href="/tier-list"
            className="rounded-[4px] border border-line-2 bg-ink-3 px-[18px] py-[11px] text-[14px] font-medium text-text transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-px"
          >
            Tier list du moment
          </Link>
        </div>
      </header>

      <div className="mt-2 grid grid-cols-12 gap-3">
        {topBuy && (
          <Link href="/boutique" className={`${TILE} border-transparent bg-paper text-paper-ink min-[900px]:col-span-5`}>
            <TileTag letter="A" className="text-paper-muted">Signal boutique</TileTag>
            <p className="text-[clamp(80px,12vw,148px)] leading-[0.85] font-medium tracking-[-0.07em] tabular-nums">
              {fmtNum(topBuy.buy_score)}
              <sup className="ml-1.5 align-top font-mono text-[14px] font-normal tracking-normal text-paper-muted">/100</sup>
            </p>
            <div>
              <h3 className={H3}>
                {topBuy.card_name}, <em className="font-serif font-normal italic tracking-[-0.01em] text-signal-deep">{topBuy.archetype}</em>.
              </h3>
              <p className="mt-2 mb-3.5 text-[14px] text-paper-muted">À surveiller avant l’arrivée de l’archétype en TCG.</p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  `Cardmarket ${fmtNum(topBuy.cm_price, 2)} €`,
                  topBuy.tcg_entry_estimated && `Entrée TCG ${fmtMonthYear(topBuy.tcg_entry_estimated)}`,
                  topBuy.ban_tcg && `${topBuy.ban_tcg} en TCG`,
                ]
                  .filter(Boolean)
                  .map((kv) => (
                    <span
                      key={kv as string}
                      className="rounded-[3px] border border-[var(--paper-line)] px-2 py-1 font-mono text-[11px] tracking-[0.06em] uppercase"
                    >
                      {kv}
                    </span>
                  ))}
              </div>
            </div>
          </Link>
        )}

        <Link href="/ban" className={`${TILE} border-line-2 bg-ink-3 min-[900px]:col-span-4`}>
          <TileTag letter="B" className="text-muted-text">Ban Radar</TileTag>
          <h3 className={H3}>
            Les cartes que Konami va <Em>toucher</Em>.
          </h3>
          <div>
            {radar.data.map((entry) => (
              <div key={entry.card_name} className="flex justify-between gap-3 border-t border-line py-[9px] text-[14px] first:border-t-0">
                <span className="min-w-0 [overflow-wrap:anywhere]">{entry.card_name}</span>
                <b className="font-mono text-[13px] font-medium text-signal tabular-nums">{fmtNum(entry.ban_risk_score, 1)}</b>
              </div>
            ))}
          </div>
        </Link>

        {rise && (
          <Link href="/predictions" className={`${TILE} border-transparent bg-signal text-on-signal min-[900px]:col-span-3`}>
            <TileTag letter="C" className="text-on-signal/70">Prédictions</TileTag>
            <div>
              <h3 className={H3}>
                {rise.archetype}
                <br />
                <span className="tabular-nums">
                  {fmtNum(rise.current * 100, 1)} → {fmtNum(rise.predicted * 100, 1)}
                </span>
              </h3>
              <p className="mt-2 text-[14px] text-on-signal/70">Score méta actuel, puis prévu le mois prochain (×100).</p>
            </div>
            <PredictionSpark current={rise.current} predicted={rise.predicted} />
          </Link>
        )}

        <Link href="/graph" className={`${TILE} border-line-2 bg-ink-3 min-[900px]:col-span-7`}>
          <TileTag letter="D" className="text-muted-text">Graphe de synergies</TileTag>
          <div className="grid items-center gap-[22px] min-[700px]:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
            <div>
              <h3 className={H3}>
                {SITE_FACTS.graphCommunities} communautés de cartes, <Em>une</Em> carte pont.
              </h3>
              <p className="mt-2.5 text-[14px] text-muted-text">
                La centralité d’intermédiarité montre quelles cartes relient les archétypes : les premières touchées
                par un ban.
              </p>
            </div>
            <GraphSketch />
          </div>
        </Link>

        {topRisk && (
          <Link
            href={`/ban?tab=simulateur&card=${encodeURIComponent(topRisk.card_name)}`}
            className={`${TILE} border-line-2 bg-ink-3 min-[900px]:col-span-5`}
          >
            <TileTag letter="E" className="text-muted-text">Recherche</TileTag>
            <h3 className={H3}>
              Tape une carte. <Em>Vois</Em> son impact.
            </h3>
            <div className="rounded-[6px] border border-line bg-ink px-4 py-3.5 font-mono text-[13px] leading-[1.9] text-soft">
              <p>
                <span className="text-faint">&gt;</span> impact si ban de
              </p>
              <p className="text-text">
                {topRisk.card_name}
                <span aria-hidden className="ml-0.5 inline-block h-[15px] w-2 bg-signal align-[-3px]" />
              </p>
              {[
                ["archétypes qui la jouent", fmtNum(topRisk.n_archetypes)],
                ["part des decks", fmtPct(topRisk.deck_share, 2)],
                ["risque de ban", `${fmtNum(topRisk.ban_risk_score, 1)} / 100`],
              ].map(([label, value]) => (
                <p key={label} className="mt-1.5 flex justify-between gap-3 border-t border-dashed border-line pt-1.5">
                  <span>{label}</span>
                  <span className="text-signal">{value}</span>
                </p>
              ))}
            </div>
          </Link>
        )}
      </div>
    </Page>
  );
}
