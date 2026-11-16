import Image from "next/image";
import { artCropUrl } from "@/lib/card-images";

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

  if (!src) {
    return (
      <span
        aria-hidden
        className={`grid shrink-0 place-items-center border border-line-2 bg-ink-4 font-mono text-[11px] text-muted-text ${box.className} ${className}`}
      >
        {name.slice(0, 2).toUpperCase()}
      </span>
    );
  }

  return (
    // Décorative : le nom de la carte est toujours écrit à côté.
    <Image
      src={src}
      alt=""
      width={box.width}
      height={box.height}
      loading={eager ? "eager" : "lazy"}
      className={`shrink-0 border border-line-2 object-cover ${box.className} ${className}`}
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
