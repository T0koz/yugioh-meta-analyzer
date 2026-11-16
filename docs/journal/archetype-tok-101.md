# TOK-101 — Page d'archétype et transitions de vue (2026-11-17)

Branche `claude/tok-101-archetype-49be45`, non fusionnée dans `main`. Modèle : Claude Fable 5.2 (`claude-fable-5-2`).

## Ce qui est livré
- **Page** `/archetype/{slug}` (`frontend/src/app/archetype/[slug]/`) : en-tête (nom, tier, tendance, fenêtre
  précédente, carte), bande de chiffres, part de méta par mois (`ShareChart`, SVG serveur + tableau des valeurs),
  cartes clés (`CardArt`), signal boutique s'il existe, un `DataFooter` par bloc. `generateMetadata` (titre, description).
- **API** `GET /api/v1/archetypes/{slug}` (`backend/app/routers/archetypes.py`) ; 404 si le slug est inconnu.
  Champs ajoutés ailleurs : `slug` et `decks` dans `/meta/tier-list`, `archetype_slug` dans `/boutique/signals`.
- **Liens** : chaque ligne de la tier list (lien étendu à toute la ligne, anneau de focus clavier) ; colonne Archétype
  de `/boutique`.
- **Transitions de vue** : `experimental.viewTransition`, `components/view-transitions.tsx`, règles dans `globals.css`.

## D'où viennent les chiffres (aucun calcul nouveau)
| Bloc | Table | Fenêtre |
|---|---|---|
| Part, decks, rang, tier, tendance | `meta_scores`, mêmes règles que la tier list (`compute_tier_list`) | fenêtre de la tier list (≥ 300 decks) |
| Part par mois | `meta_scores` (`deck_count` / `total_decks`), 0 deck les mois sans ligne | du premier mois joué au dernier mois de la base |
| Cartes clés | `ban_radar` où `top_archetype` = l'archétype, 12 premières par nombre de decks | fenêtre du Ban Radar (`as_of`, `n_decks_window`) |
| Part OCG | `ocg_archetype_scores` (`share_ocg`, `n_ocg_decks`) | `computed_at` |
| Signal boutique | `boutique_buy_signals` + libellé de `signal_label.py` | `computed_at` |

## URL
`slugify` (`backend/app/slugs.py`) : NFKD, accents retirés, minuscules, tout le reste devient un tiret.
« Harpie/Amazoness » → `harpie-amazoness`, « D/D/D » → `d-d-d`, « @Ignister » → `ignister`, « Live☆Twin Spright » →
`live-twin-spright`, « Gold Pride P.U.N.K. » → `gold-pride-p-u-n-k`. 231 archétypes, aucune collision (les deux bases).
En cas de collision future, l'archétype le plus joué garde l'adresse. Testé sur le build de production :
`/archetype/harpie-amazoness` 200, `/archetype/d-d-d` 200, `/archetype/live-twin` 200, `/archetype/Harpie%2FAmazoness`
404, `/archetype/harpie/amazoness` 404, `/archetype/inconnu-xyz` 404 (page « Page introuvable »), `/archetype/Branded`
200 (même page que `branded`, voir context.md).

## Mesures (build de production, mobile, `LH_THROTTLING=devtools`)
| Page | Perf. | Access. | LCP | CLS |
|---|---|---|---|---|
| `/archetype/elfnote` | 99 | 100 | 1,76 à 1,78 s | 0 |
| `/archetype/harpie-amazoness` (signal boutique) | 99 | 100 | 1,72 à 1,75 s | 0 |
| `/archetype/branded` | 99 | 100 | 1,72 à 1,75 s | 0 |
| `/archetype/angelechy`, `artmage`, `dark-magician-chaos-ritual`, `raise-moon` | 99 | 100 | 1,73 à 1,76 s | 0 |
| `/archetype/radiant-typhoon` | 98 | 100 | 1,84 s | 0 |
| `/tier-list` | 98 | 100 | 1,84 à 1,86 s (avant : 1,65 à 1,75 s au lot 02) | 0 |

