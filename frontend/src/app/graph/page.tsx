import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtNum } from "@/lib/format";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { DataFooter, Page, PageHero } from "@/components/ds/page";
import { GraphView } from "./GraphView";

export const metadata: Metadata = {
  title: "Graphe de synergies",
  description: "Les cartes Yu-Gi-Oh! qui se jouent ensemble : le graphe des co-occurrences dans les decks de tournoi.",
};

const MIN_JACCARD = 0.15;

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
