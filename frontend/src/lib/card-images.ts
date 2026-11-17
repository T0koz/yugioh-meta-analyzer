// Un seul endroit sait d'où viennent les images de cartes (TOK-92). L'API sert encore l'adresse
// d'origine (images.ygoprodeck.com/…/{id}.jpg) : on n'en garde que l'identifiant de carte, et chaque
// image est demandée à NOTRE hébergement, jamais à YGOPRODeck (hotlink interdit).
//
// Trois tailles pré-générées par `scripts/download_card_images.py` :
//   art      illustration seule, carrée, 256 px (pastilles, lignes de liste)
//   card-sm  carte entière, 168 px de large (vignettes)
//   card-lg  carte entière, 421 px de large (au-delà de 134 px d'affichage)
//
// Adresse de base : NEXT_PUBLIC_CARD_IMAGES_URL (voir .env.example). Sans valeur, `/card-images`,
// servi en local par app/card-images/[...path]/route.ts depuis le dossier de téléchargement.

const BASE = (process.env.NEXT_PUBLIC_CARD_IMAGES_URL || "/card-images").replace(/\/+$/, "");

/** Identifiant de carte tiré de l'adresse servie par l'API (`…/{id}.jpg`) ; null si elle n'en porte pas. */
function cardId(imageUrl: string): string | null {
  return imageUrl.match(/\/(\d+)\.jpg(?:\?|$)/)?.[1] ?? null;
}

function url(folder: "art" | "card-sm" | "card-lg", imageUrl: string): string {
  const id = cardId(imageUrl);
  // Adresse inattendue : on ne la transmet jamais telle quelle (elle pourrait pointer chez YGOPRODeck).
  return id ? `${BASE}/${folder}/${id}.webp` : `${BASE}/missing.webp`;
}

/** Illustration seule (sans le cadre de la carte), carrée. */
export function artCropUrl(imageUrl: string): string {
  return url("art", imageUrl);
}

/** Carte entière, petite taille : vignettes. */
export function smallCardUrl(imageUrl: string): string {
  return url("card-sm", imageUrl);
}

/** Carte entière en grande taille (421 px de large) : pour les cartes affichées au-delà de 134 px. */
export function fullCardUrl(imageUrl: string): string {
  return url("card-lg", imageUrl);
}
