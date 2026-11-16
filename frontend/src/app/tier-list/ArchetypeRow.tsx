"use client";

import { useHoverPreview } from "@/components/hover-preview-context";
import Link from "next/link";
import { CardArt, CardImage } from "@/components/card-art";
import { artCropUrl } from "@/lib/card-images";
import { IntervalBar } from "@/components/ds/explain";
import { TierTag, TrendLabel } from "@/components/ds/tags";
import { NAV_FORWARD, SharedElement, archetypeArtName, archetypeTitleName } from "@/components/view-transitions";
import { fmtNum, fmtPct } from "@/lib/format";
import { wilsonInterval } from "@/lib/wilson";
import type { TierEntry } from "@/types";

// Colonnes : rang · vignette · nom · tier · barre (part de méta) · part · tendance.
// Sous 760 px, tier et barre disparaissent (docs/design-system.md §4).
const GRID =
  "grid grid-cols-[22px_34px_minmax(0,1fr)_54px_88px] gap-2.5 px-3 min-[760px]:grid-cols-[28px_40px_minmax(0,1.2fr)_60px_minmax(80px,1fr)_64px_92px] min-[760px]:gap-4 min-[760px]:px-4";

export function ArchetypeRow({
  entry,
  rank,
  nDecks,
  maxShare,
  highlighted,
}: {
  entry: TierEntry;
  rank: number;
  /** Decks de la fenêtre, tous archétypes : n de la part. */
  nDecks: number;
  maxShare: number;
  highlighted: boolean;
}) {
  const { setPreview } = useHoverPreview();
  const banner = entry.tier !== "Rogue";
  const [lo, hi] = wilsonInterval(entry.decks, nDecks);

  return (
    <div
      onMouseEnter={() => entry.image_url && setPreview({ name: entry.archetype, imageUrl: entry.image_url })}
      onMouseLeave={() => setPreview(null)}
      className={`${GRID} group relative isolate items-center border-t border-line transition-colors duration-200 first:border-t-0 hover:bg-ink-3 ${
        banner ? "py-2 min-[760px]:py-4" : "py-2"
      } ${
        highlighted
          ? "bg-[linear-gradient(90deg,color-mix(in_srgb,var(--signal)_9%,var(--ink)),var(--ink)_60%)]"
          : "bg-ink"
      }`}
    >
      {banner && entry.image_url && (
        // Bandeau d'archétype (T0 à T3) : l'illustration recadrée passe derrière
        // le nom. Le masque la garde très sombre sous le texte (contraste) et la
        // laisse monter dans le vide entre le nom et l'étiquette de tier.
        <span
          aria-hidden
          className="pointer-events-none absolute inset-y-0 left-0 -z-10 hidden w-[52%] [mask-image:linear-gradient(90deg,transparent,rgb(0_0_0/0.22)_30%,rgb(0_0_0/0.45)_78%,transparent)] min-[760px]:block"
        >
          <CardImage
            src={artCropUrl(entry.image_url)}
            alt=""
            fill
            sizes="(min-width: 1200px) 600px, 52vw"
            loading={rank <= 4 ? "eager" : "lazy"}
            className="object-cover object-[center_30%]"
          />
        </span>
      )}

      <span className="font-mono text-[12px] text-faint tabular-nums">{String(rank).padStart(2, "0")}</span>

      {/* Vignette et nom portent le même nom de transition que sur la page de
          l'archétype : le navigateur les anime de la ligne vers l'en-tête. */}
      <SharedElement name={archetypeArtName(entry.slug)}>
        <CardArt src={entry.image_url} name={entry.archetype} eager={rank <= 8} />
      </SharedElement>

      <span
        className={`min-w-0 font-medium tracking-[-0.01em] [overflow-wrap:anywhere] ${
          banner ? "min-[760px]:text-[19px] min-[760px]:[text-shadow:0_1px_10px_var(--ink)]" : ""
        }`}
      >
        {/* Le lien couvre toute la ligne (::after), le survol garde l'aperçu de la carte. */}
        <Link
          href={`/archetype/${entry.slug}`}
          transitionTypes={NAV_FORWARD}
          className="outline-none transition-colors duration-200 group-hover:text-signal-hi after:absolute after:inset-0 after:content-[''] focus-visible:after:outline-2 focus-visible:after:-outline-offset-2 focus-visible:after:outline-signal-hi"
        >
          <SharedElement name={archetypeTitleName(entry.slug)}>
            <span className="inline-block">{entry.archetype}</span>
          </SharedElement>
        </Link>
        <small className={`block text-[12px] font-normal tabular-nums ${banner ? "text-soft" : "text-muted-text"}`}>
          {fmtNum(entry.decks)} sur {fmtNum(nDecks)} decks · score {fmtNum(entry.meta_score * 100, 1)} ·{" "}
          {/* Au-dessus du lien de ligne (::after) : mène à la fiche de composition (TOK-114). */}
          <Link
            href={`/decks/${entry.slug}`}
            className="relative z-10 -my-1.5 inline-block py-1.5 underline decoration-line-2 underline-offset-4 transition-colors duration-200 hover:text-signal-hi"
          >
            composition
          </Link>
        </small>
      </span>

      <span className="hidden min-[760px]:block">
        <TierTag tier={entry.tier} />
      </span>

      <span className="hidden min-[760px]:block">
        <IntervalBar
          value={entry.share}
          lo={lo}
          hi={hi}
          max={maxShare}
          color="var(--soft)"
          label={`Part ${fmtPct(entry.share * 100)}, intervalle à 95 % de ${fmtPct(lo * 100)} à ${fmtPct(hi * 100)}`}
        />
      </span>

      <span className="text-right font-mono text-[14px] font-medium tabular-nums">{fmtPct(entry.share * 100)}</span>

      <span className="text-right">
        <TrendLabel trend={entry.trend} />
      </span>
    </div>
  );
}
