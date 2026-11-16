// Briques communes d'explication graphique (lot 15, charte « ton et explication »).
// Ordre de préférence de la charte §2 : encodage → annotation → incertitude →
// légende → infobulle de définition → pied de données → couche « Méthode ».
// Tout est rendu côté serveur (aucun "use client") : ces briques se lisent sans
// JavaScript et s'importent aussi depuis un composant client.
// Documentation : docs/design-system.md §4 « Explication graphique ».
import Link from "next/link";
import { fmtNum } from "@/lib/format";
import { WEAK_MONTH_DECKS } from "@/lib/wilson";

/* ------------------------------------------------------------------ effectif */

/**
 * Badge d'effectif « k sur n » : accompagne tout pourcentage (charte §3).
 * `unit` s'ajoute après n (« 15 sur 16 listes »).
 */
export function SampleBadge({ k, n, unit, className = "" }: { k: number; n: number; unit?: string; className?: string }) {
  return (
    <span
      className={`inline-flex items-baseline gap-1 rounded-[3px] border border-line px-1.5 py-px font-mono text-[12px] leading-[1.5] whitespace-nowrap text-muted-text tabular-nums ${className}`}
    >
      {fmtNum(k)} sur {fmtNum(n)}
      {unit && ` ${unit}`}
    </span>
  );
}

/* ------------------------------------------------------ données atténuées */

/** Vrai si le mois compte moins de 100 decks (tous archétypes) : tracé atténué. */
export const isWeakMonth = (decks: number) => decks < WEAK_MONTH_DECKS;

/**
 * Style SVG d'un segment ou d'un point atténué : pointillé et plus pâle
 * (mois de moins de 100 decks, mois en cours). Même rendu sur tous les graphiques.
 */
export const WEAK_STROKE = { strokeDasharray: "3 4", strokeOpacity: 0.55 } as const;
export const WEAK_FILL_OPACITY = 0.55;
/** Opacité de remplissage d'une bande d'incertitude (couleur de la série). */
export const BAND_OPACITY = 0.16;

/** Chemin SVG fermé d'une bande d'incertitude (points déjà projetés en pixels ou en %). */
export function bandPath(points: { x: number; lo: number; hi: number }[]): string {
  if (points.length === 0) return "";
  const top = points.map((p, i) => `${i ? "L" : "M"}${p.x.toFixed(2)} ${p.hi.toFixed(2)}`).join(" ");
  const bottom = [...points]
    .reverse()
    .map((p) => `L${p.x.toFixed(2)} ${p.lo.toFixed(2)}`)
    .join(" ");
  return `${top} ${bottom} Z`;
}

/* ------------------------------------------------------------- annotation */

/**
 * Annotation posée sur un graphique HTML/SVG étiré : libellé court accroché à un
 * point (coordonnées en % du cadre). Au plus deux par graphique (charte §2).
 * Le texte est du HTML à 12 px, lisible par un lecteur d'écran sauf `decorative`.
 */
export function ChartAnnotation({
  x,
  y,
  children,
  decorative = false,
}: {
  x: number;
  y: number;
  children: React.ReactNode;
  decorative?: boolean;
}) {
  const align = x < 15 ? "" : x > 80 ? "-translate-x-full" : "-translate-x-1/2";
  return (
    <span
      aria-hidden={decorative || undefined}
      className={`absolute -mt-3 -translate-y-full font-mono text-[12px] leading-none font-medium whitespace-nowrap text-text tabular-nums ${align}`}
      style={{ left: `${x < 15 ? x - 1 : x > 80 ? x + 1.5 : x}%`, top: `${y}%` }}
    >
      {children}
    </span>
  );
}

/* ---------------------------------------------------------------- légende */

export type LegendSwatch = "line" | "dashed" | "band" | "bar" | "dot" | "ring" | "span" | "zone";

