# Étape 1 — Audit de l'existant

Date : 2026-11-16. Branche auditée : `main` (commit 830bf96). Front sur `localhost:3000` (serveur `next dev` déjà lancé par Thomas à 14 h 45, je ne l'ai ni arrêté ni relancé), API sur `localhost:8000` (lancée par moi).

## Comment lire ce document

- **VÉRIFIÉ** : mesuré ou observé pendant cette session (capture, script, requête chronométrée).
- **SUPPOSÉ** : déduction raisonnable non mesurée. Toujours signalé.
- Les mesures viennent d'un script Playwright (navigateur Chromium sans interface, `.venv`) qui lit les API de performance du navigateur : `PerformanceObserver` pour le LCP et le CLS, Navigation Timing pour le temps serveur, Resource Timing pour les poids. **Lighthouse n'est pas installé** sur la machine : je ne l'ai pas installé, les scores Lighthouse cités dans la feuille de route sont donc des objectifs, pas des mesures.
- L'INP (réactivité au clic) ne se mesure vraiment qu'avec de vrais utilisateurs. J'ai seulement une sonde : un clic sur le premier bouton de la page et le temps jusqu'à l'image suivante.
- Les captures sont dans `captures/` : `<page>-desktop-fold.png` (écran 1440 × 900), `<page>-desktop-full.png` (page entière), idem `-mobile-` (375 × 812). Planche mobile : `captures/_planche-mobile.png`.

## Verdict court

Le site n'est pas « moche ». Il est **propre, cohérent et rapide à afficher**, mais il est **muet** : aucune animation, presque aucune image de carte, aucune profondeur, et une page d'accueil qui ressemble à un tableau de bord interne plutôt qu'à la vitrine d'un produit. L'écart avec les sites que Thomas voit en publicité ne vient pas d'un manque de goût dans le système Ember : il vient de trois absences (mouvement, imagerie, récit), plus un vrai problème de données lentes et de crédibilité des chiffres affichés.

Dit autrement : la **charpente** (typographie, tokens, grille, rendu serveur) est au niveau. C'est la **couche d'expression** qui manque, et elle se rajoute par-dessus sans tout casser.

## 0. Trois faits techniques à connaître avant le reste

### 0.1 Les 15 secondes de `/` et `/ban` : cause trouvée (VÉRIFIÉ)

Ce n'est pas le front, c'est une requête SQL de l'API.

| Appel API (sur `main`, base `yugioh.db`) | Temps mesuré |
|---|---|
| `GET /ban-radar?limit=3` (utilisé par `/`) | **5,9 à 6,3 s**, à chaque appel |
| `GET /ban-radar?limit=50` (utilisé par `/ban`) | **5,9 s** |
| `GET /card-impact?limit=50` | **6,2 à 6,4 s** |
| `GET /graph/synergies` | **4,0 à 4,1 s** |
| Trois appels `/ban-radar` lancés en même temps | **36 s chacun** |
| `GET /meta/*`, `/boutique/signals`, `/cards/search` | 2 à 250 ms |

Pourquoi : les trois routeurs lents font `LEFT JOIN cards c ON REPLACE(REPLACE(c.name,'<',''),'>','') = r.card_name`. Une jointure sur une **expression** ne peut pas utiliser un index ordinaire : pour chacune des 966 lignes de `ban_radar`, SQLite relit les 13 797 cartes et recalcule deux `REPLACE`, soit environ 13 millions d'évaluations. Le `LIMIT 3` n'aide pas, car le tri se fait après la jointure. Le plan d'exécution le confirme : `SCAN r` puis `SCAN c LEFT-JOIN`.

Preuve par l'expérience (lecture seule, rien modifié) : la même requête sans la jointure prend 0,2 ms ; avec `= +r.card_name` et l'index d'expression `idx_cards_name_clean`, elle prend 2 ms.

**Ce correctif existe déjà** : commit `4d8f8df` « perf(TOK-83) » d'une autre session, sur une branche qui n'est pas encore dans `main`. L'index est déjà présent dans `data/yugioh.db`, mais le code de `main` ne l'utilise pas (il manque le `+` qui neutralise l'affinité de type). Tant que TOK-83 n'est pas fusionné, `main` reste lent.

Pourquoi 15 s et pas 6 : la page d'accueil lance trois appels en parallèle, et plusieurs requêtes lentes simultanées se ralentissent entre elles (36 s mesurées à trois). Deux déclencheurs côté Next (documentation lue dans `node_modules/next/dist/docs/01-app/03-api-reference/04-functions/fetch.md` et `02-guides/incremental-static-regeneration.md`) :
- le cache de `fetch` (`revalidate: 300`) expire au bout de 5 minutes ;
- **en développement, un rechargement forcé (Cmd+Maj+R) ou les outils de développement ouverts avec « désactiver le cache » envoient `cache-control: no-cache`, et Next ignore alors `revalidate` : l'API est rappelée à chaque fois.**

Quand le cache est chaud, les pages répondent en 30 à 300 ms (mesuré).

Ce que le front ajoute au problème (VÉRIFIÉ dans le code) : aucun fichier `loading.tsx`, aucun `<Suspense>` autour des données, aucun délai maximal sur `fetch`. Pendant que l'API calcule, l'utilisateur regarde une page blanche ou figée, sans squelette ni message.

### 0.2 Le build de production échoue aujourd'hui sur `main` (VÉRIFIÉ)

J'ai copié `frontend/` dans le scratchpad et lancé `next build` (rien écrit dans le dépôt). Résultat :

```
Error occurred prerendering page "/early-signals"
Error: API error 500: /early-signals
```

`GET /early-signals` renvoie une erreur 500 depuis la modification de la base de 15 h 15 : une ligne de `early_card_signals` a un `archetype` nul et le schéma Pydantic `EarlySignal` exige une chaîne (`backend/app/routers/boutique.py`, ligne 55). La page fonctionnait encore dans le navigateur parce que Next servait une réponse en cache.

Deux leçons :
- 8 pages sur 9 sont **pré-rendues au build** en appelant l'API. Si l'API est éteinte ou renvoie une erreur ce jour-là, le déploiement casse. Il faut une API joignable au build, ou un repli (données vides + message).
- Il n'y a ni `error.tsx` ni `not-found.tsx` : une erreur d'API donne la page d'erreur brute de Next.

### 0.3 `/ban-simulator` n'existe plus (VÉRIFIÉ)

L'URL renvoie 404 (le simulateur vit dans `/ban?tab=simulateur`). La page 404 est celle de Next par défaut, en anglais, fond blanc dans un site sombre : le logo `YGO META` y est blanc sur blanc (contraste 1,18:1). `context.md` mentionne encore `/ban-simulator`. Une redirection suffirait.

## 1. Mesures globales

### Développement (`next dev`, cache chaud)

| Page | TTFB | LCP | CLS | Nœuds DOM | Hauteur desktop | Hauteur mobile | HTML |
|---|---|---|---|---|---|---|---|
| `/` | 48 ms | 228 ms | 0 | 170 | 1 295 px | 2 243 px | 41 ko |
| `/tier-list` | 57 ms | 120 ms | 0 | 743 | 3 767 px | 4 168 px | 102 ko |
| `/evolution` | 30 ms | 64 ms | 0 | 244 | 965 px | 1 166 px | 36 ko |
| `/predictions` | 63 ms | 104 ms | 0 | 438 | 1 260 px | 1 287 px | 97 ko |
| `/boutique` | 142 ms | 196 ms | 0 | 1 234 | 5 073 px | 5 120 px | **334 ko** |
| `/early-signals` | 68 ms | 112 ms | 0 | 699 | 4 106 px | 4 410 px | 162 ko |
| `/graph` | 43 ms | 84 ms | 0 | 135 | 1 199 px | 1 139 px | 127 ko |
| `/ban` (radar) | 142 ms | 204 ms | 0 | 938 | 6 524 px | **10 535 px** | 261 ko |
| `/ban?tab=impact` | 152 ms | 208 ms | 0 | 724 | 6 511 px | 9 487 px | 200 ko |
| `/ban?tab=simulateur` | 113 ms | 152 ms | 0,005 | 108 | 900 px | 1 118 px | 25 ko |

Lecture : le LCP (moment où le plus gros élément visible est affiché) est partout le titre `h1`, un texte, donc quasi instantané. Le CLS (décalages de mise en page) est nul. **Quand les données sont en cache, le site est très rapide.** Les poids JavaScript du mode développement (3,4 à 5,5 Mo décompressés) ne veulent rien dire : ils contiennent les outils de développement. Voir le tableau production ci-dessous.

### Production (copie construite dans le scratchpad)

Conditions : `next build` puis `next start` sur une copie de `frontend/` (avec, dans la copie seulement, un repli vide pour `/early-signals` afin que le build passe). Machine locale, réseau local, donc les temps sont des planchers : en ligne, il faut ajouter la latence réseau. Mesures desktop 1440 px.

| Page | Type de rendu | TTFB | LCP | CLS | Blocage (tâches longues) | JavaScript décompressé | dont spécifique à la page |
|---|---|---|---|---|---|---|---|
| `/` | statique, régénérée toutes les 5 min | 13 ms | 84 ms | 0 | 0 ms | 560 ko | |
| `/tier-list` | statique | 5 ms | 60 ms | 0 | 0 ms | 528 ko | |
| `/evolution` | statique | 7 ms | 40 ms | 0 | 0 ms | 869 ko | recharts ≈ 340 ko (100 ko compressé) |
| `/predictions` | statique | 8 ms | 60 ms | 0 | 0 ms | 548 ko | |
| `/boutique` | statique | 6 ms | 56 ms | 0 | 0 ms | 550 ko | HTML 297 ko (14 ko compressé) |
| `/early-signals` | statique | 14 ms | 52 ms | 0 | 0 ms | 522 ko | |
| `/graph` | statique | 4 ms | 40 ms | 0 | **110 ms** | **1 141 ko** | vis-network ≈ 636 ko (147 ko compressé) |
| `/ban` (radar, cache chaud) | **dynamique** | 19 ms | 68 ms | 0 | 0 ms | 578 ko | |
| `/ban?tab=impact` (cache froid) | **dynamique** | **6 349 ms** | **6 396 ms** | 0 | 0 ms | 578 ko | attend l'API |
| `/ban` premier appel après démarrage | dynamique | **7 099 ms** | | | | | attend l'API |

Lecture :
- Le socle commun pèse environ **520 ko de JavaScript décompressé, 165 ko transférés** (React, Next, la nav, la recherche). C'est correct pour une application Next ; un site vitrine d'excellence vise 100 à 170 ko transférés sur la page d'accueil. Il reste donc peu de marge avant d'ajouter des bibliothèques d'animation : chaque ajout devra être chargé à la demande.
- Les 8 pages statiques sont irréprochables (LCP inférieur à 100 ms en local, CLS nul).
- `/ban` est la seule page rendue à chaque visite (elle lit `searchParams`), donc la seule exposée à la lenteur de l'API : 6 à 7 s d'écran vide à froid.
- En production, les liens `<Link>` visibles sont pré-chargés. Chaque page contient un lien vers `/ban` dans la nav : j'ai compté 10 à 29 requêtes de pré-chargement par page. SUPPOSÉ (non isolé) : ces pré-chargements déclenchent eux aussi l'appel lent à l'API et expliquent que mon script ait mis jusqu'à 27 s à voir le réseau se calmer sur certaines pages.

### Constats transverses mesurés

- **Aucune animation en cours sur aucune page** (`document.getAnimations()` = 0 partout). Les seules transitions sont des changements de couleur au survol (200 ms) et un déplacement d'un pixel sur les tuiles.
- **Images** : 0 image sur 7 pages sur 9. Les seules images de cartes sont les vignettes 34 × 48 px de la tier list et une vignette 64 × 92 px dans le simulateur.
- Les vignettes de la tier list chargent un fichier de 268 × 391 px pour l'afficher en 34 × 48 px (8 fois trop de pixels par côté), sans `width`/`height`, sans `loading="lazy"`, depuis `images.ygoprodeck.com` (39 requêtes vers un domaine tiers).
- **Polices** : 3 familles auto-hébergées par `next/font` (Inter Tight 400/500, Instrument Serif italique, JetBrains Mono 400/500), 90 ko au total. Très bien.
- **Répartition des polices** : sur `/boutique`, 80 % des caractères sont en JetBrains Mono ; sur `/early-signals`, 92 %. Le mono, prévu pour les chiffres et labels, est devenu la police de lecture principale des pages de données.
- **Tailles de texte** : la taille la plus fréquente est 12 px, puis 11 px. Le corps à 16 px prévu par le design system n'apparaît que dans le paragraphe d'introduction.
- **SEO** : toutes les pages ont le même `<title>` (« Yu-Gi-Oh! Meta Analyzer ») et la même description, en anglais, sur un site en français. Aucune balise Open Graph (pas d'aperçu quand on partage un lien), pas de `sitemap`, pas de `robots`, pas de données structurées, pas de pied de page.
- **Cibles tactiles** : presque tous les éléments cliquables font moins de 44 px de haut (pills de filtre 30 px, liens de nav 30 px, bouton Menu 30 px). Le critère WCAG AA (2.5.8) demande 24 px minimum : respecté, sauf l'icône ⓘ. Le confort mobile recommandé (44 px) ne l'est pas.
- **Structure** : un `h1` par page (bien), mais aucun `h2` : on passe du `h1` aux `h3` (50 `h3` sur `/ban`). Pas de lien d'évitement, pas de `<footer>`.

### Contrastes (objectif WCAG AA : 4,5:1 pour le texte, 3:1 pour le grand texte)

| Paire | Ratio calculé | Verdict |
|---|---|---|
| `--text` sur `--ink` | 17,15:1 | conforme |
| `--soft` sur `--ink` | 10,84:1 | conforme |
| `--muted-text` sur `--ink` / `--ink-3` / `--ink-4` | 6,33 / 5,85 / 5,37:1 | conforme |
| `--signal` sur `--ink` | 6,51:1 | conforme |
| `--on-signal` sur `--signal` | 6,23:1 | conforme |
| `--signal-deep` sur `--paper` | 5,40:1 | conforme |
| `--good`, `--warn` sur `--ink` | 11,4 / 12,4:1 | conforme |
| **`--faint` sur `--ink`** | **3,23:1** | **non conforme** en 12 px |
| **`--faint` sur `--ink-3`** | **2,98:1** | **non conforme** |
| **`--on-signal` à 70 % sur `--signal`** (tuile orange de l'accueil, texte 14 px et label 11 px) | **≈ 3,9:1** (calculé à la main, le script ne lit pas `color-mix`) | **non conforme** |
| Bordures `--line` / `--line-2` sur `--ink` | 1,21 / 1,50:1 | sous les 3:1 demandés pour un contour de champ de saisie |

`--faint` porte de l'information dans 47 à 100 éléments par page : les rangs (`01`, `#1`), les tirets des cellules vides du tableau boutique, l'invite `>`. Le design system dit lui-même de le réserver au décoratif : la règle n'est pas tenue.

## 2. Page par page

Pour chaque page, les 8 critères demandés : (1) hiérarchie, (2) typographie, (3) couleur, (4) mouvement, (5) imagerie, (6) dataviz, (7) technique, (8) contenu.

### `/` — Accueil

Captures : `captures/home-desktop-full.png`, `captures/home-mobile-full.png`.

1. **Hiérarchie.** Le titre et le « 100 » de la tuile claire accrochent l'œil, c'est voulu et ça marche. Mais toute la moitié droite du hero est vide (environ 580 × 400 px de fond pointillé à 1440 px) : c'est exactement l'endroit où les sites de référence placent leur visuel. La page entière tient en 1 295 px : il n'y a **rien à faire défiler**, donc aucun récit.
2. **Typographie.** Le couple Inter Tight serré + un mot en Instrument Serif italique est la meilleure idée du système. Le `h1` plafonne à 72 px ; il peut monter.
3. **Couleur.** Trois tuiles de trois couleurs (claire, sombre, orange) : c'est le seul endroit du site où la palette vit. Le texte à 70 % sur la tuile orange est sous le seuil de contraste.
4. **Mouvement.** Aucun. Le curseur orange du « terminal » de la tuile E ne clignote même pas. Le graphe de la tuile D est un dessin fixe.
5. **Imagerie.** **Zéro image de carte sur la page d'accueil d'un site de cartes.** La tuile A parle d'« Elfnotes: Rhapsodia of Madness » sans la montrer. C'est le manque le plus visible.
6. **Dataviz.** La mini-courbe « actuel → prévu » relie deux points (6,3 → 7,0) : honnête, mais sans échelle, elle ne dit rien de l'ampleur. Le graphe « pont » est une illustration, pas une donnée.
7. **Technique.** Trois appels API dont `ban-radar` (6 s à froid). Pré-rendue au build, régénérée toutes les 5 minutes.
8. **Contenu.** La promesse (« Le TCG suit l'OCG, quatre mois plus tard ») est forte et originale. Mais elle s'adresse aux boutiques alors que les tuiles mélangent trois publics. Pas de preuve sociale, pas d'explication de qui parle, pas de pied de page, pas de « comment ça marche ». Et le signal vedette est une carte à **0,12 €** notée 100/100 : pour une boutique, ça ne ressemble pas à une opportunité. Les lettres A à E encadrées n'apportent pas d'information (le design system déconseille d'ailleurs la numérotation décorative).

### `/tier-list`

Captures : `captures/tier-list-desktop-fold.png`, `-full.png`, `-mobile-`.

1. **Hiérarchie.** Bonne : titre, bande de quatre chiffres, filtres, liste. La liste ne commence qu'à 615 px du haut à 1440 px : sur un écran de portable, on voit deux lignes et demie de la tier list avant de défiler.
2. **Typographie.** `h1` à 92 px, très réussi. Dans les lignes, tout le reste est en mono 11-12 px.
3. **Couleur.** Sobre. La première ligne teintée fonctionne.
4. **Mouvement.** Survol de ligne seulement. Changer de filtre remplace la liste d'un coup, sans transition.
5. **Imagerie.** Seule page avec des images de cartes, mais en timbre-poste (34 × 48 px). Le panneau d'aperçu au survol n'apparaît qu'au-delà de 1280 px de large et n'existe pas au tactile.
6. **Dataviz.** Incohérence lisible sur la capture : la liste est triée par part de méta (29,6 %, 17,5 %…), mais la barre représente le **score** (Elfnote, 4ᵉ, a la barre pleine avec 16,5 ; Kewl Tune, 1ᵉʳ, a une barre au tiers avec 5,8). Deux mesures se contredisent sur la même ligne sans explication. Les tendances sont en anglais (`Declining`, `Stable`) dans une interface en français.
7. **Technique.** 44 images non dimensionnées, non différées, surdimensionnées.
8. **Contenu.** L'eyebrow annonce « MISE À JOUR 17 JUIN 2026 » alors qu'on est le 16 novembre : cinq mois de retard affichés en tête de page. Les quatre chiffres de la bande (19 888, 13 797, 0,771, 4 mois) sont des constantes écrites à la main dans `site-facts.ts`, répétées sur plusieurs pages.

### `/evolution`

Capture : `captures/evolution-desktop-full.png`.

1. **Hiérarchie.** Titre, pills, graphique. Simple et clair.
2. **Typographie.** RAS.
3. **Couleur.** Une série en accent, deux en gris-bleu presque identiques : on ne distingue pas Angelechy d'Artmage.
4. **Mouvement.** L'animation de tracé par défaut de recharts, rien d'autre.
5. **Imagerie.** Aucune. Les archétypes n'ont pas de visage.
6. **Dataviz.** **Le graphique est vide à 85 %.** L'axe vertical est fixé de 0 à 100 (`domain={[0, 100]}` dans `EvolutionChart.tsx`) alors que les valeurs ne dépassent pas 16. L'axe horizontal commence en février 2024 alors que les séries démarrent en juillet 2025. Les trois courbes sont écrasées dans le coin inférieur droit. Pas d'annotation (dates de banlist, sorties de sets), pas d'étiquette au bout des lignes, pas de légende directe.
7. **Technique.** recharts ajoute environ 300 ko de JavaScript (mode dev) pour un seul graphique en lignes.
8. **Contenu.** « Qui monte, qui s'efface » est un bon titre, mais le graphique ne raconte pas qui monte : c'est à l'utilisateur de cliquer sur 15 pills pour le découvrir.

### `/predictions`

Capture : `captures/predictions-desktop-fold.png`.

1. **Hiérarchie.** Un tableau de 45 lignes identiques. Rien ne ressort : la seule ligne « Rising » (Branded, +0,6) est noyée en 5ᵉ position.
2. **Typographie.** RAS.
3. **Couleur.** Barre « actuel » grise, barre « prévu » orange : 45 barres orange, l'accent ne signale plus rien (contraire au principe n° 1 du design system).
4. **Mouvement.** Aucun.
5. **Imagerie.** Aucune.
6. **Dataviz.** Deux barres côte à côte obligent à comparer des longueurs à 270 px de distance. Les écarts sont minuscules (±0,5) : un graphique en haltères (un point actuel, un point prévu, un trait entre les deux) ou un tri par delta les rendrait visibles. Pas d'intervalle d'incertitude.
7. **Technique.** RAS.
8. **Contenu.** Le sous-titre dit « Modèle : Ridge + Naïf blend (ρ≈+0.65) » : jargon brut, point décimal anglais. `context.md` parle d'un modèle AR(1) : le libellé est à vérifier (la branche `front-vitrine` semble le traiter, commit 53666c6). `+0,0` est affiché en vert comme une hausse.

### `/boutique`

Capture : `captures/boutique-desktop-fold.png`.

1. **Hiérarchie.** Titre, bande de chiffres, tableau de 100 lignes sur 5 073 px.
2. **Typographie.** Noms de cartes en mono 12 px dans des chips : fatigant à lire sur 100 lignes.
3. **Couleur.** Les 14 premières lignes portent la même étiquette orange « FORT » : même remarque que pour les prédictions.
4. **Mouvement.** Aucun.
5. **Imagerie.** **Aucune image dans la page censée faire acheter des cartes.** L'image n'apparaît qu'au survol, dans un panneau latéral, sur grand écran uniquement.
6. **Dataviz.** Aucune. Pas d'historique de prix alors que la table `card_price_history` existe (41 395 lignes), pas de courbe OCG en regard.
7. **Technique.** 334 ko de HTML pour 100 lignes (1 234 nœuds) : acceptable, mais sans pagination ni regroupement.
8. **Contenu.** C'est la page qui porte le modèle économique (150 €/mois) et elle affiche **huit cartes Elfnote entre 0,12 € et 0,59 €** en tête, toutes avec « mars 2027 ». Colonne « Banlist TCG » remplie de tirets. Contradiction VÉRIFIÉE dans la base : la page annonce l'entrée d'Elfnote en TCG pour mars 2027, alors que `meta_scores` (TCG) donne déjà Elfnote à 20 % des decks en octobre 2026, que la tier list TCG le classe 4ᵉ et que le Ban Radar TCG liste ses cartes. Soit la date estimée est fausse, soit les decks TCG sont pollués par d'autres formats : à trancher avec l'agent data-scientist, c'est le cœur de la promesse. Aucun regroupement par archétype, aucun budget, aucun export, aucun « pourquoi ». Un gérant de boutique ne peut pas en tirer une commande.

### `/early-signals`

Capture : `captures/early-signals-desktop-fold.png`.

1. **Hiérarchie.** Liste de 50 lignes ; les sept premières sont toutes « Kewl Tune ».
2. **Typographie.** 92 % de mono.
3. **Couleur.** 50 barres orange.
4. **Mouvement.** Aucun.
5. **Imagerie.** Aucune (chips texte).
6. **Dataviz.** Une barre par ligne ; les « vues / semaine » sont un nombre nu, sans tendance.
7. **Technique.** L'API renvoie 500 sur `main` au moment de l'audit (voir 0.2).
8. **Contenu.** Titre en français, eyebrow et entrée de menu en anglais (« Early Signals »). La différence avec `/boutique` n'est pas expliquée ; un commentaire dans `nav.tsx` reconnaît que les deux scores se recouvrent pour un tiers.

### `/graph`

Capture : `captures/graph-desktop-fold.png`.

1. **Hiérarchie.** Le graphe est sous la ligne de flottaison à moitié.
2. **Typographie.** RAS.
3. **Couleur.** Tous les nœuds sont du même gris-bleu. On ne sait pas quel amas est quel archétype.
4. **Mouvement.** La simulation physique de vis-network à l'ouverture, puis plus rien.
5. **Imagerie.** Des points. Les cartes ont pourtant des illustrations.
6. **Dataviz.** C'est la page qui devrait être la plus spectaculaire, et c'est la plus décevante : **une vingtaine d'amas isolés, sans étiquette, sans lien entre eux**. Le graphe ne montre donc pas ce que le texte promet ailleurs (« une carte pont relie les archétypes ») : avec un seuil de Jaccard à 0,15, les ponts ont disparu. On ne peut rien lire sans survoler chaque point. Le sélecteur est une liste déroulante native.
7. **Technique.** Rendu `canvas` : invisible pour un lecteur d'écran, aucun équivalent textuel, pas de navigation clavier. Tâches longues : 120 ms de blocage (le plus élevé du site). vis-network pèse environ 300 ko.
8. **Contenu.** « Co-occurrence Jaccard », « Jaccard ≥ 0,15 » : vocabulaire de data scientist, sans traduction pour un joueur.

### `/ban` — Ban Radar, Cartes à impact, Simulateur

Captures : `captures/ban-radar-desktop-fold.png`, `ban-impact-…`, `ban-simulateur-…`.

1. **Hiérarchie.** Le score en 60 px à gauche est très réussi : c'est la meilleure page du site. Mais il faut 520 px (titre, onglets, bouton d'explication, filtres) avant la première carte.
2. **Typographie.** Bonne échelle (60 / 20 / 12).
3. **Couleur.** La barre empilée en six opacités d'une même teinte est élégante mais illisible : les trois dernières opacités (45 %, 30 %, 18 %) sont indiscernables, et la légende n'apparaît que sous la première ligne.
4. **Mouvement.** Aucun : les barres n'ont pas d'animation d'entrée, les scores ne comptent pas.
5. **Imagerie.** **Aucune image de carte dans le radar**, alors que l'API renvoie `image_url` pour chaque entrée (champ présent dans `BanRadarEntry`). C'est le gain le plus facile de tout l'audit.
6. **Dataviz.** Sur mobile, la page fait 10 535 px de haut pour 50 cartes. Simulateur : « 710 bridge score » sans unité ni repère, « communauté inconnue », et « 7 archétypes impactés » pour Ash Blossom alors que le radar en annonce 95 pour la même carte.
7. **Technique.** Seule route dynamique (rendue à chaque visite) : c'est elle qui subit de plein fouet les 6 s de l'API.
8. **Contenu.** Les trois premières cartes « critiques » sont Ash Blossom (100), Mulcharmy Fuwalos (97,9) et Droll & Lock Bird (97,8), des staples génériques présentes dans 93 % des decks. `context.md` écrit lui-même que « l'omniprésence seule ne prédit rien ». Un joueur qui voit Ash Blossom à 100/100 de risque de ban cesse de croire au reste. Le filtre « Pièces d'archétype » devrait sans doute être la vue par défaut (décision de fond, hors design : à voir avec l'agent data-scientist).

### `/ban-simulator`

404 (voir 0.3). Capture : `captures/ban-simulator-404-desktop-fold.png`.

## 3. Synthèse par critère

| Critère | Note /5 | En une phrase |
|---|---|---|
| 1. Hiérarchie et mise en page | 3,5 | Claire, mais des vides non utilisés (moitié droite des heros) et des listes interminables. |
| 2. Typographie | 4 | Très bon trio de polices ; le mono 11-12 px est surutilisé pour la lecture. |
| 3. Couleur et système | 4 | Tokens cohérents, zéro couleur brute ; l'accent est dilué dans les tableaux ; 3 contrastes à corriger. |
| 4. Mouvement | 0,5 | Rien, à part des survols. |
| 5. Imagerie | 1 | Un site de cartes sans cartes. |
| 6. Dataviz | 2 | Un graphique vide à 85 %, un graphe sans étiquettes, des barres partout. |
| 7. Performance et technique | 3 | Excellent en cache chaud ; API à 6 s, build cassé, pas d'états de chargement ni d'erreur, SEO absent. |
| 8. Contenu et crédibilité | 2,5 | Bonne accroche ; dates périmées, chiffres qui se contredisent, jargon, mélange français / anglais. |

## 4. Problèmes → gravité → effort

Gravité : **bloquant** (empêche de mettre en ligne ou trompe l'utilisateur), **fort** (dégrade nettement la perception), **moyen**, **faible**. Effort pour une personne seule aidée d'un assistant de code.

| # | Problème | Gravité | Effort |
|---|---|---|---|
| 1 | API `/ban-radar`, `/card-impact`, `/graph/synergies` à 4-6 s (36 s en simultané) : correctif TOK-83 non fusionné dans `main` | bloquant | 10 min (fusionner la branche) |
| 2 | `GET /early-signals` en erreur 500 → build de production impossible | bloquant | 15 min (champ optionnel ou filtre SQL) |
| 3 | Aucun `loading.tsx`, `error.tsx`, `not-found.tsx` ; pas de repli si l'API tombe | fort | 2 h |
| 4 | Aucune image de carte sur l'accueil, le radar, la boutique, les signaux | fort | 1 jour |
| 5 | Aucune animation (entrée, défilement, transitions de page, compteurs) | fort | 3 à 5 jours pour un socle soigné |
| 6 | Accueil sans récit (une seule hauteur d'écran, pas de preuve, pas de pied de page) | fort | 1 à 2 semaines avec le contenu |
| 7 | `/graph` : amas isolés sans étiquette, sans couleur, sans ponts | fort | 1 à 2 semaines |
| 8 | `/evolution` : axe 0-100 pour des valeurs ≤ 16, axe du temps vide à 60 % | fort | 30 min |
| 9 | Crédibilité : date « 17 juin 2026 », Ash Blossom à 100, carte à 0,12 € en signal vedette, 7 contre 95 archétypes | fort | décision produit + 1 jour |
| 10 | SEO : titre et description uniques en anglais, pas d'Open Graph, pas de sitemap | fort | 3 h |
| 11 | Tier list : la barre (score) contredit le tri (part de méta) | moyen | 1 h |
| 12 | Accent dilué : 45 à 100 barres ou étiquettes orange par page | moyen | 2 h |
| 13 | Contrastes : `--faint` porteur d'information (3,2:1), texte à 70 % sur tuile orange (≈ 3,9:1) | moyen | 1 h |
| 14 | Mono 11-12 px comme police de lecture (80 à 92 % des caractères sur 2 pages) | moyen | 3 h |
| 15 | Images : surdimensionnées (268 px pour 34 px), sans dimensions, sans chargement différé, domaine tiers | moyen | 3 h (`next/image` + `remotePatterns`) |
| 16 | Mélange français / anglais (`Declining`, `Early Signals`, `UNLIMITED`, « bridge score ») | moyen | 2 h |
| 17 | Ban Radar mobile : 10 535 px de haut, pas de pagination | moyen | 3 h |
| 18 | `/graph` inaccessible (canvas sans alternative textuelle ni clavier) | moyen | 1 jour (tableau équivalent) |
| 19 | `/ban-simulator` en 404, page 404 par défaut blanche et en anglais | faible | 30 min |
| 20 | Pas de `h2`, pas de lien d'évitement, pas de pied de page | faible | 1 h |
| 21 | Cibles tactiles de 30 px (confort mobile : 44 px) | faible | 1 h |
| 22 | Barre empilée du radar : opacités indiscernables, légende sur la première ligne seulement | faible | 2 h |
| 23 | recharts + vis-network : environ 600 ko de JavaScript pour deux visualisations | faible | inclus dans la refonte dataviz |

Les lignes 1, 2, 8, 11, 13 et 19 se corrigent en une demi-journée et ne dépendent d'aucune décision de design.
