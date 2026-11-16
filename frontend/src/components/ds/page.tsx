// Briques de mise en page communes à toutes les pages (docs/design-system.md §4-5).
import { controlClass } from "@/components/ds/control";

/** Conteneur de page : largeur max 1200 px, gutter latéral, marge basse. */
export function Page({ children }: { children: React.ReactNode }) {
  return <main className="mx-auto w-full max-w-[var(--maxw)] px-[var(--gutter)] pb-24">{children}</main>;
}

/** Label mono en majuscules précédé d'un point accent. */
export function Eyebrow({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p
      className={`flex items-center gap-2.5 font-mono text-[11px] uppercase tracking-[0.12em] text-muted-text before:h-1.5 before:w-1.5 before:shrink-0 before:rounded-full before:bg-signal ${className}`}
    >
      {children}
    </p>
  );
}

/**
 * En-tête de page. `size="xl"` = hero (tier list, home), `"lg"` = pages
 * d'outil. `aside` se place à droite (date des données, en mono).
 */
export function PageHero({
  eyebrow,
  title,
  intro,
  aside,
  size = "lg",
  children,
}: {
  eyebrow: React.ReactNode;
  title: React.ReactNode;
  intro?: React.ReactNode;
  aside?: React.ReactNode;
  size?: "xl" | "lg";
  children?: React.ReactNode;
}) {
  const h1 =
    size === "xl"
      ? "max-w-[14ch] text-[clamp(40px,7.4vw,92px)] leading-[0.95] tracking-[-0.05em]"
      : "max-w-[20ch] text-[clamp(34px,5.4vw,64px)] leading-none tracking-[-0.045em]";

  return (
    <header className="pt-14 pb-10">
      <div className="flex flex-wrap items-end justify-between gap-5">
        <div className="min-w-0">
          <Eyebrow className="enter">{eyebrow}</Eyebrow>
          <h1 className={`enter mt-[18px] font-medium text-balance [--i:1] ${h1}`}>{title}</h1>
        </div>
        {aside && (
          <div className="font-mono text-[11px] uppercase leading-[1.8] tracking-[0.08em] text-muted-text min-[760px]:text-right">
            {aside}
          </div>
        )}
      </div>
      {intro && <p className="enter mt-[22px] max-w-[52ch] text-soft [--i:2]">{intro}</p>}
      {children}
    </header>
  );
}

/** Bande de chiffres clés séparés par des filets verticaux. */
export function StatBand({ stats }: { stats: { value: React.ReactNode; label: string }[] }) {
  return (
    // Les filets sont le fond --line vu à travers le gap de 1 px : ils suivent
    // le nombre de colonnes (2 sur mobile, toutes sur desktop) sans calcul.
    <dl
      className="mt-9 grid grid-cols-2 gap-px border-y border-line bg-line min-[760px]:grid-cols-[repeat(var(--n),minmax(0,1fr))]"
      style={{ "--n": stats.length } as React.CSSProperties}
    >
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="grid gap-1 bg-ink py-4 pr-[18px] pl-[18px] min-[760px]:first:pl-0"
        >
          <dd className="text-[clamp(24px,3vw,34px)] font-medium leading-none tracking-[-0.03em] tabular-nums">
            {stat.value}
          </dd>
          <dt className="order-last font-mono text-[11px] uppercase tracking-[0.08em] text-muted-text">{stat.label}</dt>
        </div>
      ))}
    </dl>
  );
}

/** Barre de filtres + compteur aligné à droite. */
export function Toolbar({ children, count }: { children: React.ReactNode; count?: React.ReactNode }) {
  return (
    <div className="mb-3.5 flex flex-wrap items-center gap-2">
      {children}
      {count && (
        <span className="ml-auto font-mono text-[11px] uppercase tracking-[0.08em] text-muted-text">{count}</span>
      )}
    </div>
  );
}

/** Encart d'info : titre mono accent + texte doux. */
export function Callout({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="grid gap-1.5 rounded-[4px] border border-line-2 bg-ink-3 px-4 py-3.5">
      <p className="font-mono text-[11px] uppercase tracking-[0.1em] text-signal">{title}</p>
      <div className="grid gap-2 text-[14px] text-soft">{children}</div>
    </div>
  );
}

/**
 * Explication repliable (« Comment lire ce score ? ») : `<details>` natif,
 * donc utilisable depuis un server component, sans JS.
 */
export function Explainer({ label, title, children }: { label: string; title: string; children: React.ReactNode }) {
  return (
    <details className="group mb-6">
      <summary className={controlClass({ size: "sm" })}>
        {label}
        <span aria-hidden className="font-mono text-muted-text transition-transform group-open:rotate-45">
          +
        </span>
      </summary>
      <div className="mt-3 max-w-[72ch]">
        <Callout title={title}>{children}</Callout>
      </div>
    </details>
  );
}

/** Barre de progression 4 px, relative à un max donné. */
export function Meter({ value, max, tone = "signal" }: { value: number; max: number; tone?: "signal" | "soft" }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="h-1 overflow-hidden rounded-[2px] bg-ink-4">
      <div className={`fill-in h-full rounded-[2px] ${tone === "signal" ? "bg-signal" : "bg-soft/60"}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

/**
 * Pied de données : source, date et échantillon sous chaque graphique ou tableau
 * (TOK-99). `date` est obligatoire : une visualisation sans date ne se publie pas.
 */
export function DataFooter({
  source,
  date,
  sample,
  children,
}: {
  source: string;
  /** Déjà rédigée : « au 14 novembre 2026 », « août 25 à nov. 26 »… */
  date: string;
  sample?: string;
  /** Note de lecture facultative (légende, limite connue). */
  children?: React.ReactNode;
}) {
  return (
    <p className="mt-3 font-mono text-[12px] leading-[1.7] text-muted-text">
      Source : {source} · {date}
      {sample && ` · ${sample}`}
      {children && <> · {children}</>}
    </p>
  );
}
