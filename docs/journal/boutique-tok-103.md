# TOK-103 — Boutique regroupée par archétype, courbes de prix (lot 11, 2026-11-17)

Branche `claude/lot11-tok-103-boutique-e98c5d`, non fusionnée.

## Livré

- `scripts/build_boutique_price_history.py` → table `boutique_price_history` (113 lignes : 11 cartes du signal ×
  10 ou 11 relevés), recopiée telle quelle depuis `card_price_history` (138 776 lignes, non servie). Prix ≤ 0 écartés ;
  une seule ligne par (nom nettoyé, date), `card_id` le plus récent en cas de renumérotation. Servie (`SERVED_TABLES`).
- `GET /api/v1/boutique/prices` : relevés par carte, `gaps` (écarts > `max_step_days`), `sparse` (< `min_points`),
  période commune, nombre de dates, source, `computed_at`. Table absente → réponse vide (la page tient).
- Règles d'affichage dans `backend/app/price_history.py` seulement : `MAX_STEP_DAYS = 10`, `MIN_POINTS = 3`.
- `refresh_all.py` : `snapshot_prices.py` puis `build_boutique_price_history.py` après `build_buy_signals.py`.
- Page `/boutique` : frise « rang en OCG et arrivée en TCG » (jauge de rang à deux graduations, fenêtre à 80 % sur
  une échelle de mois commune, trait au jour du calcul), calendrier des relevés (trous hachurés avec leur durée), un
  bloc par archétype avec une tuile par carte (dernier prix, courbe, pied « Cardmarket via YGOPRODeck · n relevés »),
  tableau des relevés et tableau de tous les signaux en `<details>`, `DataFooter` sous chaque bloc.
- Composants : `app/boutique/PriceChart.tsx` (`PriceChart`, `SnapshotStrip`, `MonthAxis`), `app/boutique/ArrivalTimeline.tsx`.

## Mesures

- Lighthouse mobile, build de production, `LH_THROTTLING=devtools` : LCP 1,75 / 1,75 / 1,77 / 1,79 s ; une
  première mesure juste après le démarrage du serveur à 2,42 s (`/tier-list`, mesurée dans la même série, 2,20 s).
  Accessibilité 100, Performance 95 à 99, CLS 0, JavaScript transféré 183 ko.
- Tests visuels : 3 captures changées (`boutique-375`, `-768`, `-1440`), 42 identiques.

## Pièges

- **Les relevés de prix n'étaient pris qu'au lancement de Streamlit** (`run.sh`) : 11 dates en 2026, écarts de 14, 33,
  79 et 15 jours. Avec la règle des 10 jours, seules deux suites sont reliées (13 → 19 juin, 5 → 14 août). C'est voulu.
- Trous en hachures HTML (dégradé répété), pas en `<rect>` dans le SVG étiré : un aplat `--ink-4` sur `--ink-3`
  ne se voyait pas, et un motif SVG se déforme avec `preserveAspectRatio="none"`.
- Pas d'annotation de valeur dans la courbe : à 300 px, elles chevauchaient les points. Dernier prix en tête de tuile,
  premier dans le pied.
- `buy_score` n'est plus affiché (ordre d'affichage, pas une force de signal) mais reste servi : la tuile de
  l'accueil lit `/boutique/signals`.
