# Avancement de l'audit front

Dernière mise à jour : 2026-11-16 (session 1) — **mission terminée, en attente de la validation de Thomas.**

## Fait
- Étape 1 : `1-audit.md` (captures desktop 1440 et mobile 375 de toutes les pages, mesures dev et production, contrastes, cause des 15 s).
- Étape 2 : `2-benchmark.md` (30 sites ouverts, 5 inaccessibles signalés), captures dans `captures/bench/` (exclues de git).
- Étape 3 : `3-proposition.md` + `prototype/index.html` (vérifié desktop, mobile, mouvement réduit).
- `rapport.md` (synthèse + liens + annexes).
- `docs/bench-design.md` remplacé par un renvoi vers ces fichiers.

## Reste
- Rien côté audit. Décisions de Thomas attendues (formulaire transmis par l'orchestrateur).
- Aucune implémentation tant que la direction n'est pas validée.

## Prochaine action
Après validation : commencer par le « jour 1 » de la feuille de route (`3-proposition.md`, section 10), en premier la fusion de TOK-83 et la correction du 500 de `/early-signals`.

## Pour reprendre les mesures
- Scripts dans le scratchpad de la session (`audit.py`, `bench.py`) : ils peuvent avoir disparu. Ils utilisent Playwright de `.venv` et lisent `PerformanceObserver`, Navigation Timing et Resource Timing.
- Lighthouse n'est pas installé.
- Le serveur `next dev` du port 3000 appartenait à Thomas : non arrêté. L'API lancée pour l'audit a été arrêtée.
