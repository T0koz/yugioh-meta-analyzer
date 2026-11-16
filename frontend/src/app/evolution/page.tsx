import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtMonthShort } from "@/lib/format";
import { Em } from "@/components/ds/em";
import { Page, PageHero } from "@/components/ds/page";
import { EvolutionChart } from "./EvolutionChart";

export const metadata: Metadata = {
  title: "Évolution de la méta",
  description: "Score méta mensuel de chaque archétype Yu-Gi-Oh! : qui monte, qui s’efface, mois après mois.",
};

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
        intro={`Score méta mensuel ×100 des ${archetypes.length} premiers archétypes TCG${lastMonth ? ` de ${fmtMonthShort(lastMonth)}` : ""}, quatre séries au plus.`}
      />
      <EvolutionChart data={data} images={images} decks_by_month={decks_by_month} />
    </Page>
  );
}
