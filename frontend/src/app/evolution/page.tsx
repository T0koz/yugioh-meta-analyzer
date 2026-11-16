import type { Metadata } from "next";
import { api } from "@/lib/api";
import { Em } from "@/components/ds/em";
import { Page, PageHero } from "@/components/ds/page";
import { EvolutionChart } from "./EvolutionChart";

export const metadata: Metadata = {
  title: "Évolution de la méta",
  description: "Score méta mensuel de chaque archétype Yu-Gi-Oh! : qui monte, qui s’efface, mois après mois.",
};

export default async function EvolutionPage() {
  const { data, images } = await api.evolution();

  return (
    <Page>
      <PageHero
        eyebrow="Méta · Évolution"
        title={
          <>
            Qui monte, qui <Em>s’efface</Em>.
          </>
        }
        intro="Score méta mensuel par archétype (×100). Compare jusqu'à quatre archétypes : le premier choisi passe en accent."
      />
      <EvolutionChart data={data} images={images} />
    </Page>
  );
}
