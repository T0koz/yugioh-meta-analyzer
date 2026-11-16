# À appliquer à la revue du matin (fichiers suivis, non modifiés pendant que l'orchestrateur tourne)

## CLAUDE.md — ajouter dans « Avec qui tu travailles »
- **Journal de décisions** : toute décision structurante (architecture, données, design, process) est notée dans
  `docs/decisions/` (une note par décision, modèle et index dans `docs/decisions/README.md`). Une décision prise
  par défaut en autonomie va d'abord dans le `decisions-prises.md` du jour, et rejoint le journal après validation.
- **Plan mode** : ne le propose à Thomas que lorsqu'il est vraiment la solution (changement large, risqué ou mal
  cadré, que le brief n'a pas préparé), jamais par défaut ni par habitude.
- **Règle d'or (précision du 17/11)** : un lot à la fois ; une deuxième session seulement si la première est
  bloquée par une attente longue et passive (téléchargement, build long, attente de validation), sur des fichiers
  différents, et jamais plus de deux sessions en même temps.
- **Rigueur statistique (principe de Thomas, 17/11)** : tout score, prédiction, seuil ou libellé affiché est
  estimé à partir des données, validé hors échantillon dans le temps, comparé à une méthode naïve (hasard,
  popularité, « le mois dernier ») et affiché avec son incertitude. Un réglage à la main n'est acceptable que
  s'il est déclaré comme tel. Toute session qui crée ou modifie un score sollicite `data-scientist-ygo`.
