# Explication graphique et page Méthode (lot 15, étape 2, 2026-11-17)

Branche `claude/lot15-explication-graphique-d831c8`, non fusionnée. Référence : `docs/charte-ton-et-explication.md`
(validée par Thomas le 17/11), brief `docs/planning/sprint-3/12-explication-graphique.md` §2. Modèle : Opus 5.5
(`claude-opus-5-5`).

## Livré

- **Composants communs** `frontend/src/components/ds/explain.tsx` : `SampleBadge` (« k sur n »), `ChartLegend`,
  `ChartAnnotation`, `IntervalBar`, `bandPath` + `BAND_OPACITY`, `isWeakMonth` + `WEAK_STROKE` / `WEAK_FILL_OPACITY`,
  `MethodNote` (couche « Méthode » repliée, lien vers `/methode#…`). Documentés dans `docs/design-system.md` §4
  « Explication graphique ».
- **`DataFooter`** : propriété `uncertainty` obligatoire (ligne « Incertitude : … ») ; les 23 pieds du site la renseignent.
- **`InfoTooltip`** réécrite : bouton (24 px), `aria-describedby` + `role="tooltip"`, ouverture au survol, au focus
  clavier et au toucher, fermeture par Échap ou toucher ailleurs. Vérifié dans le navigateur : 7 tabulations → bulle
  affichée ; clic → affichée ; Échap → masquée.
- **Intervalle de Wilson** `frontend/src/lib/wilson.ts`, testé par `frontend/scripts/test-stats.mjs` (`npm run
  test:stats`, branché dans `check.py`) : 9 cas comparés à statsmodels (`proportion_confint(method="wilson")`) et 5
  contrôles de bord.
- **Page `/methode`** sans formule : sources communes, seuils et leur origine, puis une section par outil dans l'ordre de
  la navigation (tier list, decks, évolution, prédictions, Ban Radar, historique, boutique, signaux précoces, graphe).
  Tableaux de validation lus dans l'API quand c'est possible (banlists rejouées, mois par effectif), échecs compris.
  `pageMetadata`, `opengraph-image.tsx`, sitemap, `STATIC_PATHS`, `PAGES` des tests visuels, lien dans le pied de page.
- **API** : `decks` (k) ajouté aux points de `GET /meta/evolution` (lu dans `meta_scores.deck_count`, table déjà servie) ;
  aucun champ retiré. Réponse figée des tests visuels complétée à la main (`decks = share × n`, exact).

## Graphiques : incertitude montrée ou raison

| Graphique | Incertitude |
|---|---|
| `/evolution`, courbes | bande à 95 % (Wilson) ; mois < 100 decks et mois en cours en pointillé ; la mesure tracée devient la part des decks (le score reste au survol et au tableau) |
| Page d'archétype, part mensuelle | bande à 95 % ; mois atténués ; annotation « en cours, n decks » sur le dernier mois |
| Tier list, barre de part | barre d'intervalle à 95 % sur une échelle commune ; effectif « k sur n decks » |
| `/predictions`, haltères | aucun intervalle : le modèle ne produit qu'une valeur ; erreur moyenne dans `/methode` |
| `/boutique`, frise d'arrivée TCG | intervalle à 80 % dessiné (déjà en place) ; rang sans intervalle |
| `/boutique`, courbes de prix | aucun intervalle : prix relevés, écart entre relevés inconnu (trous hachurés) |
| Ban Radar, barre empilée | aucun intervalle : score de classement, fiabilité dans l'onglet Historique |
| Ban historique, points par liste | bande du hasard à 90 % (déjà en place) |
| Ban historique, colonnes de cartes | aucun : listes de cartes, pas de mesure |
| Impact des cartes, simulateur | aucun : comptes exacts / recalcul du graphe |
| Graphe de synergies | aucun : liens au-dessus d'un seuil, un lien proche du seuil peut varier |
| Signaux précoces | aucun : note de classement, vues relevées une fois |
| Decks (index, fiche) | pas d'intervalle à 8 listes (trop large) ; chaque part avec son effectif |
| Accueil, corrélation OCG → TCG | IC 95 % dessiné (déjà en place) |
| Accueil, Kewl Tune | non dessinée : effectifs mensuels non relevés avec la série figée (dit dans la légende) |
| Accueil, Ban Radar rejoué | trait du milieu ; la bande à 90 % renvoie à l'historique |
| Accueil, constellation | schéma d'illustration, pas une donnée (déjà dit) |
| `/methode`, banlists rejouées | barre du hasard à 90 % par liste (`IntervalBar`) |
| `/methode`, corrélation | IC 95 % (`IntervalBar`) |

