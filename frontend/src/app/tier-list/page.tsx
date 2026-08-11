import { api } from "@/lib/api";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { ArchetypeCard } from "./ArchetypeCard";

export default async function TierListPage() {
  const { data, generated_at } = await api.tierList();

  // meta_score = sqrt(share × placement_score_norm) ne dépasse jamais ~0.15 en pratique :
  // la barre est calibrée en relatif au max du snapshot plutôt qu'en absolu sur [0,1].
  const maxScore = Math.max(...data.map((d) => d.meta_score), 0);

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <main className="min-h-screen bg-slate-950 text-slate-100 px-6 py-10">
        <div className="max-w-5xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Yu-Gi-Oh! Meta Tier List</h1>
            <p className="text-slate-400 mt-1 text-sm">
              Based on {">"}19,000 tournament decklists · Updated {generated_at}
              <InfoTooltip text="sqrt(part de méta × score de placement normalisé) — moyenne géométrique entre volume de decks et performance en tournoi. Vignette dégradée en saturation selon le tier." />
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((entry) => (
              <ArchetypeCard key={entry.archetype} entry={entry} maxScore={maxScore} />
            ))}
          </div>
        </div>
      </main>
    </HoverPreviewProvider>
  );
}
