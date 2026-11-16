"use client";

import { useState } from "react";
import { Button } from "@/components/ds/control";
import { Input } from "@/components/ui/input";
import { CardChip } from "@/components/card-chip";
import { Em } from "@/components/ds/em";
import { Callout, DataFooter, Eyebrow, PageHero, StatBand } from "@/components/ds/page";
import { api } from "@/lib/api";
import { fmtNum, fmtPct } from "@/lib/format";
import type { BanSimResult } from "@/types";

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

  return (
    <>
      <PageHero
        eyebrow="Ban Center · Simulateur"
        title={
          <>
            Et si Konami la <Em>bannissait</Em> ?
          </>
        }
        intro="Effet du retrait d’une carte sur le graphe de co-occurrences : archétypes touchés, position de pont, perte de cohésion."
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
          {loading ? "Simulation…" : "Simuler le ban"}
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
              <Eyebrow>Carte retirée</Eyebrow>
              <h2 className="mt-2 text-[clamp(28px,4vw,44px)] leading-[1.05] font-medium tracking-[-0.035em] [overflow-wrap:anywhere]">
                <CardChip name={result.removed_card} variant="plain" />
              </h2>
            </div>
          </div>

          <StatBand
            stats={[
              { value: fmtNum(result.bridge_score), label: "Score de pont" },
              {
                value: fmtPct(fragmentation * 100, 0),
                label: community_id >= 0 ? `Fragmentation · communauté ${community_id}` : "Fragmentation · communauté inconnue",
              },
              { value: fmtNum(result.affected_archetypes.length), label: "Archétypes impactés" },
            ]}
          />

          {result.affected_archetypes.length > 0 && (
            <div className="mt-8">
              <p className="mb-3 font-mono text-[11px] tracking-[0.08em] text-muted-text uppercase">Archétypes impactés</p>
              <div className="flex flex-wrap gap-2">
                {result.affected_archetypes.map((arch) => (
                  <span key={arch} className="rounded-[4px] border border-line-2 px-2.5 py-1 font-mono text-[12px] text-soft">
                    {arch}
                  </span>
                ))}
              </div>
            </div>
          )}
          <DataFooter
            source="graphe de co-occurrences des decklists de tournoi, yugiohmeta.com"
            date="date de calcul non enregistrée dans la base servie"
            uncertainty="aucun intervalle : la simulation recalcule le graphe sans la carte, elle ne prévoit pas ce que joueraient les joueurs"
          />
        </section>
      )}
    </>
  );
}
