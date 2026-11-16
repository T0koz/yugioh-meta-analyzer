// Vignette de carte à dimensions fixes : `width`/`height` réservent la place
// avant le chargement (CLS nul) et `loading="lazy"` diffère les images hors écran.
// Les cartes récentes absentes de la table `cards` n'ont pas d'image : on dessine
// alors un repli avec les initiales, jamais un trou.
const SIZES = {
  sm: { width: 34, height: 48, className: "h-12 w-[34px]" },
  md: { width: 44, height: 64, className: "h-16 w-11" },
} as const;

export function CardThumb({
  src,
  name,
  size = "sm",
  eager = false,
}: {
  src: string | null;
  name: string;
  size?: keyof typeof SIZES;
  /** Images visibles dès le premier écran : pas de chargement différé. */
  eager?: boolean;
}) {
  const { width, height, className } = SIZES[size];

  if (!src) {
    return (
      <span
        aria-hidden
        className={`grid shrink-0 place-items-center rounded-[3px] border border-line-2 bg-ink-4 font-mono text-[11px] text-muted-text ${className}`}
      >
        {name.slice(0, 2).toUpperCase()}
      </span>
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element -- vignette externe (YGOPRODeck), hébergement propre prévu (TOK-92)
    <img
      src={src}
      alt=""
      width={width}
      height={height}
      loading={eager ? "eager" : "lazy"}
      decoding="async"
      className={`shrink-0 rounded-[3px] border border-line-2 object-cover ${className}`}
    />
  );
}
