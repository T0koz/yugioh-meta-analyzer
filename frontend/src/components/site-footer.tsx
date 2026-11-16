import Link from "next/link";
import { fmtDate } from "@/lib/format";

const COLUMNS: { title: string; links: { href: string; label: string }[] }[] = [
  {
    title: "Méta",
    links: [
      { href: "/tier-list", label: "Tier list" },
      { href: "/evolution", label: "Évolution" },
      { href: "/predictions", label: "Prédictions" },
    ],
  },
  {
    title: "Bans",
    links: [
      { href: "/ban", label: "Ban Radar" },
      { href: "/ban?tab=impact", label: "Impact des cartes" },
      { href: "/ban?tab=simulateur", label: "Simulateur de ban" },
    ],
  },
  {
    title: "Boutique",
    links: [
      { href: "/boutique", label: "Signaux boutique" },
      { href: "/early-signals", label: "Signaux précoces" },
      { href: "/graph", label: "Graphe de synergies" },
    ],
  },
];

/** Pied de page : liens, date des données, sources et mentions. `asOf` au format « AAAA-MM-JJ ». */
export function SiteFooter({ asOf }: { asOf?: string }) {
  return (
    <footer className="mt-24 border-t border-line">
      <div className="mx-auto grid w-full max-w-[var(--maxw)] gap-10 px-[var(--gutter)] pt-12 pb-16 min-[760px]:grid-cols-[minmax(0,1.3fr)_repeat(3,minmax(0,1fr))]">
        <div>
          <p className="flex items-center gap-2 font-mono text-[14px] font-semibold tracking-[0.08em] text-text">
            <span
              aria-hidden
              className="h-3.5 w-3.5 bg-signal [clip-path:polygon(0_100%,30%_0,50%_60%,70%_0,100%_100%,80%_100%,70%_45%,50%_100%,30%_45%,20%_100%)]"
            />
            YGO META
          </p>
          <p className="mt-4 max-w-[38ch] text-[14px] text-muted-text">
            Méta Yu-Gi-Oh! TCG et OCG, calculée sur les decklists de tournoi.
          </p>
          <p className="mt-4 font-mono text-[11px] leading-[1.8] tracking-[0.08em] text-muted-text uppercase">
            {asOf && (
              <>
                Données au {fmtDate(asOf)}
                <br />
              </>
            )}
            Mise à jour chaque lundi
          </p>
        </div>

        {COLUMNS.map((column) => (
          <nav key={column.title} aria-label={column.title}>
            <p className="font-mono text-[11px] tracking-[0.1em] text-muted-text uppercase">{column.title}</p>
            <ul className="mt-3 grid gap-0.5">
              {column.links.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="-mx-2 inline-flex min-h-9 items-center rounded-[4px] px-2 text-[14px] text-soft transition-colors duration-200 hover:text-text"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ))}

        <div className="grid gap-1.5 border-t border-line pt-6 font-mono text-[12px] leading-[1.7] text-muted-text min-[760px]:col-span-4">
          <p>
            Sources : decklists de tournoi yugiohmeta.com · cartes et images YGOPRODeck · banlists Yugipedia · prix
            Cardmarket.
          </p>
          <p>
            Site indépendant, sans lien avec Konami. Yu-Gi-Oh! est une marque de ses ayants droit. Scores et signaux :
            estimations statistiques, sans garantie.
          </p>
        </div>
      </div>
    </footer>
  );
}
