### 🎨 Refonte front « Braise vivante » (TOK-94)

Audit, proposition et décisions : `docs/audit-front/`. Ordre imposé : TOK-96 (jour 1) → TOK-97 (crédibilité des
chiffres, avant la nouvelle page d'accueil) → TOK-98 (semaine 1). Une étape ne démarre qu'après validation de la précédente.

**TOK-96, jour 1 (2026-11-16, branche `claude/refonte-front-cbe8af`)** — mesuré par script Playwright, avant/après :

- **États** : `app/loading.tsx` (squelette), `app/error.tsx`, `app/not-found.tsx`. En Next 16, la prop de reprise
  d'`error.tsx` s'appelle **`unstable_retry`** (plus `reset`) : relire `node_modules/next/dist/docs/…/error.md` avant d'y toucher.
- **Redirection** `/ban-simulator` → `/ban?tab=simulateur` dans `next.config.ts` (`redirects`, la query `?card=` suit).
- **Titres** : `title.template` (« %s · YGO Meta ») dans `layout.tsx`, un `metadata` par page ; `/ban` utilise
  `generateMetadata` parce que ses trois onglets partagent une route. Toute nouvelle page exporte son `metadata`.
- **`--faint` = `#788499`** (était `#566175`, 3,2:1) : 4,5:1 au moins sur `--ink` à `--ink-4`. Il peut désormais porter
  un rang ou un tiret. Revers : il est plus proche de `--muted-text`, la hiérarchie se joue surtout à la taille.
  Texte de la tuile orange de l'accueil passé de 70 % à 100 %.
- **`/evolution`** : axe vertical `[0, auto]` et axe du temps limité aux mois où une série affichée a une valeur.
- **`CardThumb`** (`components/card-thumb.tsx`) : vignette avec `width`/`height` (CLS nul), `loading="lazy"`, repli
  dessiné sans image. Utilisée par la tier list et le Ban Center (`RankedThumb` : vignette + rang).
- **Ban Radar ouvert sur « Pièces d'archétype »** (décision 4) : `KIND_ORDER` dans `ban/kind-filter.tsx` fixe la vue
  par défaut de chaque onglet (radar : archétype ; impact : tout). La vue par défaut n'a pas de paramètre `kind` dans
  l'URL ; « Tout » s'écrit `?kind=all`. La tuile Ban Radar de l'accueil lit aussi `kind=archetype`.
- **Français** : `TrendLabel` et `BanStatus` traduisent à l'affichage (l'API garde `Rising`, `Unlimited`…) ;
  `banStatusLabel()` pour tout nouveau statut affiché. « Tier list », « Ban Radar », « Rogue » et « staples » sont gardés :
  c'est le vocabulaire des joueurs francophones.
- **Piège trouvé** : 22 des 50 premières cartes du radar n'ont pas d'image (cartes récentes absentes de `cards` :
  Angelechy, Blitzclique, Sacred Beasts…). Relancer `fetch_cards.py` puis `build_serving_db.py`.
- Captures avant/après (locales, non suivies) : `docs/audit-front/captures/tok-96/`.

**TOK-97, crédibilité des chiffres (2026-11-16)** — analyse `data-scientist-ygo` en lecture seule, correctifs dans l'API :

