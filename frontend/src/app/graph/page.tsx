import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtNum } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { DataFooter, Page, PageHero } from "@/components/ds/page";
import { GraphView } from "./GraphView";

const MIN_JACCARD = 0.15;

export const metadata: Metadata = pageMetadata({
  title: "Graphe de synergies",
  description: `Graphe de co-occurrence des cartes Yu-Gi-Oh! : un lien relie deux cartes jouées dans les mêmes decks de tournoi, indice de Jaccard ≥ ${fmtNum(MIN_JACCARD, 2)}. Source : ${DECK_SOURCE}, date de calcul non enregistrée.`,
  path: "/graph",
});

export default async function GraphPage() {
  const data = await api.graphSynergies({ limit: 200, minJaccard: MIN_JACCARD });

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          eyebrow="Graphe · Co-occurrence Jaccard"
          title={
            <>
              Les cartes qui se jouent <Em>ensemble</Em>.
            </>
          }
          intro={`Les ${data.nodes.length} cartes les plus connectées. Un lien relie deux cartes souvent jouées dans les mêmes decks (Jaccard ≥ ${fmtNum(MIN_JACCARD, 2)}).`}
        />
        <GraphView data={data} />
        <DataFooter
          source="co-occurrences de cartes dans les decklists de tournoi, yugiohmeta.com"
          date="date de calcul non enregistrée dans la base servie"
          sample={`${fmtNum(data.nodes.length)} cartes, ${fmtNum(data.edges.length)} liens`}
        />
      </Page>
    </HoverPreviewProvider>
  );
}
