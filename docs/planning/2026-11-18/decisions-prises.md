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
```
