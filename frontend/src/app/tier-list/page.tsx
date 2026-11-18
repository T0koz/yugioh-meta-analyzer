import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtMonthRange, fmtMonthShort, fmtNum } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { MethodNote } from "@/components/ds/explain";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { DataFooter, Page, PageHero, StatBand } from "@/components/ds/page";
import { PageTransition } from "@/components/view-transitions";
import { TierList } from "./TierList";

export async function generateMetadata(): Promise<Metadata> {
  const { data, window_start, window_end, n_decks } = await api.tierList();
  const period = fmtMonthRange(window_start, window_end) ?? "fenêtre courante";
  return pageMetadata({
    title: "Tier list TCG",
    description: `${data.length} archétypes Yu-Gi-Oh! TCG classés par part de decks sur ${fmtNum(n_decks)} decklists de tournoi, ${period}. Source : ${DECK_SOURCE}.`,
    path: "/tier-list",
  });
}

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
      <PageTransition id="tier-list">
        <Page>
          <PageHero
            size="xl"
            eyebrow={`Tier list · TCG · ${period} · ${fmtNum(n_decks)} decks`}
            title={
              <>
                Les archétypes TCG classés par <Em>part</Em> des decks de tournoi.
              </>
            }
            intro={
              <>
                {`${fmtNum(data.length)} archétypes classés sur ${fmtNum(n_decks)} decklists de tournoi TCG, ${period} (${DECK_SOURCE}). Tier`}
                <InfoTooltip term="Tier" text="Niveau de l’archétype selon la part des decks de tournoi qui le jouent." />{" "}
                selon la part des decks, tendance par rapport à la fenêtre précédente.
              </>
            }
          >
            <StatBand
              stats={[
                { value: fmtNum(n_decks), label: "Decks de la fenêtre" },
                { value: fmtNum(data.length), label: "Archétypes classés" },
              ]}
            />
          </PageHero>

          <TierList data={data} nDecks={n_decks} />
          <DataFooter
            source="decklists de tournoi TCG, yugiohmeta.com"
            date={period}
            sample={`${fmtNum(n_decks)} decks, ${fmtNum(data.length)} archétypes`}
            uncertainty="barre : intervalle à 95 % de la part, point : part observée ; tendance affichée seulement si l’écart dépasse le bruit d’échantillonnage"
          />
          <MethodNote anchor="tier-list">
            <p>Tier : T0 à partir de 40 % des decks de la fenêtre, T1 à partir de 15 %, T2 à partir de 7 %, T3 à partir de 3 % ; Rogue en dessous ou sous 5 decks.</p>
            <p>Sur une soixantaine d’archétypes comparés, deux ou trois tendances peuvent être dues au hasard.</p>
          </MethodNote>
        </Page>
      </PageTransition>
    </HoverPreviewProvider>
  );
}
