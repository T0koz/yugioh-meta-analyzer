# Étape 2 — Benchmark

Date de consultation de toutes les références : **2026-11-16**, depuis un navigateur Chromium sans interface (Playwright), fenêtre 1440 × 900, langue `fr-FR`. Pour chaque site : une capture à l'arrivée (`captures/bench/<nom>-1-fold.png`), une après 1 400 px de défilement (`-2-scroll.png`), et un relevé automatique. Planches récapitulatives : `captures/bench/_planche-A.jpg`, `_planche-B.jpg`, `_planche-C.jpg`, `_planche-D.jpg`, `_planche-B-scroll.jpg`. **Ces captures restent locales : ne pas les commiter ni les publier.**

## Ce qui est vérifié et ce qui ne l'est pas

- **VÉRIFIÉ** : ce que montrent les captures ; la présence d'un `canvas` WebGL actif ; le nombre d'animations en cours (`document.getAnimations()`) ; les polices calculées ; la taille du `h1` ; le marqueur `/_next/` (Next.js) ; les poids par type quand le serveur les expose.
- **INDICE, pas preuve** : la détection de bibliothèques (GSAP, Three.js…) se fait en cherchant leur nom dans les scripts et le HTML. Les sites modernes regroupent leur code dans des fichiers aux noms illisibles : une bibliothèque peut être présente sans être détectée, et un mot peut correspondre par hasard. Je note « indice » quand c'est le cas.
- **Aucun consentement donné, aucun clic, aucun formulaire, aucun compte.** Plusieurs captures montrent donc la bannière de cookies par-dessus la page.
- **Sites que je n'ai pas pu ouvrir** (je ne contourne pas) : `fbref.com` (403, vérification anti-robot), `cardmarket.com/fr/YuGiOh` (403, idem), `awwwards.com/websites/sites_of_the_year/` (403), `dora.run` (le nom de domaine ne répond pas : `ERR_NAME_NOT_RESOLVED`, avec et sans `www`), `poke-holo.simey.me` (certificat invalide). Rien n'est affirmé sur leur apparence actuelle.
- Les mesures de LCP sont prises une fois, sans cache, sur ma connexion : elles donnent un ordre de grandeur, pas un classement.

## Famille A — Produits de données grand public

| Référence | URL | Ce qui est excellent | Comment c'est fait (observé) | Transposable chez nous |
|---|---|---|---|---|
| **TradingView** | tradingview.com/markets/ | Un graphique en tête de page avant tout texte ; chaque indice a sa pastille, sa valeur, sa variation colorée. La donnée **est** le visuel. | 63 `canvas` 2D (leurs propres graphiques), 213 SVG, `h1` 56 px. Fond blanc. | Mettre un vrai graphique dans le hero. Mini-courbes (sparklines) dans chaque ligne de liste. Variation en couleur + signe. |
| **The Pudding** | pudding.cool | Chaque article est une histoire visuelle : la vignette est déjà une dataviz. Typographie de caractère (Gooper, Atlas Typewriter). | Svelte (marqueur `_app/immutable`). 3,9 Mo dont 3,4 Mo d'images. Pas de WebGL. | Le « scrollytelling » : un graphique fixe à l'écran, le texte défile et fait évoluer le graphique. C'est le format idéal pour « le TCG suit l'OCG ». |
| **Our World in Data** | ourworldindata.org | Crédibilité : source, date et licence sous chaque graphique ; recherche en tête ; compteurs (« 14 029 charts »). | React, graphiques SVG maison (122 SVG). Serif Playfair pour les titres. | Bandeau « source · date de mise à jour · méthode » sous chaque visualisation. C'est ce qui nous manque le plus en crédibilité. |
| **OP.GG** | op.gg | La recherche est l'action n° 1, au centre. Visuels de jeu partout (champions). | Next.js. 127 images, 19 animations en cours. LCP 1,7 s, CLS 0,09 (publicités). | Recherche de carte centrale et visible. L'illustration du jeu comme langage visuel. |
| **HSReplay** | hsreplay.net/meta/ | Tier list ultra dense : lettre de tier en bloc coloré, taux de victoire, nombre de parties, cartes clés en pastilles rondes. | React. CLS 0,17, LCP 4,5 s : alourdi par la publicité. | Les « cartes clés en pastilles » dans chaque ligne d'archétype. À ne pas copier : l'encombrement publicitaire. |
| **Polymarket** | polymarket.com | Chaque marché est une carte avec probabilité en gros et courbe ; onglets par thème ; chiffres en mono tabulaire. | Next.js, 6 `canvas`, 21 animations en cours. 3,2 Mo dont 2,8 Mo de JavaScript. | Présenter une prédiction comme une « cote » avec historique. Très proche de notre Ban Radar. |
| **Observable Plot** | observablehq.com/plot | Hero composé d'une mosaïque d'une trentaine de petits graphiques : la variété des formes fait le spectacle. | Site de documentation léger (263 ko). SVG. | Montre qu'un mur de mini-graphiques bien dessinés vaut une scène 3D. Plot est aussi une bibliothèque candidate pour nos graphiques. |
| *FBref* | fbref.com | Non consulté (403). | | |

