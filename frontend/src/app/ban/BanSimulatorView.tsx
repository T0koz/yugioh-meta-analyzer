"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ds/control";
import { Input } from "@/components/ui/input";
import { CardChip } from "@/components/card-chip";
import { Em } from "@/components/ds/em";
import { SampleBadge } from "@/components/ds/explain";
import { Callout, DataFooter, Eyebrow, PageHero, StatBand } from "@/components/ds/page";
import { api } from "@/lib/api";
import { fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import { SITE_FACTS } from "@/lib/site-facts";
import type { BanSimResult, DeckArchetypeUsage } from "@/types";

// Au-delà, la liste se replie : Ash Blossom est jouée par plus de 50 archétypes de la fenêtre.
const ARCHETYPES_SHOWN = 12;
// Banlists confrontées au graphe (TOK-132) : la même mesure que le score de diffusion.
const BAN_LISTS = SITE_FACTS.diffusionEffect.lists;

function ArchetypeList({ items, className = "" }: { items: DeckArchetypeUsage[]; className?: string }) {
  return (
    <ul className={`flex flex-wrap gap-2 ${className}`}>
      {items.map((a) => (
        <li key={a.archetype}>
          <Link
            href={`/archetype/${a.slug}`}
            className="inline-flex items-baseline gap-2 rounded-[4px] border border-line-2 px-2.5 py-1 text-[13px] text-soft transition-colors duration-200 hover:border-signal hover:text-text"
          >
            {a.archetype}
            <SampleBadge k={a.lists} n={a.decks} unit="listes" className="border-0 px-0" />
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function BanSimulatorView({
  initialCard,
  initialResult,
  tabs,
}: {
  initialCard?: string;
  initialResult: BanSimResult | null;
  tabs: React.ReactNode;
}) {
  const [query, setQuery] = useState(initialCard ?? "");
  const [result, setResult] = useState<BanSimResult | null>(initialResult);
  // Arrivée via ?card= (recherche globale, "simuler le ban →") : le résultat
  // est déjà résolu côté serveur par la page parente, pas de round-trip client.
  const [notFound, setNotFound] = useState(Boolean(initialCard) && !initialResult);
  const [loading, setLoading] = useState(false);

  async function simulate() {
    const trimmed = query.trim();
    if (!trimmed) return;
    setLoading(true);
    try {
      const found = await api.simulateBan(trimmed);
      setResult(found);
      setNotFound(!found);
    } finally {
      setLoading(false);
    }
  }

  const { community_id, fragmentation } = result?.community_impact ?? { community_id: -1, fragmentation: 0 };
  const deckArchetypes = result?.deck_archetypes ?? [];
  const shown = deckArchetypes.slice(0, ARCHETYPES_SHOWN);
  const hidden = deckArchetypes.slice(ARCHETYPES_SHOWN);
  const window =
    result?.deck_window_start && result.deck_window_end
      ? `${fmtMonthShort(result.deck_window_start)} à ${fmtMonthShort(result.deck_window_end)}`
      : null;

  return (
    <>
      <PageHero
        eyebrow="Ban Center · Simulateur"
        title={
          <>
            La <Em>position</Em> d’une carte dans le graphe de <span className="whitespace-nowrap">co-occurrences</span>.
          </>
        }
        intro={`Position d’une carte dans le graphe de co-occurrences déjà calculé : score de diffusion, centralité de pont rapportée à la carte la plus centrale, archétypes de deck qui la jouent. Ce n’est pas une prévision de l’effet d’un ban : confrontée à ${BAN_LISTS} banlists, la centralité de pont n’améliore pas la prévision de la baisse des archétypes qui jouent la carte.`}
      >
        {tabs}
      </PageHero>

      <form
        className="mb-8 flex flex-wrap gap-2.5"
        onSubmit={(e) => {
          e.preventDefault();
          void simulate();
        }}
      >
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ex : Ash Blossom & Joyous Spring"
          aria-label="Carte à simuler"
          className="h-auto min-w-0 flex-1 basis-64 rounded-[var(--r-ctl)] border-line-2 bg-ink px-3.5 py-[11px] font-mono text-[13px] md:text-[13px]"
        />
        <Button type="submit" variant="primary" disabled={loading}>
          {loading ? "Recherche…" : "Afficher la position"}
        </Button>
      </form>

      {notFound && (
        <Callout title="Carte introuvable">
          <p>
            Carte absente de la table des cartes. Exemples présents : « Ash Blossom &amp; Joyous Spring », « Nibiru,
            the Primal Being ».
          </p>
        </Callout>
      )}

      {result && (
        <section>
          <div className="flex items-center gap-5">
            {result.image_url && (
              // eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck)
              <img
                src={result.image_url}
                alt={result.removed_card}
                className="w-16 shrink-0 rounded-[4px] border border-line-2"
              />
            )}
            <div className="min-w-0">
              <Eyebrow>Carte</Eyebrow>
              <h2 className="mt-2 text-[clamp(28px,4vw,44px)] leading-[1.05] font-medium tracking-[-0.035em] [overflow-wrap:anywhere]">
                <CardChip name={result.removed_card} variant="plain" />
              </h2>
            </div>
          </div>

          <StatBand
            stats={[
              { value: fmtNum(result.bridge_score), label: "Score de diffusion" },
              {
                value: fmtPct(fragmentation * 100, 0),
                label: community_id >= 0 ? `Centralité de pont, part du maximum · communauté ${community_id}` : "Centralité de pont, part du maximum · communauté inconnue",
              },
              { value: fmtNum(deckArchetypes.length), label: window ? `Archétypes de deck qui la jouent, ${window}` : "Archétypes de deck qui la jouent" },
            ]}
          />

          <div className="mt-8">
            <p className="mb-3 font-mono text-[11px] tracking-[0.08em] text-muted-text uppercase">
              Listes de chaque archétype qui jouent la carte (Main ou Extra Deck)
            </p>
            {shown.length > 0 ? (
              <>
                <ArchetypeList items={shown} />
                {hidden.length > 0 && (
                  <details className="group mt-3">
                    <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 font-mono text-[12px] text-muted-text transition-colors duration-200 hover:text-text [&::-webkit-details-marker]:hidden">
                      <span aria-hidden className="transition-transform group-open:rotate-90">›</span>
                      {`${fmtNum(hidden.length)} autres archétypes`}
                    </summary>
                    <ArchetypeList items={hidden} className="mt-3" />
                  </details>
                )}
              </>
            ) : (
              <p className="text-[14px] text-muted-text">Aucun archétype de la fenêtre ne joue cette carte.</p>
            )}
          </div>
          <DataFooter
            source="graphe de co-occurrences et decklists de tournoi TCG, yugiohmeta.com"
            date={window ? `archétypes : ${window} ; graphe : date de calcul non enregistrée` : "date de calcul du graphe non enregistrée dans la base servie"}
            sample={result.deck_window_decks ? `${fmtNum(result.deck_window_decks)} decks dans la fenêtre des archétypes` : undefined}
            uncertainty={`description, pas une prévision : le graphe n’est pas recalculé sans la carte ; confrontée à ${BAN_LISTS} banlists, la centralité n’améliore pas la prévision de la baisse des archétypes qui jouent la carte ; chaque part est donnée avec son effectif, sans intervalle`}
          >
            communauté : la première dont les archétypes principaux contiennent le nom de l’archétype porteur ; archétypes
            de deck : même fenêtre et mêmes listes que la tier list
          </DataFooter>
        </section>
      )}
    </>
  );
}
