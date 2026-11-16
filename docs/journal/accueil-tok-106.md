### 🏠 Nouvelle page d'accueil (TOK-106, 2026-11-16)

Portage de `docs/audit-front/prototype/index.html` en composants Next. Branche `claude/tok-106-accueil-66ff33`.
Modèle utilisé : Claude Fable 5.2.

## Mesures (build de production, API locale sur `serving.db`, Chromium de Playwright)

| Critère | Cible | Mesuré |
|---|---|---|
| Hauteur de page | ≥ 4 écrans | 7,73 écrans à 1440 × 900 ; 5,62 à 768 × 1024 ; 8,86 à 375 × 812 |
| LCP mobile (`LH_THROTTLING=devtools`) | ≤ 2,0 s | 1 879, 1 808 et 1 792 ms (3 passages) |
| JavaScript transféré | ≤ 220 ko | 180 ko (11 fichiers) |
| Lighthouse Performance, mobile | ≥ 90 | 98 |
| Lighthouse Accessibilité | ≥ 95 | 100 (Bonnes pratiques 100, SEO 100, CLS 0) |
| Lighthouse desktop | — | 100 / 100 / 100 / 100, LCP 771 ms |
| Pied de données | sous chaque visualisation | 6 sur 6 : graphique Kewl Tune, tuile boutique, tuile radar, constellation (signalée comme schéma), intervalle de confiance, tableau du backtest |
| Sans JavaScript | fonctionne | les 4 sections et le graphique sont dans le HTML ; plus de squelette « Chargement… » |
| Mouvement réduit | fonctionne | 0 animation en cours, 0 élément à opacité nulle, récit au défilement désactivé (graphique dans son état final) |
| Défilement horizontal | aucun | `scrollWidth` = largeur aux 3 tailles, 0 erreur de console |

Captures (locales, non suivies) : `docs/audit-front/captures/tok-106/` (`avant-*`, `apres-*`, `apres-mvt-reduit-*`,
`apres-sans-js-*`, `scrolly-1` à `3`). Avant : 1,50 écran à 1440 px.

Autres pages, même passage (mobile, ralentissement réel) : `/tier-list` 1 712 ms, `/evolution` 1 677, `/predictions`
1 725, `/boutique` 1 648, `/early-signals` 1 666, `/graph` 1 705, `/ban` 1 981, `/ban?tab=impact` 1 998 ; accessibilité
100 partout. Référence du matin : 1,7 à 2,1 s.

## La cause du « 0,4 s non isolé »

`app/loading.tsx` enveloppait chaque page dans un Suspense. Le HTML statique contenait le squelette, puis le contenu
dans un bloc caché que React révèle par script, avec un délai volontaire (regroupement des révélations). Conséquences :
sans JavaScript, seul « Chargement des données… » s'affichait ; avec, le LCP attendait la révélation. Vérifié en
listant les candidats LCP sous ralentissement (un texte de 4 454 px² au premier affichage, puis le paragraphe 360 ms
plus tard, même police bloquée, même animations coupées). Le fichier est maintenant dans `app/ban/` (seule route
rendue à la demande). Pistes écartées, mesurées sans effet : différer les images du hero, les polices, l'animation.

## Choix

- **Hero** : éventail = illustrations des 5 archétypes les plus joués de la tier list (carte centrale : le premier).
  Images différées (`loading="lazy"`) : le LCP mobile est le paragraphe. Titre mot par mot derrière un masque, sans fondu.
- **Exemple Kewl Tune** : SVG serveur dans son état final ; `ProofScroll` pose `data-live` (≥ 900 px de large, ≥ 620 px
  de haut, mouvement autorisé) et relie le tracé au défilement. Données figées dans `lib/proof-data.ts`.
- **Tuile boutique** : rang de l'archétype en grand, libellé `signal_label`, fenêtre `tcg_window_*`, mentions
  « seuils provisoires, non validés hors échantillon » et « intervalle à 80 %, non validé ».
- **Constellation** : SVG animé en CSS, sans JavaScript, signalé comme schéma.
- **Méthode** : données, corrélation avec son intervalle dessiné, backtest du Ban Radar (4 des 20 listes, dont les
  deux listes TCG récentes mal anticipées).

## Textes de la page (à relire)

Titre de l'onglet : « YGO Meta · La méta OCG précède la méta TCG de 2 à 6 mois ». Description : « Méta Yu-Gi-Oh! TCG
et OCG mesurée sur 23 948 decklists de tournoi : corrélation OCG → TCG de 0,53, signaux boutique, risque de ban,
méthode et limites. »

**Hero**
- Sur-titre : « Méta Yu-Gi-Oh! · données au 14 novembre 2026 »
- Titre : « La méta OCG précède la méta TCG de 2 à 6 mois. »
- Chapeau : « Corrélation r ≈ 0,53 (IC 95 % : 0,43 à 0,59) entre le score d'un archétype en OCG et son score en TCG
  2 à 6 mois plus tard, sur 105 archétypes et 23 948 decklists de tournoi (yugiohmeta.com, mai 2023 à novembre 2026). »
- Liens : « Signaux boutique », « Méthode et limites »
- Étiquette de l'éventail : « Elfnote · 20,7 % des decks TCG · oct. 26 à nov. 26 »
- Chiffres : « Decklists analysées », « Cartes suivies », « Corrélation OCG → TCG (r) », « Écart OCG → TCG »

