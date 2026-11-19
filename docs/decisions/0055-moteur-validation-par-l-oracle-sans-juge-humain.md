# 0055 — Moteur de combos : validation par l'oracle, plus de juge humain sauf exception

- Date : 2026-11-18
- Statut : acceptée
- Décidé par : Thomas (avec Claude, session d'orchestration du 18/11)
- Tickets : TOK-84, TOK-89, TOK-118, TOK-119, TOK-86

## Contexte
J1 (taux d'erreur chiffré) et J2 (combos des guides retrouvés seuls) prévoyaient une vérification humaine : relecture à
l'aveugle de 20 effets et transcription de 5 combos par un joueur. Le seul relecteur disponible (relecture 1, 17/11) ne
peut plus être sollicité. Thomas, le 18/11 : « on peut considérer qu'il n'y aura plus de validation humaine, ou alors de
manière vraiment très très rare ». Échéance de la règle d'arrêt inchangée : J2 avant le 13/01/2027 (décision 0053).

## Options
- A : attendre un juge humain (bloque J1 et J2 sans date).
- B : faire relire par d'autres sessions LLM (deux lectures LLM du même texte : erreurs corrélées, avis `data-scientist-ygo` du lot C2).
- C : l'oracle Project Ignis comme référence de validation, avec ses limites déclarées, et un lot humain rare pour ce
  qu'il ne peut pas trancher.

## Décision
Option C.
- **`verifiee` = accord avec l'oracle** sur des situations qui exercent chacun des effets de la carte (le schéma le
  permettait déjà : « accord avec l'oracle, ou relue par un juge »).
- **J1** : le taux d'erreur est mesuré contre l'oracle, sur l'échantillon déjà tiré (20 effets, graine 20260118) et sur
  toutes les situations J1, avec borne de Wilson à 95 %. Il est écrit « mesuré contre l'oracle », jamais « vérifié par un juge ».
- **J2** : les 5 combos supplémentaires sont transcrits de guides publics par une étape séparée, **avant** toute
  lecture du code du moteur ; cible et jalons figés et commités (empreinte) avant l'exécution ; chaque séquence trouvée
  est rejouée pas à pas dans l'oracle (légalité de chaque action).
- **Questions résiduelles** (l'oracle ne tranche pas : texte TCG différent du texte OCG de sa base, comme R23 ; règles
  sans situation jouable) : rangées dans un lot unique, préparé pour environ 15 minutes de lecture, envoyé à un joueur
  seulement si Thomas le décide. Sans réponse, les cartes concernées restent `formalisee` (« non vérifié »), jamais
  `verifiee`.
- **Isolement AGPL inchangé** : la session qui joue l'oracle ne lit pas `moteur_combos/` ; aucune session du moteur ne
  lit `~/code/oracle-ignis/` ; seul `docs/moteur-combos/reponses-oracle.md` (résultats) circule. Les deux travaux vont
  donc dans deux jalons, deux sessions.

## Raison
L'oracle est une implémentation indépendante des règles, écrite par d'autres, déjà installée (lot 17) et déjà en
accord sur 27 des 30 situations J1 : c'est le seul contrôle indépendant disponible sans humain. Ses limites sont
connues et déclarées (textes OCG non officiels de sa base, options de règles, pas de documentation lue).

## Conséquences
- Ce qui disparaît : la page interne « pour le juge » (formulaire C3) et le kit de relecture humaine complet.
- Un accord avec l'oracle ne prouve pas l'absence d'erreur quand l'oracle et le moteur lisent la même ambiguïté de la
  même façon ; le rapport J1 le dit.
- Jalon n°5 (côté moteur, sans oracle) puis jalon n°6 (côté oracle, isolé), voir `docs/planning/etat.md`.
