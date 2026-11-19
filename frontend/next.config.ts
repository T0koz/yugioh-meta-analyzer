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
      // « Cartes à impact » s'appelle « Diffusion » depuis le jalon n°8 (TOK-132). Redirection serveur (308) : dans
      // la page, app/ban/loading.tsx la ferait passer en streaming (200 + meta refresh). Les valeurs de requête de
      // la destination l'emportent sur celles d'origine (tab), les autres (kind) sont transmises.
      {
        source: "/ban",
        has: [{ type: "query", key: "tab", value: "impact" }],
        destination: "/ban?tab=diffusion",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
