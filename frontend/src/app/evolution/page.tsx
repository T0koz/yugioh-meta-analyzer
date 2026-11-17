import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtMonthRange, fmtMonthShort } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { Em } from "@/components/ds/em";
import { Page, PageHero } from "@/components/ds/page";
import { EvolutionChart } from "./EvolutionChart";

export async function generateMetadata(): Promise<Metadata> {
  const { data } = await api.evolution();
  const months = Object.values(data)
    .flatMap((points) => points.map((p) => p.month))
    .sort();
  const period = months.length ? `, ${fmtMonthRange(months[0], months[months.length - 1])}` : "";
  return pageMetadata({
    title: "Évolution de la méta",
    description: `Part mensuelle des decks de tournoi des ${Object.keys(data).length} premiers archétypes Yu-Gi-Oh! TCG${period}, avec intervalle à 95 %. Source : decklists de tournoi, ${DECK_SOURCE}.`,
    path: "/evolution",
  });
}

export default async function EvolutionPage() {
  const { data, images, decks_by_month } = await api.evolution();
  const archetypes = Object.keys(data);
  const lastMonth = archetypes.flatMap((a) => data[a].map((p) => p.month)).sort().at(-1);

  return (
    <Page>
      <PageHero
        eyebrow="Méta · Évolution"
        title={
          <>
            Qui monte, qui <Em>s’efface</Em>.
          </>
        }
        intro={`Part mensuelle des decks de tournoi TCG des ${archetypes.length} premiers archétypes${lastMonth ? ` de ${fmtMonthShort(lastMonth)}` : ""}, quatre séries au plus.`}
      />
      <EvolutionChart data={data} images={images} decks_by_month={decks_by_month} />
    </Page>
  );
}
