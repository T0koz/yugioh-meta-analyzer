# TOK-99 — Dataviz maison (D3) et palette de données (2026-11-17, branche `claude/tok-99-dataviz-923148`)

Lot 03 de la nuit du 17/11. recharts est supprimé ; `/evolution` et `/predictions` sont des SVG calculés avec D3 et
rendus côté serveur ; une palette catégorielle de six teintes est documentée et contrôlée par script ; chaque graphique
et tableau porte un pied de données (source, date, échantillon).

## Mesures (build de production, API locale sur `serving.db`, Chromium de Playwright)

| Critère | Avant | Après |
|---|---|---|
| recharts dans `package.json`, `package-lock.json`, `.next/` | présent | 0 / 0 / 0 fichier (la seule mention restante, `required-server-files.json`, est la liste `optimizePackageImports` par défaut de Next) |
| JavaScript transféré, `/evolution` | 274,1 ko | **190,6 ko** (budget 200) |
| JavaScript transféré, `/predictions` | 180,7 ko | 180,7 ko (graphique rendu côté serveur, aucun script ajouté) |
| Contraste de la palette (`npm run contrast`) | pas de palette | 12 tokens × 4 surfaces ≥ 4,5:1 ; minimum des `--cat-*` : 5,14:1 (`--cat-5` sur `--ink-4`) |
| Lighthouse mobile, `LH_THROTTLING=devtools`, `/evolution` | — | Perf. 99, Access. 100, Bonnes pratiques 100, LCP 1,76 s, CLS 0 |
| Idem, `/predictions` | — | Perf. 98, Access. 100, Bonnes pratiques 100, LCP 1,71 s, CLS 0 |
| Sans JavaScript | graphique vide (recharts) | `/evolution` : 3 courbes, 29 points, tableau de 16 mois ; `/predictions` : 19 haltères, tableau de 19 lignes |
| Clavier | aucun | cadre focalisable (contour 2 px), flèches, Début, Fin, Échap, lecture annoncée (`aria-live`) |
| Pied source + date | 2 vues sur 9 (aside du Ban Center) | 7 sur 9 avec date ; graphe de synergies et simulateur : source, et « date de calcul non enregistrée » |

Les autres pages gardent leur poids (accueil 181,3 ko, `/boutique` 181,3, `/ban` 192,7, `/tier-list` 174,9,
`/early-signals` 172,0, `/graph` 313,5 : vis-network, hors ticket). Aucune erreur de console, aucun défilement horizontal
à 375, 768 et 1440 px. Captures (locales, non suivies) : `docs/audit-front/captures/tok-99/` (`avant-*`, `apres-*`).

## Ce qui a changé

- **`/evolution`** (`EvolutionChart.tsx`) : courbes, axes ajustés de TOK-96 conservés (zéro → maximum affiché, temps à
  partir du premier mois mesuré), étiquette directe en bout de courbe, un point par mois mesuré, bande « decks par mois »
  sous l'axe du temps, infobulle (score ×100, part des decks, decks du mois), tableau des valeurs repliable.
- **`/predictions`** (`PredictionsChart.tsx`, composant serveur) : haltères observé → prévu sur une échelle commune,
  colonne d'écart centrée sur zéro avec sa propre échelle, tableau repliable. Les mois (observé, cible) viennent de l'API.
