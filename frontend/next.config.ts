import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Transitions de vue entre la tier list et la page d'archétype (TOK-101).
    // Embellissement : sans prise en charge du navigateur, la navigation est inchangée.
    viewTransition: true,
  },
  images: {
    // Les images de cartes viennent encore de YGOPRODeck : next/image les
    // redimensionne et les met en cache côté serveur, le navigateur ne charge
    // plus un fichier de 268 px pour une vignette de 34 px. Hébergement propre : TOK-92.
    remotePatterns: [new URL("https://images.ygoprodeck.com/images/**")],
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
