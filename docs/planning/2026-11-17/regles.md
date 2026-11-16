# Règles communes à toutes les sessions de la nuit

- Français. Pas de push, jamais. Pas de fusion dans `main`. Commits locaux sur ta branche autorisés cette nuit
  (messages en français, préfixe `feat(TOK-xxx):` etc., terminés par les lignes d'attribution exigées par le projet) ;
  Thomas relit tout le matin.
- Une seule session active à la fois. Tu ne lances aucune autre session ni sous-agent sans l'accord de
  l'orchestrateur ; sous-agent autorisé seulement pour `data-scientist-ygo` (chiffres) et `gardien-donnees`
  (écriture en base), en lecture seule sauf mention contraire.
- Tu ne touches qu'à ta section de `BACKLOG.md` et de `context.md` (une section par ticket).
- Le worktree n'a ni base ni `node_modules` : `npm install` dans `frontend/`, backend avec
  `YGO_DB_PATH=<dépôt principal>/data/serving.db`, `yugioh.db` en lecture seule (`file:…?mode=ro`).
- `python scripts/check.py` doit passer avant de rendre la main. Une étape ignorée n'est pas réussie : dis-le.
- Next.js 16 : lis `node_modules/next/dist/docs/` avant de toucher au cache, à `fetch`, aux transitions.
- Pièges déjà documentés : aucun texte du premier écran ne démarre à opacité 0 ; n'utilise que les composants et
  tokens existants (`enter`, `Reveal`, `CardArt`) ; toute page exporte son `metadata` ; mesure le LCP avec
  `LH_THROTTLING=devtools`.
- Décision imprévue : applique la recommandation par défaut du brief (ou la plus prudente et réversible), note-la
  dans `docs/planning/2026-11-17/decisions-prises.md` (ticket, question, choix, raison). Si elle est
  irréversible ou hors périmètre : arrête-toi et écris le formulaire à cocher.
- Preuve : captures avant/après (script Playwright du projet) pour tout changement visible, chiffres mesurés
  pour chaque critère. Pas d'« à vue d'œil ».
- Compte rendu de fin de session, bref : critères atteints ou non (avec mesures), fichiers touchés, pièges,
  décisions prises par défaut.