**Ce que la famille A enseigne** : les meilleurs produits de données ne décorent pas, ils montrent la donnée en grand, tout de suite, avec sa source. Aucun n'utilise de 3D.

## Famille B — Vitrines de référence

| Référence | URL | Ce qui est excellent | Comment c'est fait (observé) | Transposable chez nous |
|---|---|---|---|---|
| **Linear** | linear.app | Hero sombre, titre 64 px en graisse 510, interlettrage -1,4 px ; juste en dessous, **le vrai produit**, pas une illustration. 83 animations en cours à l'arrivée. | Next.js. Inter Variable + Berkeley Mono. Aucun WebGL : tout est DOM et CSS. Fond `rgb(8,9,10)`. | La preuve qu'on atteint le haut du panier **sans 3D**. Notre système Ember est de la même famille. Montrer l'outil réel dans le hero. |
| **Vercel** | vercel.com | Un seul objet (le triangle) animé au centre, énormément de vide, bandeau de logos clients. `h1` 64 px, interlettrage -3,84 px. | Next.js, 1 `canvas` 2D. Geist Sans et Mono. LCP 0,65 s. | Un objet-signature animé plutôt que dix effets. La preuve sociale sous le hero. |
| **Stripe** | stripe.com | Le ruban de couleur en mouvement derrière le titre ; un compteur vivant en tête (« Global GDP running on Stripe ») ; page de 15 000 px qui déroule un récit. | Next.js, **1 `canvas` WebGL** (le ruban est un shader). Police Söhne variable, graisse 300. 1,4 Mo. | Un fond animé par shader, léger, derrière le titre. Le compteur vivant : nous avons « decklists analysées ». |
| **Apple iPhone** | apple.com/iphone/ | Le produit photographié en très grand, des sections qui s'enchaînent au défilement, typographie 80 px. | Pas de WebGL à l'arrivée ; images et vidéos, animations pilotées par le défilement (12 en cours). 16 000 px de haut. | Traiter la carte comme Apple traite le téléphone : en grand, seule, éclairée. |
| **Igloo Inc** | igloo.inc | Expérience 3D plein écran (capture prise pendant l'écran de chargement). | **9 Mo dont 8 Mo de fichiers 3D**, 30 nœuds DOM seulement : tout est dans le `canvas`. Indice Three.js. | **Contre-exemple pour nous** : spectaculaire, mais aucun texte dans la page (SEO et accessibilité nuls), et 9 Mo à charger. Connu comme site primé, non vérifié aujourd'hui (Awwwards en 403). |
| **Lusion** | lusion.co | Scène 3D d'objets qui flottent dans un cadre incliné ; transitions de page fluides. | Astro + WebGL (indice Three.js), 500 ko à l'arrivée. Police Aeonik. | Le cadre incliné qui « ouvre une fenêtre » sur une scène. Montre qu'une scène 3D peut rester légère si elle est procédurale. |
| **Resend** | resend.com | Hero sombre, titre en **serif** 96 px, cube 3D sombre qui tourne à droite. Très proche de notre registre. | Next.js + Tailwind, 1 `canvas` WebGL, 5 vidéos. 4,5 Mo au total. | Le modèle le plus direct : serif + sombre + un objet 3D à droite. Chez nous l'objet est tout trouvé : une carte. |
| **Raycast** | raycast.com | Fond de bandes rouges lumineuses en 3D derrière le titre, 42 animations en cours. | Next.js + Tailwind, 1 `canvas` WebGL. Inter. | Un fond lumineux dans la couleur d'accent : exactement ce que « Ember » appelle. |
| **GSAP** | gsap.com | Typographie géante animée, formes qui traversent le titre. | La page charge 3,7 Mo de vidéo. | GSAP est gratuit pour tous depuis son rachat par Webflow (affiché en bandeau sur leur site le 2026-11-16). |
| **Motion** | motion.dev | Sphère de particules dorées en WebGL, titre sobre. | 579 ko. Se présente comme « anciennement Framer Motion ». | Bibliothèque candidate pour React. |
| *Awwwards* | awwwards.com | Non consulté (403). | | |

**Ce que la famille B enseigne** : trois niveaux de mise en scène coexistent au sommet.
1. **DOM animé, sans 3D** (Linear, Vercel) : typographie, vrai produit, micro-animations nombreuses.
2. **Un seul élément WebGL** dans une page par ailleurs classique (Stripe, Resend, Raycast) : c'est le cas majoritaire.
3. **Tout en WebGL** (Igloo, Lusion) : réservé aux studios dont le site est la démonstration.

Un produit de données a intérêt à viser le niveau 2 sur la vitrine et le niveau 1 dans les outils.

## Famille C — La niche TCG

| Référence | URL | Ce qui est excellent | Comment c'est fait (observé) | Ce que les utilisateurs attendent |
|---|---|---|---|---|
| **Untapped.gg** | mtga.untapped.gg | Méta en temps réel : « dernière mise à jour », nombre de parties (2 700 000), classement de joueurs, popularité par couleur. | Next.js, 16 857 nœuds DOM, LCP 7,2 s, bannière de consentement et publicités. | Fraîcheur affichée et taille d'échantillon : deux chiffres que tout le monde regarde d'abord. |
| **Limitless TCG** | limitlesstcg.com/decks | Tableau de méta nu : rang, icônes, nom, points, part. Zéro décor. Référence de fait pour Pokémon. | Site classique, Open Sans, 785 ko. | La densité et la vitesse priment sur le style. |
| **Moxfield** | moxfield.com | Illustration de carte en fond plein écran, logo, **une barre de recherche**. Mode sombre. | React, Inter, 196 ko mesurés. | L'illustration du jeu comme décor ; la recherche comme porte d'entrée. |
| **EDHREC** | edhrec.com | « Commandant du jour » avec la carte en grand et ses prix ; classement hebdomadaire ; contenu éditorial. Annonce une refonte (« EDHREC has a new look! »). | Next.js, 426 images. | La carte en grand avec son prix à côté. Un rendez-vous quotidien. |
| **Scryfall** | scryfall.com | Une recherche, un éventail de cartes en bas d'écran. Rien d'autre. | Site léger (583 ko), 187 nœuds. | **L'éventail de cartes** comme signature visuelle : c'est exactement le motif du prototype. |
| **YGOPRODeck** | ygoprodeck.com | Top archétypes en vignettes illustrées, actualité des tournois. | 14 899 nœuds, 1 Mo de polices, bannière de consentement. | Les archétypes ont un visage (bandeau recadré dans l'illustration). |
| **Yu-Gi-Oh! Meta** | yugiohmeta.com/tier-list | Tier list avec bandeau illustré par archétype, effectif et pourcentage. | Svelte, fond bleu nuit, 14 452 nœuds. | **Notre concurrent direct et notre source.** Sa tier list du jour affiche Elfnote à 20,64 % : voir la remarque de crédibilité dans l'audit (`/boutique` annonce Elfnote en TCG pour mars 2027). |
| **MTGGoldfish** | mtggoldfish.com/metagame/standard | Chaque archétype : illustration, part de méta, **prix du deck**. | Site classique, LCP 6,5 s, publicités. | Le prix à côté de la part de méta : le pont entre joueurs et boutiques. |
| **Master Duel Meta** | masterduelmeta.com/tier-list | Même moteur que Yu-Gi-Oh! Meta, « power rankings » mis à jour automatiquement. | Svelte. | Idem. |
| *Cardmarket* | cardmarket.com | Non consulté (403). | | |

**Ce que la famille C enseigne** : la niche est **dense, illustrée, lente et encombrée de publicités**. Personne n'y a un design de niveau « vitrine ». Il y a donc une vraie place pour un site à la fois beau et rapide, à condition de respecter trois attentes : la carte visible, la fraîcheur des données affichée, et la densité des tableaux.

## Le phénomène « sites vectorisés / 3D / générés par outils »

### Ce que j'ai pu vérifier

- **Dora** : le domaine `dora.run` ne répond pas le 2026-11-16. Je n'ai donc **rien vu** du produit actuel. Des fiches tierces trouvées par recherche web le décrivent comme un constructeur de sites sans code, avec génération par prompt, objets 3D importables et animations au défilement, en version « alpha » ; elles ne sont pas datées de 2026 et se contredisent sur le prix. À prendre comme description historique, pas comme état actuel. Thomas parle d'une « extension » : je n'ai pas pu la consulter non plus.
- **Framer** (framer.com) : se présente comme constructeur de sites avec « agent de design ». Son propre site : 5,5 Mo dont 2,4 Mo de vidéo, React.
- **Spline** (spline.design) : outil de design 3D dans le navigateur, avec un champ « Demandez à Splin » en tête de page. 2 `canvas` WebGL.
- **Webflow** (webflow.com) : constructeur visuel ; indice GSAP (Webflow en est le propriétaire, d'après le bandeau du site GSAP).
- **Rive** (rive.app) : moteur d'animation vectorielle interactive. Sa page d'accueil : **31 `canvas` WebGL, 12,6 Mo** dont 9 Mo de vidéo.

### Ce que ces outils produisent réellement (analyse, à partir des exemples ci-dessus)

Les sites « de pub » que Thomas voit reposent presque tous sur la même recette, visible dans la famille B :
1. un **fond sombre** et une typographie très grande, très serrée ;
2. **un objet 3D ou un dégradé animé** dans le hero (une scène Spline intégrée, ou un shader) ;
3. des **apparitions au défilement** (fondu + glissement) sur chaque bloc ;
4. des **cartes en bento** aux bords lumineux qui suivent la souris ;
5. un **défilement adouci**.

C'est une grammaire d'une dizaine d'effets. Elle impressionne en dix secondes de publicité. Elle ne dit rien de la qualité du produit.

### Leurs limites pour un site comme le nôtre

| Limite | Pourquoi ça nous concerne |
|---|---|
| **Données dynamiques** | Ces outils fabriquent des pages de présentation. Brancher 9 pages sur une API, filtrer en SQL, dessiner un graphe de 200 nœuds : hors de leur périmètre, ou via des intégrations fragiles. |
| **Performance** | Une scène 3D intégrée pèse vite plusieurs mégaoctets (mesuré : Igloo 9 Mo, Rive 12,6 Mo, Framer 5,5 Mo, Resend 4,5 Mo). Notre accueil actuel pèse environ 290 ko transférés. |
| **Accessibilité** | Le contenu d'un `canvas` n'existe pas pour un lecteur d'écran. Igloo : 30 nœuds DOM, aucun titre. Les animations ignorent souvent le réglage « réduire les animations ». |
| **SEO** | Même cause : pas de texte dans la page, pas de structure. |
| **Uniformité** | Les modèles se ressemblent. L'effet « généré » est reconnaissable et se démode vite. |
| **Dépendance** | Hébergement, abonnement et format de fichier propriétaires. Thomas veut précisément l'inverse. |

### Ce qu'il faut pour obtenir le même rendu à la main

| Effet | Technique | Difficulté pour un débutant motivé |
|---|---|---|
| Apparitions au défilement | CSS + `IntersectionObserver`, ou Motion (`whileInView`) | Faible : 1 jour |
| Titre révélé mot par mot | CSS (`overflow: hidden` + `translateY`) | Faible : 2 heures |
| Bords lumineux qui suivent la souris | Une variable CSS mise à jour au `pointermove` + `radial-gradient` | Faible : 2 heures |
| Compteurs animés | `requestAnimationFrame` | Faible : 1 heure |
| Carte inclinable avec reflet holographique | CSS 3D (`perspective`, `rotateX/Y`) + dégradé en `mix-blend-mode` | Moyenne : 1 à 2 jours |
| Graphique piloté par le défilement | `position: sticky` + progression de défilement, ou GSAP ScrollTrigger | Moyenne : 2 à 3 jours |
| Transitions entre pages (une vignette qui devient un hero) | View Transitions (intégrées à React et Next 16, option expérimentale) | Moyenne : 2 jours |
| Fond animé par shader | Un `canvas` WebGL plein écran et un fragment shader (GLSL) | Élevée : 1 à 2 semaines d'apprentissage |
| Scène 3D avec cartes texturées | Three.js via React Three Fiber | Élevée : 3 à 6 semaines d'apprentissage |

**Le prototype (`prototype/index.html`) réalise les six premières lignes dans un seul fichier de 32 ko, sans aucune bibliothèque.** C'est la démonstration que l'essentiel de l'effet « site de pub » est à portée de main, et que la 3D véritable n'est qu'un supplément.

## Grille de comparaison

Notes de 0 à 5, attribuées par moi à partir des captures et des relevés du 2026-11-16. C'est un jugement argumenté, pas une mesure.

| Critère | Notre site | Linear | Stripe | Resend | TradingView | Pudding | Untapped | Yu-Gi-Oh! Meta | Scryfall |
|---|---|---|---|---|---|---|---|---|---|
| Typographie | 4 | 5 | 5 | 5 | 3 | 5 | 2 | 2 | 3 |
| Couleur et cohérence | 4 | 5 | 5 | 4 | 4 | 4 | 2 | 3 | 3 |
| Mouvement | 0,5 | 4 | 5 | 4 | 3 | 4 | 1 | 1 | 1 |
| Imagerie / objet-signature | 1 | 4 | 5 | 4 | 3 | 5 | 3 | 4 | 4 |
| Récit de la page d'accueil | 2 | 5 | 5 | 4 | 3 | 5 | 2 | 1 | 2 |
| Dataviz | 2 | 3 | 3 | 1 | 5 | 5 | 3 | 2 | 0 |
| Densité utile des outils | 3 | 5 | n. c. | n. c. | 5 | n. c. | 5 | 4 | 5 |
| Crédibilité (source, date, échantillon) | 2 | n. c. | 4 | n. c. | 4 | 5 | 5 | 3 | 4 |
| Vitesse perçue | 4 (cache chaud) / 1 (API froide) | 3 | 4 | 4 | 4 | 3 | 1 | 3 | 4 |
| Accessibilité de base | 3 | 4 | 4 | 3 | 3 | 3 | 2 | 2 | 4 |

Lecture : nous sommes **au niveau des meilleurs en typographie et en couleur**, au-dessus de toute la niche TCG en propreté, et **très en dessous de tous en mouvement et en imagerie**. C'est là qu'est l'écart perçu.

## Tendances retenues, avec preuves

1. **Sombre, typographie géante et serrée.** Linear (64 px, -1,4 px), Vercel (64 px, -3,84 px), Resend (96 px en serif), Raycast, Framer, Spline. Nous y sommes déjà (92 px, -0,05 em).
2. **Mono pour les détails techniques, jamais pour lire.** Berkeley Mono (Linear), Geist Mono (Vercel, Raycast, Spline), Commit Mono (Resend). Chez tous, le mono reste minoritaire ; chez nous il atteint 92 % sur une page.
3. **Un seul objet-signature animé dans le hero.** Triangle (Vercel), ruban (Stripe), cube (Resend), bandes (Raycast), sphère (Motion). Jamais deux.
4. **Le vrai produit visible dès le premier écran.** Linear, TradingView, Polymarket, Framer.
5. **WebGL en fond, DOM au premier plan.** Stripe, Resend, Raycast, Motion : exactement un `canvas` WebGL chacun, et tout le texte reste du HTML.
6. **Beaucoup de petites animations plutôt qu'une grande.** 83 en cours chez Linear, 42 chez Raycast, 21 chez Polymarket et Spline.
7. **Preuve et fraîcheur affichées.** Logos clients (Vercel, Stripe), compteurs (OWID, Stripe), « dernière mise à jour » et taille d'échantillon (Untapped, HSReplay).
8. **Les outils d'IA sont devenus l'argument commercial des constructeurs de sites** (Framer « design agent », Spline « pour vos agents », Rive « agent-native », Motion « humans and agents »). Conséquence pour Thomas : la compétence rare n'est plus de produire un effet, c'est de **choisir lequel sert le propos** et de le tenir en performance et en accessibilité.
9. **La niche TCG n'a pas suivi.** Aucun des neuf sites consultés n'a de mouvement soigné ni de page d'accueil narrative. C'est l'opportunité.

## Sources

Toutes consultées le 2026-11-16.

- https://www.tradingview.com/markets/ · https://pudding.cool/ · https://ourworldindata.org/ · https://op.gg/ · https://hsreplay.net/meta/ · https://polymarket.com/ · https://observablehq.com/plot/
- https://linear.app/ · https://vercel.com/ · https://stripe.com/ · https://www.apple.com/iphone/ · https://www.igloo.inc/ · https://lusion.co/ · https://resend.com/ · https://www.raycast.com/ · https://gsap.com/ · https://motion.dev/
- https://mtga.untapped.gg/meta · https://limitlesstcg.com/decks · https://moxfield.com/ · https://edhrec.com/ · https://scryfall.com/ · https://ygoprodeck.com/ · https://www.yugiohmeta.com/tier-list · https://www.mtggoldfish.com/metagame/standard · https://www.masterduelmeta.com/tier-list
- https://www.framer.com/ · https://spline.design/ · https://webflow.com/ · https://rive.app/
- Non ouverts : https://fbref.com/en/ (403) · https://www.cardmarket.com/fr/YuGiOh (403) · https://www.awwwards.com/websites/sites_of_the_year/ (403) · https://dora.run/ (domaine introuvable) · https://poke-holo.simey.me/ (certificat invalide)
- Fiches tierces sur Dora, trouvées par recherche web, non datées de 2026 : https://www.creativebloq.com/news/dora-ai-website-design · https://www.producthunt.com/p/dora-ai-alpha/dora-ai-alpha · https://www.therundown.ai/tools/dora
- Documentation Next 16 lue localement : `frontend/node_modules/next/dist/docs/01-app/02-guides/view-transitions.md`, `.../03-api-reference/04-functions/fetch.md`, `.../02-guides/incremental-static-regeneration.md`
