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
| C1 (TOK-90) | Quel combo pour la tranche 0 ? | `Aluber` (Invocation Normale) → recherche de `Branded Fusion` → Fusion de `Rindbrumm` avec `Fallen of Albaz` + `Tri-Brigade Springans Kitt` pris dans le Deck → `Kitt` (envoyé au Cimetière) rappelle `Albaz` en Défense ; le déclencheur d'`Albaz` rappelé est vu et écarté (aucun monstre adverse, R01). Deux transitions (T01 puis T15). | Ouverture Branded la plus courante (`Aluber` cherche `Branded Fusion`) ; couvre Invocation Normale, Invocation Spéciale, Fusion, effet déclenché, Magie Normale, chaîne, trois formes de limite (`par_nom_carte`, `activation_par_nom`, `par_nom_effet`) ; n'a besoin ni de T37 (R23 contredit par l'oracle) ni de l'ordre de déclencheurs simultanés (R22). |
| C1 (TOK-90) | Quels tests négatifs ? | Hors timing : **T60** (`Nadir Servant`, Magie Normale, en réponse à `Aluber`). Effet déjà utilisé : **T04** (2e `Aluber`, limite « 1 effet par tour »). Matériel manquant : **T11** (`Branded Fusion` sans aucun « Fallen of Albaz » disponible). Non couvert : **T68** (`Lava Golem`). Exécutés en plus, sans règle supplémentaire : T03, T05, T08, T09. | Un test par catégorie du brief, tous sur les cartes du combo ; les quatre en plus tombent des mêmes règles. |
| C1 (TOK-90) | D5 (« non couvert ») : à quel grain l'appliquer ? | **Effet par effet.** Une formalisation déclare tous les effets d'une carte ; une résolution peut rester `NON_CODEE` (option « non couverte », la choisir renvoie `non_couvert`). Statut `brouillon` = effets déclarés, une résolution manquante (`Rindbrumm`, effet 1 : annuler l'effet d'un monstre de l'Extra Deck) ; une carte `non_traitee` jouée, déplacée ou choisie → `non_couvert`. | Sans ce grain, `Rindbrumm` (cible du combo) aurait dû être formalisé en entier, y compris une annulation que rien dans la tranche 0 n'exerce : du code non testé. Le moteur sait quand l'effet pourrait s'activer (condition écrite) et refuse de le jouer. |
| C1 (TOK-90) | Effets qui supposent l'adversaire (`Aluber` effet 2, `Rindbrumm` effet 2, Fusion d'`Albaz` avec des monstres adverses) ? | Marqués `HORS_PERIMETRE` : condition écrite (fausse au tour 1 du pilote), résolution non écrite ; s'ils devenaient activables, le moteur renverrait `hors_perimetre`. Ils comptent comme écrits pour le statut `formalisee`. | Le pilote exclut l'adversaire (§ 2.5) ; les écrire maintenant serait coder au-delà du besoin. |
| C1 (TOK-90) | Une carte non formalisée peut-elle produire un « illégal » ? | Oui, **seulement** quand l'illégalité ne dépend que de ses caractéristiques imprimées : une Magie Normale ne répond à aucun effet (T60, `Nadir Servant`). Tout résultat positif sur une carte non formalisée reste `non_couvert`. | Une Magie Normale a toujours la vitesse 1 : le verdict ne peut pas être faux. Le contraire aurait rendu T60 inexécutable sans formaliser `Nadir Servant`. |
| C1 (TOK-90) | Cartes non formalisées en main pendant un combo (`Ash Blossom`, `Ghost Ogre`, `Droll & Lock Bird`) ? | En exécution dirigée, le résultat est donné **avec des réserves** (« auraient pu agir ») ; les options de légalité inconnue (Fusions dont la ligne de matériels n'est pas formalisée, paires avec une carte non formalisée) sont listées à part (« liste peut-être incomplète »). L'arrêt `non_couvert` du cas 2 reste pour l'exploration. | Sinon toute main de départ du jeu de tests (qui contient presque toujours des cartes d'interruption) serait « non couverte ». Rien n'est caché : réserves et options indéterminées sont dans le résultat. |
| C1 (TOK-90) | Lignes de matériels des monstres Fusion non formalisés ? | Lues dans le texte sans formalisation : nombre d'éléments (« 2+ » compris) et éléments qui ne sont qu'un nom entre guillemets. Un élément décrit en mots ne se lit que par la formalisation (seul `Rindbrumm` en a une). | Suffit à trancher T09 (3 matériels), T11 (aucun « Fallen of Albaz ») et « aucune Fusion avec un seul matériel » (déclencheur d'`Albaz`) sans formaliser les 11 autres Fusions. |
| C1 (TOK-90) | Placement et position d'une Invocation Fusion ? | Deux décisions du joueur : Zone Monstre Extra / zone principale (D3), puis Attaque / Défense. Première Zone Monstre Extra libre, **une seule par joueur** (règle ajoutée : le lot 18 ne la codait pas). Colonnes non énumérées (`Rindbrumm` ne lit pas la position). | La position est un choix du joueur pour une Invocation Spéciale sans position imposée ; la limite d'une Zone Monstre Extra par joueur évite un placement illégal. |
| C1 (TOK-90) | Plusieurs effets déclenchés en même temps ? | `non_couvert` (« ordre de chaîne non codé »). | R22 et le réglage `FIRSTTRIGGER` signalé par l'oracle ne sont pas tranchés ; aucun test de la tranche n'en a besoin. |
| C1 (TOK-90) | Mémoire du tour en phrases ? | Deux phrases traduites dans `scenarios.py`, pour les cartes formalisées seulement : « effet d'X activé ce tour » (quand tous les effets de X portent la même limite) et « verrou X : Extra Deck = Fusion seulement ». Le reste demeure en texte libre ; un verdict n'est accepté malgré des faits libres que si le scénario dit pourquoi ils ne jouent pas (T04 : une limite consommée ne redevient disponible par aucun fait). Un verrou en phrases rend toute Invocation depuis l'Extra Deck indécidable. | Suite de la décision du lot 18 (« la tranche 0 formalise en même temps que les cartes ») ; traduction minimale, déclarée. |
| C1 (TOK-90) | Harnais : statut « exécuté » ? | Valeur `verifie` de `cb_test_situation.status` réutilisée (affichée « exécuté ») : aucun changement de schéma, donc pas de `gardien-donnees`. Classe « confirmé par le relecteur et l'oracle » non ajoutée. Les transitions et les pas restent en mémoire (pas d'écriture dans `cb_transition`, `cb_step`, `cb_effect`). Les classes de T03, T04, T60 restent `non_executable_sans_regles` (la classe dit l'absence de point relu, pas l'exécution). | Changer le schéma demandait une migration et une relecture pour un mot ; l'écriture des transitions se décidera avec l'exploration (C3). |
| C2 (TOK-118) | Statut `formalisee` : suffit-il que toutes les résolutions soient écrites ? | Non : il faut aussi que **chaque effet du pilote ait été exercé par au moins un test exécuté** (situations du YAML ou situations J1), compté par le moteur (`regles.EXERCES`) ; sinon `brouillon` (« écrite, non testée »). Résultat : 37 `formalisee` après les 30 situations J1 (29 seulement sans elles). | Sens d'origine de D6 (`brouillon` = « proposée, non testée ») ; la règle de C1 (« résolution manquante ») aurait déclaré formalisées des cartes jamais jouées. |
| C2 (TOK-118) | Comment exercer les 27 effets que le YAML n'exerce pas ? | 30 situations nouvelles, `docs/moteur-combos/situations-j1.yaml`, **verdicts écrits par l'agent**, exécutées par le harnais, à faire rejouer à l'oracle (`situations-pour-oracle.md`). Le YAML écrit à la main n'est pas modifié. | Elles détectent les erreurs de code ; l'oracle les rend indépendantes. Ne pas mêler au jeu de tests relu par le juge des verdicts non relus. |
| C2 (TOK-118) | R22 (déclencheurs simultanés) : coder ? | **Codé** (le brief le permet) : mise en chaîne un par un, ordre libre, obligatoires d'abord, facultatifs laissables ; réglage par défaut de l'oracle, pas `FIRSTTRIGGER`. | T45 et T62 en dépendent ; le relecteur (« choisit l'ordre ») et l'oracle (réglage par défaut) concordent. |
| C2 (TOK-118) | R23 : `Incredible Ecclesia`, effet de Phase de Fin ? | **Obligatoire** (texte TCG de notre base) ; fin de tour illégale tant qu'il attend (T37). Désaccord avec l'oracle listé, non compté comme erreur. | Le texte TCG fait foi (brief). |
| C2 (TOK-118) | Taux d'erreur de J1 : méthode ? | Avis de `data-scientist-ygo` repris tel quel : unité l'effet ; 0/30 d'aujourd'hui publié comme **constat**, pas comme taux ; mesure = oracle sur les 30 situations J1 + relecture humaine à l'aveugle de **20 effets stratifiés 10/10** (graine 20260118), hors périmètre relus en exhaustif ; taux arbitré et pessimiste ; naïf = lecture directe par un LLM (1/34 le 17/11). **J1 non déclaré atteint** avant cette mesure. | Seule une vérification indépendante de l'auteur mesure une erreur de lecture. |
| C2 (TOK-118) | Cible qui déclare J1 atteint, écrite avant le tirage ? | **Borne haute de Wilson 95 % du taux arbitré ≤ 20 %** (0 erreur sur 20 → 16,1 %). | Sans cible écrite d'avance, le seuil serait choisi après le résultat. |
| C2 (TOK-118) | Statut `verifiee` dès maintenant pour les cartes dont tous les effets passent des situations rejouées par l'oracle ? | **Non** : aucune carte `verifiee` tant que l'oracle n'a pas rejoué les situations J1 et que la relecture n'est pas faite. | L'oracle a vérifié des verdicts de situations, pas la formalisation clause par clause. |
| C2 (TOK-118) | Points que le texte ne tranche pas (N01 à N13 : `Luluwalilith` sur sa propre sortie de l'Extra Deck, `Branded Opening` sans « Despia » dans le Deck, `Sprind` depuis la Zone Monstre Extra, déclarer DIVIN, retour d'`EDD`, `Cocatorium` matériel, effet résolu après destruction, cibler un monstre insensible, choisir un monstre insensible, remplacement de `Branded Opening` contre sa propre carte, « 1 other Mulcharmy », zones centrales d'`Albion`, `Golden Swordsoul` et son propre bannissement) ? | Un choix codé pour chacun, marqué ⚖ ; N01 répond « non couvert » ; DIVIN donne une option « indéterminée ». Liste dans `situations-pour-oracle.md` § 2. | Ne jamais présenter un choix non tranché comme une règle ; le « non couvert » reste disponible quand aucun choix n'est raisonnable. |
| C2 (TOK-118) | `Mulcharmy Fuwalos` : retour aléatoire en Phase de Fin si la main dépasse 6 ; défausse de fin de tour au-delà de 6 cartes ? | Non codés : la fin du tour répond « non couvert » dans ces cas ; la carte reste `formalisee` (la résolution de son effet est écrite). | Cas rares au tour 1 ; jamais un résultat faux. |
| C2 (TOK-118) | Mémoire du tour en phrases (24 départs partiels) ? | 13 motifs traduits de plus dans `scenarios.py` (verrous de `Nadir`, `White`, `Dogmatika Ecclesia` ; « X activée ce tour » ; « 1er / 2e effet de X utilisé » ; « un monstre Fusion (X) a été envoyé au Cimetière ce tour » ; envoyé sans invocation ; notes descriptives « Invocation Fusion par X »…). Plus aucun fait libre dans les 69 situations exécutées. | Une phrase n'est traduite que si elle n'a qu'une lecture ; chaque traduction est listée dans le résultat. |
| C2 (TOK-118) | Effets continus et de remplacement (`Dogma`, `Titaniklad`, `Albion` « ne sert pas de matériel », `Branded Opening` effet 2) ? | Genre `restriction` (ne s'active pas), codés dans le moteur (`insensible`, `bonus_atk`, `interdit_materiel_fusion`, `Partie.detruire`) et comptés comme effets du pilote. | Ils changent des résultats au tour 1 (T56, J24, J26, J29). |
| C2 (TOK-118) | Schéma de `combos.db` ? | Inchangé (statuts écrits dans les colonnes existantes) ; `gardien-donnees` non sollicité. Les situations J1 ne sont pas écrites dans `cb_test_situation` (réservée aux 72 situations du YAML). | Pas de migration pour un lot de formalisation. |
| C3 (TOK-119) | N04, seconde moitié : l'oracle refuse de déclarer un Attribut déjà porté ; le texte TCG ne l'interdit pas. | **Permis** (texte TCG d'`Aeon` et de `Mixousia`) ; DIVIN déclarable (oracle, adopté). | Le texte TCG fait foi (précédent R23) ; restriction probable du script de l'oracle ; sans conséquence de jeu (une liste de choix). Taux pessimiste du volet oracle de J1 : 3/57. |
| C3 (TOK-119) | N09 : la règle (effet sans cible qui choisit un monstre insensible) vaut-elle pour `Luluwalilith` 1, `Aeon` 1 et `Rindbrumm` 1, que l'oracle n'a pas joués ? | **Oui**, même correction que `Mirrorjade` 1. | C'est la lecture générale des règles (brief), pas un texte propre à une carte ; laisser deux comportements pour la même règle serait incohérent. À faire rejouer par l'oracle. |
| C3 (TOK-119) | Quels guides ? | 5 combos tirés de 6 pages masterduelmeta (juin-août 2026, 4 auteurs), les seules lisibles en texte ; tableurs en images écartés ; lignes `Aluber` / `Branded Fusion` proposées « à faire confirmer par un joueur », non comptées. | Ne rien inventer (brief) ; les pages sont datées et publiques. |
| C3 (TOK-119) | Les guides passent par des cartes absentes (`Albion the Branded Dragon`, `Branded Retribution`, `Branded in Red`, `Khaos Starsource`). | Mesure **jusqu'à la dernière étape réalisable** ; un coût payé par une carte absente est payé par une carte de la liste qui remplit la même clause (substitution déclarée) ; la suite est classée « manqué : carte absente de la liste ». | Même règle que pour `Lubellion` (D1) ; aucun guide relevé ne passe par `Lubellion`. |
| C3 (TOK-119) | Main de départ d'un combo « à une carte » ? | La carte seule ; les 4 autres cartes (cartes de réponse) **retirées du jeu**. | Premier essai avec les 4 cartes en main : `Ghost Ogre` servait de matériel de Fusion (G2), le combo n'était plus « à une carte ». Les mains de 5 cartes sont mesurées à part (tirage au hasard). |
| C3 (TOK-119) | Filtres d'exploration (D4) ? | 8 filtres déclarés, enregistrés dans `cb_run.filters_json` (`moteur_combos/exploration.py`, `FILTRES_DISPONIBLES`) : pas de réponse à ses propres maillons, cartes de réponse jamais activées ni Invoquées Normalement, position Attaque, Zone Monstre Extra d'abord, pas de changement d'Attribut, pas d'annulation de soi, `Aeon` sans bannissement, pioche à une branche. | Sans eux, l'exploration double à chaque position, chaque réponse possible ; chacun est levable. |
| C3 (TOK-119) | Comment juger « retrouvé » ? | Deux niveaux : **plateau** (la cible du guide, conditions d'inclusion par zone) et **séquence** (les jalons du guide, actions clés dans l'ordre, sous-suite). Deux recherches : dirigée (A*) et en largeur sans cible ; plus un joueur au hasard comme méthode naïve. | Sans jalons, G3 remplissait la cible par un autre chemin (Three Champions envoyée en coût) ; avis de `data-scientist-ygo` (publier les deux taux, largeur en tête, « 4 sur 5 » et jamais « 80 % »). |
| C3 (TOK-119) | Que stocker dans `combos.db` ? | Les chemins retenus seulement : le chemin vers la cible (et vers la séquence), et pour chaque main réaliste un chemin le plus court par plateau final distinct (200 au plus) ; compteurs du parcours dans le rapport. Schéma inchangé (`gardien-donnees` non sollicité). | Le graphe complet fait des centaines de milliers d'arêtes ; les requêtes « A puis directement B » et « passe par X » portent sur les combos. |
| C3 (TOK-119) | Verdict J2 ? | **« Atteint sous réserve », horloge du 13/01/2027 maintenue** (avis `data-scientist-ygo`) : J2 plein demande cible et jalons figés avant exécution (par un humain ou l'oracle), 5 combos de plus d'autres auteurs, un essai à 5 cartes, et battre nettement le joueur au hasard. | n = 5, guides non tirés au hasard, cible et jalons écrits par l'agent qui connaissait la réponse. |
| Orchestrateur | Lancer C3 tout de suite, ou d'abord faire rejouer les situations J1 par l'oracle ? | D'abord l'oracle (lot C2 bis, Sonnet, seul), puis C3. Pas de deuxième session : aucune attente passive dans la chaîne. | Une erreur de formalisation trouvée par l'oracle doit être corrigée avant que l'exploration ne s'appuie dessus ; le brief de J1 prévoit la comparaison à l'oracle. |
| Lot 16 (textes) | Accent du titre neutre de l'accueil (`TITLE`, mots révélés un à un) ? | « *TCG et OCG* » en italique de marque (`Em`), dans le h1 et dans l'image de partage. | Le titre neutre ne porte plus de mesure ; l'accent souligne les deux formats que le graphique compare. |
| Lot 16 (textes) | Surtitre « Méta Yu-Gi-Oh! · données au … » au-dessus d'un h1 « Méta Yu-Gi-Oh! TCG et OCG » ? | Surtitre → « YGO Meta · données au … » ; surtitre de l'image de partage → « YGO Meta · decklists de tournoi ». Texte alternatif de l'image : titre neutre puis phrase de corrélation de T01. | Sinon le même nom se lit deux fois de suite ; aucun chiffre changé. |
| Lot 16 (textes) | T18 demande « {n} cartes TCG notées », l'API ne sert pas ce total. | « Cartes TCG notées de 0 à 100 sur six critères, d'après {n_decks} decks de tournoi des 6 derniers mois ; les 50 premières sont affichées. » | Aucun changement d'API pour un lot de textes (le total demanderait un champ servi et `gardien-donnees`). |
| Lot 16 (textes) | B02 à B09 : comment remplacer le tableau de 4 listes de l'accueil ? | Tableau de 2 lignes (TCG, OCG) : cartes touchées dans le top 25 de la veille, Ban Radar contre part des decks, en barres recalibrées sur le maximum ; listes où le Ban Radar fait mieux ; puis rang médian et phrase sur le hasard ; lien vers l'Historique dans la source. Chiffres figés `SITE_FACTS.banTop25` (comme le reste du bloc), relevés le 18/11 dans `ban_backtest_lists` de `serving.db` (29/16, 41/18, 6-1-3, 9-1-0, rang médian 3 et 8 sur 10). | La charte veut que le graphique explique ; l'accueil n'appelle pas l'endpoint de l'historique et en ajouter un appel changerait les captures et la charge de la page. |
| Lot 16 (textes) | Verdict TOK-115 : quelle formulation, et où ? | Texte du point 5 validé, écrit une fois (`lib/ban-verdict.ts`) : onglet Historique (sous le bilan) et `/methode` (mesures dans « Résultat » de la section Ban Radar, phrase sur le hasard dans « Lecture » de la section historique, pour ne pas répéter). Encart du Radar : formulation B12 (même chiffres, « écart non établi »). Dans l'Historique, le verdict n'est affiché que si les listes servies redonnent les mêmes sommes. | Une phrase qualitative (« plus », « moins bien ») ne se recalcule pas : mieux vaut la masquer que la laisser fausse après la prochaine banlist. |
| Lot 16 (textes) | B24, B27 : « top 25 TCG : 30 cartes avec, 28 sans » contredit le 29 affiché (le diagnostic départage les égalités autrement). | « le retirer change de 2 le nombre de cartes touchées dans le top 25 TCG ». | Même mesure (30 → 28), sans chiffre absolu qui contredise le bilan. |
| Lot 16 (textes) | B18 : déplacer la phrase de légende au-dessus de la liste ? | Laissée dans l'encart. | La légende en ligne existe déjà sous la première carte (`CriteriaLegend`). |
| Lot 16 (textes) | T35, T36 : écrire « 15 % » en dur ? | Calculé depuis `MIN_JACCARD` (`app/graph/page.tsx`). | Le seuil affiché suit le seuil appliqué. |
| Lot 16 (textes) | Titre du simulateur coupé au trait d'union (« co- / occurrences ») sur mobile. | « co-occurrences » insécable (`whitespace-nowrap`). | Lisibilité ; aucun texte changé. |
| Lot 16 (textes) | Temps passé. | ≈ 1 h 15 de session (lecture, application, captures, vérification, documentation). | Note demandée par le brief. |
| Orchestrateur (Linear, 18/11 matin) | Formulaire « Organisation de Linear » du 17/11 (recommandation pré-cochée), appliqué sur la consigne de Thomas « commence par orga linear ». | Groupe d'étiquettes « Sujet » (6 valeurs) ; 2 jalons dans le projet : « File de nuit 16-17/11 » et « File du 18/11 (moteur de combos) » (échéance 13/01/2027) ; numéro de lot en première ligne. **Done** = fusionné dans `main` (TOK-55, 92, 99, 100, 101, 103, 106, 114) ; **In Review** = fusionné dans `claude/moteur-18-11` seulement (TOK-86, 90, 117, TOK-128 lot 16) ; **In Progress** = jalon pas encore atteint (TOK-118 J1, TOK-119 J2) ou en cours (TOK-122) ; **Todo** = dans la file (TOK-120, 121, 123). Tickets créés après coup : TOK-124 (lot 8), 125 (lot 13), 126 (lot 15), 127 (lot 19), 128 (lot 16). Les anciens tickets terminés ne sont pas reclassés, sauf ceux du moteur (TOK-85, 87, 89). | Distinguer ce qui est dans `main` de ce qui attend la revue. Sujets mis par défaut : Phase C (TOK-56 à 66) et affiliation (TOK-37) en Front, TOK-121 (dates d'annonce) en Données et pipeline. **TOK-91** (tier list maison) semble couvert par TOK-97 (tier list calculée à la volée) : laissé en Backlog, à fermer par Thomas s'il confirme. |
| Lot 20 (A1) | Où mettre le calcul corrigé des signaux précoces ? | `scripts/build_early_signals.py`, branché dans `refresh_all.py` à la place du notebook 11, qui n'écrit plus en base. | Règle du projet : un calcul qui écrit en base va dans `scripts/` ; une seule source. |
| Lot 20 (A1) | « Cartes déjà en méta exclues » : quelle règle ? | Jouées dans ≥ 3 % des decks TCG légaux des 90 jours avant la référence (seuil T3 de la tier list) : 70 cartes. Fenêtre de 90 jours choisie par la session, déclarée. | Le critère de fin ne disait pas comment ; un seuil existant et déclaré plutôt qu'un nouveau. |
| Lot 20 (A1) | Semi-Limited exclues ? | Non (Forbidden et Limited seulement). | Lecture littérale du critère ; avis data-scientist : défendable. |
| Lot 20 (A1) | La proximité de texte vaut 0 pour les 263 cartes retenues. | Poids inchangés ; l'API sert `text_signal_cards` et `as_of`, la page le dit sans date en dur. | Changer les poids sort du ticket ; `text_synergies` vient du notebook 07, hors chaîne (suite à ouvrir). |
| Lot 20 (A1) | Réserve data-scientist : la part sur 90 jours sous-estime les cartes sorties en cours de fenêtre. | Non corrigé, renvoyé à B2. | Il faudrait un plancher de decks, nouveau réglage hors ticket. |
| Lot 20 (A2) | Le « 80 % » apparaît aussi sur l'accueil, la page d'archétype et la boutique. | Corrigé partout (`ARRIVAL_COVERAGE_RANGE`, « couverture vérifiée de 62 à 67 % »). | Même défaut que le ticket ; un texte qui garderait le 80 % contredirait `/methode`. |
| Lot 20 (A3) | Où dire que le score suit la part OCG (question 4) ? | Paragraphe de `/boutique` et ligne « Comparaison naïve » de `/methode` (ρ 0,94 recalculé, identique). | Validé par Thomas le 17/11 (question 4). |
| Lot 20 (A4) | Libellés du simulateur. | « Fragmentation » → « Centralité de pont, part du maximum » ; « Archétypes touchés » → « Archétypes voisins ». | Les anciens libellés décrivaient un effet que le calcul ne mesure pas. |
| Lot 20 (A5) | Changer `BOUTIQUE_MODEL` puisque `predicted_label` change de sens ? | Non ; marqueur `label_source` et `buy_label` dans le payload. | Avis data-scientist : une nouvelle version doublerait les prédictions déjà journalisées. |
| Lot 20 (A6) | L'IC du critère ([−0,00116 ; −0,00051], −4 %) n'est plus reproductible (ancienne table TCG + OCG). | Non affiché ; seul le résultat TCG seul (−6 %, 0,10 à 0,30 point, évaluation du 16/11, recompté) l'est. « Environ 5 % » devient « environ 6 % » sur `/predictions`. | Règle : un chiffre qui diffère de l'audit ne s'applique pas sans formulaire ; le résultat TCG seul était déjà demandé par le critère. |
| Lot 20 (A6) | Flèche « sur l'écart dessiné » : quel seuil ? | 0,003 = 0,3 × 0,01 du notebook 05, servi (`direction_threshold`) et déclaré « fixé à la main ». 0 direction changée sur 19. | Même classement, rendu lisible ; aucun nouveau réglage. |
| Lot 20 (A7) | Dates des réglages manuels. | Lues dans l'historique git (tiers, Decks, Fort/Modéré : 16/11 ; poids du Ban Radar : 14/08 ; mois atténué : 17/11). | Le critère demande une date par réglage. |
| Lot 20 (A8) | BH ou Benjamini-Yekutieli ? Marquer aussi les Rogue proches de T3 ? | BH (simulation : 3,75 % sous l'hypothèse nulle) ; Rogue marqués (8 sur 13). | Avis data-scientist ; BY ne garderait que 6 signaux sur 10. Variante « T0 à T3 seulement » au formulaire. |
| Lot 20 (A8) | Tableau « environ 60 archétypes, environ 3 fausses tendances » de `/methode` : faux (20 testés, ≈ 1 attendue). | Laissé tel quel, formulaire. | Chiffre affiché différent de l'audit : pas de changement sans Thomas. |
| Lot 20 | Temps passé. | ≈ 1 h 30 de session (lecture, huit correctifs, six relectures de sous-agents, deux passages de `check.py --all --visuel`, 24 captures régénérées, documentation). | Note demandée par le brief. |
| Lot 21 (TOK-121) | « Date d'annonce » : laquelle retenir ? | Deux dates séparées dans la table : `announced_date` (ce que dit Yugipedia) et `content_date` (jour où les cartes sont devenues publiques). La mesure principale coupe à `content_date`. | Konami OCG publie la date de la liste ~10 jours avant son contenu ; Yugipedia écrit « first announced » pour l'une ou l'autre (OCG 2026, TCG septembre 2024 : date de sortie seule). Seule la publication des cartes change ce que les joueurs anticipent. |
| Lot 21 (TOK-121) | 4 listes TCG sans phrase d'annonce (2024-04-15, 2026-02-02, 2026-05-18, 2026-09-21). | `content_date` vide avec `missing_reason` ; la date de la source citée est gardée à part (`first_source_date`, borne haute) et n'entre que dans le scénario `contenu+borne`, déclaré. | Règle du brief : jamais de date devinée. La borne est postérieure ou égale à l'annonce : elle sous-estime l'effet. |
| Lot 21 (TOK-121) | Liste TCG du 2026-10-19 (révélée en 5 parties du 16 au 18 oct.) ; listes « le jour précédent » (2024-12, 2025-04). | Coupure au 16 oct. (« weekend of », premier jour de l'événement) ; « on the day prior » accepté seulement parce qu'une référence citée porte ce jour (8 déc., 6 avr.). | Choix le plus conservateur (retire le plus de decks) ; déduction relative acceptée seulement si une source la confirme. |
| Lot 21 (TOK-121) | Où brancher l'étape dans `refresh_all.py` ? | En dernier (après les images), sans dépendance ; sauvegarde de la base à la première création seulement ; une page en échec garde sa ligne. | Réseau : une panne ne doit rien bloquer en aval ; la table se reconstruit chaque lundi, une sauvegarde de 270 Mo par semaine s'empilerait (relecture `gardien-donnees`). |
| Lot 21 (TOK-121) | Table dans `SERVED_TABLES` ? | Non : aucun endpoint ne la lit (grep sur `backend/`) ; `serving.db` n'est pas à reconstruire. | Rien d'affiché ne change. |
| Lot 21 (TOK-121) | Comment mesurer sans changer le backtest affiché ? | Paramètre optionnel `as_of_override` de `backtest_lists` (défaut inchangé) et option `--annonces` de `diagnose_ban_radar.py` (le diagnostic TOK-115 n'est pas relancé par défaut). | Le brief interdit de changer le comportement par défaut ; une seule fonction de backtest (pas de copie). |
| Lot 21 (TOK-121) | Relecture `data-scientist-ygo` de la mesure. | Pas de fuite ; 60 tests du signe, aucun ne survit à Bonferroni (≈ 0,0008) ; le p = 0,008 du top 25 TCG (`contenu+borne`) ne se cite pas seul ; placebo manquant, à demander à la collaboratrice. Formulation retenue dans le journal. | Fenêtres de 6 mois qui se recouvrent, 10 listes par format : exploratoire. |
| Lot 21 | Temps passé. | ≈ 40 min de session, dont ≈ 15 min d'attente réseau (Yugipedia, 170 pages à 0,5 s, deux relances après des réponses vides) ; deux relectures de sous-agents. | Note demandée par le brief. |
| Lot 22 (TOK-120) | `statsmodels.ConditionalLogit` déborde en récursion sur des listes de ≈ 1 000 cartes. | Vraisemblance conditionnelle de Breslow (softmax par liste), vectorisée, vérifiée contre la vraisemblance exacte (récurrence en log, départ à zéro) : poids à ±0,01. | k/n ≈ 1 % : l'écart à l'exacte est d'ordre k/n ; la vérification est dans le script. |
| Lot 22 (TOK-120) | À quelle date de coupure appliquer la règle d'adoption ? | Aux deux (veille de l'entrée en vigueur, veille du contenu `content_date` du lot 21), adoption seulement si les deux passent ; candidats (`rangs_poids_ecrits`, `clogit_rangs`) et règle figés avant la première exécution. | La plus prudente ; le brief demande d'utiliser les dates du lot 21 sans abandonner la référence TOK-115. |
| Lot 22 (TOK-120) | Pont daté : intermédiarité échantillonnée (500 sources, sans graine, notebook 03) ou exacte ? `weight = jaccard` lu comme une distance ? | Exacte ; `weight = jaccard` gardé tel quel (déclaré). | Reproductible ; dater le critère, pas en changer la définition. |
| Lot 22 (TOK-120) | Relecture `data-scientist-ygo`. | Méthode et chiffres validés (règle d'adoption recalculée, rang médian TCG 2026-05-18 refait de zéro : 36/889) ; recommandation A ; pont à retirer au prochain changement de poids ; deux suites signalées (`card_graph_metrics` périmée, `load_usage` filtre `created` et non `uploaded` : 925 decks sur 36 917 mis en ligne après la coupure). | Corrections appliquées : vérification de Breslow partie de zéro, colonne `n_train_lists_tcg_ocg`. |
| Lot 26 (TOK-132) | Quelle mesure de l'« impact » d'un ban ? | Variation de la part cumulée des archétypes porteurs (≥ 50 % de leurs decks jouent la carte, archétypes ≥ 5 decks), 3 mois avant la coupure contre 3 mois après l'entrée en vigueur ; listes dont les 3 mois suivants sont complets (17 sur 20). | Mesure proposée par l'audit (§ 9) ; validée par Q1 (un ban la fait baisser). |
| Lot 26 (TOK-132) | La règle de gain (Q3) ne fixait pas le sens attendu ; le « gain » du score de pont vient d'un coefficient de signe contraire à « Impact ». | Signe des coefficients ajouté après lecture (« Q3 bis », déclaré dans le script et le journal) ; c'est lui qui tranche : pas d'impact, une mesure de diffusion. | Ne pas cacher un résultat favorable sur la forme mais contraire au sens. Leçon : fixer le signe dans toute règle future. |
| Lot 26 (TOK-132) | Relecture `data-scientist-ygo`. | Q1 à Q3 validés (effet −3,1 et coefficient +6,5 recalculés) ; Q4 refait en variation relative avec le filtre de 5 decks des deux côtés (la version en points favorisait la liste naïve) ; variante de Q1 sans contrôles contaminés ajoutée (effet −5,5 au lieu de −3,1). | Corrections appliquées avant le commit. |
| Jalon 1 (TOK-129) | Les vues n'existent qu'à une date (instantané du 13/06/2026) : comment rejouer les signaux à des dates passées ? | Deux analyses : une origine propre le 13/06/2026 (vues du même jour) et 25 origines glissantes avec les vues du 13/06, fuite déclarée et chiffrée. | Aucune autre série de vues n'existe ; la fuite avantage les vues seules plus que le score, le test reste donc lisible. |
| Jalon 1 (TOK-129) | « Entrer en méta » ? | ≥ 3 % des decks TCG légaux de ]t ; t + 120 j], toutes zones (seuil « déjà en méta » du lot 20) ; sensibilité 1 %. Figé avant la première exécution. | Même seuil pour exclure (« déjà en méta ») et pour réussir ; 120 j = horizon de 4 mois du produit. |
| Jalon 1 (TOK-129) | Relecture `data-scientist-ygo` : dépendance entre dates, comptage par archétype, décomposition. | Intégrées au script après la première exécution, déclarées : bootstrap par 8 épisodes (découpage posé après lecture), précision par archétype, variantes sans vues et sans texte ; docstring « 54 % de vues » corrigée (34 / 32 / 33 % aux dates passées). | Le critère est rempli en cartes mais nul en archétypes ; ne pas laisser un résultat favorable sur la forme cacher sa fragilité. |
| Jalon 1 (TOK-93) | Où brancher le contrôle de fraîcheur ? | Dernière étape de `refresh_decks.py`, après `serving`, lancée même après un échec amont, sur `serving.db` (dates de référence de `yugioh.db`) ; et `deploy_prebuilt.py` (étape base de service). Ni `refresh_all.py`, ni `build_serving_db.py --check`. | Relecture `gardien-donnees` : dans `refresh_all.py`, le code 1 faisait sauter la reconstruction de `serving.db` ; dans `--check`, `check.py` aurait bloqué des pushes sans rapport. |
| Jalon 1 (TOK-93) | 3 défauts connus (graphe TOK-136 ×2, vues figées) feraient échouer le job chaque lundi. | Tolérance déclarée `KNOWN_STALE` par motif (table:contrôle), avec ticket et expiration au 2026-12-31 ; jamais pour une table absente, vide ou illisible. | Avis du gardien : un contrôle toujours rouge masque une 4e table périmée ; la date d'expiration rend la tolérance réversible d'elle-même. |
| Jalon 1 (TOK-93) | Complément de l'orchestrateur : journal, `--status`, endpoint `/top-decks`, plan B. | Ligne `{"step": "fraicheur_tables", …}` dans `data/fetch_health.jsonl` du checkout courant (ignoré par Git) ; `--status` (aussi dans `refresh_decks.py --status`) ; un GET sur `/top-decks` par contrôle, échec = code 1, jamais d'appel dans les tests ni au déploiement ; plan B dans le journal. | Nom d'étape distinct de `"freshness"`, que `refresh_decks.py` relit pour vérifier que le nombre de decks ne baisse pas. |
| Jalon 1 (TOK-93) | Une table périmée qu'aucun routeur ne lit (`meta_tier_list`, 154 j) ? | « non lue » : affichée et journalisée, sans faire échouer. | Sans effet sur le site ; la retirer de `SERVED_TABLES` est au formulaire. |

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

C1 (TOK-90) — grain de « non couvert » (D5)
[x] Effet par effet : carte « brouillon » déplaçable, effet sans résolution jamais joué (Rindbrumm, effet 1)
[ ] Carte entière : coder tout de suite la résolution de l'effet 1 de Rindbrumm (annuler, renvoyer en main)
Commentaire libre :

C1 (TOK-90) — illégal décidé sur une carte non formalisée
[x] Oui, seulement par ses caractéristiques imprimées (Magie Normale = vitesse 1, T60)
[ ] Non : toute action qui cite une carte non formalisée renvoie « non couvert »
Commentaire libre :

C1 (TOK-90) — cartes non formalisées en main pendant un combo dirigé
[x] Résultat donné avec réserves et options indéterminées listées
[ ] « non couvert » dès qu'une carte non formalisée pourrait agir (toute main avec Ash Blossom)
Commentaire libre :

C1 (TOK-90) — effets qui supposent l'adversaire
[x] HORS_PERIMETRE : condition écrite, résolution non écrite, carte « formalisee » pour le pilote
[ ] Carte « brouillon » tant que ces résolutions ne sont pas écrites
Commentaire libre :

C1 (TOK-90) — harnais
[x] Réutiliser `verifie` (affiché « exécuté »), pas de migration du schéma
[ ] Ajouter une valeur `execute` à cb_test_situation.status (migration 002, relecture gardien-donnees)
Commentaire libre :

C2 (TOK-118) — statut `formalisee`
[x] Résolutions écrites ET chaque effet du pilote exercé par un test (sinon `brouillon`, « non testée »)
[ ] Résolutions écrites suffisent (règle de C1)
Commentaire libre :

C2 (TOK-118) — situations J1 écrites par l'agent
[x] Fichier à part (`situations-j1.yaml`), à faire rejouer à l'oracle ; le YAML relu par le juge n'est pas touché
[ ] Les ajouter à `tests-branded.yaml`
Commentaire libre :

C2 (TOK-118) — R22 (déclencheurs simultanés)
[x] Ordre libre, obligatoires d'abord, facultatifs laissables (réglage par défaut de l'oracle)
[ ] Ordre imposé (« premier déclenché d'abord », FIRSTTRIGGER)
[ ] Laisser « non couvert »
Commentaire libre :

C2 (TOK-118) — méthode du taux d'erreur (avis data-scientist-ygo)
[x] Oracle sur les 30 situations J1 + relecture à l'aveugle de 20 effets stratifiés 10/10 (graine 20260118), hors périmètre en exhaustif
[ ] Relecture de 35 effets (borne haute < 10 % si 0 erreur), coût humain plus élevé
[ ] Oracle seul, sans relecture humaine
Commentaire libre :

C2 (TOK-118) — cible de J1, écrite avant le tirage
[x] Borne haute de Wilson 95 % du taux arbitré ≤ 20 %
[ ] Borne haute ≤ 10 % (demande ≈ 35 effets relus)
Commentaire libre :

C2 (TOK-118) — statut `verifiee`
[x] Aucune carte `verifiee` avant le passage de l'oracle sur J1 et la relecture
[ ] `verifiee` dès maintenant pour les cartes dont tous les effets sont exercés par des situations rejouées par l'oracle
Commentaire libre :

C2 (TOK-118) — points non tranchés N01 à N13
[x] Choix codés et marqués ⚖, N01 en « non couvert », à faire trancher par l'oracle
[ ] « non couvert » pour tous les N
Commentaire libre :

C2 (TOK-118) — R23 (Incredible Ecclesia)
[x] Obligatoire, texte TCG de notre base (désaccord avec l'oracle listé, non compté comme erreur)
[ ] Facultatif, comme l'oracle
Commentaire libre :

C3 (TOK-119) — N04, déclarer un Attribut déjà porté
[x] Permis (texte TCG), DIVIN déclarable (oracle)
[ ] Interdit, comme l'oracle
Commentaire libre :

C3 (TOK-119) — N09 étendu à Luluwalilith 1, Aeon 1, Rindbrumm 1
[x] Oui, même règle générale (à faire rejouer par l'oracle)
[ ] Seulement Mirrorjade (ce que l'oracle a joué)
Commentaire libre :

C3 (TOK-119) — cartes absentes des guides
[x] Mesurer jusqu'à la dernière étape réalisable, substitution déclarée des coûts, suite « manqué : carte absente »
[ ] Ne compter que les combos entièrement réalisables avec la liste (aucun aujourd'hui)
Commentaire libre :

C3 (TOK-119) — main d'un combo « à une carte »
[x] La carte seule, les 4 autres retirées du jeu
[ ] La carte + 4 cartes de réponse en main (elles peuvent servir de matériel ou de coût)
Commentaire libre :

C3 (TOK-119) — filtres d'exploration (D4)
[x] Les 8 filtres déclarés de `exploration.py`, enregistrés avec chaque exploration
[ ] Sans filtre (exploration bien plus lente)
Commentaire libre :

C3 (TOK-119) — verdict J2
[x] Atteint sous réserve, horloge du 13/01/2027 maintenue (conditions d'un J2 plein listées dans `j2-rapport.md`)
[ ] Atteint
[ ] Non atteint
Commentaire libre :

Lot 16 (textes) — accent et surtitres de l'accueil
[x] « TCG et OCG » accentué ; surtitres « YGO Meta · … » (accueil, image de partage)
[ ] Aucun accent ; surtitres d'origine
Commentaire libre :

Lot 16 (textes) — bloc « Ban Radar rejoué » de l'accueil
[x] Tableau TCG / OCG du top 25 (Ban Radar contre part des decks), chiffres figés dans SITE_FACTS.banTop25
[ ] Texte seul (deux phrases), sans tableau
[ ] Chiffres lus dans l'API de l'historique (un appel de plus sur l'accueil)
Commentaire libre :

Lot 16 (textes) — verdict TOK-115 masqué dans l'Historique si les sommes servies changent
[x] Oui (relancer le diagnostic et réécrire le texte après chaque banlist)
[ ] Non, toujours affiché
Commentaire libre :

Lot 16 (textes) — critère « pont »
[x] « le retirer change de 2 le nombre de cartes touchées dans le top 25 TCG »
[ ] « 30 avec, 28 sans » (chiffres du diagnostic)
Commentaire libre :
Lot 20 (A6) — gain du modèle de prévision cité par le critère de l'audit (−4 %, IC −0,00116 à −0,00051)
[x] Ne pas l'afficher : il vient de l'ancienne table TCG + OCG ; seul le résultat TCG seul (−6 %, 0,10 à 0,30 point) est affiché
[ ] L'afficher en plus, étiqueté « ancienne table TCG + OCG, avant le 16/11 »
[ ] Afficher la valeur recalculée sur la table actuelle (−5,7 %, IC −0,00295 à −0,00071, 27 mois)
Commentaire libre :

Lot 20 (A8) — tableau « Tendances dues au hasard » de /methode (« environ 60 / 5 % / environ 3 »), faux en dénominateur
[x] Le retirer : la correction de Benjamini-Hochberg, décrite juste au-dessus, le rend sans objet
[ ] Le remplacer par les nombres du jour servis par l'API (archétypes testés, tendances avant et après correction ; nouveau champ)
[ ] Le laisser
Commentaire libre :

Lot 20 (A8) — marquage « limite »
[x] Tous les archétypes à partir de 5 decks, Rogue compris (13 aujourd'hui, dont 8 Rogue)
[ ] Tiers T0 à T3 seulement (5 aujourd'hui), déclaré comme réglage d'affichage
Commentaire libre :

Lot 20 (A3) — bloc « Le signal OCG → TCG » de l'accueil (r ≈ 0,53 à côté des libellés boutique)
[x] Préciser la population : « archétypes déjà joués dans les deux formats »
[ ] Laisser tel quel
Commentaire libre :

Lot 20 (A1) — part « déjà en méta » d'une carte sortie en cours de fenêtre (réserve data-scientist)
[x] Traiter dans B2 (part depuis la sortie TCG, avec un plancher de decks)
[ ] Corriger tout de suite (nouveau seuil à fixer)
Commentaire libre :

Lot 21 (TOK-121) — la page Historique doit-elle passer de « veille de l'entrée en vigueur » à « veille de l'annonce » ?
[x] Non, rien ne change : l'effet mesuré est faible et exploratoire (OCG ≈ 5 rangs médians, 9 listes sur 10, aucun des 60 tests ne survit à la correction ; TCG rien de net, coupure à 1 à 3 jours). Le verdict de l'Historique tient. Ne jamais écrire « avant l'annonce » pour le TCG.
[ ] Oui, passer à « la veille de la publication des cartes » (`content_date`, scénario `contenu+borne`) dans un lot dédié : change les chiffres affichés (top 25 : OCG 41 → 46, TCG 29 → 33), `SITE_FACTS.banTop25`, le verdict et la table servie
[ ] Oui, mais à la date écrite par Yugipedia (`announced_date`) : non recommandé, elle n'est que la date de sortie pour 4 listes sur 16
Commentaire libre :

Lot 21 (TOK-121) — suite de la mesure
[x] Relecture par la collaboratrice d'abord (dépendance entre listes, comparaisons multiples, placebo, choix des scénarios, dates de la table : `docs/journal/dates-annonce-banlists-tok-121.md` § 4), puis décider
[ ] Ajouter tout de suite un placebo et un test par blocs (nouveau lot de méthode)
[ ] Abandonner (effet trop petit pour justifier plus de travail)
Commentaire libre :
Lot 22 (TOK-120) — poids du Ban Radar après les rangs centiles et le logit conditionnel
[x] A. Ne rien changer. La règle figée n'est pas remplie : le logit conditionnel sur les rangs la remplit à la veille de l'entrée en vigueur, pas à la veille du contenu (OCG : mieux que les poids actuels sur 3 listes sur 7, top 25 32 contre 33) ; aucun candidat ne bat les staples de façon démontrée (TCG : −0,15 à −0,27 point, 5 listes sur 7, p = 0,45)
[ ] B. Rangs centiles avec les poids écrits (meilleur que les poids actuels en TCG sur 7 listes sur 7, p = 0,016 ; moins bien que les staples en TCG, +0,7 point)
[ ] C. Rangs centiles avec les poids du logit conditionnel (0,29 / 0,20 / 0,17 / 0,16 / 0,12 / −0,05)
Commentaire libre :

Lot 22 (TOK-120) — suivi des candidats
[x] Relancer `diagnose_ban_radar.py --rangs` (deux coupures) à chaque nouvelle banlist et prolonger le tableau « listes postérieures au calage » (3 listes aujourd'hui)
[ ] En plus, journaliser les classements B et C dans `prediction_log` pour les dater par un tiers (ticket, Thomas seul lance `log_predictions.py`)
Commentaire libre :

Lot 22 (TOK-120) — critère `bridge`
[x] Le retirer au prochain changement de poids, sans le recalculer par date (poids estimé −0,05 [−0,10 ; −0,01] ; pont daté seul AUC 0,52 en TCG ; retirer ne change rien de mesurable)
[ ] Le remplacer par le pont daté (`bridge_date.py`) au prochain changement de poids
[ ] Le retirer maintenant (changement de `WEIGHTS`, `--backtest`, Historique recalculé)
Commentaire libre :

Lot 22 (TOK-120) — `card_graph_metrics` périmée (663 nœuds, le graphe actuel en a 1 402 ; lue par le Ban Radar et par la « fragmentation » du simulateur)
[x] Ticket : refaire la table dans la chaîne du lundi (script daté issu de `bridge_date.py`, à la place du notebook 03), en déclarant l'intermédiarité exacte
[ ] La laisser en l'état jusqu'au retrait du pont
Commentaire libre :

Lot 22 (TOK-120) — fenêtre du backtest filtrée sur la date du tournoi (`created`) et non de mise en ligne (`uploaded`) : 925 decks sur 36 917 (2,5 %) connus après la coupure, surtout dans le critère « tendance »
[x] Ticket dédié : filtrer aussi sur `uploaded ≤ coupure` dans `load_usage` (change `--backtest` et l'Historique : formulaire avant application)
[ ] Laisser tel quel, déclaré dans le journal
Commentaire libre :

Lot 26 (TOK-132) — onglet « Impact » (score de pont `n_archetypes × log(1 + decks)`)
[x] Renommer « Impact » en « Diffusion » et écrire ce que mesure la formule : à part des decks égale, plus le score est haut, MOINS les archétypes porteurs perdent après un ban (+6,5 points par écart type [+4,5 ; +8,6], 158 cartes, 17 listes)
[ ] Garder « Impact » (non recommandé : contredit par la mesure)
[ ] Retirer l'onglet
Commentaire libre :

Lot 26 (TOK-132) — simulateur de ban
[x] Le décrire comme la position de la carte dans le graphe, sans prévision ; remplacer les « archétypes voisins » (31 % seulement sont des archétypes de deck, pas meilleurs qu'une liste naïve) par les archétypes de deck qui jouent la carte, avec leur effectif
[ ] Retirer le simulateur
[ ] Laisser tel quel (textes déjà conformes au calcul depuis A4)
Commentaire libre :

Lot 26 (TOK-132) — suite
[x] Relecture de la collaboratrice (cible, contrôles de Q1, Q3 bis ajouté après lecture, Q4 relatif), puis lot de textes pour appliquer les deux choix ci-dessus
[ ] Appliquer tout de suite les textes, relecture ensuite
Commentaire libre :

Jalon 1 (TOK-129) — page « signaux précoces » (/early-signals)
[ ] Garder telle quelle (critère B2 rempli en cartes : +0,154, IC dates [+0,066 ; +0,252])
[x] Revoir : afficher les archétypes classés par la force OCG (cartes de l'archétype sans rang), après un backtest propre à ce classement ; la page reste telle quelle en attendant
[ ] Revoir, et masquer la page en attendant
[ ] Masquer la page
Commentaire libre :

Jalon 1 (TOK-129) — suites
[x] Poids du texte à 0 (il coûte −0,106 [−0,212 ; −0,018] par épisodes ; nul aujourd'hui dans le calcul servi, il reviendrait si text_synergies était recalculée)
[x] Archiver views_week chaque lundi (table datée nouvelle) pour tester les vues dans 6 à 12 mois
[x] Ticket : backtest du classement d'archétypes (unité archétype × date, bases part OCG seule et archétypes annoncés en TCG, critères figés avant exécution, bootstrap par épisodes)
[ ] Fusionner la page avec /boutique (la force OCG est presque le rang déjà affiché, ρ 0,94) : à trancher avec le ticket ci-dessus
Commentaire libre :

Jalon 1 (TOK-93) — contrôle de fraîcheur
[ ] Strict : toute table périmée fait échouer le contrôle (le job du lundi échoue tant que TOK-136 et les vues ne sont pas faits)
[x] Tolérance déclarée KNOWN_STALE (ticket + expiration au 31/12 : graphe → TOK-136, vues → ticket à créer), jamais pour une table absente, vide ou illisible
Commentaire libre :

Jalon 1 (TOK-93) — seuils (réglages manuels : calcul 8 j, retard sur le dernier deck 7 j, tables mensuelles 1 mois, vues 8 j)
[x] Valider tels quels
[ ] À revoir
Commentaire libre :

Jalon 1 (TOK-93) — tables servies lues par aucun routeur (meta_tier_list figée au 17/06, archetype_trend)
[x] Les retirer de SERVED_TABLES (ticket court, avis gardien-donnees)
[ ] Les garder, signalées « non lues »
Commentaire libre :

Jalon 1 (TOK-93) — suites
[x] Ticket : rafraîchir cards.views_week chaque lundi avec la date du relevé (sans init_db.py), utile aussi à TOK-129
[x] Ticket : colonne computed_at dans les notebooks 02 et 04 (card_cooccurrence, archetype_trend non datées)
Commentaire libre :
```

## Linear : jalons glissants 1-2-3 (18/11, décision de Thomas, note 0054)

Remplace l'essai du matin (une étiquette « Lot NN » par ticket) : étiquettes enlevées des tickets, groupe « Lot » retiré.
- Trois jalons dans le projet : **Jalon 1** (en cours), **Jalon 2**, **Jalon 3**. Un jalon = un groupe de fonctionnalités
  composé selon la charge, tous sujets confondus. Une fonctionnalité a le jalon 1, 2 ou 3, ou pas de jalon (non planifiée).
- Quand le Jalon 1 est fini, ses tickets sortent du jalon, le contenu du 2 passe dans le 1, celui du 3 dans le 2, et un
  nouveau 3 est composé. Historique jalon par jalon dans `etat.md`.
- Charge dans le champ « estimate » de Linear : S = 1, M = 2, L = 3 points (la barre d'avancement en tient compte).
- Composition au 18/11 :
  - Jalon 1 : TOK-120 Ban Radar en rangs (3), TOK-132 pont et simulateur (2), TOK-129 signaux précoces (2), TOK-93 fraîcheur des tables (1) ;
  - Jalon 2 : TOK-130 fenêtre d'arrivée par survie (3), TOK-131 intervalles de prévision (2), TOK-116 parts OCG servies (2) ;
  - Jalon 3 : TOK-133 vérification des données, TOK-134 doc désynchronisée, TOK-135 tests (créés, 1 chacun), TOK-82 chiffres de la vitrine (1).
- TOK-123 découpé en sous-tickets TOK-129 à 132 (B2, B1, B4, B3) ; C1 reste sur TOK-123.

Décidé par défaut (à confirmer) :
- **« Fini » = tous les tickets du jalon fusionnés dans la branche d'intégration et vérifiés (In Review)**, sans attendre le push ;
- dans un jalon, une session par groupe de tickets qui touchent les mêmes fichiers (120 + 132 ensemble), un commit par ticket.

**Validé par Thomas le 18/11 : retrait d'une fonctionnalité d'un jalon** (formulaire rendu tel que proposé, inscrit dans
la note 0054) : règle en 3 cas (pas fusionnée / fusionnée → revert de ses commits / poussée → retour arrière Vercel puis
revert) ; un commit par ticket, écriture en base additive, dépendances « bloqué par » dans Linear ; `main` avance jalon
par jalon. Interrupteur par variable d'environnement non retenu (rien de déployé). Règle ajoutée à
`docs/planning/2026-11-17/regles.md` et `docs/planning/sprint-4/regles-methode.md`.

**Validé par Thomas le 18/11 : une session par jalon, lancée sans l'attendre** (inscrit dans la note 0054). Décidé par
défaut : armement d'avance (la session du jalon suivant attend le commit `jalon n°N fini`), une seule session armée à la
fois, glissement Linear par renommage (« Fini n°N ») plutôt que détachement des tickets.

À faire par Thomas dans Linear (l'outil ne sait ni retirer un jalon d'un ticket ni supprimer un jalon) : **supprimer les
jalons « File de nuit 16-17/11 » et « File du 18/11 (moteur de combos) »**, ce qui détache leurs tickets. L'échéance du
13/01/2027 reste sur TOK-119.

## Jalon 2 — TOK-130 (B1) : fenêtre d'arrivée en TCG par analyse de survie

Journal : `docs/journal/fenetre-survie-tok-130.md` ; script `scripts/build_arrival_survival.py` (lecture seule, ≈ 8 s).
Critère de l'audit **non atteint et non testable** : sur 2024-2025, la survie ne produit que 5 prévisions (4 cohortes ;
données OCG à partir de janvier 2024, 8 arrivées connues seulement à mi-2025) : 85 % annoncés, 60 % observés, écart
−25 points, IC [−60 ; +15]. Sur 2025-2026 (hors critère) : 18 fenêtres justes sur 23 (78 %) pour 89 % annoncés (trop
confiante d'environ 11 points) ; fenêtre actuelle 75-202 : 15 sur 23 (65 %), à largeur égale ; écart non démontré
(p = 0,45). Biais du survivant faible dans la population du notebook 10 (42 arrivées sur 44 unités). Rien d'affiché ne change.

Décidé par défaut (à confirmer) :
- arrivée définie par les cartes (la moitié des cartes inédites sorties en TCG), pas par le nom : 9 libellés sur 62
  étaient déjà joués en TCG sous ce nom avant l'ancre ;
- libellés qui partagent ≥ 50 % de leurs cartes inédites fusionnés en une unité (7 fusions) ;
- ancres antérieures au 2024-03-01 écartées (données OCG à partir de janvier 2024) ;
- minimum de 8 arrivées connues pour estimer la courbe à une origine donnée.

```
1. Fenêtre d'arrivée affichée (boutique, accueil, page d'archétype)
[x] Garder 75-202 jours, libellé corrigé en unité archétype :
    « arrivée dans la fenêtre pour 27 archétypes sur 36 (2024-2026) ; 12 sur 18 pour 2026 »
[ ] Remplacer par la fenêtre de survie, libellé = couverture observée en validation
    (« 18 fenêtres sur 23 justes, 2025-2026 »), jamais la probabilité Kaplan-Meier
[ ] Remplacer par la fenêtre de survie avec sa probabilité Kaplan-Meier (≈ 82-89 %) : déconseillé, trop confiante d'environ 11 points
[ ] Retirer la fenêtre
Commentaire libre :

2. Rendre le critère testable (effectif actuel : 5 prévisions sur 2024-2025)
[x] Nouveau script d'ingestion : liste complète YGOPRODeck sans filtre format=tcg (cartes OCG seules comprises),
    survie par archétype depuis 2015 avec censure ; avec gardien-donnees, puis relancer B1
[ ] Attendre que les données s'accumulent (revalidation dans 6 à 12 mois)
[ ] Abandonner la validation à ± 5 points
Commentaire libre :

3. Validateur (validate_predictions.py, arrivée par le nom)
[x] Ticket à part : l'aligner sur l'arrivée par les cartes (moitié des cartes inédites sorties en TCG)
[ ] Garder l'arrivée par le nom
Commentaire libre :

4. Tables tcg_arrival_survival / tcg_arrival_km (nouvelles, non servies)
[x] Les écrire sur la base de référence (après sauvegarde) pour garder une trace datée des 3 fenêtres actuelles
    (échéances au printemps 2027) : `python scripts/build_arrival_survival.py --write --reference`
    (`--write --reference` depuis le dépôt principal ; sans `--reference`, le script refuse cette base)
[ ] Ne rien écrire pour l'instant
Commentaire libre :
```

## Jalon 2 — TOK-131 (B4) : intervalles de prévision par archétype

Journal : `docs/journal/intervalles-tok-131.md` ; script `scripts/build_prediction_intervals.py` (lecture seule, ≈ 6 s).
Conformité séquentielle sur les résidus du walk-forward (prévision servie, TCG), calibration sur les mois antérieurs,
24 mois de test (2024-11 → 2026-10, 507 prévisions). Méthode retenue par la règle figée avant mesure : **Mondrian par
terciles de niveau**, couverture **75,7 % [67,7 ; 82,0]** pour 80 % visés (critère ± 5 points atteint de justesse,
non démontré) ; tiers haut 72,8 %, 5 premiers du mois 68,3 %. Naïves : « le mois dernier » ± quantile 78,7 % (battue
au score de Winkler, −1,59 [−2,72 ; −0,43]), gaussienne 82,8 % (écart non démontré). Ratés concentrés sur 4 mois de
rupture de méta (30-59 %). Rien d'affiché ne change : API et dessin prêts derrière l'option
`NEXT_PUBLIC_PREDICTION_INTERVALS=1` (capture : `tok-131-intervalles-option.jpg`).

Décidé par défaut (à confirmer) :
- calibration cumulée (une fenêtre de 12 mois donne 80,1 %, sans différence) ; amorce de 3 mois ;
- troncature de la borne basse à 0 (sans effet sur la couverture, la cible étant ≥ 0) ;
- deux variantes asymétriques ajoutées après lecture, marquées exploratoires et non retenues ;
- dessin derrière l'option : trait épais `--cat-1` à 35 % d'opacité derrière l'haltère, légende « fourchette visée à 80 % ».

```
1. Dessiner les intervalles par archétype sur /predictions ?
[ ] Non : garder « aucun intervalle par archétype » et réévaluer dans 6 mois
[x] Oui, derrière l'option, avec la couverture OBSERVÉE dans le libellé (jamais « 80 % » seul)
[ ] Oui, sans réserve
Commentaire libre :

2. Niveau
[x] 80 % visé, méthode Mondrian (retenue par la règle figée)
[ ] 90 % visé (≈ 82 % observé sur les 5 premiers) : choix fait après lecture des résultats, à confirmer sur les mois à venir
[ ] Les deux, 90 % en trait fin
Commentaire libre :

3. Libellé de couverture
[x] « Fourchette visée à 80 % ; rejouée sur 24 mois (507 prévisions), elle a contenu la valeur réalisée 3 fois
    sur 4, 2 fois sur 3 pour les 5 premiers archétypes du mois »
[ ] « Intervalle à 80 % » (faux pour les gros archétypes)
[ ] Pas de libellé chiffré, renvoi vers /methode
Commentaire libre :

4. Suites
[x] Ticket : corriger le notebook 05 (entraînement sur la cible partielle de novembre, 25 lignes périmées de 2026-08/09)
[x] Pré-enregistrer Mondrian asymétrique et le niveau 90 %, puis les réévaluer sur les mois à venir
Commentaire libre :

Si « oui » : notebook 05 → `python scripts/build_prediction_intervals.py --write --reference` (après sauvegarde) →
ajouter `meta_prediction_intervals` à SERVED_TABLES (et une règle dans check_freshness.py) → `build_serving_db.py` →
build avec NEXT_PUBLIC_PREDICTION_INTERVALS=1.
```

## Jalon 2 — TOK-116 : parts OCG mensuelles servies par l'API

Journal : `docs/journal/parts-ocg-servies-tok-116.md`. `meta_scores_ocg` ajoutée à `SERVED_TABLES` ; `GET
/archetypes/{slug}` sert `ocg_history` et `ocg_history_computed_at` ; l'accueil lit `GET /archetypes/kewl-tune` au lieu
de `proof-data.ts` figé. Valeurs dessinées identiques au relevé du 16/11 (16 mois × 2 formats, 0 écart), 51 captures
identiques. Rien d'autre ne change à l'écran.

Décidé par défaut (à confirmer) :
- date affichée = `MAX(computed_at)` d'`ocg_archetype_scores` (notebook 10, juste après le notebook 04) :
  `meta_scores_ocg` n'a pas de date, et lui en ajouter une ne serait pas additif ;
- fenêtre fixe août 2025 → novembre 2026 (les textes nomment ses mois) ;
- sans données complètes, la section n'est pas rendue (pas de repli sur des chiffres figés) ;
- champ ajouté à `GET /archetypes/{slug}` plutôt qu'un endpoint nouveau.

```
1. Légende du graphique : « Incertitude non dessinée : les effectifs mensuels n'ont pas été relevés avec cette
   série figée » est devenue inexacte (les effectifs sont servis)
[x] Remplacer par « Incertitude non dessinée : effectifs mensuels de 145 à 574 decks en OCG », chiffres tirés de l'API
[ ] Dessiner la bande de Wilson à 95 % comme sur /evolution (charte, lot 15)
[ ] Laisser tel quel
Commentaire libre :

2. Fenêtre de l'exemple
[x] Garder la fenêtre fixe (août 2025 → novembre 2026) et les textes actuels
[ ] Fenêtre glissante (16 derniers mois), textes calculés depuis les données
Commentaire libre :
```

## Jalon 3 — TOK-82 : chiffres de vitrine (`frontend/src/lib/site-facts.ts`) et notebook 11

Journal : `docs/journal/chiffres-vitrine-tok-82.md`. Chaque chiffre de `SITE_FACTS` remesuré le 18/11 sur la base de
référence (lecture seule, dernier deck du 14/11). Identiques : r = 0,53 [0,43 ; 0,59] sur 105 archétypes (relancé avec
`evaluate_prediction.py --part B`), « 2 à 6 mois », ρ 0,94 sur 89 archétypes, top 10 du Ban Radar 6 contre 19,
`banTop25` (TCG 29 contre 16, OCG 41 contre 18 ; `verdictMatches` reste vrai), 23 948 decklists. Deux écarts affichés :
cartes suivies 13 797 contre 14 084, et « légales à la date du tournoi » accolé aux 23 948 listes, dont 22 422 seulement
sont légales. Fenêtre d'arrivée : laissée au formulaire TOK-130 (point 1). Le commit du front
(`feat(TOK-82): chiffres de vitrine (en attente du formulaire)`, dernier de la branche) applique les cases pré-cochées ;
ne le fusionner qu'après ce formulaire.

Décidé par défaut (à confirmer) :
- le relevé n'a pas été relu par `data-scientist-ygo` (lancement de sous-agent refusé dans la session) : chiffres
  recalculés avec les scripts existants, aucun calcul nouveau ;
- le commentaire faux de `site-facts.ts` (« Decklists légales + Genesys ») est corrigé dans le commit du front (sans
  effet à l'écran).

```
1. Cartes suivies (accueil : compteur et section des sources)
[x] 14 084 (table `cards` au 18/11)
[ ] 13 982 (cartes avec un prix Cardmarket) et libellé « cartes avec un prix Cardmarket »
[ ] Garder 13 797
Commentaire libre :

2. « 23 948 decklists … légales à la date du tournoi » (accueil, sources) et « … Seules les listes légales à la date
   de leur tournoi sont comptées » après 11 618 + 12 330 (`/methode`) : 1 526 de ces listes sont illégales (611) ou
   Genesys (915)
[x] Garder les totaux relevés et écrire la part légale : accueil « 23 948 decklists de tournoi, mai 2023 à novembre
    2026 : 11 618 en TCG, 12 330 en OCG, dont 22 422 légales à la date du tournoi, seules comptées dans les calculs. » ;
    `/methode` « … 11 618 listes TCG et 12 330 listes OCG au 14 novembre 2026, collectées chaque lundi ; 22 422 sont
    légales à la date de leur tournoi (10 369 TCG, 12 053 OCG) et seules comptées. » ; compteur de l'accueil
    « Decklists analysées » → « Decklists relevées »
[ ] Afficher partout les listes légales : 22 422 (10 369 TCG, 12 053 OCG)
[ ] Laisser tel quel
Commentaire libre :

3. Corrélation OCG → TCG : 0,53, IC 95 % [0,43 ; 0,59], 105 archétypes, « 2 à 6 mois »
[x] Garder (recalcul du 18/11 identique : 0,529 [0,427 ; 0,589], n = 652)
[ ] Remplacer « 2 à 6 mois » par « 1 à 6 mois » (r interne 0,60 à lag 1, IC chevauchants de 1 à 6)
Commentaire libre :

4. « 63 communautés de cartes détectées » (accueil, tuile du graphe ; `/methode`, glossaire du graphe) : exact pour
   le graphe affiché (663 cartes), mais le graphe n'a pas de date et n'a pas été recalculé au rafraîchissement du
   16/11 (le graphe recalculé aurait 1 402 nœuds, TOK-136)
[x] Garder 63 en le qualifiant : « 63 communautés détectées sur 663 cartes (graphe non recalculé au rafraîchissement
    du 16 novembre 2026). »
[ ] Retirer le chiffre jusqu'au recalcul du graphe (TOK-136)
[ ] Laisser tel quel
Commentaire libre :

5. Notebook 11 (déjà marqué « remplacé », n'écrit plus aucune table, fenêtres relatives à la date du jour)
[x] Laisser tel quel
[ ] Le déplacer dans `notebooks/archive/`
Commentaire libre :
```

## Jalon 4 — TOK-136 : recalcul de `card_graph_metrics` et `graph_communities`

Journal : `docs/journal/graphe-recalcul-tok-136.md`. Script `scripts/build_graph_metrics.py` (notebook 03 en script),
mesuré sur une copie de la base de référence (référence intacte). Relu par `data-scientist-ygo` (chiffres retrouvés,
recommande le recalcul) et `gardien-donnees` (écriture rendue atomique après sa relecture).

Effet mesuré : 663 → 1 402 nœuds, 63 → 151 communautés (32 de 2 cartes) ; backtest : rangs médians ±8 (TCG 2026-05-18
84 → 86/889, OCG 2026-07-01 19 → 19), top 25 inchangés (TCG 29 contre 16, OCG 41 contre 18), listes OCG où le rang
médian bat les staples 8 → 7, listes TCG où le top 25 bat les staples 6 → 7 ; classement du jour : Spearman 0,998,
10 premiers identiques, 24 des 25 premiers, 15 libellés de risque changés ; page du graphe : 48 des 150 nœuds restent.
Fuite connue (TOK-120) : le critère pont du backtest lit le graphe du jour pour les 20 listes ; après recalcul, elle
touche plus de cartes (237 au lieu de 176 avec un pont non nul), effet mesuré ≤ 8 rangs.

Décidé par défaut (à confirmer) :
- étape `graph_metrics` ajoutée à `refresh_all.py` mais **verrouillée** (`PENDING_FORM`) : le job du lundi tourne
  depuis le dépôt principal, sur la branche d'intégration ; sans verrou, la fusion recalculerait la référence ;
- tolérance de `check_freshness.py` pour les deux tables **gardée** (la retirer ferait échouer le contrôle du lundi
  tant que la référence n'est pas recalculée) ;
- communautés : même algorithme que le notebook (Clauset-Newman-Moore, sans hasard), arêtes triées pour un résultat
  reproductible ; pas de seuil de taille pour l'affichage.

```
1. Recalculer le graphe sur la base de référence
[x] Oui, maintenant : retirer `graph_metrics` de `PENDING_FORM` et les deux tolérances de `check_freshness.py`
    (un commit), puis lancer la séquence du compte rendu (graphe, ban_radar, ban_history, serving)
[ ] Oui, mais seulement au prochain changement de poids du Ban Radar (le pont serait retiré au même moment)
[ ] Non : garder la table de 663 nœuds (tolérance jusqu'au 31/12, à reconduire)
Commentaire libre :

2. Verdict de l'onglet Historique (`SITE_FACTS.banTop25`, `frontend/src/lib/ban-verdict.ts`) après recalcul
[x] Réécrire les chiffres : OCG `medianBetter` 8 → 7, TCG `better` 6 → 7 ; la phrase reste vraie telle quelle
    (« en OCG, il fait mieux sur les deux mesures », 7 sur 10 ; seul l'écart de top 25 OCG reste démontré, p = 0,021)
[ ] Laisser le verdict masqué (`verdictMatches` faux) jusqu'au prochain diagnostic
Commentaire libre :

3. Chiffre « 63 communautés » (accueil, `/methode`, `SITE_FACTS.graphCommunities`)
[x] Passer à 151 communautés sur 1 402 cartes, au même commit que le recalcul (retirer la mention « graphe non
    recalculé » si le formulaire TOK-82 point 4 l'a ajoutée)
[ ] Compter seulement les communautés d'au moins 3 cartes (119)
Commentaire libre :

4. Critère « pont » du Ban Radar (5 % du score, poids estimé négatif en rangs, fuite non datable, TOK-120 et TOK-132)
[x] Ne rien changer maintenant ; le retirer au prochain changement de poids, avec backtest et formulaire
[ ] Le retirer dès maintenant (changement de scoring : backtest et formulaire dédiés)
Commentaire libre :
```

## Jalon 4 — TOK-137 : fenêtre du backtest limitée aux decks connus à la coupure

Journal : `docs/journal/fenetre-backtest-tok-137.md`. Paramètre `require_uploaded` (défaut `False`) dans
`build_ban_radar.backtest_lists` ; rien d'affiché ne change. Relu par `data-scientist-ygo` (chiffres retrouvés,
mécanisme vérifié).

Effet mesuré (20 listes) : 2,5 % des decks retirés (0,1 à 7,8 % par liste, aucune liste sous 600 decks) ; top 25 TCG
29 → 32 (staples 16), OCG 41 → 45 (staples 18 → 17) ; rang médian meilleur que les staples : TCG 3 → 3, OCG 8 → 9
(p = 0,021) ; écart OCG par liste −0,44 point d'univers [−0,76 ; −0,18], TCG nul. Références : TCG 2026-05-18 84/889 →
81/877, OCG 2026-07-01 19/1236 → 19/1226. Les decks retirés sont joués en fin de fenêtre, en OCG surtout après la
publication du contenu de la liste : **l'ancienne mesure était pessimiste ; ce n'est pas une amélioration du radar**.
Avec TOK-136 en plus : TCG 32/16, 7 mieux / 1 moins bien, 3 ; OCG 44/17, 9 / 1, 9.

Décidé par défaut (à confirmer) :
- sens du filtre : le brief disait « filtrer sur la date du tournoi (aujourd'hui sur la mise en ligne) » ; le code
  faisait l'inverse (fenêtre sur la date du tournoi, fuite par la mise en ligne, constat de TOK-120). Correctif dans le
  sens du constat : date du tournoi dans la fenêtre ET mise en ligne avant la coupure ;
- le classement du jour (`ban_radar` servi) n'est pas concerné (pas de coupure : sa date est le dernier deck).

```
1. Fenêtre du backtest (`backtest_lists`, `--backtest`, onglet Historique)
[x] Adopter « connus à la coupure » comme défaut du backtest (passer `require_uploaded` à True par défaut dans
    `backtest_lists` et `backtest` seulement ; le classement du jour reste tel quel), sur le principe, pas pour le gain
[ ] Garder la fenêtre actuelle et documenter la fuite
[ ] Attendre une mesure combinée avec la coupure « contenu » (TOK-121) avant de changer le défaut
Commentaire libre :

2. Si oui : ordre avec TOK-136
[x] Une seule mise à jour du site avec les deux tickets : recalcul du graphe, défaut changé, `build_ban_history.py`,
    `build_serving_db.py`, puis `SITE_FACTS.banTop25` réécrit avec les chiffres combinés (TCG radar 32, staples 16,
    better 7, worse 1, medianBetter 3 ; OCG radar 44, staples 17, better 9, worse 1, medianBetter 9)
[ ] Deux mises à jour séparées
Commentaire libre :

3. Phrase de significativité du verdict (`frontend/src/lib/ban-verdict.ts`, « significance »)
[x] « Avec 10 listes par format, seuls les écarts en OCG (top 25 et rang médian, 9 listes sur 10 chacun) dépassent ce
    que le hasard produit couramment ; aucun ne le fait si l'on tient compte des quatre comparaisons. »
[ ] Autre formulation (à écrire)
Commentaire libre :

4. Chiffres de référence cités dans `context.md` et `CLAUDE.md` (84/889, 19/1236)
[x] Les remplacer par 81/877 et 19/1226 au même commit que le changement de défaut (avec TOK-136 : à remesurer)
[ ] Garder les deux séries côte à côte pendant un mois
Commentaire libre :
```

## Jalon 4 — TOK-138 : vues de la semaine rafraîchies et archivées par date

Journal : `docs/journal/views-week-tok-138.md`. Script `scripts/fetch_card_views.py` (met à jour `cards.views_week`
seule, garde de nom, cartes renumérotées rattrapées par le nom, table nouvelle `card_views_snapshots`, une transaction),
testé sur une copie avec un vrai relevé de l'API le 18/11 (référence intacte). Relu par `gardien-donnees` (5
corrections, toutes appliquées).

Effet mesuré : 13 853 vues sur 14 084 changent (juin → novembre). Signal précoce (263 cartes) : Spearman des rangs
0,90, 14 des 20 premières cartes restent, top 20 avec 3 cartes Unchained de plus et 4 Dark Time Wizard de moins.
Signal boutique (notebook 10) : Spearman 0,995, aucun libellé Fort / Modéré / Faible changé, mêmes 3 archétypes.

Décidé par défaut (à confirmer) :
- étape `card_views` dans `refresh_all.py` (après `fetch_new_cards`, même API, avant `early_signals`), verrouillée par
  `PENDING_FORM` et **non bloquante** (`NON_BLOCKING`, nouveau) ;
- tolérance `early_card_signals:vues` gardée (rattachée à TOK-138) ; le contrôle date les vues servies par le dernier
  relevé archivé ;
- l'instantané du 13/06 (`data/raw/cards.json`) n'est pas versé dans l'archive.

```
1. Rafraîchir les vues chaque lundi (déverrouiller l'étape `card_views`)
[x] Oui : retirer `card_views` de `PENDING_FORM` et la tolérance `early_card_signals:vues` de `check_freshness.py`
    (un commit), puis lancer la séquence du compte rendu sur la référence
[ ] Oui, mais archiver seulement (table `card_views_snapshots`) sans toucher à `cards.views_week` tant que le critère
    « vues » du signal précoce n'est pas revu (TOK-129)
[ ] Non
Commentaire libre :

2. Premier point ancien dans l'archive
[ ] Verser l'instantané `data/raw/cards.json` dans `card_views_snapshots` à la date de son commit (2026-06-13), avec
    une colonne `source` pour le distinguer
[x] Non : l'archive commence au premier relevé ; l'instantané reste dans Git et dans la première sauvegarde
Commentaire libre :

3. `fetch_new_cards` est bloquante dans `refresh_all.py` (une panne de l'API arrête la chaîne et `serving`), alors que
   `refresh_decks.py` la déclare non bloquante
[x] Ticket à part : l'ajouter à `NON_BLOCKING` de `refresh_all.py` (avis `gardien-donnees`)
[ ] Laisser tel quel
Commentaire libre :
```

## Jalon 7 — TOK-144 : verdicts J1 et J2 mesurés contre l'oracle

Rapports : `docs/moteur-combos/j1-rapport.md` § 8 (règle figée avant la comparaison, commit `5fb4193`) et § 9
(résultats) ; `docs/moteur-combos/j2-rapport.md` § 9. Commande : `python scripts/combos_jalon7.py`. Relu par
`data-scientist-ygo` (comptage conforme, intervalles recalculés).

En bref : sur l'échantillon (20 effets tirés, 86 situations jouées par l'oracle), **3 effets en erreur sur 20**, Wilson
95 % [5,2 % ; 36,0 %] → **J1 non atteint** (critère : borne haute ≤ 20 %). Deux causes : le moteur ignorait le terrain
adverse (`Super Polymerization`, `The Fallen & The Virtuous`) ; « bannir jusqu'à N » lu comme « 0 à N »
(`Hyperinvoked Aeon`). Corrigées (commit `b31e5df`), **non revalidées** par l'oracle. J2 : 23 séquences sur 23 légales
pas à pas dans l'oracle ; condition principale inchangée, 4 sur 5 (développement) et **1 sur 5 hors échantillon**.

Décidé par défaut (à confirmer) :
- `Ecclesia and the Dark Dragon` remplit la règle `verifiee` mais reste `formalisee` (différence de modèle J2-a) ;
- J2-a non corrigé dans ce jalon (changerait le graphe d'exploration et tous les chiffres J2) ;
- pour la question Q2 (R22), seuls les effets que `questions-residuelles.md` nomme bloquent `verifiee` (lecture large :
  tout effet déclenché facultatif, qui bloquerait presque toutes les cartes) ;
- les statuts sont écrits dans `data/combos.db` du worktree ; après fusion, à relancer sur le dépôt principal
  (`python scripts/combos_harnais.py` puis `python scripts/combos_jalon7.py --ecrire-statuts`).

```
1. J1 (37 cartes formalisées, taux d'erreur chiffré)
[x] Déclarer J1 non atteint : 3 effets sur 20 en erreur, Wilson 95 % [5,2 % ; 36,0 %] (mesuré contre l'oracle, avant
    correction) ; corrections faites, non revalidées
[ ] Déclarer J1 atteint sur la base du taux après correction (0 sur 20) — déconseillé : chiffre optimiste par
    construction, pas une mesure
Commentaire libre :

2. Remesurer J1 après les corrections
[x] Nouveau tirage de 20 effets non vus (graine nouvelle, fixée avant le tirage), situations écrites et jouées par une
    session de l'oracle isolée, même règle de comptage ; 0 erreur sur 20 donnerait une borne haute de 16,1 %
[ ] Rejouer seulement les 3 situations en désaccord dans l'oracle (confirme les corrections, ne remesure pas le taux)
[ ] Ne pas remesurer avant J2
Commentaire libre :

3. J2 (le moteur retrouve seul les combos des guides publics)
[ ] Atteint
[x] Atteint sous réserve : toutes les séquences retrouvées sont légales dans l'oracle ; réserve = la longueur
    (4 à 7 transitions retrouvées seules, 8 à 11 seulement avec une cible) et 1 sur 5 hors échantillon
[ ] Non atteint
Commentaire libre :

4. Statuts `verifiee` (base `data/combos.db`, rien d'affiché)
[x] Garder les 20 cartes `verifiee` (règle figée, moteur mesuré) et `Ecclesia and the Dark Dragon` en `formalisee`
    jusqu'à la correction de J2-a
[ ] Passer aussi `Ecclesia and the Dark Dragon` en `verifiee` (elle remplit la règle à la lettre)
[ ] Aucune carte `verifiee` tant que J1 n'est pas atteint
Commentaire libre :

5. Différence de modèle J2-a (retour d'`Ecclesia and the Dark Dragon` en Phase de Fin)
[x] La corriger dans un lot dédié : effet obligatoire de Phase de Fin ordonnable, puis rejouer J2 (≈ 12 min + passage
    long) et faire rejouer les 8 séquences concernées par l'oracle
[ ] Laisser tel quel (les 23 plateaux sont identiques ; seules des zones diffèrent si le retour est joué en dernier)
Commentaire libre :

6. Terrain adverse dans les autres effets (`Three Champions` 2, `Luluwalilith` 1, `Aeon` 1, `Mirrorjade` 1…)
[x] Ticket à part : même défaut que E32 / E49, sans incidence au tour 1 du pilote ; à faire avant tout essai avec
    un adversaire
[ ] Plus tard (hors pilote)
Commentaire libre :

7. Questions résiduelles (Q1 à Q8, `questions-residuelles.md`)
[x] Ne rien envoyer pour l'instant (décision 0055) ; si un lot part, Q1 et Q2 d'abord
[ ] Envoyer Q1 et Q2 maintenant
Commentaire libre :

8. Suite et horloge de la règle d'arrêt (décision 0053, J2 avant le 13/01/2027)
[x] Horloge maintenue au 13/01/2027 ; prochain jalon : remesure J1 (point 2) et correction de J2-a (point 5)
[ ] Considérer J2 comme atteint et arrêter l'horloge
Commentaire libre :
```
