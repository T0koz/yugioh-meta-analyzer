import { Page } from "@/components/ds/page";

// Squelette commun à toutes les routes : même gabarit que PageHero + une liste,
// pour que l'arrivée des données ne décale pas la mise en page.
export default function Loading() {
  return (
    <Page>
      <div role="status" aria-live="polite" className="pt-14">
        <p className="flex items-center gap-2.5 font-mono text-[11px] tracking-[0.12em] text-muted-text uppercase before:h-1.5 before:w-1.5 before:shrink-0 before:animate-pulse before:rounded-full before:bg-signal">
          Chargement des données…
        </p>
        <div aria-hidden className="mt-[18px] grid animate-pulse gap-3">
          <div className="h-[clamp(34px,5.4vw,64px)] w-[min(100%,520px)] rounded-[4px] bg-ink-3" />
          <div className="h-5 w-[min(100%,420px)] rounded-[4px] bg-ink-3" />
          <div className="mt-10 grid gap-px overflow-hidden rounded-[6px] border border-line bg-line">
            {Array.from({ length: 8 }, (_, i) => (
              <div key={i} className="h-14 bg-ink-2" />
            ))}
          </div>
        </div>
      </div>
    </Page>
  );
}
