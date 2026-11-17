# Décisions prises par défaut — 2026-11-18

Une ligne par décision imprévue : ticket, question, choix, raison. À valider par Thomas avant de rejoindre
`docs/decisions/`. Formulaire à copier-coller en fin de fichier.

| Ticket | Question | Choix | Raison |
|---|---|---|---|
| Lot 18 (TOK-85) | Les trois classes du brief se recouvrent : presque tout verdict « demande la tranche 0 ». Comment classer chaque test dans une seule classe ? | Ordre de priorité : (1) `un_seul_avis` si le test dépend de R08, R27 (b) ou R34 ; (2) `non_executable_sans_regles` s'il ne dépend d'**aucun** point relu (verdict tiré du livret ou du texte, à coder en tranche 0) ; (3) `regles_confirmees` sinon. T68 (« non couvert ») va en (3) : son verdict se vérifie dès aujourd'hui sans règle de jeu. Résultat : **54 / 6 / 12**. | La seule lecture qui donne trois classes non vides et utiles à la tranche 0 : quels tests peuvent servir de vérité (54), lesquels sont fragiles (6), lesquels n'ont aucun appui relu (12). Le classement est calculé, pas écrit à la main : changer la règle est une ligne dans `moteur_combos/classement.py`. |
| Lot 18 (TOK-85) | Le YAML écrit « R27 » sans dire (a) ou (b). | Partie lue dans l'action de chaque test et déclarée dans `classement.py` : T32 → R27a (nom temporaire de COCA), T33 et T62 → R27b (bannissement en coût, déclencheurs). Seuls T33 et T62 passent en « un seul avis ». | La confiance du point diffère par partie (« moyenne (a), basse (b) ») ; ne pas modifier le YAML écrit à la main. |
| Lot 18 (TOK-85) | T72 est hors pilote (adversaire) **et** dépend de R08 : quelle classe ? | `un_seul_avis` (la priorité 1 l'emporte) ; le périmètre reste visible dans `cb_test_situation.perimetre`. | L'avertissement de confiance est l'information la plus utile ; T72 ne sera de toute façon pas joué en tranche 0. |
| Lot 18 (TOK-85) | La mémoire du tour du YAML est en phrases (« verrou NADIR », « effet d'ALUBER activé ce tour ») : la traduire en limites et verrous formels ? | Non. Seule « Invocation Normale utilisée » est structurée ; le reste est gardé **en texte libre dans l'état** (il compte dans l'empreinte) et le départ est marqué « partiel » : 24 départs partiels, 48 complets. | Traduire « NADIR activée » en limite demande de savoir quelle forme de limite porte NADIR : c'est de la formalisation (tranche 0). D7 prévoit le texte libre jusque-là. |
| Lot 18 (TOK-85) | Le YAML ne donne pas la case des cartes sur le terrain, alors que l'état doit toujours la porter (D3 révisée). | Convention de départ déclarée : monstre du Main Deck → première zone principale libre ; premier monstre de l'Extra Deck → Zone Monstre Extra gauche, les suivants → zones principales ; Magie/Piège → première zone libre. Chaque placement est listé dans le rapport du départ. | Aucun test actuel ne lit la case (jeu-de-tests-branded.md § 4) ; la convention est visible et se change en un endroit (`situations.py`). |
| Lot 18 (TOK-85) | Un monstre de l'Extra Deck sur le terrain sans annotation : « correctement invoqué » ? Une Invocation Normale annoncée sur un monstre sans « Invocation Normale utilisée » en mémoire (T22) ? | Oui dans les deux cas, comme **déductions de cohérence déclarées** dans le rapport du départ. Au Cimetière sans annotation, le drapeau reste « non précisé » (`None`), jamais `False` par défaut. | Un monstre de l'Extra Deck n'arrive sur le terrain que par une invocation ; un monstre Invoqué Normalement ce tour a consommé l'Invocation Normale. Au Cimetière, l'absence d'information ne doit pas devenir une affirmation (T22 en dépend). |
| Lot 18 (TOK-85) | Archétype « par le nom » : mot entier ou sous-chaîne ? | Sous-chaîne sensible à la casse : « Despian Luluwalilith » est « Despia ». Vocabulaire des archétypes extrait des textes du deck (« "X" monster/card/Spell… », moins les noms de cartes). ⚖ À confirmer (R11 a confirmé « par le nom », pas le cas « Despian »). | Lecture habituelle des noms d'archétype ; aucun test actuel n'en dépend (LULU est dans l'Extra Deck, hors des zones cherchées par BOPENING). |
| Lot 18 (TOK-85) | Le relecteur cite trois formes de « une fois par tour » ; les textes du deck en montrent cinq. | Cinq formes enregistrables : les trois du relecteur + « 1 "X" effect per turn, and only once that turn » (`par_nom_carte`) + « Special Summon "X" once per turn this way » (`invocation_par_nom`). Le harnais vérifie que les 39 clauses du deck tombent dans l'une d'elles. | « Le schéma doit pouvoir enregistrer les trois » : les deux variantes existent dans le deck (Aluber, BHIGH, AEON ; Incredible Ecclesia), les omettre aurait obligé à changer le schéma en tranche 0. |
| Lot 18 (TOK-85) | Les Zones Monstre Extra appartiennent-elles au joueur ? | Non : elles sont au terrain, communes aux deux joueurs ; chaque occupant porte son contrôleur. Colonnes enregistrées : `ZME_G` = colonne 2, `ZME_D` = colonne 4. | Structure du terrain, pas une règle d'action (aucune contrainte « une seule ZME par joueur » n'est codée). Le relecteur insiste sur l'importance de la ZME, y compris pour l'adversaire. |
| Lot 18 (TOK-85) | Où mettre `combos.db` dans un worktree ? | `data/combos.db` du checkout courant (worktree ou dépôt principal), reconstruite par le harnais ; `--base` pour en choisir une autre. | Base de travail locale, régénérable ; ne pas écrire dans le dépôt principal depuis un worktree (une autre session y travaille). |
| Lot 18 (TOK-85) | Le texte des cartes dans `combos.db` ? | Oui, copié dans `cb_card.text` (base ignorée par Git, jamais commitée). | Le schéma fige le texte formalisé (errata) ; un texte changé remet le statut à `non_traitee`. |
| Lot 18 (TOK-85) | Relecture du schéma par `gardien-donnees` : 3 défauts bloquants et ≈ 15 mineurs. | Bloquants corrigés (garde-fou par chemin résolu, casse, lien et tables étrangères ; migrations `migrations/NNN.sql` avant tout changement de version ; `copy_index` dans la clé de `cb_step_card`). Mineurs corrigés : index, `CHECK` sur `verified_by` et `status_reason`, unicité des relations, empreinte hexadécimale, URI échappée, errata qui remet les effets à zéro, renumérotation refusée, purge des situations. **Non corrigé** : déclencheur de cohérence entre `cb_combo_step.actor_card_id` et `cb_transition` (aucune écriture de combo avant l'exploration ; noté dans `schema.sql`). Version de schéma laissée à 1 : aucune `combos.db` n'a été distribuée, celle du worktree a été reconstruite. | Corrections mécaniques et réversibles ; le déclencheur se décidera avec l'écrivain des combos. |
| Lot 18 (TOK-85) | Le tableau des points de règle cite T49 pour R11, le YAML de T49 ne liste que R02. | Signalé par le harnais (avertissement), YAML non modifié. Sans effet sur la classe (R11 est confirmé). | Écart de donnée dans un fichier écrit à la main ; à trancher par l'auteur du jeu de tests. |

## Formulaire

```
Lot 18 — classement des 72 tests
[x] Priorité un_seul_avis > aucun point relu > règles confirmées (54 / 6 / 12), T68 en « confirmées »
[ ] Les tests sans point de règle comptent comme « règles confirmées » (vide = rien à contester) : 66 / 6 / 0
[ ] Hors pilote d'abord (T71, T72 en « non exécutable »), puis un seul avis, puis le reste
Commentaire libre :

Lot 18 — mémoire du tour en texte libre (24 départs partiels)
[x] Garder le texte libre jusqu'à la tranche 0, qui formalise en même temps que les cartes
[ ] Formaliser dès maintenant les phrases récurrentes (« verrou X », « X activée ce tour »)
Commentaire libre :

Lot 18 — archétype par sous-chaîne du nom (« Despian » ⊃ « Despia »)
[x] Sous-chaîne, à confirmer par le prochain relecteur ou l'oracle
[ ] Mot entier (Despian Luluwalilith ne serait pas « Despia »)
Commentaire libre :

Lot 18 — écart T49 / R11
[x] Ajouter R11 aux `regles` de T49 dans tests-branded.yaml (le texte de TFTV « treated as Branded » est en jeu)
[ ] Retirer T49 de la colonne « Tests » de R11
Commentaire libre :
```