JavaScript transféré : 190 ko sur ces pages. Un passage à 2,96 s et CLS 0,127 a été relevé sur la toute première
requête après le démarrage du serveur (cache d'images vide) ; il ne s'est pas reproduit sur 5 pages jamais visitées.

## Navigation (Playwright, Chromium, build de production)
| Cas | Résultat |
|---|---|
| Transitions prises en charge | 1 `startViewTransition` par navigation ; groupes `archetype-art-*`, `archetype-title-*` et glissement (`vt-slide`, `vt-fade`) ; 14 animations de durée non nulle ; 0 erreur console |
| Mouvement réduit | 0 animation de durée non nulle ; navigation correcte |
| API de transition retirée (`delete Document.prototype.startViewTransition`) | navigation correcte, 0 erreur |
| JavaScript désactivé | les 60 liens sont de vrais `<a>`, la page s'affiche |
| Clavier | lien atteint au Tab, anneau 2 px `--signal-hi` sur la ligne, Entrée ouvre la page ; retour du navigateur correct |

Captures (375, 768, 1440 px ; non suivies par git) : dossier de notes de la nuit, `lot-04-captures/`.

## Textes ajoutés ou modifiés
Tier list et boutique : aucun texte changé (le nom de l'archétype devient un lien).
Page d'archétype :
- Lien de retour : « ← Tier list ».
- Surtitre : « Archétype · TCG · {période} · {n} decks ».
- Sous le nom : étiquette de tier, « En hausse / Stable / En baisse », « fenêtre précédente : 14,6 % (76 decks sur 519) » ;
  sans deck TCG : « Hors tier list : aucun deck TCG relevé de {période}. » ; « SIGNAL MODÉRÉ » (ancre vers le bloc).
- Bande de chiffres : « Part de méta TCG », « Decks sur 396 », « Rang sur 60 archétypes », « Part de méta OCG »,
  « Score méta ×100 », « Deck TCG sur 396 », « Dernier mois joué en TCG », « Decks OCG », « Rang OCG sur 89 ».
- Pied de l'en-tête : « tiers : T0 dès 40 % des decks, T1 15 %, T2 7 %, T3 3 % ; tendance : test de deux proportions
  à 5 % contre la fenêtre précédente », « OCG : 202 decks, calcul du 16 novembre 2026 ».
- « Part de méta par mois » ; légende : « part mensuelle des decks TCG », « fenêtre de la tier list (oct. 26 à nov. 26) »,
  « decks relevés par mois (max. 519) » ; annotations « 21,2 % · nov. 26 » ; pied : « 249 decks Elfnote sur 2 947 »,
  « le dernier mois est en cours » ; « Tableau des valeurs » (Mois, Part, Decks {archétype}, Decks relevés).
- « Cartes clés » ; « Les 12 cartes les plus jouées dont {archétype} est le deck d'attache, sur 1 883 decks TCG au
  14 novembre 2026 : decks qui la jouent, part de tous les decks, exemplaires moyens par deck. » ; par carte :
  « 433 decks · 23,0 % », « 1,7 ex. par deck » ; pied : « deck d'attache : au moins la moitié des decks qui jouent la
  carte sont de cet archétype ; statut : banlist TCG en vigueur ».
- « Signal boutique » ; « Libellé », « seuils provisoires, non validés hors échantillon » ; « Rang parmi les archétypes
  OCG », « 18ᵉ sur 89 », « Fort : rang 8 ou mieux · Modéré : rang 22 ou mieux » ; « Arrivée en TCG, intervalle à 80 % »,
  « premier deck OCG + 75 à 202 jours, délai mesuré sur 1 897 cartes sorties de 2022 à 2025 ; non vérifié sur des cas
  nouveaux » ; colonnes « Carte », « Ordre dans le lot », « Prix CM », « Banlist TCG » ; pied : « ordre dans le lot :
  100 = première carte de tous les signaux affichés, ce n'est pas une force de signal », « tous les signaux ».
- Balises : titre = nom de l'archétype ; description, par exemple « Elfnote : 20,7 % des decks de tournoi TCG (82 sur
  396, oct. 26 à nov. 26), tier T1. Part mensuelle et cartes clés. »

## Limites connues
- Les textes « 75 à 202 jours » et « 1 897 cartes » sont recopiés de `/boutique` (non servis par l'API) : à modifier
  aux deux endroits si le délai est recalculé.
- La vignette d'un archétype sans entrée dans `cards.archetype` est une carte de son signal ou de ses cartes clés.
- Un archétype qui apparaît après le build a sa page à la première visite (rendu à la demande, cache de 5 min).
- Pas de lien canonique ni d'Open Graph : lot 05.
- Le panneau de survol de la tier list peut afficher une image en retard sur le nom après un retour arrière (existant).
