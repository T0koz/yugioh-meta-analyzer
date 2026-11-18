import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtNum } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { DataFooter, Page, PageHero } from "@/components/ds/page";
import { MethodNote } from "@/components/ds/explain";
import { GraphView } from "./GraphView";

const MIN_JACCARD = 0.15;
/** Seuil du lien, en mots : part des decks qui jouent l’une ou l’autre carte et les jouent ensemble. */
const LINK_RULE = `jouées ensemble dans au moins ${Math.round(MIN_JACCARD * 100)} % des decks de tournoi qui jouent l’une ou l’autre`;

export const metadata: Metadata = pageMetadata({
  title: "Graphe de synergies",
  description: `Graphe de co-occurrence des cartes Yu-Gi-Oh! : un lien relie deux cartes ${LINK_RULE}. Source : ${DECK_SOURCE}, date de calcul non enregistrée.`,
  path: "/graph",
});

export default async function GraphPage() {
  const data = await api.graphSynergies({ limit: 200, minJaccard: MIN_JACCARD });

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          eyebrow="Graphe · Co-occurrences"
          title={
            <>
              Les cartes qui se jouent <Em>ensemble</Em>.
            </>
          }
          intro={`Les ${data.nodes.length} cartes les plus connectées. Un lien relie deux cartes ${LINK_RULE}.`}
        />
        <GraphView data={data} />
        <DataFooter
          source="co-occurrences de cartes dans les decklists de tournoi, yugiohmeta.com"
          date="date de calcul non enregistrée dans la base servie"
          sample={`${fmtNum(data.nodes.length)} cartes, ${fmtNum(data.edges.length)} liens`}
          uncertainty="pas d’intervalle : le graphe dessine des liens au-dessus d’un seuil, un lien proche du seuil peut apparaître ou disparaître d’un calcul à l’autre"
        />
        <MethodNote anchor="graphe">
          <p>Deux cartes sont reliées quand, parmi les decks qui jouent l’une ou l’autre, au moins {fmtNum(MIN_JACCARD * 100, 0)} % jouent les deux.</p>
          <p>Seules les 200 cartes les plus connectées sont affichées.</p>
        </MethodNote>
      </Page>
    </HoverPreviewProvider>
  );
}
