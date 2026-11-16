# 0014 — Moteur de combos : n'afficher que ce qui est démontré, « exhaustif » = couverture publiée

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (réunion du 2026-11-16)
- Tickets : TOK-84

## Contexte
Le moteur s'appuie sur des effets de cartes formalisés par un LLM ; certains seront incertains ou non formalisables.

## Options
- Non consignées en tant qu'options dans la source.

## Décision
Un combo contenant une carte non vérifiée reste visible mais étiqueté « non vérifié » et séparé des combos démontrés. « Exhaustif » signifie 100 % des cartes classées avec un statut et un taux de couverture publié, pas la promesse que tout est exécutable. Erreur tolérée : borne haute inférieure à 5 % à 95 % de confiance (environ 60 cas indépendants par strate à risque). Le système recense sans juger.

## Raison
Raison non consignée au-delà de la formulation des décisions.

## Conséquences
Alimente les statuts de formalisation (D6) et la propagation du « non couvert » (D5).

## Sources
- `docs/moteur-combos/decisions-2026-11-16.md` (§ 4)
