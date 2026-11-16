import type { Metadata } from "next";
import { SITE_NAME } from "@/lib/site";

interface PageSeo {
  /** Titre court : le gabarit du layout ajoute « · YGO Meta ». */
  title: string;
  /** Titre complet, sans gabarit (accueil). */
  absoluteTitle?: string;
  description: string;
  /** Chemin canonique, résolu sur `metadataBase` : « /tier-list », « /ban?tab=impact ». */
  path: string;
}

/**
 * Métadonnées d'une page : titre, description, lien canonique, Open Graph et
 * carte Twitter. Next ne fusionne pas `openGraph` champ par champ entre le
 * layout et la page : chaque page doit donc le fournir en entier, d'où cette fonction.
 * L'image vient du fichier `opengraph-image.tsx` le plus proche de la route.
 */
export function pageMetadata({ title, absoluteTitle, description, path }: PageSeo): Metadata {
  const shareTitle = absoluteTitle ?? title;
  return {
    title: absoluteTitle ? { absolute: absoluteTitle } : title,
    description,
    alternates: { canonical: path },
    openGraph: {
      type: "website",
      locale: "fr_FR",
      siteName: SITE_NAME,
      title: shareTitle,
      description,
      url: path,
    },
    twitter: { card: "summary_large_image", title: shareTitle, description },
  };
}
