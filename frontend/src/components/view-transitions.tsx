import { ViewTransition } from "react";

// Transitions de vue (TOK-101, décision 10 de l'audit) : un embellissement.
// Sans prise en charge du navigateur, la navigation est celle de toujours ;
// en mouvement réduit, le changement de page est instantané (globals.css).
// Tout est en `default="none"` : rien ne s'anime hors des deux cas voulus,
// le morphing d'un élément partagé et le glissement entre liste et détail.

/** Types posés par les liens (`transitionTypes`) : sens de la navigation. */
export const NAV_FORWARD = ["nav-forward"];
export const NAV_BACK = ["nav-back"];

const DIRECTIONAL = { "nav-forward": "slide-forward", "nav-back": "slide-back", default: "none" };

/**
 * Contenu de page qui glisse selon le sens du lien suivi (jamais au chargement).
 * À placer AUTOUR du conteneur de page (`<Page>`), pas dedans : React ne joue
 * l'entrée et la sortie que si le ViewTransition est lui-même inséré ou retiré,
 * pas s'il arrive à l'intérieur d'un nœud DOM qui vient d'être monté.
 * `id` sert de clé : deux pages de même structure seraient sinon vues comme un
 * seul élément mis à jour, sans sortie ni entrée.
 */
export function PageTransition({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <ViewTransition key={id} enter={DIRECTIONAL} exit={DIRECTIONAL} default="none">
      {children}
    </ViewTransition>
  );
}

/** Élément présent sur deux pages sous le même nom : le navigateur l'anime de l'une à l'autre. */
export function SharedElement({ name, children }: { name: string; children: React.ReactNode }) {
  return (
    <ViewTransition name={name} share="shared-morph" default="none">
      {children}
    </ViewTransition>
  );
}

// Le slug ne contient que a-z, 0-9 et le tiret : c'est un identifiant CSS valide.
export const archetypeArtName = (slug: string) => `archetype-art-${slug}`;
export const archetypeTitleName = (slug: string) => `archetype-title-${slug}`;
