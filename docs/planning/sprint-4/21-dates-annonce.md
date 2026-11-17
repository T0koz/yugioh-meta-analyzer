# 21 — Collecte des dates d'annonce des banlists (TCG et OCG)

Modèle : Sonnet. Sous-agent : `gardien-donnees`. Décision TOK-115 du 17/11, question 4.
Aujourd'hui seule la date d'entrée en vigueur est connue (`banlist_history.effective_date`). Ajouter la date
d'annonce (sources publiques citées : site officiel Konami, Yugipedia), dans une colonne ou table nouvelle, par script
de `scripts/` (sauvegarde, transaction), rejoué par la chaîne du lundi. Couvrir les 20 listes du backtest au minimum.
Puis mesurer, avec `scripts/diagnose_ban_radar.py`, l'effet de classer « la veille de l'annonce » au lieu de « la
veille de l'entrée en vigueur ». Rapport + formulaire ; rien d'affiché ne change sans Thomas.
