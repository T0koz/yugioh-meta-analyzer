# 12 — Charte « ton et explication » + système d'explication graphique

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front. À faire après la refonte (lots 2 à 9).

**But** : un site sobre, tourné statistique, où la complexité est portée par le design plutôt que par des phrases.
Garder une explication, mais pas sous forme de paragraphes ni d'infobulles de formules.

**1. Charte** `docs/charte-ton-et-explication.md` (une à deux pages) : ton (constat chiffré, jamais de promesse),
ordre de préférence pour expliquer — encodage visuel, annotation sur le graphique, incertitude dessinée
(intervalle, bande, effectif n, données faibles atténuées), légende sobre, couche « méthode » repliée —, et
10 exemples avant / après tirés du site. Références de registre : Our World in Data, graphiques du FT et de
Bloomberg, The Pudding. **S'arrêter et faire valider la charte par Thomas** (formulaire dans `etat.md`) avant l'étape 2.

**2. Composants communs** : annotation, bande ou barre d'incertitude, badge d'effectif, couche méthode repliable,
légende. Page `/methode` qui reprend les formules sorties des infobulles. Appliqués à toutes les visualisations.

**Critères** : plus aucune formule dans une infobulle ; chaque graphique montre son incertitude ou dit pourquoi il
n'en a pas ; source + date partout ; Accessibilité ≥ 95 ; captures avant/après ; `check.py` vert.

## Pistes visuelles de Thomas (16/11, à étudier, rien d'imposé)
- **Composition en couches**, inspirée de solidroad.com : une illustration au premier plan qui déborde **devant**
  un panneau de données (comme leur montagne devant le tableau de bord). Chez nous : une fiche de deck avec ses
  vraies stats (HTML, chiffres vivants, accessibles, jamais une image de chiffres) et, devant, une illustration ou
  une mise en situation. Leur tracé de « route » peut devenir le chemin OCG → TCG.
  Illustration : originale, ou recadrage d'illustration de carte comme les bandeaux déjà présents sur la tier list ;
  jamais une scène ou un personnage de l'anime.
- **Hero animé local** : emplacement `frontend/public/local-hero/` ignoré par git (`hero.webm`, `hero.mp4`,
  `hero.jpg`), boucle lente sous un voile ; image fixe si mouvement réduit ; repli original (courbes OCG / TCG)
  si le fichier est absent. Le contenu de la vidéo est fourni par Thomas et ne va jamais dans git ni en ligne.
- **clears.ai** : Thomas aime l'élément central ; idée pour représenter un combo plus tard (capture à demander).
- **Boutons et contrôles « smooth »** (Thomas, 16/11) : formes arrondies, ombres douces en plusieurs couches,
  légère variation de couleur, animation au survol et à l'appui. Traduction : rayon généreux ; ombre de contact +
  ombre diffuse ; reflet interne subtil en haut ; survol = légère élévation et teinte qui s'éclaircit ; appui =
  enfoncement (échelle ~0,97, ombre réduite) avec un ressort court ; focus visible net ; transitions 120-200 ms ;
  aucune animation avec « réduire les animations ». Un seul composant de bouton (et pills, onglets, filtres)
  décliné partout, documenté dans `docs/design-system.md`. Contraste AA conservé.
- **Cas prioritaire : page historique du Ban Center** (`/ban?tab=historique`, Thomas 17/11) : trop d'informations,
  illisible sans la légende. Garder une phrase de verdict en tête et **un seul visuel par format** (par ex. cartes
  touchées dans le top 25 : radar contre « cartes les plus jouées ») ; replier le détail par banlist (bandes de
  hasard, rangs médians, étiquettes de calage) derrière « voir le détail ». Colonnes en langage simple. Le message
  du verdict attend le diagnostic du ticket « Ban Radar TCG ne bat pas les staples » (Linear) : ne pas l'écrire avant.
