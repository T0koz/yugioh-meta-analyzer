// Adresse publique du site. Le domaine définitif n'est pas choisi (TOK-35) :
// elle vient de NEXT_PUBLIC_SITE_URL (voir frontend/.env.example), sinon du
// domaine de production que Vercel fournit au build, sinon de l'adresse locale.
// Tout ce qui écrit une URL absolue (canonique, Open Graph, sitemap, robots) lit SITE_URL.
const LOCAL_URL = "http://localhost:3000";

function resolveSiteUrl(): string {
  const explicit = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  if (explicit) return explicit.replace(/\/+$/, "");
  const vercel = process.env.VERCEL_PROJECT_PRODUCTION_URL?.trim();
  if (vercel) return `https://${vercel}`;
  return LOCAL_URL;
}

export const SITE_URL = resolveSiteUrl();
export const SITE_NAME = "YGO Meta";
/** Source des decklists, citée dans les descriptions et les images de partage. */
export const DECK_SOURCE = "yugiohmeta.com";

/**
 * Indexation ouverte seulement sur le déploiement de production. Un aperçu
 * Vercel (VERCEL_ENV=preview) ne doit pas concurrencer le site dans un moteur.
 */
export const INDEXABLE = process.env.VERCEL_ENV !== "preview";

/** « /tier-list » → adresse absolue. */
export function absoluteUrl(path: string): string {
  return path === "/" ? SITE_URL : `${SITE_URL}${path}`;
}