**Exemple**
- Sur-titre : « Exemple · un archétype, deux formats »
- Titre : « Kewl Tune : pic en OCG en avril 2026, en TCG 3 mois plus tard. »
- « 1 · OCG » : « 2,2 % des decks en janvier 2026, 10,3 % en février, pic à 26,7 % en avril. »
- « 2 · TCG » : « 0,7 % en avril 2026, 22,5 % en mai, pic à 32,1 % en juillet. »
- « 3 · Écart » : « Courbe OCG décalée de 3 mois. Un seul archétype : sur 105 archétypes, l'écart observé va de 2 à 6 mois. »
- Légende : « OCG (Japon, Asie) », « TCG (Europe, Amériques) » ; annotations « 26,7 % · avril », « 32,1 % · juillet », « 3 mois »
- Pied : « Part des decks de tournoi par mois, août 2025 à novembre 2026 (novembre incomplet). Source : decklists
  yugiohmeta.com, relevé du 16 novembre 2026. »

**Outils**
- Sur-titre : « Outils » ; titre : « Trois outils, les mêmes decklists. »
- Boutique : « Signal boutique » ; « 3ᵉ sur 89 archétypes OCG » ; « Raise Moon » ; « Carte suivie : Pot of Desires. » ;
  « FORT », « Cardmarket 0,10 € », « Arrivée TCG nov. 26 à mars 27 » ; pied : « Libellé : rang de l'archétype en OCG,
  seuils provisoires, non validés hors échantillon. Fenêtre d'arrivée : intervalle à 80 %, non validé. Source :
  decklists OCG et prix Cardmarket, au 14 novembre 2026. »
- Radar : « Ban Radar · pièces d'archétype » ; « Risque de restriction, score sur 100. » ; par carte « 14,1 % des decks ·
  2,99 ex. en moyenne » ; pied : « Barre : ubiquité, porteur, copies, restriction, élan, pont. Source : 1 883 decks de
  tournoi TCG, au 14 novembre 2026. »
- Graphe : « Graphe de synergies » ; « Cartes jouées ensemble dans les mêmes decks. » ; « 63 communautés de cartes
  détectées. En orange, les cartes « pont », qui en relient plusieurs (centralité d'intermédiarité). » ; pied : « Schéma
  d'illustration : positions et liens ne sont pas des données. Graphe réel : cooccurrences dans les decklists de tournoi. »
- Bande de liens : « Tier list » (« Elfnote : 20,7 % de 396 decks TCG, oct. 26 à nov. 26. ») ; « Évolution » (« Part
  mensuelle des archétypes TCG, depuis mai 2023. ») ; « Prédictions » (« Score méta prévu à un mois, par archétype. ») ;
  « Signaux précoces » (« Cartes classées par score précoce. »)

**Méthode**
- Sur-titre : « Méthode » ; titre : « Méthode et limites. »
- « Les données » : « 23 948 — decklists de tournoi, mai 2023 à novembre 2026 : 11 618 en TCG, 12 330 en OCG, légales à
  la date du tournoi. » ; « 13 797 — cartes suivies : prix Cardmarket et statut sur la banlist. » ; « Lundi — mise à
  jour hebdomadaire. Prédictions datées et archivées depuis le 1ᵉʳ novembre 2026. » ; pied : « Sources : yugiohmeta.com
  (decklists), YGOPRODeck (cartes), Yugipedia (banlists), Cardmarket (prix). Décompte au 14 novembre 2026. »
- « Le signal OCG → TCG » : « r ≈ 0,53 · IC 95 % : 0,43 à 0,59 » ; « Corrélation entre le score d'un archétype en OCG
  et son score en TCG 2 à 6 mois plus tard, sur 105 archétypes. » ; « Libellés Fort, Modéré, Faible des signaux
  boutique : seuils provisoires, non validés hors échantillon. Premières prédictions datées à échéance en mars 2027. » ;
  pied : « Source : méta TCG et OCG mensuelles, calcul du 16 novembre 2026. »
- « Ban Radar rejoué sur les banlists passées » : « Rang médian, dans le classement calculé la veille de la banlist,
  des cartes ensuite restreintes. Trait vertical : rang attendu au hasard (milieu du classement). » ; colonnes
  « Banlist », « Rang médian des cartes touchées », « Au hasard », « Cartes classées » ; « Top 10 du radar sur 10
  banlists TCG (avril 2024 à octobre 2026) : 19 places sur 100 suivies d'une restriction pour les pièces d'archétype,
  6 sur 100 pour les staples génériques. » ; pied : « Source : backtest du 16 novembre 2026, 4 des 20 listes rejouées
  (les deux de référence et les deux plus récentes en TCG). Poids du score réglés sur la liste TCG de mai 2026. »

**Pied de page**
- « Méta Yu-Gi-Oh! TCG et OCG, calculée sur les decklists de tournoi. » ; « Données au 14 novembre 2026 » ; « Mise à
  jour chaque lundi » ; colonnes « Méta », « Bans », « Boutique » ; « Sources : decklists de tournoi yugiohmeta.com ·
  cartes et images YGOPRODeck · banlists Yugipedia · prix Cardmarket. » ; « Site indépendant, sans lien avec Konami.
  Yu-Gi-Oh! est une marque de ses ayants droit. Scores et signaux : estimations statistiques, sans garantie. »

## Points à relire en priorité

- Le verbe « précède » du titre : la mesure est une corrélation (r ≈ 0,53), pas une avance démontrée archétype par archétype.
- « Écart OCG → TCG : 2 à 6 mois » vient de `SITE_FACTS.ocgTcgLagRange` (signal à peu près constant sur cette plage).
- « 63 communautés » n'a pas été recalculé depuis le rafraîchissement de la base (noté dans `site-facts.ts`).
- « Mention légale » du pied de page : formulation à valider.

## Non vérifié

Safari et Firefox (Chromium seul) ; lecteur d'écran réel ; téléphone réel.
