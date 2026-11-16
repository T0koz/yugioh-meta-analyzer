import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      // Le simulateur vit dans le Ban Center depuis la refonte Ember. La query
      // (?card=…) est transmise telle quelle par Next.
      { source: "/ban-simulator", destination: "/ban?tab=simulateur", permanent: true },
    ];
  },
};

export default nextConfig;
