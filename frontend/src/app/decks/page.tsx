import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { api } from "@/lib/api";
import { artCropUrl } from "@/lib/card-images";
import { fmtCopies, fmtDate, fmtNum, fmtPct, fmtWindow } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { CardArt } from "@/components/card-art";
import { DataFooter, Page, PageHero, StatBand } from "@/components/ds/page";
import { TierTag } from "@/components/ds/tags";
import { PageTransition } from "@/components/view-transitions";
import type { DeckIndexEntry } from "@/types";

const SOURCE = "decklists de tournoi TCG légales à la date du tournoi, yugiohmeta.com";
const H2 = "text-[clamp(22px,2.6vw,30px)] leading-tight font-medium tracking-[-0.03em]";

export async function generateMetadata(): Promise<Metadata> {
  const { data, window, rule } = await api.decks();
  const profiled = data.filter((d) => d.has_profile);
  const period = window ? fmtWindow(window) : "fenêtre courante";
  return pageMetadata({
    title: "Decks TCG : composition par archétype",
    description: `Composition de ${profiled.length} archétypes Yu-Gi-Oh! TCG relevés dans au moins ${rule.min_decks} listes de tournoi, sur ${fmtNum(window?.n_decks ?? 0)} decks, ${period}. Source : ${DECK_SOURCE}.`,
    path: "/decks",
  });
}

function DeckTile({ entry, nWindow }: { entry: DeckIndexEntry; nWindow: number }) {
  return (
    <li className="group relative isolate grid content-start gap-4 overflow-hidden rounded-[8px] border border-line bg-ink-2 p-4 transition-colors duration-200 hover:border-line-2 hover:bg-ink-3">
      {entry.image_url && (
        // Illustration recadrée en fond de tuile, très assombrie : même traitement que la tier list.
        // Écran large seulement et jamais prioritaire : chargée d'emblée sur mobile, elle devenait
        // l'élément LCP (2,6 s mesurés, contre 1,8 s une fois différée).
        <span
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 -z-10 hidden w-[62%] [mask-image:linear-gradient(270deg,rgb(0_0_0/0.34),transparent)] min-[760px]:block"
        >
          <Image
            src={artCropUrl(entry.image_url)}
            alt=""
            fill
            sizes="(min-width: 1000px) 250px, 31vw"
            loading="lazy"
            className="object-cover object-[center_28%]"
          />
        </span>
      )}

      <div className="flex items-start justify-between gap-3">
        <h3 className="min-w-0 text-[20px] leading-tight font-medium tracking-[-0.02em] [overflow-wrap:anywhere] [text-shadow:0_1px_10px_var(--ink)]">
          {/* Le lien couvre toute la tuile (::after). */}
          <Link
            href={`/decks/${entry.slug}`}
            className="outline-none transition-colors duration-200 group-hover:text-signal-hi after:absolute after:inset-0 after:content-[''] focus-visible:after:rounded-[8px] focus-visible:after:outline-2 focus-visible:after:-outline-offset-2 focus-visible:after:outline-signal-hi"
          >
            {entry.archetype}
          </Link>
        </h3>
        <TierTag tier={entry.tier} />
      </div>

      <p className="font-mono text-[12px] leading-[1.7] text-soft tabular-nums">
        {fmtNum(entry.decks)} listes sur {fmtNum(nWindow)} · {fmtPct(entry.share * 100)}
      </p>

      <ul className="flex gap-2" aria-label="Cartes de base propres à l’archétype">
        {entry.preview.map((card) => (
          <li key={card.card_name} className="grid justify-items-center gap-1.5">
            <CardArt src={card.image_url} name={card.card_name} size="sm" />
            <span className="sr-only">
              {card.card_name} : {card.n_lists} listes sur {entry.decks}
            </span>
            <span aria-hidden className="font-mono text-[12px] text-muted-text tabular-nums">
              {fmtPct(card.share * 100, 0)}
            </span>
          </li>
        ))}
      </ul>

      <p className="text-[14px] text-soft">
        <strong className="font-medium text-text tabular-nums">{fmtNum(entry.base_cards)} cartes de base</strong> au
        main deck, {fmtCopies(entry.base_copies)} exemplaires
      </p>
    </li>
  );
}

