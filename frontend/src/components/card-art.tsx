import Image from "next/image";
import { SafeImage } from "@/components/safe-image";
import { artCropUrl, fullCardUrl, smallCardUrl } from "@/lib/card-images";

// Image de carte à dimensions fixes (rapport 59:86 d'une carte Yu-Gi-Oh!).
// `width`/`height` réservent la place avant le chargement (CLS nul) et
// next/image sert un fichier à la taille d'affichage, différé hors écran.
// Les cartes récentes absentes de la table `cards` n'ont pas d'image : on
// dessine alors un repli avec les initiales, jamais un trou.
const SIZES = {
  xs: { width: 34, height: 48, className: "h-12 w-[34px] rounded-[3px]" },
  sm: { width: 44, height: 64, className: "h-16 w-11 rounded-[3px]" },
  lg: { width: 132, height: 192, className: "h-48 w-[132px] rounded-[8px]" },
} as const;

export function CardArt({
  src,
  name,
  size = "xs",
  eager = false,
  className = "",
}: {
  src: string | null;
  name: string;
  size?: keyof typeof SIZES;
  /** Images visibles dès le premier écran : pas de chargement différé. */
  eager?: boolean;
  className?: string;
}) {
  const box = SIZES[size];

  const placeholder = (
    <span
      aria-hidden
      className={`grid shrink-0 place-items-center border border-line-2 bg-ink-4 font-mono text-[11px] text-muted-text ${box.className} ${className}`}
    >
      {name.slice(0, 2).toUpperCase()}
    </span>
  );
  if (!src) return placeholder;

  return (
    // Décorative : le nom de la carte est toujours écrit à côté.
    <SafeImage
      fallback={placeholder}
      src={size === "lg" ? fullCardUrl(src) : smallCardUrl(src)}
      alt=""
      width={box.width}
      height={box.height}
      loading={eager ? "eager" : "lazy"}
      className={`shrink-0 border border-line-2 object-cover ${box.className} ${className}`}
    />
  );
}

/**
 * Carte entière qui remplit son parent (positionné, rapport 59:86) : éventail du
 * hero, carte vedette. `sizes` = largeur d'affichage, pour que next/image serve
 * le bon fichier. Sans image : le nom de la carte, jamais un trou.
 */
export function CardArtFill({
  src,
  name,
  sizes,
  eager = false,
}: {
  src: string | null;
  name: string;
  sizes: string;
  eager?: boolean;
}) {
  const placeholder = (
    <span
      aria-hidden
      className="absolute inset-0 grid place-items-center p-3 text-center font-mono text-[11px] tracking-[0.1em] text-muted-text uppercase"
    >
      {name}
    </span>
  );
  if (!src) return placeholder;
  return (
    <SafeImage
      fallback={placeholder}
      src={fullCardUrl(src)}
      alt=""
      fill
      sizes={sizes}
      loading={eager ? "eager" : "lazy"}
      className="object-cover"
    />
  );
}

/** Pastille ronde recadrée sur l'illustration (pills, légendes). */
export function ArtDot({ src, size = 18 }: { src: string; size?: number }) {
  return (
    <Image
      src={artCropUrl(src)}
      alt=""
      width={size}
      height={size}
      className="shrink-0 rounded-full border border-line-2 object-cover"
      style={{ width: size, height: size }}
    />
  );
}