## Mesures (build de production, API sur `serving.db`)

- JavaScript transféré de `/evolution` : **192 ko avant, 190 ko après** (d3-shape n'est plus chargé). Tier list et page
  d'archétype : 200 → 201 ko (l'infobulle est un composant client).
- Lighthouse mobile, Accessibilité : **100** sur `/evolution`, `/tier-list`, `/archetype/branded`, `/methode`,
  `/predictions`, `/early-signals`, `/graph`, `/ban`, `/boutique`.
- Formules : recherche dans le HTML rendu de 16 pages (texte, `aria-label`, `title`, `alt`, `content`) pour Jaccard,
  Ridge, α, log(, √, Σ, alert_score, meta_score, « r = », « = », ≥, ≤, intermédiarité, régression, « test de deux
  proportions » : **0 occurrence** après correction (3 trouvées au premier passage : « modèle 70 % naïf + 30 % Ridge » sur
  l'accueil, « n = » dans deux annotations).
- Tests visuels : 48 captures changées sur 48 (ligne « Incertitude » sous chaque pied, pied de page avec « Méthode »),
  3 nouvelles (`/methode`). Avant / après : `docs/planning/2026-11-17/lot-15-captures/`.

## Pièges

- **Un mois atténué ne fixe pas l'échelle** : à 1 deck (juillet 2023), une part peut valoir 100 % et sa bande va de 21 %
  à 100 % ; l'axe se cale sur les mois d'au moins 100 decks, le point plus haut est posé au bord.
- **Mois en cours** : le dernier mois relevé (job du lundi) est traité comme en cours, comme le disait déjà la page
  d'archétype ; aucune date système (les captures restent déterministes).
- **`next build` refuse un `node_modules` en lien symbolique** hors du projet (Turbopack) : pour un build d'un autre
  commit, `cp -cR` (clone APFS) du dossier.
- **Lignes de la tier list sur mobile** : l'effectif complet et le score faisaient passer chaque ligne à 4 lignes de
  texte ; sous 760 px, seul « N decks » reste.

## À relire par la collaboratrice data scientist

Le calcul de l'intervalle de Wilson (`frontend/src/lib/wilson.ts`) et ses trois usages (Évolution, page d'archétype,
tier list), **avant mise en ligne** (charte §3). Hypothèse à discuter : decks traités comme indépendants, alors que
plusieurs listes d'un même joueur ou d'un même tournoi sont corrélées ; c'est un intervalle minimal, l'incertitude
réelle est plus large.

Avis du data scientist (agent `data-scientist-ygo`, lecture seule, 17/11) : **validé sur le calcul et les données.**
- Formule conforme à statsmodels sur 15 couples (k, n), dont 6 sous 100 decks : écart max 3,9e-9 (arrondi de z).
- `share` = `deck_count / total_decks` sur les 1 316 lignes de `meta_scores` ; `total_decks` constant dans chacun des
  41 mois ; somme des `deck_count` d'un mois = `total_decks` (aucune catégorie exclue). Tier list : k et n cohérents.
- Correction appliquée : « borne basse » remplacé par « intervalle minimal » (code et `/methode`), et ajout « deux
  bandes qui se chevauchent ou non ne valent pas un test » (une dizaine de bandes sur ~180 manquent la vraie part par
  hasard).
- Réserves gardées : à très petit n, Wilson est anticonservateur près des bords (0 sur 1 : [0 ; 79 %] contre
  [0 ; 97,5 %] en Clopper-Pearson) ; ces mois sont déjà atténués. Un mois à k = 0 n'a pas de ligne dans `meta_scores`
  et n'est donc pas tracé (sa bande vaudrait environ [0 ; 3,7/n]).
