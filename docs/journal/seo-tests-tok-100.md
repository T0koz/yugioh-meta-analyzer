# SEO de partage et tests visuels (TOK-100, 2026-11-16)

Branche `claude/tok-100-seo-tests-409521`, coupée de `claude/front-nuit-17-11` (lots 01 à 04). Mode d'emploi : `docs/tests-visuels.md`.

## Mesures

| Critère | Mesure |
|---|---|
| Lighthouse SEO (mobile, build de production) | 100 sur 12 pages : les 10 principales, `/archetype/branded`, `/archetype/raise-moon` |
| Balises vérifiées par script (`npm run check:meta`) | 10 pages principales + 63 pages d'archétype, 73 adresses dans le sitemap, 0 règle non tenue |
| Suite visuelle | 12 pages × 3 largeurs = 36 captures, 44 à 45 s build compris |
| Bruit entre passages | 0 pixel sur 36 captures, quatre passages |
| Seuil | pixel changé au-delà de 16/255 sur un canal ; échec au-delà de 0,01 % de pixels changés |
| Preuve du diff | `--signal` `#ff5a3c` → `#e8503a` : 36 échecs sur 36 (0,054 % à 1,743 %) ; annulé : 36 réussites |
| Références | 36 WebP sans perte, 3,4 Mo (12,4 Mo en PNG) ; données figées : 12 JSON, 268 ko |
| Accueil (mobile, `LH_THROTTLING=devtools`, 2 passages) | LCP 1,80 s, Performance 98, JavaScript 182 ko |

## Textes ajoutés ou modifiés

Titres inchangés. Descriptions réécrites : une mesure, une période, une source ; les nombres viennent de l'API au
moment du rendu (valeurs du 2026-11-16 ci-dessous).

| Page | Titre | Description |
|---|---|---|
| `/` | YGO Meta · La méta OCG précède la méta TCG de 2 à 6 mois | inchangée (lot 02) |
| `/tier-list` | Tier list TCG | 60 archétypes Yu-Gi-Oh! TCG classés par part de decks sur 396 decklists de tournoi, oct. 26 à nov. 26. Source : yugiohmeta.com. |
| `/evolution` | Évolution de la méta | Score méta mensuel des N premiers archétypes Yu-Gi-Oh! TCG, [premier mois] à [dernier mois]. Source : decklists de tournoi, yugiohmeta.com. |
| `/predictions` | Prédictions de méta | Score méta prévu pour [mois] sur N archétypes Yu-Gi-Oh! TCG, modèle 70 % naïf + 30 % Ridge, calcul du [date]. Données : decklists de tournoi, yugiohmeta.com. |
| `/boutique` | Signaux boutique | N cartes de K archétypes joués en OCG et pas encore sortis en TCG, calcul du [date]. Libellé : rang parmi 89 archétypes OCG, seuils provisoires, non validés hors échantillon. |
| `/early-signals` | Signaux précoces | N cartes Yu-Gi-Oh! récentes notées de 0 à 100 : vues hebdomadaires, co-occurrences en decks de tournoi, tier de l’archétype, calcul du [date]. Sources : YGOPRODeck, yugiohmeta.com. |
| `/graph` | Graphe de synergies | Graphe de co-occurrence des cartes Yu-Gi-Oh! : un lien relie deux cartes jouées dans les mêmes decks de tournoi, indice de Jaccard ≥ 0,15. Source : yugiohmeta.com, date de calcul non enregistrée. |
| `/ban` | Ban Radar | Cartes Yu-Gi-Oh! TCG notées de 0 à 100 sur six critères de risque de restriction, sur 1 883 decks de tournoi, relevé du 14 novembre 2026. Source : yugiohmeta.com. |
| `/ban?tab=impact` | Cartes à impact | Cartes Yu-Gi-Oh! TCG classées par nombre d’archétypes et de decks qui les jouent, sur 1 883 decks de tournoi, relevé du 14 novembre 2026. Source : yugiohmeta.com. |
| `/ban?tab=simulateur` | Simulateur de ban | Archétypes et decks de tournoi Yu-Gi-Oh! TCG reliés à une carte dans le graphe de co-occurrences, et cohésion du graphe sans elle. Source : yugiohmeta.com, date de calcul non enregistrée. |
| `/archetype/{slug}` | nom de l'archétype | inchangée (lot 04) |

Textes dessinés dans les images de partage (surtitre, titre, pied ; « Source : yugiohmeta.com » partout) :

| Image | Surtitre | Titre | Pied ou chiffre |
|---|---|---|---|
| accueil (et défaut) | Méta Yu-Gi-Oh! · TCG et OCG | La méta OCG précède la méta TCG de 2 à 6 mois | r = 0,53 · Corrélation OCG, TCG 2 à 6 mois plus tard · IC 95 % : 0,43 à 0,59 · 105 archétypes · 23 948 decklists de tournoi, mai 2023 à novembre 2026 |
| tier-list | Méta · TCG | Tier list TCG | Part de decks par archétype, decklists de tournoi TCG |
| evolution | Méta · TCG | Évolution de la méta | Score méta mensuel par archétype, decklists de tournoi TCG |
| predictions | Méta · TCG | Prédictions de méta | Score méta prévu à un mois, modèle 70 % naïf + 30 % Ridge |
| boutique | Boutique · OCG vers TCG | Signaux boutique | Archétypes joués en OCG, pas encore sortis en TCG |
| early-signals | Boutique · Cartes récentes | Signaux précoces | Vues hebdomadaires et co-occurrences en decks de tournoi |
| graph | Graphe · Co-occurrence | Graphe de synergies | Cartes jouées dans les mêmes decks, indice de Jaccard |
| ban (trois onglets) | Bans · TCG | Ban Center | Risque de restriction, cartes à impact, simulateur |
| archétype | Archétype · TCG · tier X (ou · OCG) | nom | part des decks, « N sur M · fenêtre », courbe « Part mensuelle TCG, mois à mois » ; OCG : « N decks · calcul du [date] », « Aucun deck TCG dans la fenêtre courante » |

## Pièges

- **`openGraph` n'est pas fusionné champ par champ** entre le layout et la page : une page sans `openGraph` hérite
  du titre et de l'adresse du layout. Toute page passe donc par `pageMetadata` (`lib/seo.ts`).
- **Une route à onglets (`/ban`) n'a qu'une image de partage** : le fichier `opengraph-image.tsx` ne voit pas la
  query. Titre et description, eux, changent par onglet.
- **Satori (images)** : ni WOFF2, ni texte qui coule autour d'un `<span>` (le titre est posé mot à mot), ni
  variables CSS (les tokens sont lus dans `globals.css`). Les polices et `globals.css` sont lus par `readFile`
  depuis `process.cwd()` : à vérifier au premier déploiement Vercel pour l'image d'archétype, rendue à la demande.
- **Fausse API et build Next** : le build interroge l'API depuis une dizaine de processus ; un serveur Python
  avec la file d'attente par défaut (5) renvoie des `ECONNRESET`.
- **Gestionnaire `route` de Playwright (Python)** : une fonction à deux paramètres reçoit `(route, request)` ;
  des valeurs par défaut en deuxième position sont écrasées.
- **`next build` réécrit `tsconfig.json`** quand `distDir` change : les entrées `.next-visual/…` sont commitées.
- **Le build dépend du réseau** (polices Google) : échec passager observé, d'où les trois essais.
- Le sitemap n'a pas de `lastModified` : l'API ne sert pas de date commune aux pages.