- **Tier list maison** : `GET /meta/tier-list` ne lit plus `meta_tier_list` (figée au 17 juin) ni `archetype_trend`.
  Elle est calculée à la volée depuis `meta_scores` ; règles dans `backend/app/tiering.py`, testées par
  `backend/tests/test_tiering.py`. La réponse porte `window_start`, `window_end`, `n_decks` (plus de `generated_at`).
  - Fenêtre : mois récents cumulés jusqu'à **300 decks** (au 16/11 : oct. + nov., 396 decks). Novembre seul
    (156 decks) donne ±3,4 points d'incertitude sur une part de 5 %.
  - Tiers sur la **part de decks** (T0 ≥ 40 %, T1 ≥ 15 %, T2 ≥ 7 %, T3 ≥ 3 %, Rogue sinon ou sous 5 decks), **pas sur
    `meta_score`** : un deck unique classé premier y vaut `sqrt(1/n)` et passe devant des archétypes dix fois plus joués.
  - Tendance : test de deux proportions contre la fenêtre précédente (|z| ≥ 1,96), Stable d'office sous 10 decks cumulés.
    L'ancienne `archetype_trend` étiquetait « émergence » tout archétype nouveau (45 sur 90) et « stable » les disparus.
  - Limites connues : la fenêtre chevauche la banlist du 2026-10-19 (25 % des decks datent d'avant) ; les hybrides sont
    comptés à part (« Angelechy Elfnote ») ; Angelechy et Blitzclique n'ont pas d'image (absents de `cards`).
- **`tcg_entry_estimated` n'est pas une estimation** : le notebook 10 y écrit `date.today() + 4 mois`, identique pour
  toutes les lignes. Le champ n'est plus servi ni affiché. ⚠ `scripts/log_predictions.py` le journalise encore comme
  `target_date` : à neutraliser avant l'échéance de mars 2027.
- **Signaux boutique filtrés dans l'API** *(remplacé le jour même par TOK-113, filtre retiré : voir plus bas)* : un
  archétype qui cumule ≥ 5 decks TCG sur 12 mois de `meta_scores` (`TCG_PRESENCE_MIN_DECKS`) était écarté. 7 archétypes sur 10 sortent (Elfnote, Kewl Tune, Branded, Sky Striker…),
  il reste Toon, Witchcrafter, Raise Moon : 41 lignes, **aucun signal « Fort »**, des staples à quelques centimes.
  Le score mesurait « fort en OCG », pas « fort en OCG et absent du TCG » : le vrai correctif est dans le notebook 10.
- **Ban Radar** : poids inchangés. `SITE_FACTS.banTop10Hits*` porte le constat affiché sur les vues Staples et Tout :
  6 des 100 places du top 10 des staples suivies d'une restriction sur 10 banlists TCG, contre 19 pour les pièces
  d'archétype ; Ash Blossom, première à chaque fois, jamais touchée. **À recalculer à chaque banlist.**
- Fallback d'image d'archétype par mots entiers (« Ashtra » prenait l'image de « Ra »).

**TOK-98, semaine 1 (2026-11-16)** — cartes, mouvement, typographie, mesurés par script Playwright et Lighthouse :

- **Images** : `components/card-art.tsx` (`CardArt` en tailles `xs`/`sm`/`lg`, `ArtDot` pastille ronde) remplace
  `CardThumb`. Il passe par **`next/image`** (`images.remotePatterns` dans `next.config.ts`) : le serveur Next
  redimensionne et met en cache, le navigateur ne parle plus à `images.ygoprodeck.com`. C'est une étape : l'hébergement
  propre reste TOK-92. `lib/card-images.ts` (`artCropUrl`) est le seul fichier qui connaît la forme des URL.
  Next 16 : la prop `priority` est dépréciée (`preload`), on utilise `loading="eager"` au premier écran.
- **L'API renvoie `image_url`** sur `/boutique/signals`, `/early-signals`, `/meta/predictions`, et une carte `images`
  sur `/meta/evolution`. Jointure `cards` avec l'expression indexée et `= +s.card_name` (TOK-83).
- **Bandeau d'archétype** (tier list, lignes T0 à T3, ≥ 760 px) : illustration recadrée derrière le nom, sous un masque
  qui la garde sombre sous le texte. Si on touche au masque, revérifier le contraste du nom sur une illustration claire.
- **Mouvement, CSS seul** : tokens `--dur-1/2/3`, `--stagger`, `--glow` ; utilitaires `enter` (avec `[--i:n]` pour
  décaler), `fill-in` (barres), `cursor-blink`. Les keyframes ne décrivent que l'état de départ : sans animation,
  l'élément est à sa place. `components/reveal.tsx` (apparition au défilement, une fois) ne cache un élément que
  depuis le JavaScript, s'il est sous l'écran et si le mouvement est autorisé : ne jamais poser `reveal-pending` dans
  le HTML serveur. Limite : l'animation d'ouverture se rejoue à chaque navigation.
- **Typographie** : Inter Tight en police variable ; noms de cartes (`CardChip`), tendances, pills de filtre et lignes
  de détail en Inter Tight ; le mono reste aux chiffres, rangs et labels en majuscules.
- **Accent rationné** : barres de la tier list et des prédictions en neutre ; la barre de la tier list montre la
  **part de méta** (la mesure du tri), plus le score.
- Titres : `h2` après le `h1` (les `h3` directs faisaient échouer `heading-order` dans Lighthouse).
- **Lighthouse** : `npm run lighthouse` (`frontend/scripts/lighthouse.mjs`), référence dans
  `docs/audit-front/lighthouse-2026-11-16.md`.
- **Piège Lighthouse** : par défaut il *simule* le réseau lent et son LCP est instable (1,6 à 3,9 s pour une même
  page). Pour citer un LCP, lancer avec `LH_THROTTLING=devtools` (ralentissement réel) : **≈ 2,0 s sur les 9 pages**.
- **Piège LCP : ne jamais faire démarrer à opacité 0 un texte du premier écran.** Le LCP ne le compte qu'une fois
  visible ; le fondu d'entrée coûtait jusqu'à 0,8 s. L'utilitaire `enter` glisse sans fondu (`rise-in`) ; le fondu
  (`fade-rise`) est réservé à `Reveal`, sous le premier écran.

**Après fusion de TOK-113 (2026-11-16)** : `GET /boutique/signals` n'a plus de filtre (la règle « pas encore en TCG »
est appliquée à la source, sur les cartes) et sert `tcg_window_start` / `tcg_window_end`. La page boutique et la tuile
de l'accueil affichent la fenêtre (« nov. 26 à mars 27 », `fmtMonthRange`) avec son avertissement : intervalle à 80 %,
non validé hors échantillon. Une branche qui lit encore `tcg_entry_estimated` répond 500 sur la base en schéma v3.
