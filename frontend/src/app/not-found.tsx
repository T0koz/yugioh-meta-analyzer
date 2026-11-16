import type { Metadata } from "next";
import Link from "next/link";
import { Em } from "@/components/ds/em";
import { Page, PageHero } from "@/components/ds/page";

export const metadata: Metadata = { title: "Page introuvable" };

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
          <Link
            href="/"
            className="rounded-[4px] border border-signal bg-signal px-[18px] py-[11px] text-[14px] font-medium text-on-signal transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-px"
          >
            Retour à l’accueil
          </Link>
          <Link
            href="/tier-list"
            className="rounded-[4px] border border-line-2 bg-ink-3 px-[18px] py-[11px] text-[14px] font-medium text-text transition-transform duration-[250ms] ease-[var(--ease)] motion-safe:hover:-translate-y-px"
          >
            Voir la tier list
          </Link>
        </div>
      </PageHero>
    </Page>
  );
}
