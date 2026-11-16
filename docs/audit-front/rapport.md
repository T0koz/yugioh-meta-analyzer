# Audit front, benchmark et proposition de refonte — rapport

Date : 2026-11-16 · Branche auditée : `main` (830bf96) · Rien n'a été modifié dans `frontend/` ni `backend/`, rien n'a été commité.

## Synthèse

### Verdict

**Le site n'est pas moche : il est muet.** La charpente (typographie, couleurs, grille, rendu serveur) est au niveau des références. Ce qui manque, c'est tout ce qui fait qu'un site « de pub » accroche : le mouvement (0 animation mesurée sur 9 pages), l'image (0 carte visible sur 7 pages sur 9, dans un site de cartes) et un récit (la page d'accueil tient en un seul écran). S'y ajoutent deux problèmes plus graves que l'esthétique : une API à 6 secondes sur trois routes et des chiffres affichés qui se contredisent.

Bonne nouvelle : l'essentiel de l'écart se comble **par-dessus l'existant, sans outil de génération et sans 3D lourde**. Un prototype d'accueil de 32 ko, sans aucune bibliothèque, le montre.

### Cinq constats

1. **Les 15 secondes viennent d'une jointure SQL, pas du front.** `/ban-radar`, `/card-impact` et `/graph/synergies` prennent 4 à 6 s par appel (36 s à trois appels simultanés) à cause d'une jointure sur une expression non indexée. Le correctif existe déjà (TOK-83, commit 4d8f8df) mais n'est pas dans `main`. En plus, `/early-signals` renvoie une erreur 500 et **fait échouer le build de production**.
2. **Aucun mouvement, presque aucune image.** `document.getAnimations()` vaut 0 partout. Les cartes n'apparaissent qu'en vignettes de 34 px sur la tier list, alors que l'API fournit l'image pour chaque carte du Ban Radar.
3. **La dataviz dessert la donnée.** Le graphique d'évolution est vide à 85 % (axe fixé à 100 pour des valeurs de 16 au plus), le graphe de synergies montre des amas sans étiquette ni pont, les prédictions sont 45 barres orange identiques.
4. **La crédibilité est fragile.** Tier list datée du 17 juin (cinq mois), Ash Blossom à 100/100 de risque de ban, signal d'achat vedette à 0,12 €, Elfnote annoncé en TCG pour mars 2027 alors qu'il pèse déjà 20 % des decks TCG. Embellir ces chiffres sans les corriger serait contre-productif.
5. **Le benchmark est rassurant.** Les meilleures vitrines (Linear, Vercel, Stripe, Resend) reposent sur un seul objet animé, une typographie proche de la nôtre et beaucoup de petites animations ; aucun produit de données de référence n'utilise de 3D ; et aucun site de la niche TCG n'a de design soigné. La place est libre.

### Recommandation

Direction **« Braise vivante »** : garder Ember, lui ajouter la carte comme objet-signature (éventail 3D, reflet holographique, bandeaux d'archétype), un langage de mouvement (CSS d'abord, puis la bibliothèque Motion), et un récit au défilement qui prouve la promesse avec de vraies courbes. Vitrine expressive, outils sobres. La 3D véritable (Three.js) reste une option tardive, limitée au graphe de synergies.

Ordre : **jour 1**, les préalables et corrections sans débat ; **semaine 1**, images et socle de mouvement ; **mois 1**, nouvelle page d'accueil et graphiques maison ; **mois 2 à 3**, page d'archétype et graphe. Environ 11 à 16 semaines à temps partiel, sans abonnement à payer.

## Documents

| Document | Contenu |
|---|---|
| [1-audit.md](1-audit.md) | Mesures, analyse page par page selon 8 critères, tableau problème → gravité → effort |
| [2-benchmark.md](2-benchmark.md) | 30 sites consultés en trois familles, analyse des outils sans code, grille de comparaison, tendances |
| [3-proposition.md](3-proposition.md) | Trois options, système de design cible, mouvement, imagerie, dataviz, technique, besoins, risques |
| [3-proposition.md, section 10](3-proposition.md#10-feuille-de-route) | Feuille de route avec critères mesurables |
| [prototype/index.html](prototype/index.html) | Prototype statique de la page d'accueil (ouvrir dans un navigateur) |
| [avancement.md](avancement.md) | État de la mission, pour reprise |

## Annexes

### Captures de l'existant (`captures/`)

Pour chaque page : `<page>-desktop-fold.png`, `<page>-desktop-full.png`, `<page>-mobile-fold.png`, `<page>-mobile-full.png`. Pages : `home`, `tier-list`, `evolution`, `predictions`, `boutique`, `early-signals`, `graph`, `ban-radar`, `ban-impact`, `ban-simulateur`, `ban-simulator-404`. Planche mobile : `captures/_planche-mobile.png`.

### Captures du prototype (`captures/`)

`prototype-desktop-1-hero.png`, `prototype-desktop-2-preuve-1.png` à `-3.png`, `prototype-desktop-3-outils.png`, `prototype-desktop-4-mouvement-reduit.png`, `prototype-mobile-1-hero.png`, `prototype-mobile-2-preuve.png`, `prototype-mobile-3-outils.png`.

### Captures du benchmark (`captures/bench/`)

Locales uniquement, exclues de git par `captures/.gitignore`. `<site>-1-fold.png` et `<site>-2-scroll.png`, plus les planches `_planche-A.jpg` (données), `_planche-B.jpg` et `_planche-B-scroll.jpg` (vitrines), `_planche-C.jpg` (TCG), `_planche-D.jpg` (outils).

### Sources

Liste complète avec URL et date de consultation à la fin de [2-benchmark.md](2-benchmark.md#sources). Cinq sites n'ont pas pu être ouverts et sont signalés comme tels (FBref, Cardmarket, Awwwards, Dora, poke-holo).

### Limites de ce rapport

- Lighthouse n'est pas installé : les Web Vitals sont mesurés par les API du navigateur, en local. Les scores Lighthouse de la feuille de route sont des objectifs.
- L'INP n'est qu'approché par une sonde.
- Les mesures de production viennent d'une copie construite dans le scratchpad, avec un repli ajouté dans cette copie pour contourner l'erreur 500.
- La détection des bibliothèques des sites tiers est un indice, pas une preuve.
- Le prototype n'a été testé que dans Chromium.
- Les ressources d'apprentissage et les ordres de grandeur de poids des bibliothèques sont cités de mémoire, à vérifier.
- Les notes de la grille de comparaison sont un jugement argumenté.
