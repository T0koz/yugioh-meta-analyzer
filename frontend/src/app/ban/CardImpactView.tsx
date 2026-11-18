import Link from "next/link";
import { api } from "@/lib/api";
import { fmtDate, fmtNum } from "@/lib/format";
import { CardChip } from "@/components/card-chip";
import { ButtonLink } from "@/components/ds/control";
import { Em } from "@/components/ds/em";
import { DataFooter, Explainer, Meter, PageHero } from "@/components/ds/page";
import type { CardImpactEntry } from "@/types";
import { KindFilterTabs, apiKind, type KindView } from "./kind-filter";
import { BigScore, RankedThumb, ROW_GRID } from "./BanRadarView";

function ImpactRow({ entry, rank, max }: { entry: CardImpactEntry; rank: number; max: number }) {
  // top_archetype est nul quand la carte est jouée un peu partout sans deck
  // d'attache : c'est une staple, pas une pièce d'archétype.
  const origin = entry.top_archetype ?? "Générique";

  return (
    <div className={ROW_GRID}>
      <BigScore value={fmtNum(entry.bridge_score)} label="Impact" tone="text-muted-text" />
      <RankedThumb src={entry.image_url} name={entry.card_name} rank={rank} />
      <div className="min-w-0">
        <h2 className="text-[20px] leading-tight font-medium tracking-[-0.02em] [overflow-wrap:anywhere]">
          <CardChip name={entry.card_name} subtitle={origin} variant="plain" />
        </h2>
        <p className="mt-1 text-[13px] text-muted-text">
          {[origin, `${fmtNum(entry.n_archetypes)} archétypes`, `${fmtNum(entry.decks)} decks`].join(" · ")}
        </p>
        <div className="mt-3">
          <Meter value={entry.bridge_score} max={max} />
        </div>
      </div>
      <ButtonLink
        href={`/ban?tab=simulateur&card=${encodeURIComponent(entry.card_name)}`}
        size="sm"
        className="col-start-3 w-fit min-[760px]:col-start-auto min-[760px]:justify-self-end"
      >
        Simuler le ban →
      </ButtonLink>
    </div>
  );
}

export async function CardImpactView({ view, tabs }: { view: KindView; tabs: React.ReactNode }) {
  const { data, as_of, n_decks_window } = await api.cardImpact({ limit: 50, kind: apiKind(view) });
  const max = Math.max(...data.map((d) => d.bridge_score), 0);

  return (
    <>
      <PageHero
        eyebrow="Ban Center · Cartes à impact"
        title={
          <>
            Les cartes jouées par le plus d’<Em>archétypes</Em> à la fois.
          </>
        }
        aside={
          <>
            Données au {fmtDate(as_of)}
            <br />
            {fmtNum(n_decks_window)} decks · 6 mois
          </>
        }
        intro={`Cartes TCG classées par nombre d’archétypes et de decks qui les jouent, sur ${fmtNum(n_decks_window)} decks de tournoi des 6 derniers mois.`}
      >
        {tabs}
      </PageHero>

      <Explainer label="Lecture du score" title="Lecture du score">
        <p>
          Score d’<strong className="font-medium text-text">impact</strong>, distinct du score de risque du{" "}
          <Link href="/ban?tab=radar" className="text-signal underline-offset-4 hover:underline">
            Ban Radar
          </Link>{" "}
          : nombre d’archétypes et de decks qui jouent la carte.
        </p>
        <p>
          Le score de pont augmente avec le nombre d’archétypes qui jouent la carte et, plus lentement, avec le nombre
          de decks.
        </p>
        <p>
          Les <strong className="font-medium text-text">staples génériques</strong> occupent le haut du classement : ce
          sont les cartes jouées par le plus d’archétypes. Le filtre « Pièces d’archétype » isole les cartes
          rattachées à un deck précis.
        </p>
      </Explainer>

      <KindFilterTabs tab="impact" active={view} count={`Top ${data.length}`} />

      <div className="border-b border-line">
        {data.map((entry, index) => (
          <ImpactRow key={entry.card_name} entry={entry} rank={index + 1} max={max} />
        ))}
      </div>
      <DataFooter
        source="decklists de tournoi TCG, yugiohmeta.com"
        date={`au ${fmtDate(as_of)}, 6 mois glissants`}
        sample={`${fmtNum(n_decks_window)} decks, ${fmtNum(data.length)} cartes affichées`}
        uncertainty="aucun intervalle : le score ordonne les cartes à partir de comptes exacts sur la fenêtre"
      />
    </>
  );
}
