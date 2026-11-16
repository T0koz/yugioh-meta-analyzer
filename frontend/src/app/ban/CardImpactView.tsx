import Link from "next/link";
import { api } from "@/lib/api";
import { fmtDate, fmtNum } from "@/lib/format";
import { CardChip } from "@/components/card-chip";
import { Em } from "@/components/ds/em";
import { Explainer, Meter, PageHero } from "@/components/ds/page";
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
        <h3 className="text-[20px] leading-tight font-medium tracking-[-0.02em] [overflow-wrap:anywhere]">
          <CardChip name={entry.card_name} subtitle={origin} variant="plain" />
        </h3>
        <p className="mt-1 font-mono text-[12px] text-muted-text">
          {[origin, `${fmtNum(entry.n_archetypes)} archétypes`, `${fmtNum(entry.decks)} decks`].join(" · ")}
        </p>
        <div className="mt-3">
          <Meter value={entry.bridge_score} max={max} />
        </div>
      </div>
      <Link
        href={`/ban?tab=simulateur&card=${encodeURIComponent(entry.card_name)}`}
        className="col-start-3 w-fit rounded-[4px] border border-line-2 px-3 py-1.5 font-mono text-[12px] text-soft transition-colors duration-200 hover:text-text min-[760px]:col-start-auto min-[760px]:justify-self-end"
      >
        Simuler le ban →
      </Link>
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
            Les cartes qui <Em>tiennent</Em> la méta.
          </>
        }
        aside={
          <>
            Données au {fmtDate(as_of)}
            <br />
            {fmtNum(n_decks_window)} decks · 6 mois
          </>
        }
        intro="Les cartes dont le retrait fragmenterait le plus la méta : combien d'archétypes et de decks une interdiction toucherait."
      >
        {tabs}
      </PageHero>

      <Explainer label="Comment lire ce score ?" title="Lecture du score">
        <p>
          Ce n’est pas un score de risque de ban (voir l’onglet{" "}
          <Link href="/ban?tab=radar" className="text-signal underline-offset-4 hover:underline">
            Ban Radar
          </Link>{" "}
          pour ça) mais une mesure d’<strong className="font-medium text-text">impact</strong> : si Konami retire
          cette carte demain, combien d’archétypes et de decks sont concernés.
        </p>
        <p>
          Score de pont = nombre d’archétypes qui jouent la carte × log(1 + nombre de decks). Une carte adoptée par
          beaucoup d’archétypes, en volume, est une pièce de connexion : la retirer touche plusieurs decks à la fois.
        </p>
        <p>
          Les <strong className="font-medium text-text">staples génériques</strong> trustent le haut du classement parce
          qu’elles sont jouées par le plus d’archétypes à la fois. Le filtre « Pièces d’archétype » isole
          les cartes rattachées à un deck précis.
        </p>
      </Explainer>

      <KindFilterTabs tab="impact" active={view} count={`Top ${data.length}`} />

      <div className="border-b border-line">
        {data.map((entry, index) => (
          <ImpactRow key={entry.card_name} entry={entry} rank={index + 1} max={max} />
        ))}
      </div>
    </>
  );
}