- **Palette** : `--cat-1` à `--cat-6` dans `globals.css`, appliquée aux séries de `/evolution` et à la barre des six
  critères du Ban Radar (page `/ban` et tuile de l'accueil), à la place des six opacités d'une même teinte.
- **`DataFooter`** sur tier list, évolution, prédictions, boutique, signaux précoces, radar, cartes à impact, simulateur, graphe.
- **API (champs ajoutés, rien de retiré)** : `decks_by_month` (`/meta/evolution`), `data_month` et `computed_at`
  (`/meta/predictions`), `computed_at` (`/boutique/signals`, `/boutique/early-signals`). Colonnes déjà présentes dans
  `serving.db` : aucune reconstruction nécessaire.
- **`npm run contrast`** (`frontend/scripts/contrast.mjs`).

## Pièges

- **`d3-scale` côté client coûte ≈ 12 ko transférés** (il entraîne `d3-interpolate`, `d3-format`, `d3-color`) : `/evolution`
  montait à 202,2 ko. Dans un composant client, écrire l'échelle linéaire à la main avec `nice` et `ticks` de `d3-array` ;
  `d3-scale` reste utilisable dans un composant serveur (`PredictionsChart`), où il ne pèse rien.
- **Texte de graphique à 11 px** : Lighthouse (« font-size ») fait tomber les bonnes pratiques à 96 quand plus de 40 % du
  texte de la page est sous 12 px. Axes et pieds de données sont à 12 px.
- **SVG en pourcentage** : pour un graphique en lignes (une ligne HTML par archétype), des `cx="42%"` sans `viewBox`
  gardent le texte à sa taille réelle à 375 px ; un `viewBox` fixe le réduirait à 5 px.
- **Graphique client et largeur** : le serveur rend le SVG avec un `viewBox` de 1100 × 400 ; un `ResizeObserver` le recale
  sur la largeur réelle. Le cadre a une hauteur fixe en CSS (320 / 400 px), sinon le recalage décale la page (CLS).
- **Une courbe relie les mois mesurés** : `meta_scores` n'a pas de ligne quand un archétype n'a aucun deck un mois donné.
  Le point par mois mesuré et la mention du pied rendent ces trous visibles ; ils ne valent pas zéro dans le tracé.
- **`/meta/evolution` choisit toujours ses 15 archétypes sur le dernier mois**, parfois incomplet (156 decks en nov. 26) :
  défaut connu, non traité ici ; la bande d'échantillon le rend visible.
- **Aucun intervalle d'incertitude par archétype** n'existe dans `meta_predictions` : le pied le dit, rien n'est dessiné.
- **Dates absentes de la base servie** pour `card_cooccurrence` / `card_graph_metrics` (graphe, simulateur).

## Textes ajoutés ou modifiés

- `/evolution`, introduction : « Score méta mensuel ×100 des 15 premiers archétypes TCG de nov. 26, quatre séries au plus. »
  (remplace « Score méta mensuel par archétype (×100). Compare jusqu'à quatre archétypes : le premier choisi passe en accent. »)
- `/evolution`, graphique : « score méta ×100 », « 156 decks en nov. 26 », infobulle « score ×100 · part des decks »,
  bouton « Tableau des valeurs », en-têtes « Mois », « Decks ».
- `/predictions`, introduction : « Score méta ×100 de 19 archétypes TCG : observé en oct. 26, prévu pour nov. 26. Modèle :
  70 % de prévision naïve et 30 % de régression Ridge. Il prolonge la tendance et ramène vers la moyenne : il n'anticipe ni
  les ruptures ni l'arrivée d'un nouvel archétype. » (première phrase datée ; « surtout » retiré ; info-bulle inchangée)
- `/predictions`, graphique : « observé oct. 26 », « prévu nov. 26 », « Score méta ×100 », « Écart (points) », « − 0 + »,
  « Tableau des valeurs », en-têtes « Observé oct. 26 », « Prévu nov. 26 », « Écart ».
- Pieds de données (valeurs du 16/11) :
  - tier list : « Source : decklists de tournoi TCG, yugiohmeta.com · {période} · {n} decks, {n} archétypes »
  - évolution : « Source : decklists de tournoi TCG, yugiohmeta.com · août 25 à nov. 26 · 4 596 decks · barres grises :
    decks comptés chaque mois ; point : mois mesuré, un mois sans deck de l'archétype n'a pas de point »
  - prédictions : « Source : decklists de tournoi TCG, yugiohmeta.com · observé oct. 26, calcul du 16 novembre 2026 ·
    19 archétypes · modèle 70 % naïf + 30 % Ridge · anneau : observé ; point plein : prévu ; aucun intervalle d'incertitude
    n'est calculé par archétype »
  - boutique : « Source : decklists OCG (yugiohmeta.com), vues et prix Cardmarket (YGOPRODeck) · calcul du 16 novembre 2026 ·
    12 cartes, {n} archétypes »
  - signaux précoces : « Source : vues par semaine (YGOPRODeck), co-occurrences dans les decklists de tournoi
    (yugiohmeta.com) · calcul du 16 novembre 2026 · {n} cartes »
  - radar : « Source : decklists de tournoi TCG (yugiohmeta.com), banlists (Yugipedia) · au 14 novembre 2026, 6 mois
    glissants · 1 883 decks, 50 cartes affichées »
  - cartes à impact : « Source : decklists de tournoi TCG, yugiohmeta.com · au {date}, 6 mois glissants · {n} decks,
    {n} cartes affichées »
  - simulateur : « Source : graphe de co-occurrences des decklists de tournoi, yugiohmeta.com · date de calcul non
    enregistrée dans la base servie »
  - graphe : « Source : co-occurrences de cartes dans les decklists de tournoi, yugiohmeta.com · date de calcul non
    enregistrée dans la base servie · {n} cartes, {n} liens »