export default async function DecksPage() {
  const { data, window, rule, computed_at } = await api.decks();
  const profiled = data.filter((d) => d.has_profile);
  const others = data.filter((d) => !d.has_profile);
  const period = window ? fmtWindow(window) : "fenêtre inconnue";
  const nWindow = window?.n_decks ?? 0;
  const covered = profiled.reduce((sum, d) => sum + d.decks, 0);
  const basePct = fmtPct(rule.base_min_share * 100, 0);
  const calc = computed_at ? `calcul du ${fmtDate(computed_at)}` : "date de calcul inconnue";

  return (
    <PageTransition id="decks">
      <Page>
        <PageHero
          eyebrow={`Decks · TCG · ${period} · ${fmtNum(nWindow)} decks`}
          title="Composition des decks"
          intro={
            <>
              Pour chaque archétype relevé dans au moins {rule.min_decks} listes de tournoi TCG de {period} : part des
              listes qui jouent chaque carte, et nombre d’exemplaires médian.
            </>
          }
        >
          <StatBand
            stats={[
              { value: fmtNum(profiled.length), label: `Archétypes à ${rule.min_decks} listes ou plus` },
              { value: fmtNum(covered), label: `Listes couvertes sur ${fmtNum(nWindow)}` },
              { value: nWindow ? fmtPct((covered / nWindow) * 100, 0) : "—", label: "Part des decks de la fenêtre" },
              { value: `≥ ${basePct}`, label: "Des listes : carte « de base »" },
            ]}
          />
        </PageHero>

        {data.length === 0 ? (
          <p className="rounded-[6px] border border-line bg-ink-2 px-4 py-6 text-[14px] text-soft">
            Aucun profil de composition dans la base servie.
          </p>
        ) : (
          <>
            <section aria-labelledby="h-fiches">
              <h2 id="h-fiches" className={H2}>
                Archétypes avec fiche
              </h2>
              <ul className="mt-5 grid gap-3 min-[640px]:grid-cols-2 min-[1000px]:grid-cols-3">
                {profiled.map((entry) => (
                  <DeckTile key={entry.slug} entry={entry} nWindow={nWindow} />
                ))}
              </ul>
              <DataFooter source={SOURCE} date={`${period}, ${calc}`} sample={`${fmtNum(covered)} listes, ${fmtNum(profiled.length)} archétypes`}>
                carte de base : dans au moins {basePct} des listes de l’archétype ; pourcentage sous une vignette :
                part des listes qui jouent la carte ; exemplaires : somme des médianes ; tier : celui de la tier list,
                même fenêtre
              </DataFooter>
            </section>

            {others.length > 0 && (
              <section aria-labelledby="h-autres" className="mt-16">
                <h2 id="h-autres" className={H2}>
                  Moins de {rule.min_decks} listes
                </h2>
                <p className="mt-2 max-w-[68ch] text-[14px] text-soft">
                  {fmtNum(others.length)} archétypes, {fmtNum(nWindow - covered)} listes sur {fmtNum(nWindow)} de {period}.
                  Sous {rule.min_decks} listes, aucune part n’est calculée : la page de l’archétype montre ses listes.
                </p>
                <ul className="mt-5 gap-x-8 [column-width:240px]">
                  {others.map((entry) => (
                    <li
                      key={entry.slug}
                      className="flex break-inside-avoid items-baseline justify-between gap-3 border-b border-line py-2 text-[14px]"
                    >
                      <Link
                        href={`/decks/${entry.slug}`}
                        className="min-w-0 transition-colors duration-200 [overflow-wrap:anywhere] hover:text-signal-hi"
                      >
                        {entry.archetype}
                      </Link>
                      <span className="shrink-0 font-mono text-[12px] text-muted-text tabular-nums">
                        {fmtNum(entry.decks)} {entry.decks > 1 ? "listes" : "liste"}
                      </span>
                    </li>
                  ))}
                </ul>
                <DataFooter source={SOURCE} date={`${period}, ${calc}`} sample={`${fmtNum(nWindow - covered)} listes, ${fmtNum(others.length)} archétypes`}>
                  seuil de {rule.min_decks} listes : à 5 listes, 19 à 24 % des étiquettes changent d’un tirage de
                  listes à l’autre, 9 à 13 % à 8 listes (mesuré sur Elfnote et Angelechy)
                </DataFooter>
              </section>
            )}
          </>
        )}
      </Page>
    </PageTransition>
  );
}
