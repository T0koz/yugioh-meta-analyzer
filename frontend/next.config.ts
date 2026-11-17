import type { NextConfig } from "next";

function cardImagesPatterns(): URL[] {
  const base = process.env.NEXT_PUBLIC_CARD_IMAGES_URL;
  if (!base || !/^https?:\/\//.test(base)) return [];
  return [new URL(`${base.replace(/\/+$/, "")}/**`)];
}

const nextConfig: NextConfig = {
  // Les tests visuels construisent le site contre des données figées dans un dossier à part
  // (scripts/visual_tests.py), pour ne pas écraser le build courant.
  distDir: process.env.NEXT_DIST_DIR || ".next",
  experimental: {
    // Transitions de vue entre la tier list et la page d'archétype (TOK-101).
    // Embellissement : sans prise en charge du navigateur, la navigation est inchangée.
    viewTransition: true,
  },
  images: {
    // Les images de cartes viennent de notre hébergement (TOK-92, lib/card-images.ts) : en local, la
    // route /card-images ; au déploiement, l'adresse NEXT_PUBLIC_CARD_IMAGES_URL, autorisée ici si elle
    // est absolue. Plus aucun accès à images.ygoprodeck.com.
    remotePatterns: cardImagesPatterns(),
    // Une illustration de carte ne change pas : cache d'un mois plutôt que 4 h.
    minimumCacheTTL: 2_678_400,
  },
  async redirects() {
    return [
      // Le simulateur vit dans le Ban Center depuis la refonte Ember. La query
      // (?card=…) est transmise telle quelle par Next.
      { source: "/ban-simulator", destination: "/ban?tab=simulateur", permanent: true },
    ];
  },
};

export default nextConfig;
