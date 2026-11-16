import { api } from "@/lib/api";
import { fmtDate, fmtNum } from "@/lib/format";
import { SITE_FACTS } from "@/lib/site-facts";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { Page, PageHero, StatBand } from "@/components/ds/page";
import { TierList } from "./TierList";

export default async function TierListPage() {
  const { data, generated_at } = await api.tierList();

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          size="xl"
          eyebrow={`Tier list · TCG · mise à jour ${fmtDate(generated_at)}`}
          title={
            <>
              Ce que joue la méta, <Em>maintenant</Em>.
            </>
          }
          intro={
            <>
              Score = part de méta × performance en tournoi, calculé sur chaque decklist publiée.
              <InfoTooltip text="sqrt(part de méta × score de placement normalisé) : moyenne géométrique entre volume de decks et performance en tournoi. La barre est relative au meilleur score du moment." />
            </>
          }
        >
          <StatBand
            stats={[
              { value: fmtNum(SITE_FACTS.decklists), label: "Decklists analysées" },
              { value: fmtNum(SITE_FACTS.cardsTracked), label: "Cartes suivies" },
              { value: fmtNum(SITE_FACTS.ocgTcgCorrelation, 2), label: "Corrélation OCG → TCG (4 mois)" },
              { value: SITE_FACTS.ocgTcgLagRange, label: "Fenêtre du signal sur le TCG" },
            ]}
          />
        </PageHero>

        <TierList data={data} />
      </Page>
    </HoverPreviewProvider>
  );
}
