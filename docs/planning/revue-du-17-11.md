# Revue du matin — 17/11/2026 (à faire avec Thomas)

## 1. État de la nuit
- [x] Relire `etat.md`, les comptes rendus et `2026-11-17/decisions-prises.md`
- [x] La reprise automatique a-t-elle fonctionné ? → **non démontrée** : la file s'est arrêtée à 2 h 43, rien de noté ensuite
- [x] Vérifier que l'étape 2 du lot 15 n'a pas écrit le verdict de la page historique → retiré (« lecture en attente du diagnostic TOK-115 »), noté dans `etat.md`
- [ ] Confirmer que c'est bien Thomas qui a répondu au formulaire de la charte (vers 0 h 20)
- [x] Pourquoi les lots front sont passés de Fable à Opus → consigne de Thomas du 16/11 au soir (`decisions-prises.md`) ; à reporter dans `CLAUDE.md` si elle est durable

## 2. Validations de Thomas
- [x] Formulaire TOK-115, audit de rigueur, textes du lot 16, source de TOK-86 (11 h 39 à 11 h 45)
- [x] D1 à D7 du moteur de combos (11 h 50, options pré-cochées) → lot 18 débloqué
- [x] Les 14 décisions « à valider » de `docs/decisions/` (11 h 55, toutes acceptées ; ticket TOK-116 créé)
- [x] Formulaire du déploiement (`docs/deploiement.md`, §9) : R2, site public non diffusé, voie 2 (réponses du 17/11, lot 14 bis)
- [ ] Trous de la nuit : carte en double → brief du lot 11 (déjà refait ?), date du graphe → ignorée

## 3. Git et ménage
- [x] Commiter les fichiers de planning modifiés (`d09a4ed`, 23 fichiers)
- [x] Appliquer `a-appliquer-a-la-revue.md` à `CLAUDE.md` : journal de décisions et plan mode y étaient déjà (lot 13) ;
      ajoutés le 17/11 : précision de la règle d'or (deuxième session pendant une attente passive) et principe de rigueur statistique
- [x] `python scripts/check.py --all --visuel` : vert le 17/11 vers 12 h 10 (46 tests sur chaque base, 19 tables servies,
      51 captures identiques, backtest aux rangs de référence) ; 13 textes signalés par `check_copy.py` (non bloquant, lot 16)
- [x] Fusion de `claude/front-nuit-17-11` dans `main` (`--no-ff`, `bd22ae8`), dépôt principal revenu sur `main`
- [ ] Push de `main` par Thomas (120 commits d'avance sur `origin/main`)
- [ ] Supprimer les worktrees des lots terminés (`lot11`, `lot12` : fusionnés et propres ; `lot06-benchmark` porte le
      rapport de la tâche de fond, branche `claude/fond-2026-11-17-b80f1e` non fusionnée) et les branches fusionnées
- [ ] Mettre Linear à jour (lots fusionnés → Done)

## 4. Hors projet code
- [ ] Questionnaire du juge envoyé au pote (doc « Relecture des règles Yu-Gi-Oh! — Branded »)
- [ ] Exemples pour l'animation du hero (captures + ce qui plaît)
- [ ] Rouvrir à la main les sites bloqués du benchmark (si utile)