/** Échantillon de marque d'une légende (24 × 12 px). */
function Swatch({ kind, color }: { kind: LegendSwatch; color: string }) {
  switch (kind) {
    case "line":
      return <span aria-hidden className="h-0.5 w-4" style={{ backgroundColor: color }} />;
    case "dashed":
      return <span aria-hidden className="h-0 w-4 border-t-2 border-dashed opacity-60" style={{ borderColor: color }} />;
    case "band":
      return <span aria-hidden className="h-2.5 w-4 rounded-[1px] opacity-30" style={{ backgroundColor: color }} />;
    case "bar":
      return <span aria-hidden className="h-3 w-1" style={{ backgroundColor: color }} />;
    case "dot":
      return <span aria-hidden className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />;
    case "ring":
      return <span aria-hidden className="h-2.5 w-2.5 rounded-full border-2" style={{ borderColor: color }} />;
    case "span":
      return (
        <span aria-hidden className="relative h-2.5 w-5">
          <span className="absolute inset-x-0 top-1/2 h-1 -translate-y-1/2 rounded-full" style={{ backgroundColor: color }} />
        </span>
      );
    case "zone":
      return <span aria-hidden className="h-3 w-3 border-x border-line-2 bg-ink-4" />;
  }
}

/**
 * Légende sobre, en ligne au-dessus du graphique : une entrée par marque, sans phrase
 * (charte §2, étage 4). `as="figcaption"` quand elle ouvre une `<figure>`.
 */
export function ChartLegend({
  items,
  as: Tag = "div",
  className = "",
}: {
  items: { label: React.ReactNode; swatch: LegendSwatch; color?: string }[];
  as?: "div" | "figcaption";
  className?: string;
}) {
  return (
    <Tag
      className={`flex flex-wrap items-center gap-x-5 gap-y-1.5 font-mono text-[12px] leading-none text-muted-text tabular-nums ${className}`}
    >
      {items.map((item, i) => (
        <span key={i} className="inline-flex items-center gap-1.5">
          <Swatch kind={item.swatch} color={item.color ?? "var(--soft)"} />
          {item.label}
        </span>
      ))}
    </Tag>
  );
}

/* ------------------------------------------------------ barre d'intervalle */

/**
 * Barre d'incertitude horizontale (HTML) : segment [lo, hi] sur une échelle
 * [min, max] commune à toutes les lignes, point à la valeur observée.
 * `label` décrit l'intervalle pour les lecteurs d'écran (« 95 % : 3,1 à 8,4 % »).
 */
export function IntervalBar({
  value,
  lo,
  hi,
  min = 0,
  max,
  label,
  color = "var(--cat-1)",
}: {
  value: number;
  lo: number;
  hi: number;
  min?: number;
  max: number;
  label: string;
  color?: string;
}) {
  const pos = (v: number) => (max > min ? Math.min(100, Math.max(0, ((v - min) / (max - min)) * 100)) : 0);
  return (
    <span role="img" aria-label={label} className="relative block h-3 w-full">
      <span aria-hidden className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-line" />
      <span
        aria-hidden
        className="absolute top-1/2 h-1.5 -translate-y-1/2 rounded-full opacity-40"
        style={{ left: `${pos(lo)}%`, width: `${Math.max(0.5, pos(hi) - pos(lo))}%`, backgroundColor: color }}
      />
      <span
        aria-hidden
        className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-ink-2"
        style={{ left: `${pos(value)}%`, backgroundColor: color }}
      />
    </span>
  );
}

/* --------------------------------------------------------- couche Méthode */

/**
 * Couche « Méthode » repliée en bas d'un bloc (charte §2, étage 7) : 1 à 3 lignes en
 * langage simple (fenêtre, population, seuil appliqué), aucune formule, et un lien vers
 * l'ancre de /methode. `<details>` natif : sans JavaScript.
 */
export function MethodNote({ anchor, children }: { anchor: string; children: React.ReactNode }) {
  return (
    <details className="group/method mt-3">
      <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 rounded-[3px] font-mono text-[12px] text-muted-text transition-colors duration-200 hover:text-text [&::-webkit-details-marker]:hidden">
        <span aria-hidden className="transition-transform group-open/method:rotate-90">
          ›
        </span>
        Méthode
      </summary>
      <div className="mt-2 grid max-w-[72ch] gap-1 border-l border-line-2 pl-3 text-[13px] leading-[1.6] text-soft">
        {children}
        <Link href={`/methode#${anchor}`} className="w-fit font-mono text-[12px] text-muted-text underline underline-offset-4 hover:text-text">
          Détail dans la page Méthode
        </Link>
      </div>
    </details>
  );
}
