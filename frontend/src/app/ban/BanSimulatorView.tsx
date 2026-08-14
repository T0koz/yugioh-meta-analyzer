"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { CardChip } from "@/components/card-chip";
import { api } from "@/lib/api";
import type { BanSimResult } from "@/types";

export function BanSimulatorView({
  initialCard,
  initialResult,
}: {
  initialCard?: string;
  initialResult: BanSimResult | null;
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

  return (
    <>
      <p className="mb-6 text-sm text-slate-400">
        Simule l&apos;impact de bannir une carte sur le graphe de synergies
      </p>

      <div className="flex gap-3 mb-8">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && simulate()}
          placeholder="Ex: Ash Blossom & Joyous Spring"
          className="bg-slate-900 border-slate-700 text-slate-100 placeholder:text-slate-500 flex-1"
        />
        <button
          onClick={() => simulate()}
          disabled={loading}
          className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-md text-sm font-semibold transition-colors"
        >
          {loading ? "..." : "Simuler"}
        </button>
      </div>

      {notFound && (
        <div className="rounded-lg border border-slate-700 bg-slate-900 px-5 py-4 text-slate-400 text-sm">
          Carte non trouvée dans la base. Essaie <span className="text-indigo-400">Ash Blossom & Joyous Spring</span> ou <span className="text-indigo-400">Nibiru, the Primal Being</span>.
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4 flex items-center gap-4">
            {result.image_url && (
              // eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck)
              <img
                src={result.image_url}
                alt={result.removed_card}
                className="w-16 rounded-md border border-slate-700 shrink-0"
              />
            )}
            <div>
              <p className="text-xs text-slate-500 mb-1">Carte bannie</p>
              <p className="text-lg font-bold">
                <CardChip name={result.removed_card} className="!bg-transparent !border-0 !px-0 !text-red-400 !text-lg hover:!text-red-300" />
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4">
              <p className="text-xs text-slate-500 mb-1">Bridge Score</p>
              <p className="text-2xl font-bold tabular-nums text-indigo-400">
                {result.bridge_score.toFixed(5)}
              </p>
              <p className="text-xs text-slate-500 mt-1">Centralité de type pont</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4">
              <p className="text-xs text-slate-500 mb-1">
                Fragmentation{" "}
                {result.community_impact.community_id >= 0
                  ? `communauté #${result.community_impact.community_id}`
                  : "(communauté inconnue)"}
              </p>
              <p className="text-2xl font-bold tabular-nums text-orange-400">
                {(result.community_impact.fragmentation * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-slate-500 mt-1">Perte de cohésion</p>
            </div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4">
            <p className="text-xs text-slate-500 mb-3">Archétypes impactés ({result.affected_archetypes.length})</p>
            <div className="flex flex-wrap gap-2">
              {result.affected_archetypes.map((arch) => (
                <span
                  key={arch}
                  className="px-2 py-1 bg-slate-800 border border-slate-700 rounded text-sm text-slate-300"
                >
                  {arch}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
