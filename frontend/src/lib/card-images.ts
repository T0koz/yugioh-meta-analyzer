// Un seul endroit sait d'où viennent les images de cartes : le jour où elles
// seront hébergées par nous (TOK-92), seul ce fichier change.

/**
 * Illustration seule (sans le cadre de la carte), carrée, à partir de l'URL de
 * la vignette : YGOPRODeck range les trois variantes dans des dossiers voisins.
 */
export function artCropUrl(imageUrl: string): string {
  return imageUrl.replace(/\/images\/cards(_small)?\//, "/images/cards_cropped/");
}
