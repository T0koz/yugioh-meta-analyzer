import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtMonthShort, fmtNum } from "@/lib/format";
import { SITE_FACTS } from "@/lib/site-facts";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { Page, PageHero, StatBand } from "@/components/ds/page";
import { TierList } from "./TierList";

export const metadata: Metadata = {
  title: "Tier list TCG",
  description: "Les archétypes Yu-Gi-Oh! qui dominent les tournois TCG, classés par part de méta et par performance.",
};

export default async function TierListPage() {
  const { data, window_start, window_end, n_decks } = await api.tierList();
  // La fenêtre cumule les mois récents jusqu'à 300 decks : un ou plusieurs mois.
  const period =
    window_start === window_end
      ? fmtMonthShort(window_end)
      : `${fmtMonthShort(window_start)} à ${fmtMonthShort(window_end)}`;

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          size="xl"
          eyebrow={`Tier list · TCG · ${period} · ${fmtNum(n_decks)} decks`}
          title={
            <>
              Ce que joue la méta, <Em>maintenant</Em>.
            </>
          }
          intro={
            <>
              Classement calculé sur nos decklists de tournoi TCG. Tier selon la part de méta, tendance par rapport
              à la période précédente.
              <InfoTooltip text="Tiers : T0 à partir de 40 % des decks, T1 15 %, T2 7 %, T3 3 %, Rogue en dessous ou sous 5 decks. Tendance : en hausse ou en baisse seulement si la part a bougé au-delà du bruit d’échantillonnage (test de deux proportions à 5 %) ; sur une soixantaine d’archétypes, deux ou trois signaux peuvent être dus au hasard. Score = racine de (part × placement moyen normalisé) ; la barre est relative au meilleur score." />
            </>
          }
        >
          <StatBand
            stats={[
              { value: fmtNum(SITE_FACTS.decklists), label: "Decklists analysées" },
              { value: fmtNum(SITE_FACTS.cardsTracked), label: "Cartes suivies" },
              { value: fmtNum(SITE_FACTS.ocgTcgCorrelation, 2), label: "Corrélation OCG → TCG" },
              { value: SITE_FACTS.ocgTcgLagRange, label: "Fenêtre du signal sur le TCG" },
            ]}
          />
        </PageHero>

        <TierList data={data} />
      </Page>
    </HoverPreviewProvider>
  );
}
