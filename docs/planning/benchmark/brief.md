# Benchmark fonctionnel des sites de méta de jeux de cartes

Modèle : Sonnet (recherche et vérification, pas de code produit). Réponds en français.
À lancer **après** la fin du sprint 1 (une seule session à la fois). Aucune session ni sous-agent : fais les
recherches toi-même. Ne touche à aucun fichier du projet hors de `docs/benchmark/`. Pas de commit, pas de push.

## But
Situer Yugioh Meta Analyzer face aux sites d'analyse de méta des jeux de cartes les plus joués au monde.

## Périmètre : 20 à 25 sites, 2 à 5 par jeu, choisis par usage réel
- Yu-Gi-Oh : yugiohmeta.com, masterduelmeta.com, ygoprodeck.com (+ 1 ou 2 autres)
- Pokémon (TCG et Pocket) : Limitless TCG et autres références
- Magic : MTGGoldfish, MTGTop8, Aetherhub, 17lands, Moxfield
- One Piece, Lorcana, Hearthstone, Marvel Snap : 2 sites de référence chacun
Une ligne par site pour dire pourquoi il est retenu.

## Méthode
1. Construis la liste des fonctionnalités (25 à 40) à partir de 5 ou 6 sites représentatifs, regroupées par thème :
   méta et tier list, decks et composition, cartes, prix et marché, prédictions et signaux, bans, outils joueur,
   communauté, compte et monétisation. Écris-la dans `docs/benchmark/fonctionnalites.md`.
   **Thomas n'est pas là** : ne l'attends pas, continue avec ta liste et signale en tête du rapport ce qu'il
   pourrait vouloir ajouter ou retirer.
2. Vérifie chaque site en ouvrant ses pages (WebSearch / WebFetch). Une case sans preuve vue = « non vérifié »,
   jamais « oui » par déduction. Pages payantes ou derrière connexion : le noter, ne pas deviner.
3. Colonne « Yugioh Meta Analyzer » : remplis-la depuis le dépôt (`context.md`, pages de `frontend/src/app/`) :
   tier list calculée, Ban Radar avec backtest, simulateur de ban, signal OCG → TCG, signal boutique avec prix,
   évolution du méta, prédictions journalisées, et ce que le sprint 1 a ajouté.

## Livrables dans `docs/benchmark/`
- `benchmark.xlsx` (skill xlsx) :
  - onglet « Fonctionnalités » : une ligne par fonctionnalité, une colonne par site (« oui », « non », « partiel »,
    « non vérifié »), colonne commentaire, colonnes **Total oui** et **Total partiel** calculées par FORMULE
    (NB.SI / COUNTIF), colonne « Yugioh Meta Analyzer » ;
  - onglet « Sites » : nom, jeu, URL, modèle économique, date de vérification ;
  - onglet « Sources » : les pages réellement ouvertes.
- `benchmark.csv` : l'onglet principal, lisible dans git.
- `synthese.md` : les fonctionnalités que presque tous ont (minimum attendu), celles que peu ont, celles où le
  projet est seul, et la liste des cases « non vérifié » à revoir. Sources en fin de fichier.

## Arrêt
Si une limite d'usage approche, enregistre ce qui est fait (cases restantes en « non vérifié ») et arrête-toi.
