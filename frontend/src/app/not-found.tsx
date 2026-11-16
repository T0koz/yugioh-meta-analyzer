import type { Metadata } from "next";
import { ButtonLink } from "@/components/ds/control";
import { Em } from "@/components/ds/em";
import { Page, PageHero } from "@/components/ds/page";

export const metadata: Metadata = { title: "Page introuvable", robots: { index: false, follow: false } };

export default function NotFound() {
  return (
    <Page>
      <PageHero
        eyebrow="Erreur 404"
        title={
          <>
            Cette page n’est pas dans le <Em>deck</Em>.
          </>
        }
        intro="L’adresse est fausse ou la page a été déplacée. Les outils sont toujours là."
      >
        <div className="mt-7 flex flex-wrap gap-2.5">
          <ButtonLink href="/" variant="primary">
            Retour à l’accueil
          </ButtonLink>
          <ButtonLink href="/tier-list">Voir la tier list</ButtonLink>
        </div>
      </PageHero>
    </Page>
  );
}
