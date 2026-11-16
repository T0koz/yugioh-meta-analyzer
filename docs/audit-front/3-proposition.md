# Étape 3 — Proposition « au top »

Date : 2026-11-16. S'appuie sur `1-audit.md` (ce qui manque) et `2-benchmark.md` (ce qui se fait). **Rien n'est implémenté** : ce document attend la validation de Thomas. Seul un prototype statique existe, hors de `frontend/` : `prototype/index.html`.

## 1. Le principe directeur

L'audit dit : la charpente est bonne (typographie 4/5, couleur 4/5), l'expression est absente (mouvement 0,5/5, imagerie 1/5). Le benchmark dit : les meilleurs sites n'ont pas dix effets, ils ont **un objet-signature**, **le vrai produit à l'écran** et **beaucoup de petites animations justes**.

Donc : **on ne jette pas Ember, on lui donne un corps.** Trois ajouts, dans cet ordre de rendement :
1. **La carte comme objet-signature** (aujourd'hui presque absente du site).
2. **Le mouvement comme langage** (aujourd'hui inexistant).
3. **Le récit par la donnée** (aujourd'hui une seule hauteur d'écran).

Et une règle de tempo : **vitrine expressive, outils sobres.** La page d'accueil peut être cinématographique ; la tier list, le radar et la boutique sont des instruments de travail, où une animation de plus de 300 ms devient une gêne dès la troisième visite.

## 2. Trois directions possibles

### Option A — « Salle des marchés »

Le site assume d'être le terminal de trading du TCG. Chaque carte est une valeur cotée : bandeau défilant de variations en tête, mini-courbes dans toutes les lignes, chiffres qui clignotent quand ils changent, grilles denses.

- Références : TradingView, Polymarket, Linear.
- Forces : colle au public boutique, peu de 3D donc léger, très crédible.
- Faiblesses : froid ; ne répond pas à l'envie de Thomas (« vectorisé, 3D, animé ») ; suppose des données qui bougent souvent, or les nôtres bougent une fois par semaine. Un ticker qui ne change pas est un mensonge visuel.

### Option B — « Braise vivante » (recommandée)

Ember, plus la carte, plus le mouvement. La carte Yu-Gi-Oh! devient l'objet-signature : éventail en 3D dans le hero, reflet holographique au survol, illustration recadrée comme visage de chaque archétype, vignette qui « s'envole » vers la page de détail lors d'un changement de page. Un récit au défilement démontre la promesse avec de vraies courbes. Les outils gardent la sobriété Ember, enrichie d'images et de micro-animations.

- Références : Resend (serif + sombre + un objet 3D), Stripe (un seul fond animé), Scryfall (l'éventail), The Pudding (le graphique qui évolue au défilement), Linear (le produit réel à l'écran).
- Forces : part de l'existant validé le 31 octobre ; chaque étape est livrable seule ; l'essentiel se fait en CSS et en DOM, donc reste rapide, accessible et indexable ; la 3D véritable arrive en dernier, comme un supplément.
- Faiblesses : demande de la retenue (la tentation d'en mettre partout) ; l'éventail dépend d'images hébergées par un tiers tant qu'on ne les sert pas nous-mêmes.

### Option C — « Monde 3D »

Le site entier est une scène : un plateau de duel en WebGL, la caméra vole d'une zone à l'autre, le graphe de synergies est une galaxie navigable, les cartes sont des objets 3D avec physique.

- Références : Igloo, Lusion.
- Forces : effet de souffle maximal, digne d'un prix.
- Faiblesses : 3 à 6 mois pour une personne qui apprend ; plusieurs mégaoctets (Igloo : 9 Mo mesurés) ; contenu invisible pour les moteurs de recherche et les lecteurs d'écran ; inutilisable pour consulter un tableau de 100 lignes ; fragile sur mobile. C'est un site de studio, pas un produit de données.

### Recommandation

**Option B**, avec un emprunt à A (mini-courbes dans les listes, fraîcheur des données affichée) et un emprunt à C limité à **une seule scène** : le graphe de synergies, qui est le seul endroit où la 3D ou le WebGL apporte de la lisibilité et pas seulement du spectacle.

Pourquoi, en une phrase : c'est la seule option qui atteint le niveau visuel visé **sans dégrader** ce que l'audit a mesuré de bon (LCP inférieur à 100 ms, CLS nul, texte indexable).

## 3. Concept et narration

### Page d'accueil (prototype : `prototype/index.html`)

Captures : `captures/prototype-desktop-1-hero.png`, `-2-preuve-1.png` à `-3.png`, `-3-outils.png`, `prototype-mobile-*.png`, `prototype-desktop-4-mouvement-reduit.png`.

| Section | Rôle | Ce qu'on voit |
|---|---|---|
| 1. Hero | La promesse | Titre révélé mot par mot ; à droite, **éventail de cinq cartes en 3D** qui s'incline avec la souris, reflet holographique ; braises qui montent en fond ; bande de quatre chiffres qui comptent. |
| 2. La preuve | La démonstration | Graphique fixe, texte qui défile : la courbe OCG de Kewl Tune se trace, puis la courbe TCG, puis la courbe OCG **glisse de trois mois** et vient se poser sur l'autre. Données réelles de `meta_scores` et `meta_scores_ocg`. |
| 3. Les outils | L'offre | Bento de trois tuiles avec **vraies images** : signal boutique (carte inclinée + score), Ban Radar (vignettes + barres qui se remplissent), graphe (constellation animée, ponts en orange). |
| 4. La méthode | La confiance | (non prototypé) D'où viennent les données, combien de decklists, quand mises à jour, résultats du backtest avec ses limites. C'est le bloc « Our World in Data ». |
| 5. Pour qui | L'orientation | (non prototypé) Deux portes : « Je tiens une boutique » / « Je joue ». Prépare TOK-52. |
| 6. Pied de page | La finition | Liens, date de mise à jour, mentions. |

Le prototype montre un point important trouvé en le construisant : **sur Kewl Tune, l'écart mesuré est de 3 mois, pas 4**. Le prototype le dit dans sa légende plutôt que de forcer le chiffre. Le récit de la page dépendra donc des chiffres que la branche `front-vitrine` est en train de réviser : le design doit s'adapter au chiffre vrai, pas l'inverse.

### Pages clés

- **Tier list** : chaque archétype a un **visage** (illustration recadrée en bandeau de 120 × 48 px, comme Yu-Gi-Oh! Meta et YGOPRODeck), une mini-courbe sur 6 mois, ses trois cartes clés en pastilles. Clic sur une ligne : la vignette s'agrandit en en-tête de la page d'archétype (transition de vue).
- **Page d'archétype** (à créer, TOK-56 en dépend) : c'est la page qui manque le plus. Bandeau illustré, courbe OCG et TCG superposées, cartes clés, signaux boutique, risque de ban. Elle relie les cinq outils aujourd'hui cloisonnés.
- **Ban Radar** : vignette de carte à gauche du score (l'API renvoie déjà `image_url`), barres qui se remplissent à l'entrée dans l'écran, pagination ou « voir plus » au lieu de 10 000 px de défilement mobile. Vue par défaut à trancher (voir formulaire).
- **Boutique** : regroupement par archétype, une carte illustrée par groupe, courbe de prix (la table `card_price_history` existe), total du « panier », export.
- **Graphe** : voir section 7.

## 4. Système de design cible : « Ember 2 »

Ember reste la base. Les changements sont des **ajouts** et quelques corrections issues de l'audit.

### Couleurs

| Token | Valeur | Statut | Raison |
|---|---|---|---|
| `--ink` à `--ink-4`, `--text`, `--soft`, `--muted-text` | inchangés | conservé | Contrastes conformes (6,3 à 17:1). |
| `--signal`, `--signal-hi`, `--on-signal` | inchangés | conservé | |
| `--faint` | `#566175` → **`#7482a0`** | corrigé | 3,2:1 aujourd'hui. La nouvelle valeur donne 4,8:1 sur `--ink-3`, la surface la plus défavorable où il est utilisé (calculé ; `#6e7a90` ne suffisait pas : 4,3:1 sur `--ink-3`). |
| `--ocg` | **`#7fb0ff`** | nouveau | Une seconde série de données est indispensable (OCG contre TCG). 9,2:1 sur `--ink`, 8,5:1 sur `--ink-3` (calculé). Bleu contre orange : distinguable par les daltoniens. |
| `--glow` | `rgba(255,90,60,.28)` | nouveau | Lueur d'accent (hero, carte vedette, survol). |
| `--cat-1` à `--cat-6` | à définir | nouveau | Palette catégorielle pour la barre des six critères du radar et les amas du graphe. Aujourd'hui : six opacités d'une teinte, indiscernables. À valider avec un outil de simulation du daltonisme. |
| Thème clair | non | écarté | Le sombre est l'identité ; un second thème double le travail de test. À reconsidérer seulement si des boutiques le demandent. |

Règle maintenue et resserrée : **l'accent orange signale, il ne remplit pas.** Dans un tableau, une seule colonne ou une seule ligne peut être orange. Les 45 barres « prévu » de `/predictions` passent en neutre ; seul l'écart est coloré.

### Typographie

- Trio conservé (Inter Tight, Instrument Serif italique, JetBrains Mono).
- **Le mono redevient un condiment** : labels, chiffres, étiquettes. Les noms de cartes et d'archétypes, lus en liste, passent en Inter Tight 15 à 16 px. Objectif mesurable : moins de 40 % des caractères en mono sur chaque page (92 % aujourd'hui sur `/early-signals`).
- Taille minimale de lecture : 13 px ; 11 px réservé aux labels en majuscules.
- Corps de la vitrine : 17 à 18 px.
- Passer Inter Tight en **police variable** (un seul fichier, toutes les graisses, permet d'animer la graisse).
- `h1` de la vitrine : jusqu'à 96 à 112 px à 1440 px.

### Espacements, formes, profondeur

- Échelle d'espacement sur une base 4 px : 4, 8, 12, 16, 24, 32, 48, 72, 120. Rythme vertical de la vitrine : 120 px entre sections (44 px aujourd'hui, trop serré pour un récit).
- Rayons : 4 px (contrôles), 8 px (cartes à jouer), 14 px (tuiles).
- **Profondeur : le principe « pas d'ombres » est assoupli pour un seul objet, la carte.** Ombre portée + lueur d'accent pour la carte vedette. Le reste garde les filets.
- Cibles tactiles : 44 px de haut minimum sur mobile.

### Tokens de mouvement (nouveaux)

| Token | Valeur | Usage |
|---|---|---|
| `--dur-1` | 150 à 200 ms | Survol, focus, pression |
| `--dur-2` | 400 à 600 ms | Apparition d'un bloc, changement d'onglet ou de filtre |
| `--dur-3` | 900 à 1 200 ms | Séquence d'ouverture du hero, tracé d'une courbe |
| `--ease` | `cubic-bezier(.16,1,.3,1)` | Sortie douce, déjà dans Ember |
| `--ease-spring` | ressort (raideur ≈ 260, amortissement ≈ 24) | Cartes : inclinaison, retournement, distribution |
| `--stagger` | 60 à 90 ms | Décalage entre éléments d'une même liste |

### Composants à créer ou refondre

`CardArt` (image de carte : dimensions fixes, `next/image`, repli dessiné, variantes vignette / pastille / bandeau / grande), `HoloCard` (carte inclinable avec reflet), `CardFan` (éventail), `Sparkline`, `StatCounter`, `Reveal` (apparition à l'entrée dans l'écran), `ScrollStory` (graphique fixe + étapes), `DataFooter` (source · date · échantillon · méthode), `Skeleton` de chaque liste, `EmptyState`, `ErrorState`, `ArchetypeBanner`, `StackedBar` avec palette catégorielle et légende intégrée, `Footer`.

## 5. Mouvement : cahier des charges

### Les sept familles d'animation

| # | Quoi | Où | Comment | Bibliothèque |
|---|---|---|---|---|
| 1 | **Ouverture** : titre mot par mot, cartes distribuées, chiffres qui comptent | Hero de l'accueil ; version courte (titre seul) sur les autres pages | Une séquence de 1,2 s maximum, jouée une fois | CSS seul |
| 2 | **Apparition au défilement** : fondu + 24 px de glissement, décalage en cascade | Sections de la vitrine, premières lignes des listes | Déclenchée une fois à l'entrée dans l'écran | CSS + `IntersectionObserver`, ou Motion `whileInView` |
| 3 | **Récit au défilement** : un graphique fixe évolue pendant que le texte défile | Accueil (« la preuve »), page méthode | Progression de défilement reliée au tracé | `position: sticky` + JS léger ; GSAP ScrollTrigger si les séquences se compliquent |
| 4 | **Transitions de page** : la vignette devient l'en-tête, les listes se réordonnent en glissant | Tier list → archétype, changement de filtre ou d'onglet | View Transitions | React `<ViewTransition>` + `experimental.viewTransition` de Next 16 |
| 5 | **Micro-interactions** : survol, pression, focus, bord lumineux qui suit la souris, curseur qui clignote | Partout | 150 à 200 ms | CSS |
| 6 | **Données qui s'animent** : barres qui se remplissent, courbes qui se tracent, compteurs, valeur qui « flashe » quand elle change | Radar, prédictions, évolution | À l'entrée dans l'écran, une fois | CSS + Motion pour les valeurs |
| 7 | **Objet-signature** : éventail inclinable, reflet holographique, braises | Hero ; carte vedette de la boutique ; panneau d'aperçu | CSS 3D ; `canvas` 2D pour les braises ; shader WebGL en option plus tard | CSS, puis OGL ou Three.js en option |

### Choix des bibliothèques, et pourquoi

- **CSS d'abord.** Les familles 1, 2, 5 et une partie de 6 et 7 n'ont besoin d'aucune bibliothèque : le prototype le prouve (32 ko, zéro dépendance). C'est aussi ce qui se dégrade le mieux et ce qui coûte le moins en JavaScript.
- **Motion** (`motion`, anciennement Framer Motion, environ 15 à 35 ko selon les fonctions importées — ordre de grandeur à confirmer au bundle) : pour ce que le CSS fait mal dans React. Ressorts physiques, animation de sortie d'un élément qui disparaît, réordonnancement de liste (`layout`), gestes. **C'est la bibliothèque à apprendre en premier.**
- **View Transitions** : intégrées à React et Next 16. Vérifié dans `node_modules/next/dist/docs/01-app/02-guides/view-transitions.md` : il faut `experimental: { viewTransition: true }` dans `next.config.ts`, le drapeau est marqué **expérimental**, et la documentation prévient que certaines animations se comportent différemment dans Safari. Sans prise en charge, la page marche, sans animation. Risque acceptable pour un embellissement.
- **GSAP + ScrollTrigger** (gratuit, d'après le bandeau de gsap.com consulté le 16 novembre) : seulement si le récit au défilement dépasse ce que `sticky` + 30 lignes de JS savent faire (plusieurs graphiques synchronisés, épinglages imbriqués). À ne pas installer « au cas où » : environ 25 à 45 ko de plus.
- **Three.js via React Three Fiber** (`three`, `@react-three/fiber`, `@react-three/drei`) : uniquement pour la scène du graphe en version 3D ou le fond en shader, **chargé à la demande** (`next/dynamic` avec `ssr: false`), jamais dans le socle commun. Three.js pèse environ 150 à 170 ko compressé.
- **Rive / Lottie** : écartés pour l'instant. Ils servent à jouer des animations dessinées par un illustrateur dans un outil dédié. Nous n'avons ni illustrateur ni besoin de personnage animé. À reconsidérer pour un logo animé.
- **Spline** : écarté. Scène 3D dessinée dans un outil tiers puis intégrée : lourd, dépendant d'un service, et contraire au but « le faire soi-même ».
- **Lenis** (défilement adouci) : écarté par défaut. Il modifie le défilement natif, ce qui gêne certains utilisateurs et complique `position: sticky`. Le défilement natif suffit.

### Règles `prefers-reduced-motion`

Le réglage système « réduire les animations » est respecté ainsi (déjà appliqué dans le prototype, vérifié : 0 animation en cours, titre visible, graphique dans son état final — capture `prototype-desktop-4-mouvement-reduit.png`) :

1. Tout contenu est **visible sans animation** : l'état initial « caché » n'existe que si le mouvement est autorisé.
2. Les déplacements, rotations, zooms et parallaxes sont **supprimés**. Les fondus courts (150 ms) peuvent rester.
3. Les récits au défilement deviennent des **sections statiques empilées**, graphique dans son état final.
4. Les boucles infinies (braises, pulsation, constellation) sont **arrêtées**.
5. Aucune information n'existe **seulement** dans une animation.
6. Les `canvas` animés se mettent en pause hors écran (`IntersectionObserver`) et quand l'onglet est caché.

Trois autres règles de tenue :
- N'animer que `transform` et `opacity` (pas de `width`, `top`, `box-shadow` en boucle) pour rester à 60 images par seconde.
- Jamais d'animation qui retarde l'accès à l'information dans un outil : les listes s'affichent, puis s'embellissent.
- Une animation d'entrée ne se rejoue pas quand on revient sur la page.

## 6. Imagerie : exploiter les cartes

Les images sont le capital visuel inutilisé du projet (13 797 cartes avec `image_url` et `image_url_small`).

| Composition | Où | Détail |
|---|---|---|
| **Éventail 3D** | Hero | Cinq cartes choisies par la donnée du jour (signal n° 1 au centre). Prototype fait. |
| **Carte holographique** | Carte vedette boutique, panneau d'aperçu, page carte | Inclinaison au pointeur + dégradé en `mix-blend-mode: color-dodge`. Prototype fait. |
| **Bandeau d'archétype** | Tier list, évolution, prédictions, page d'archétype | Recadrage dans l'illustration (zone de l'œuvre, environ 12 % à 60 % de la hauteur), dégradé vers `--ink`. |
| **Pastilles de cartes clés** | Lignes de tier list et de boutique | Rond de 28 px recadré sur l'illustration, comme HSReplay. |
| **Mur de cartes en perspective** | Section « 13 797 cartes suivies », page 404 | Grille inclinée en CSS 3D, défilement lent, masque en dégradé. |
| **Pile de deck** | Page d'archétype | Cartes empilées avec décalage ; au survol, la pile s'étale. |
| **Graphe avec visages** | `/graph` | Les nœuds importants affichent l'illustration recadrée en rond. Voir section 7. |
| **Image de partage** | Chaque page | Image Open Graph générée (`opengraph-image.tsx`) : titre + carte + chiffre. Indispensable pour Discord et les réseaux, où se trouve le public. |

Conditions techniques :
- **Servir les images nous-mêmes.** Aujourd'hui elles viennent de `images.ygoprodeck.com`, en 268 × 391 px même pour une vignette de 34 px. Passer par `next/image` (formats AVIF/WebP, tailles adaptées, `remotePatterns` à déclarer) ou, mieux, pré-générer trois tailles (60, 268, 600 px de large) au build et les héberger avec le site. Cela supprime 39 requêtes vers un tiers et une dépendance en production.
- Toujours des **dimensions réservées** (`width`/`height` ou `aspect-ratio: 59/86`) pour garder le CLS à 0.
- `loading="lazy"` hors du premier écran ; `fetchpriority="high"` pour la carte centrale du hero.
- Un **repli dessiné** (dos de carte + nom) pour les quelque 19 cartes sans image.
- Texte alternatif : nom de la carte si elle porte l'information, vide si elle est décorative.

## 7. Dataviz

### Principes communs

1. **Un graphique répond à une question écrite au-dessus de lui.** Le titre est la conclusion (« Kewl Tune a percé au Japon trois mois avant »), pas le nom de la mesure.
2. **Étiquettes directes** au bout des lignes, pas de légende à part.
3. **Axes ajustés aux données** (corrige `/evolution`, vide à 85 %).
4. **Annotations d'événements** : dates de banlist (table `banlist_history`), sorties de sets.
5. **Incertitude montrée** quand on prédit : une bande, pas seulement un point.
6. **Pied de données** sous chaque graphique : source, date, taille d'échantillon, lien « comment c'est calculé ».
7. **Équivalent tabulaire** accessible (`<details>` avec un tableau) pour chaque graphique.
8. Deux séries maximum en couleur (`--signal`, `--ocg`), le reste en gris.

### Graphiques de méta

| Page | Aujourd'hui | Cible |
|---|---|---|
| `/evolution` | Lignes, axe 0-100, 3 gris indistincts | **Graphique de rangs** (« bump chart ») des 10 premiers archétypes, ou aires empilées de part de méta ; survol qui isole une série ; bandes verticales aux dates de banlist ; bascule OCG / TCG / superposé avec décalage réglable. |
| `/predictions` | 45 lignes × 2 barres | **Haltères** (point actuel → point prévu) triés par écart, top 5 hausses et baisses mis en avant, le reste replié ; intervalle d'incertitude. |
| Tier list | Barre de score | Mini-courbe 6 mois + part de méta en chiffre ; une seule mesure par barre. |
| Ban Radar | Barre empilée en 6 opacités | Barre empilée en palette catégorielle, légende intégrée, détail des critères au survol et au toucher. |
| Boutique | Tableau | Mini-courbe de prix par carte, courbe OCG de l'archétype en tête de groupe. |

Bibliothèque : remplacer **recharts** (340 ko décompressés pour un graphique) par des **composants SVG maison** s'appuyant sur les modules de calcul de D3 (`d3-scale`, `d3-shape`, `d3-array` : quelques dizaines de ko) ou sur **visx**. Raisons : contrôle total du style et de l'animation, rendu possible côté serveur (le graphique est dans le HTML, donc visible sans JavaScript et indexable), et c'est **la compétence dataviz la plus formatrice pour un data scientist**. Observable Plot est une alternative plus rapide à écrire, moins personnalisable.

### Graphe de synergies : refonte

Problème mesuré : amas isolés, sans étiquette, sans couleur, sans ponts, illisible sans survol, inaccessible.

Cible en trois niveaux de lecture :
1. **Vue d'ensemble : la carte du ciel.** Un nœud par **archétype** (environ 60), taille = part de méta, couleur = tier, position stable d'une visite à l'autre (calculée une fois par le pipeline, pas à chaque chargement). Les liens entre archétypes sont les **cartes pont**, en orange. On lit enfin ce que le site promet : qui est relié à qui, et par quoi.
2. **Zoom sémantique.** En zoomant sur un archétype, il s'ouvre en ses cartes ; les plus centrales montrent leur illustration en rond. Étiquettes toujours visibles pour les nœuds importants.
3. **Fiche.** Clic sur une carte : panneau latéral (image, centralité, archétypes reliés, risque de ban, bouton « simuler son ban »). Le simulateur se joue **dans le graphe** : la carte s'éteint, les liens tombent, les amas se séparent. C'est la démonstration la plus forte du produit et elle n'existe pas encore visuellement.

Technique :
- **Positions précalculées** côté Python (le pipeline a déjà NetworkX : `spring_layout` ou ForceAtlas2, graines fixes), stockées en base et servies par l'API. Avantages : affichage instantané, plus de 110 ms de blocage, mise en page identique pour tous, capturable pour les images de partage.
- Rendu : **Sigma.js** (WebGL, conçu pour les graphes, images dans les nœuds) ou **PixiJS**, ou `canvas` 2D maison pour 200 à 700 nœuds. Three.js seulement si on veut la version 3D « galaxie » (option, voir formulaire).
- Abaisser ou adapter le seuil de Jaccard pour faire réapparaître les ponts, ou tracer les ponts depuis `card_graph_metrics` : **décision de données, à valider avec l'agent data-scientist**.
- Accessibilité : liste triable équivalente (archétype, cartes pont, voisins), navigation clavier entre nœuds, résumé textuel généré.

## 8. Technique

### Pile recommandée

**On reste sur Next.js 16.2 / React 19 / Tailwind 4.** Aucune rupture n'est justifiée : le rendu serveur, la génération statique et le cache donnent déjà d'excellents chiffres (LCP inférieur à 100 ms en local). Changer de cadre (Astro, SvelteKit) coûterait des semaines sans gain visible.

| Besoin | Choix | Remarque |
|---|---|---|
| Animation | CSS, puis `motion` | GSAP seulement si nécessaire |
| Transitions de page | `<ViewTransition>` de React + `experimental.viewTransition` | Expérimental dans Next 16 : relire la doc locale avant d'activer |
| Graphiques | SVG maison + `d3-scale`, `d3-shape` | Remplace recharts |
| Graphe | Sigma.js ou PixiJS, positions précalculées | Remplace vis-network |
| 3D (option) | `three`, `@react-three/fiber`, `@react-three/drei` | Chargé à la demande uniquement |
| Images | `next/image` ou tailles pré-générées | Voir section 6 |
| États | `loading.tsx`, `error.tsx`, `not-found.tsx`, `<Suspense>` par bloc | Absents aujourd'hui |
| SEO | `generateMetadata` par page, `opengraph-image.tsx`, `sitemap.ts`, `robots.ts`, données structurées | Absents aujourd'hui |
| Tests visuels | Playwright (déjà dans `.venv`) : captures de référence par page et par largeur | Voir plus bas |
| Accessibilité | `@axe-core/playwright` | À installer (dépendance de développement) |
| Performance | Lighthouse CI, ou `unlighthouse` | À installer ; Lighthouse est absent de la machine |

Préalables hors design (bloquants, voir audit) : fusionner TOK-83 (API à 6 s), corriger le 500 de `/early-signals`, ajouter un repli quand l'API ne répond pas au build.

### Budget de performance

Mesuré sur un profil mobile moyen (Lighthouse mobile : processeur ralenti 4 fois, réseau 4G lent). Les valeurs actuelles viennent de l'audit, en local.

| Indicateur | Aujourd'hui | Budget cible |
|---|---|---|
| LCP accueil | 84 ms en local (texte) | **≤ 2,0 s** en profil mobile (le LCP deviendra une image de carte : `fetchpriority="high"`, AVIF, dimensions réservées) |
| CLS | 0 | **≤ 0,02** |
| INP | non mesurable sans utilisateurs ; sondes de 9 à 46 ms | **≤ 200 ms**, à suivre avec la bibliothèque `web-vitals` en production |
| Temps de blocage (TBT) | 0 ms, sauf `/graph` 110 ms | **≤ 150 ms** partout |
| JavaScript transféré, accueil | ≈ 165 ko | **≤ 220 ko** (soit environ 55 ko de marge pour Motion et le hero) |
| JavaScript transféré, pages outils | ≈ 165 ko (+100 ko `/evolution`, +147 ko `/graph`) | **≤ 200 ko** hors graphe ; graphe ≤ 320 ko, chargé à la demande |
| Poids total accueil, premier écran | ≈ 290 ko | **≤ 700 ko** images comprises ; scène 3D éventuelle hors budget, chargée après interaction ou inactivité |
| Polices | 90 ko, 3 familles | ≤ 120 ko |
| Temps de réponse API | 6 s sur 3 routes | **≤ 100 ms** au 95ᵉ centile |
| Score Lighthouse (mobile) | non mesuré | Performance ≥ 90, Accessibilité ≥ 95, Bonnes pratiques ≥ 95, SEO = 100 |
| Images par seconde des animations | sans objet | ≥ 55 sur un portable de milieu de gamme |

### Accessibilité (WCAG 2.2 AA)

- Contrastes : 100 % des textes ≥ 4,5:1 (3:1 pour le grand texte et les contours de champ). Trois corrections identifiées dans l'audit.
- Clavier : tout est atteignable et utilisable, focus toujours visible (déjà bien), lien d'évitement, ordre logique.
- Structure : un `h1`, des `h2` par section, repères `main` / `nav` / `footer`.
- Mouvement : règles de la section 5.
- `canvas` et graphiques : alternative textuelle systématique.
- Cibles tactiles ≥ 24 px (norme), 44 px visés sur mobile.
- Langue : tout en français, termes anglais du jeu balisés `lang="en"`.
- Contrôle automatique : axe sur chaque page dans les tests, zéro violation « sérieuse » ou « critique ».

### SEO

Titre et description uniques par page, en français ; Open Graph et image de partage ; `sitemap.xml` ; données structurées (`Dataset`, `BreadcrumbList`) ; pages d'archétype et de carte en génération statique (des centaines de pages d'entrée depuis les moteurs : « Kewl Tune meta », « Ash Blossom ban ») ; URL lisibles (`/archetype/kewl-tune`).

### Tests visuels

Le script d'audit de cette mission est une base réutilisable. Cible : un test Playwright qui capture chaque page à 375, 768 et 1440 px, avec le mouvement réduit activé pour des images stables, et compare aux références (`toHaveScreenshot`). Toute modification de style produit un diff d'images à relire avant validation : c'est le garde-fou qui rend la règle « Thomas valide sur capture » automatique.

## 9. Besoins

### Outils et bibliothèques

| Besoin | Outil | Coût |
|---|---|---|
| Animation React | `motion` | Gratuit (licence MIT) |
| Récit au défilement avancé | `gsap` + ScrollTrigger | Gratuit d'après gsap.com (à relire dans leur licence avant usage commercial) |
| Calcul de graphiques | `d3-scale`, `d3-shape`, `d3-array` ou `@visx/*` | Gratuit |
| Graphe | `sigma` + `graphology`, ou `pixi.js` | Gratuit |
| 3D (option) | `three`, `@react-three/fiber`, `@react-three/drei` | Gratuit |
| Mesure | Lighthouse (dans Chrome), `web-vitals`, `@axe-core/playwright` | Gratuit |
| Maquettes | Figma (offre gratuite suffisante) ou directement le code | 0 € |
| Débogage d'animation | Panneau « Animations » et « Performance » de Chrome | Gratuit |
| Hébergement des images | Vercel (optimisation d'images incluse avec quota) ou fichiers statiques pré-générés | 0 à 20 $/mois, à vérifier selon l'offre choisie pour TOK-35 |
| Police | Inter Tight variable, Instrument Serif, JetBrains Mono (Google Fonts) | Gratuit |
| Option : police de titrage payante pour se distinguer | Fonderie indépendante | Environ 50 à 300 € en licence web (ordre de grandeur, non vérifié) |

**Aucun abonnement n'est nécessaire** pour atteindre la cible de l'option B. Le budget est du temps.

### Assets à produire

- Trois tailles d'images par carte (script de build).
- Recadrage « bandeau » par archétype (automatique, avec une table de corrections manuelles pour les 20 principaux).
- Logo vectoriel propre et favicon (le glyphe actuel est un `clip-path` CSS).
- Images de partage générées.
- Positions du graphe précalculées (pipeline Python).
- Textes : section méthode, pied de page, pages d'erreur, descriptions par page.

### Compétences à acquérir, avec ressources

Ressources citées de mémoire : elles existent à ma connaissance, mais **je n'ai pas vérifié leurs URL ni leur contenu aujourd'hui**. À vérifier avant de s'y engager.

| Compétence | Pourquoi | Ressource | Temps d'apprentissage |
|---|---|---|---|
| **Transitions et animations CSS** (`transform`, `opacity`, `@keyframes`, courbes d'accélération, `animation-delay`) | 70 % du rendu visé | MDN « Using CSS animations » ; web.dev « Learn CSS », chapitres animations | 3 à 5 jours |
| **Principes de mouvement d'interface** (durées, accélérations, hiérarchie, retenue) | Savoir quoi animer, pas seulement comment | Les « 12 principes d'animation » appliqués à l'interface ; cours « Animations on the Web » d'Emil Kowalski (payant) ; guide Material Design « Motion » | 1 semaine, en parallèle |
| **Motion pour React** | Ressorts, sorties, listes réordonnées | Documentation motion.dev | 1 semaine |
| **View Transitions** | Transitions de page | Guide local `node_modules/next/dist/docs/01-app/02-guides/view-transitions.md` ; MDN « View Transition API » | 2 à 3 jours |
| **CSS 3D** (`perspective`, `preserve-3d`, `rotate3d`) | Éventail, carte inclinable, mur de cartes | MDN « Using CSS transforms » ; lire le code du prototype | 2 à 3 jours |
| **SVG et D3 pour la dataviz** | Graphiques maison | « D3 in Depth » ; documentation d'Observable ; livre « Fullstack D3 » d'Amelia Wattenberger | 2 semaines |
| **Conception de graphiques** (choix de la forme, annotation, couleur) | Très utile aussi pour le bootcamp | « Fundamentals of Data Visualization » de Claus Wilke (gratuit en ligne) ; « Storytelling with Data » de Cole Knaflic | 1 semaine de lecture |
| **Performance web** (Web Vitals, chargement différé, images) | Tenir le budget | web.dev « Learn Performance » et « Core Web Vitals » | 3 jours |
| **Accessibilité** | WCAG AA | web.dev « Learn Accessibility » ; liste de contrôle de l'A11Y Project | 3 jours |
| **Three.js et React Three Fiber** (option) | Graphe 3D, fond en shader | Cours « Three.js Journey » de Bruno Simon (payant, environ 95 $ à ma connaissance) ; documentation R3F | 4 à 6 semaines |
| **Shaders GLSL** (option) | Fond animé type Stripe | « The Book of Shaders » (gratuit) | 2 à 3 semaines |
| **Typographie et mise en page** | Affiner l'œil | « Practical Typography » de Matthew Butterick (en ligne) ; « Refactoring UI » d'Adam Wathan et Steve Schoger | 1 semaine de lecture |

### Temps par chantier

Estimations pour Thomas travaillant avec un assistant de code, apprentissage compris. Fourchettes larges : c'est un premier projet de ce type.

| Chantier | Temps |
|---|---|
| 0. Préalables (API, build, états de chargement et d'erreur, 404) | 1 à 2 jours |
| 1. Corrections sans débat (axes, contrastes, langue, barre de tier list, SEO de base) | 1 à 2 jours |
| 2. Images partout (`CardArt`, radar, boutique, signaux, bandeaux d'archétype) | 3 à 5 jours |
| 3. Socle de mouvement (tokens, `Reveal`, ouverture, micro-interactions, mouvement réduit) | 4 à 6 jours |
| 4. Nouvelle page d'accueil (hero, preuve, outils, méthode, pied de page) | 2 à 3 semaines |
| 5. Dataviz maison (évolution, prédictions, mini-courbes, radar) | 2 à 3 semaines |
| 6. Page d'archétype + transitions de vue | 1 à 2 semaines |
| 7. Graphe de synergies (positions précalculées, niveaux de zoom, simulateur intégré) | 3 à 4 semaines |
| 8. Qualité (tests visuels, axe, Lighthouse, budget) | 1 semaine, puis continu |
| 9. Option 3D (graphe en galaxie ou fond en shader) | 4 à 8 semaines, apprentissage compris |
| **Total option B sans la 3D** | **environ 11 à 16 semaines à temps partiel soutenu** |

Avec le bootcamp qui se termine en décembre 2026, un calendrier réaliste est : chantiers 0 à 3 avant la fin du bootcamp (le site devient présentable), chantiers 4 à 8 de janvier à mars 2027.

## 10. Feuille de route

Chaque étape est livrable seule et a un critère mesurable.

### Jour 1 — Gains rapides (aucune décision de design requise)

| Action | Critère de réussite |
|---|---|
| Fusionner TOK-83 dans `main` | `GET /ban-radar`, `/card-impact`, `/graph/synergies` ≤ 100 ms ; `/ban` à froid ≤ 500 ms |
| Corriger le 500 de `/early-signals` | `next build` passe sur `main` |
| `loading.tsx`, `error.tsx`, `not-found.tsx` aux couleurs du site ; redirection `/ban-simulator` → `/ban?tab=simulateur` | Plus aucun écran blanc ; 404 en français sur fond `--ink` |
| `/evolution` : axes ajustés aux données | La courbe occupe plus de 60 % de la hauteur du graphique (capture avant/après) |
| `--faint` corrigé, texte de la tuile orange à 100 % | 0 échec de contraste dans le script d'audit, sur toutes les pages |
| Vignettes de cartes dans le Ban Radar (le champ existe déjà) | 50 images sur `/ban`, CLS toujours à 0 |
| Titre et description par page, en français | 9 titres distincts |
| Tout en français (`Declining` → « En baisse », etc.) | 0 terme anglais d'interface dans les captures |

### Semaine 1 — Le site prend un visage

| Action | Critère de réussite |
|---|---|
| Composant `CardArt` + images sur boutique, signaux, accueil ; bandeaux d'archétype sur la tier list | Au moins une image de carte visible au premier écran de 8 pages sur 9 (1 sur 9 aujourd'hui) |
| Images servies en tailles adaptées | Aucune image plus de 2 fois plus grande que son affichage ; 0 requête vers `images.ygoprodeck.com` si l'hébergement propre est retenu |
| Tokens de mouvement, `Reveal`, ouverture de page, micro-interactions | `document.getAnimations()` > 0 à l'arrivée sur chaque page ; = 0 avec le mouvement réduit |
| Mono ramené aux chiffres et labels | Moins de 40 % de caractères en mono par page (mesure du script) |
| Tier list : une seule mesure par barre ; accent rationné dans les tableaux | Au plus une colonne orange par tableau |
| Lighthouse installé, première mesure | Rapport de référence archivé pour les 9 pages |

### Mois 1 — La vitrine

| Action | Critère de réussite |
|---|---|
| Nouvelle page d'accueil d'après le prototype (hero, preuve au défilement, outils, méthode, pied de page) | Hauteur de page ≥ 4 écrans ; LCP mobile ≤ 2,0 s ; JavaScript transféré ≤ 220 ko ; Lighthouse Performance ≥ 90 et Accessibilité ≥ 95 |
| Open Graph + images de partage + sitemap | Aperçu correct en collant un lien dans Discord ; Lighthouse SEO = 100 |
| `/evolution` et `/predictions` en SVG maison | recharts supprimé ; JavaScript de `/evolution` ≤ 200 ko transférés |
| Pied de données sous chaque visualisation | Source et date visibles sur 100 % des graphiques et tableaux |
| Tests visuels Playwright sur 9 pages × 3 largeurs | Suite verte ; un changement de style produit un diff d'images |

### Mois 2 à 3 — La profondeur

| Action | Critère de réussite |
|---|---|
| Page d'archétype + transitions de vue depuis la tier list | Transition fluide dans Chrome et Safari, navigation correcte sans prise en charge |
| Graphe de synergies refondu (positions précalculées, zoom sémantique, simulateur intégré) | Étiquettes lisibles sans survol ; temps de blocage ≤ 150 ms ; alternative tabulaire présente ; vis-network supprimé |
| Boutique regroupée par archétype avec courbes de prix | Test avec 3 gérants de boutique : chacun sait dire quoi commander en moins d'une minute |
| Suivi des Web Vitals réels (`web-vitals`) | INP au 75ᵉ centile ≤ 200 ms sur un mois |

### Option, après le mois 3 — La 3D véritable

Graphe en galaxie 3D ou fond en shader, **si** les étapes précédentes tiennent le budget et que l'envie est toujours là. Critère : chargé à la demande, 0 octet ajouté au premier écran, repli 2D sans WebGL.

## 11. Prototype

- Fichier : `docs/audit-front/prototype/index.html` (32 ko, un seul fichier, aucune bibliothèque, aucun build). S'ouvre par double-clic.
- Il charge les polices depuis Google Fonts et neuf images de cartes depuis `images.ygoprodeck.com`, comme le site actuel. Hors connexion, les cartes affichent un repli dessiné avec leur nom.
- Données réelles relevées le 16 novembre 2026 (parts de méta mensuelles de Kewl Tune, top du Ban Radar « pièces d'archétype », premier signal boutique). La constellation du graphe est une **illustration**, signalée comme telle dans le pied de page.
- Vérifié : desktop 1440 px et mobile 375 px sans défilement horizontal, aucune erreur de console, mouvement réduit respecté.
- **Non vérifié** : Safari et Firefox (seul Chromium a été testé) ; lecteur d'écran réel ; fluidité sur un téléphone d'entrée de gamme.
- Ce qu'il n'est pas : une page du site. Il n'utilise ni React ni Tailwind ; le portage en composants reste à faire (chantier 4).
- Écart assumé avec Ember : la barre du radar y utilise quatre couleurs dont `--warn`, que le design system réserve aux restrictions de banlist. La palette catégorielle définitive reste à valider (formulaire, décision 6).

## 12. Risques et alternatives écartées

| Risque | Probabilité | Parade |
|---|---|---|
| **Sur-animation** : le site devient fatigant, les outils ralentissent | élevée | Règle « vitrine expressive, outils sobres » ; durées plafonnées ; revue à la troisième visite. |
| **Le fond prime la forme** : embellir des chiffres contradictoires (Elfnote « mars 2027 » déjà à 20 % en TCG, Ash Blossom à 100) | élevée | Traiter les incohérences de l'audit **avant** la vitrine. Une belle page qui affiche un chiffre faux fait plus de dégâts qu'une page terne. |
| Dérive du budget de performance avec Motion, D3, Sigma, Three | moyenne | Budget chiffré et contrôlé en test ; chargement à la demande ; une bibliothèque n'entre que si elle remplace quelque chose. |
| `viewTransition` expérimental : comportement différent selon les navigateurs, API qui change | moyenne | Embellissement uniquement ; le site marche sans. Relire la doc locale à chaque montée de version de Next. |
| Dépendance aux images d'un tiers | moyenne | Héberger les tailles pré-générées. |
| Charge d'apprentissage en plein bootcamp | élevée | Chantiers 0 à 3 seulement d'ici décembre ; la 3D est explicitement optionnelle. |
| Conflit avec la branche `claude/front-vitrine-*` (chiffres et textes) | moyenne | Attendre sa fusion avant de toucher à l'accueil ; la proposition ne modifie pas `site-facts.ts`. |
| Mobile : effets 3D coûteux, pas de survol | moyenne | Éventail simplifié et statique sous 760 px ; aucune information au survol seul. |

| Alternative écartée | Pourquoi |
|---|---|
| Constructeur sans code (Framer, Webflow, Dora) | Contraire au but ; ne sait pas servir neuf pages de données ; dépendance et abonnement. |
| Tout refaire dans un autre cadre (Astro, SvelteKit) | Aucun gain mesurable ; Next 16 donne déjà d'excellents chiffres. |
| Site entièrement en WebGL (option C) | Poids, accessibilité, SEO, temps. |
| Scène Spline intégrée dans le hero | Plusieurs mégaoctets pour un effet que le CSS 3D obtient en 32 ko. |
| Thème clair | Double le coût de test ; pas de demande. |
| Défilement adouci (Lenis) | Altère un comportement natif pour un gain discutable. |
| Rive ou Lottie | Pas d'illustrateur, pas de besoin. |
| Garder recharts et vis-network en les restylant | 490 ko de JavaScript pour un résultat qu'on ne peut ni animer finement ni rendre côté serveur. |
| Acheter un modèle de site | Uniformité, et rien appris. |
