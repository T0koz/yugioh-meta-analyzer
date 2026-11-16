import { Page } from "@/components/ds/page";

// Squelette du Ban Center, seule route rendue à la demande (elle lit ?tab= et ?kind=).
// Il vivait à la racine (app/loading.tsx) : Next enveloppait alors TOUTES les pages
// dans un Suspense, et le HTML statique livrait ce squelette puis le contenu dans
// un bloc caché, révélé par un script. Conséquences mesurées (TOK-106) : sans
// JavaScript, les pages statiques n'affichaient que « Chargement des données… »,
// et React retardait la révélation d'environ 0,4 s (LCP mobile 2,1 s au lieu de 1,7 s).
// Ne pas le remettre à la racine tant que les autres pages sont statiques.
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
