# Formulaires à trancher — récapitulatif du 19/11

Ce fichier rassemble toutes les décisions qui t'attendent, classées selon leur effet sur la mise en ligne. Les formulaires
d'origine (contexte, chiffres, détail) restent dans `docs/planning/2026-11-18/decisions-prises.md` ; la section exacte est
indiquée sous chaque titre. Les options sont résumées, pas recopiées : en cas de doute, la section d'origine fait foi.

**Comment répondre** : copie un bloc (ou tout le fichier), change les `[x]` si tu n'es pas d'accord, et renvoie-le. Un
bloc renvoyé sans changement vaut « recommandation acceptée ».

| Bloc | Quoi | Effet | Questions | Urgence |
|---|---|---|---|---|
| A | Ce que le site affiche, plus deux correctifs techniques du déploiement | corrige des chiffres ou des libellés faux en ligne | 22 | **avant la mise en ligne** (≈ 10 min de lecture) |
| B | Jalon 4 : graphe, fenêtre du backtest, vues | change des chiffres affichés, débloque le déploiement après le 31/12 | 11 | avant le 31/12 |
| C | Méthode, rien d'affiché | scripts, tables non servies, process | 19 | quand tu veux |
| D | Moteur de combos (en pause) | rien d'affiché | 8 + 1 bloc | à la reprise du moteur |
| E | Organisation | Linear, process | 4 | quand tu veux |

Aucun formulaire ne bloque techniquement le déploiement. Le bloc A fait que la première version en ligne ne porte pas
d'erreur connue. Si tu y réponds avant de pousser, j'applique en un petit lot (≈ 45 min, `check.py --all --visuel`), puis
je refais la release (`v2026.11.19`) et tu pousses celle-là.

---

## Bloc A — avant la mise en ligne

### A1. Chiffres de vitrine (TOK-82) — § « Jalon 3 — TOK-82 »
Aujourd'hui l'accueil affiche **13 797 cartes suivies** (la base en a 14 084) et **« 23 948 decklists légales »** (22 422
seulement le sont : 611 illégales et 915 Genesys). Le correctif est prêt (`f485ca1`), avec les cases pré-cochées.

```
A1.1 Cartes suivies
[x] 14 084 (table cards au 18/11)
[ ] 13 982 « cartes avec un prix Cardmarket »
[ ] Garder 13 797
Commentaire libre :

A1.2 « 23 948 decklists légales »
[x] Garder les totaux relevés et écrire la part légale (« … dont 22 422 légales à la date du tournoi, seules comptées
    dans les calculs ») ; compteur « Decklists analysées » → « Decklists relevées »
[ ] Afficher partout 22 422 (10 369 TCG, 12 053 OCG)
[ ] Laisser tel quel
Commentaire libre :

A1.3 Corrélation OCG → TCG (0,53 [0,43 ; 0,59], 105 archétypes, « 2 à 6 mois »), recalculée à l'identique le 18/11
[x] Garder
[ ] Écrire « 1 à 6 mois »
Commentaire libre :

A1.4 « 63 communautés de cartes » : exact pour le graphe affiché, mais ce graphe n'a pas été recalculé depuis des mois
     (voir B1 : s'il est recalculé, le chiffre devient 151 et cette question tombe)
[x] Garder 63 en le qualifiant (« sur 663 cartes, graphe non recalculé au rafraîchissement du 16 novembre 2026 »)
[ ] Retirer le chiffre jusqu'au recalcul
[ ] Laisser tel quel
Commentaire libre :

A1.5 Notebook 11 (déjà marqué « remplacé », n'écrit plus rien)
[x] Laisser tel quel
[ ] Le déplacer dans notebooks/archive/
Commentaire libre :
```

### A2. Page Méthode et accueil (lot 20, correctifs de l'audit) — § « Formulaire », lignes « Lot 20 »
Le tableau « Tendances dues au hasard » de `/methode` est **faux aujourd'hui** : il dit « environ 60 archétypes testés,
environ 3 fausses tendances », alors que 20 sont testés et qu'environ 1 fausse tendance est attendue.

```
A2.1 Tableau « Tendances dues au hasard » de /methode
[x] Le retirer (la correction de Benjamini-Hochberg décrite juste au-dessus le rend sans objet)
[ ] Le remplacer par les nombres du jour servis par l'API (nouveau champ)
[ ] Le laisser
Commentaire libre :

A2.2 Marquage « limite » de la tier list
[x] Tous les archétypes à partir de 5 decks, Rogue compris (13 aujourd'hui, dont 8 Rogue)
[ ] Tiers T0 à T3 seulement (5 aujourd'hui), déclaré comme réglage d'affichage
Commentaire libre :

A2.3 Bloc « Le signal OCG → TCG » de l'accueil (r ≈ 0,53 à côté des libellés boutique)
[x] Préciser la population : « archétypes déjà joués dans les deux formats »
[ ] Laisser tel quel
Commentaire libre :

A2.4 Gain du modèle de prévision (l'IC −4 % de l'audit vient de l'ancienne table TCG + OCG)
[x] Ne pas l'afficher ; seul le résultat TCG seul (−6 %, 0,10 à 0,30 point) reste affiché (c'est déjà le cas)
[ ] L'afficher en plus, étiqueté « ancienne table, avant le 16/11 »
[ ] Afficher la valeur recalculée sur la table actuelle (−5,7 %, IC −0,00295 à −0,00071, 27 mois)
Commentaire libre :
```

### A3. Légende du graphique Kewl Tune de l'accueil (TOK-116) — § « Jalon 2 — TOK-116 »
La légende dit « effectifs mensuels non relevés ». Depuis TOK-116, l'API les sert : la phrase est fausse.

```
A3.1 Légende
[x] « Incertitude non dessinée : effectifs mensuels de 145 à 574 decks en OCG » (chiffres lus dans l'API)
[ ] Dessiner la bande de Wilson à 95 %, comme sur /evolution
[ ] Laisser tel quel
Commentaire libre :

A3.2 Fenêtre de l'exemple
[x] Garder la fenêtre fixe (août 2025 → novembre 2026) et les textes actuels
[ ] Fenêtre glissante (16 derniers mois), textes calculés depuis les données
Commentaire libre :
```

### A4. Fenêtre d'arrivée en TCG affichée (TOK-130, point 1) — § « Jalon 2 — TOK-130 »
Boutique, accueil et page d'archétype affichent la fenêtre de 75 à 202 jours avec « couverture vérifiée de 62 à 67 % »,
un chiffre compté en cartes. Compté en archétypes (l'unité qui est affichée), la couverture est de 27 sur 36.

```
A4.1 Fenêtre affichée
[x] Garder 75-202 jours, libellé en archétypes : « arrivée dans la fenêtre pour 27 archétypes sur 36 (2024-2026) ;
    12 sur 18 pour 2026 »
[ ] Remplacer par la fenêtre de survie, libellé « 18 fenêtres sur 23 justes, 2025-2026 » (jamais la probabilité
    Kaplan-Meier)
[ ] Remplacer par la fenêtre de survie avec sa probabilité Kaplan-Meier (déconseillé : trop confiante d'environ 11 points)
[ ] Retirer la fenêtre
Commentaire libre :
```

### A5. Onglet « Impact » et simulateur de ban (lot 26, TOK-132) — § « Formulaire », lignes « Lot 26 »
L'onglet « Impact » affiche un score que la mesure contredit : plus il est haut, **moins** les archétypes qui jouent la
carte perdent après un ban. Il mesure la diffusion d'une carte, pas l'impact d'un ban.

**Recommandation changée pour A5.3** : le 18/11, j'avais proposé « relecture de la collaboratrice d'abord ». Mais ta
décision du 18/11 (1 h 27) dit que la relecture vient après, sur les résultats, et que ta validation suffit pour ce qui
s'affiche. La collaboratrice n'a pas encore accès (TOK-108) : je recommande d'appliquer avant la mise en ligne.

```
A5.1 Onglet « Impact »
[x] Le renommer « Diffusion » et écrire ce que mesure le score (à part des decks égale, plus il est haut, moins les
    porteurs perdent après un ban : +6,5 points par écart type [+4,5 ; +8,6], 158 cartes, 17 listes)
[ ] Garder « Impact » (contredit par la mesure)
[ ] Retirer l'onglet
Commentaire libre :

A5.2 Simulateur de ban
[x] Le décrire comme la position de la carte dans le graphe, sans prévision ; remplacer les « archétypes voisins »
    (31 % seulement sont des archétypes de deck) par les archétypes de deck qui jouent la carte, avec leur effectif
[ ] Retirer le simulateur
[ ] Laisser tel quel
Commentaire libre :

A5.3 Quand
[x] Appliquer maintenant, avant la mise en ligne ; la collaboratrice relit ensuite
[ ] Relecture de la collaboratrice d'abord (le site part avec « Impact »)
Commentaire libre :
```

### A6. Page des signaux précoces (TOK-129) — § « Formulaire », lignes « Jalon 1 (TOK-129) »
Le score bat « les vues seules » quand on compte en cartes. Quand on compte en archétypes, l'écart est nul : environ
8 épisodes, donc un résultat fragile. Ce qui tient est la force OCG, qui désigne l'archétype qui va arriver.

```
A6.1 Page /early-signals
[ ] Garder telle quelle
[x] Revoir (archétypes classés par la force OCG, après un backtest propre) ; la page reste telle quelle en attendant
[ ] Revoir, et masquer la page en attendant
[ ] Masquer la page
Commentaire libre :

A6.2 Suites (plusieurs cases possibles)
[x] Poids du texte à 0 (il coûte −0,106 [−0,212 ; −0,018] ; déjà nul dans le calcul servi)
[x] Archiver views_week chaque lundi (déjà prêt, voir B3)
[x] Ticket : backtest du classement d'archétypes (critères figés avant exécution)
[ ] Fusionner la page avec /boutique (ρ 0,94 avec le rang déjà affiché)
Commentaire libre :
```

### A7. Textes déjà appliqués (lot 16) — § « Formulaire », lignes « Lot 16 »
Ces quatre choix sont déjà en ligne dans la release. Les confirmer ne change rien.

```
A7 Valider en bloc : accent « TCG et OCG » et surtitres « YGO Meta · … » ; tableau TCG / OCG du top 25 sur l'accueil
   (chiffres figés dans SITE_FACTS.banTop25) ; verdict de l'Historique masqué si les sommes servies changent ;
   critère pont « le retirer change de 2 le nombre de cartes touchées dans le top 25 TCG »
[x] Oui, tels quels
[ ] Non, je précise lesquels en commentaire
Commentaire libre :
```

### A8. Correctifs techniques avant la mise en ligne (revue de code du 17/11, lots C et D)
Ce rapport n'avait pas encore de formulaire : `docs/planning/fond/2026-11-17.md`, sur la branche non fusionnée
`claude/fond-2026-11-17-b80f1e`. Il ne contient aucun constat bloquant. Deux lots touchent à ce qui part en ligne. Je les ai
revérifiés aujourd'hui : les défauts sont toujours dans le code.

```
A8.1 Lot C : deploy_prebuilt.py ne vérifie pas que l'API du build lit serving.db (avertissement seulement) : les pages
     construites et l'API en ligne peuvent montrer des données différentes
[x] Corriger avant la mise en ligne : valeur témoin comparée à serving.db, échec bloquant (S)
[ ] Plus tard
Commentaire libre :

A8.2 Lot D : durcir l'API publique — GET /ban-radar?limit=-1 renvoie toute la table ; « % » et « _ » non échappés dans
     la recherche de cartes (« %% » renvoie toutes les cartes, test xfail) ; slug vide possible (S)
[x] Corriger avant la mise en ligne, avec des tests
[ ] Plus tard
Commentaire libre :

A8.3 Lots A (garde-fou : contournements par la syntaxe du shell, faux positif des heredocs), B (build_ban_history.py
     sans transaction), E (mineurs)
[x] Après la mise en ligne, un lot à la fois
[ ] Jamais (je précise en commentaire)
Commentaire libre :

A8.4 Le rapport lui-même
[x] Fusionner la branche du rapport (documentation seule) dans la branche d'intégration
[ ] Le laisser sur sa branche
Commentaire libre :
```

---

## Bloc B — avant le 31/12 (Jalon 4)

Après le 31/12, `deploy_prebuilt.py` refuse de déployer tant que le graphe et les vues ne sont pas recalculés, parce que
leurs tolérances expirent ce jour-là. Ces trois tickets changent des chiffres affichés : verdict de l'Historique, nombre
de communautés, cartes de la page du graphe. Je recommande de les traiter **juste après** la première mise en ligne, en
une seule mise à jour.

### B1. Recalcul du graphe des cartes (TOK-136) — § « Jalon 4 — TOK-136 »
Le graphe passe de 663 à 1 402 cartes et de 63 à 151 communautés. Le backtest bouge peu (rangs médians ±8, top 25
inchangé). Sur la page du graphe, 48 des 150 cartes affichées restent.

```
B1.1 Recalculer le graphe sur la base de référence
[x] Oui, maintenant : déverrouiller graph_metrics et retirer les deux tolérances (un commit), puis graphe, ban_radar,
    ban_history, serving
[ ] Oui, mais au prochain changement de poids du Ban Radar
[ ] Non : garder 663 nœuds (tolérance à reconduire)
Commentaire libre :

B1.2 Verdict de l'Historique après recalcul
[x] Réécrire les chiffres (OCG medianBetter 8 → 7, TCG better 6 → 7) ; la phrase reste vraie telle quelle
[ ] Laisser le verdict masqué jusqu'au prochain diagnostic
Commentaire libre :

B1.3 Chiffre des communautés
[x] 151 communautés sur 1 402 cartes, au même commit
[ ] Compter seulement les communautés d'au moins 3 cartes (119)
Commentaire libre :

B1.4 Critère « pont » du Ban Radar
[x] Ne rien changer maintenant ; le retirer au prochain changement de poids, avec backtest et formulaire
[ ] Le retirer dès maintenant
Commentaire libre :
```

### B2. Fenêtre du backtest limitée aux decks connus à la coupure (TOK-137) — § « Jalon 4 — TOK-137 »
Aujourd'hui, 2,5 % des decks de la fenêtre ont été mis en ligne après la coupure. Les retirer améliore les chiffres (top 25
TCG 29 → 32, OCG 41 → 45). Ce n'est pas un progrès du radar : l'ancienne mesure était pessimiste.

```
B2.1 Défaut du backtest
[x] Adopter « connus à la coupure » par principe (backtest seulement, le classement du jour ne change pas)
[ ] Garder la fenêtre actuelle et documenter la fuite
[ ] Attendre une mesure combinée avec la coupure « contenu » (TOK-121)
Commentaire libre :

B2.2 Ordre avec TOK-136
[x] Une seule mise à jour du site avec les deux tickets (chiffres combinés : TCG 32 / 16, OCG 44 / 17)
[ ] Deux mises à jour séparées
Commentaire libre :

B2.3 Phrase de significativité du verdict
[x] « Avec 10 listes par format, seuls les écarts en OCG (top 25 et rang médian, 9 listes sur 10 chacun) dépassent ce
    que le hasard produit couramment ; aucun ne le fait si l'on tient compte des quatre comparaisons. »
[ ] Autre formulation (à écrire)
Commentaire libre :

B2.4 Chiffres de référence de context.md et CLAUDE.md (84/889, 19/1236)
[x] Les remplacer au même commit (à remesurer avec TOK-136)
[ ] Garder les deux séries côte à côte pendant un mois
Commentaire libre :
```

### B3. Vues de la semaine rafraîchies et archivées (TOK-138) — § « Jalon 4 — TOK-138 »
Les vues sont figées au 13/06. Le rafraîchissement change peu les classements : signal précoce Spearman 0,90, boutique 0,995,
aucun libellé changé.

```
B3.1 Rafraîchir les vues chaque lundi
[x] Oui : déverrouiller card_views et retirer la tolérance des vues (un commit), puis relevé sur la référence
[ ] Oui, mais archiver seulement, sans toucher à cards.views_week
[ ] Non
Commentaire libre :

B3.2 Premier point de l'archive
[ ] Verser l'instantané du 13/06 (data/raw/cards.json), colonne source
[x] Non : l'archive commence au premier relevé
Commentaire libre :

B3.3 fetch_new_cards bloquante dans refresh_all.py (une panne de l'API arrête la chaîne)
[x] Ticket à part : la rendre non bloquante
[ ] Laisser tel quel
Commentaire libre :
```

---

## Bloc C — méthode, rien d'affiché

### C1. Dates d'annonce des banlists (lot 21, TOK-121) — § « Formulaire », lignes « Lot 21 »
```
C1.1 Historique : passer de « veille de l'entrée en vigueur » à « veille de l'annonce » ?
[x] Non, rien ne change (effet faible et exploratoire ; ne jamais écrire « avant l'annonce » pour le TCG)
[ ] Oui, à la veille de la publication des cartes, dans un lot dédié (top 25 OCG 41 → 46, TCG 29 → 33)
[ ] Oui, à la date de Yugipedia (non recommandé)
Commentaire libre :

C1.2 Suite
[x] Relecture de la collaboratrice d'abord, puis décider
[ ] Placebo et test par blocs tout de suite
[ ] Abandonner
Commentaire libre :
```

### C2. Ban Radar en rangs (lot 22, TOK-120) — § « Formulaire », lignes « Lot 22 »
```
C2.1 Poids du Ban Radar (WEIGHTS)
[x] A. Ne rien changer (règle d'adoption figée non remplie)
[ ] B. Rangs centiles avec les poids écrits
[ ] C. Rangs centiles avec les poids du logit conditionnel
Commentaire libre :

C2.2 Suivi des candidats
[x] Relancer diagnose_ban_radar.py --rangs à chaque nouvelle banlist
[ ] En plus, journaliser les classements B et C dans prediction_log (toi seul lances log_predictions.py)
Commentaire libre :

C2.3 Critère bridge
[x] Le retirer au prochain changement de poids (même réponse que B1.4)
[ ] Le remplacer par le pont daté
[ ] Le retirer maintenant
Commentaire libre :

C2.4 card_graph_metrics périmée
[x] Fait par TOK-136 : répondre en B1.1
Commentaire libre :

C2.5 Fenêtre filtrée sur la date du tournoi et non la mise en ligne
[x] Fait par TOK-137 : répondre en B2.1
Commentaire libre :
```

### C3. Contrôle de fraîcheur des tables (TOK-93) — § « Formulaire », lignes « Jalon 1 (TOK-93) »
```
C3.1 Tables périmées connues
[ ] Strict (le job du lundi échoue tant que le bloc B n'est pas fait)
[x] Tolérance déclarée, expiration au 31/12, jamais pour une table absente, vide ou illisible
Commentaire libre :

C3.2 Seuils (calcul 8 j, retard 7 j, tables mensuelles 1 mois, vues 8 j : réglages à la main)
[x] Valider tels quels
[ ] À revoir
Commentaire libre :

C3.3 Tables servies lues par aucun routeur (meta_tier_list, archetype_trend)
[x] Les retirer de SERVED_TABLES (ticket court)
[ ] Les garder, signalées « non lues »
Commentaire libre :

C3.4 Suites
[x] Ticket : rafraîchir views_week chaque lundi (fait par TOK-138, voir B3)
[x] Ticket : colonne computed_at dans les notebooks 02 et 04
Commentaire libre :
```

### C4. Fenêtre d'arrivée par survie, suites (TOK-130, points 2 à 4) — § « Jalon 2 — TOK-130 »
```
C4.2 Rendre le critère testable (5 prévisions seulement sur 2024-2025)
[x] Nouveau script d'ingestion (liste YGOPRODeck complète, cartes OCG seules comprises, depuis 2015), puis relancer B1
[ ] Attendre que les données s'accumulent (6 à 12 mois)
[ ] Abandonner la validation à ± 5 points
Commentaire libre :

C4.3 validate_predictions.py juge l'arrivée par le nom
[x] Ticket : l'aligner sur l'arrivée par les cartes
[ ] Garder l'arrivée par le nom
Commentaire libre :

C4.4 Tables tcg_arrival_survival / tcg_arrival_km (non servies)
[x] Les écrire sur la référence après sauvegarde (trace datée des 3 fenêtres, échéances au printemps 2027)
[ ] Ne rien écrire pour l'instant
Commentaire libre :
```

### C5. Intervalles de prévision (TOK-131) — § « Jalon 2 — TOK-131 »
Les intervalles ne s'affichent pas : ils sont derrière `NEXT_PUBLIC_PREDICTION_INTERVALS`, non renseignée. Couverture
75,7 % [67,7 ; 82,0] pour 80 % visés, 68,3 % sur les 5 premiers archétypes du mois.
```
C5.1 Dessiner les intervalles sur /predictions
[ ] Non, réévaluer dans 6 mois
[x] Oui, derrière l'option, avec la couverture OBSERVÉE dans le libellé
[ ] Oui, sans réserve
Commentaire libre :

C5.2 Niveau
[x] 80 % visé, Mondrian (retenu par la règle figée)
[ ] 90 % visé (choix fait après lecture des résultats)
[ ] Les deux
Commentaire libre :

C5.3 Libellé
[x] « Fourchette visée à 80 % ; rejouée sur 24 mois (507 prévisions), elle a contenu la valeur réalisée 3 fois sur 4,
    2 fois sur 3 pour les 5 premiers archétypes du mois »
[ ] « Intervalle à 80 % » (faux pour les gros archétypes)
[ ] Pas de libellé chiffré
Commentaire libre :

C5.4 Suites
[x] Ticket : corriger le notebook 05 (entraînement sur la cible partielle du mois en cours)
[x] Pré-enregistrer Mondrian asymétrique et le niveau 90 %, réévaluer sur les mois à venir
Commentaire libre :
```

### C6. Signaux précoces, cartes sorties en cours de fenêtre (lot 20, A1)
```
C6.1 Part « déjà en méta » d'une carte sortie en cours de fenêtre
[x] Traiter avec le backtest des signaux (part depuis la sortie TCG, plancher de decks)
[ ] Corriger tout de suite (nouveau seuil)
Commentaire libre :
```

---

## Bloc D — moteur de combos (en pause depuis le 19/11)

### D1. Jalon 7 (TOK-144) — § « Jalon 7 — TOK-144 »
```
D1.1 J1
[x] Non atteint : 3 effets sur 20, Wilson 95 % [5,2 % ; 36,0 %], mesuré avant correction
[ ] Atteint sur la base du taux après correction (déconseillé)
Commentaire libre :

D1.2 Remesurer J1
[x] Nouveau tirage de 20 effets non vus, oracle isolé, même règle (0 sur 20 → borne haute 16,1 %)
[ ] Rejouer seulement les 3 situations en désaccord
[ ] Ne pas remesurer avant J2
Commentaire libre :

D1.3 J2
[ ] Atteint
[x] Atteint sous réserve (longueur ; 1 sur 5 hors échantillon)
[ ] Non atteint
Commentaire libre :

D1.4 Statuts « vérifiée » (combos.db, rien d'affiché)
[x] Garder les 20 cartes vérifiées, Ecclesia and the Dark Dragon en « formalisée » jusqu'à J2-a
[ ] Passer aussi Ecclesia and the Dark Dragon en vérifiée
[ ] Aucune carte vérifiée tant que J1 n'est pas atteint
Commentaire libre :

D1.5 Différence de modèle J2-a
[x] La corriger dans un lot dédié, puis rejouer J2 et les 8 séquences concernées
[ ] Laisser tel quel
Commentaire libre :

D1.6 Terrain adverse dans les autres effets
[x] Ticket à part, avant tout essai avec un adversaire
[ ] Plus tard
Commentaire libre :

D1.7 Questions résiduelles Q1 à Q8
[x] Ne rien envoyer pour l'instant
[ ] Envoyer Q1 et Q2 maintenant
Commentaire libre :

D1.8 Horloge (J2 avant le 13/01/2027)
[x] Maintenue ; prochain jalon du moteur = D1.2 + D1.5 (la pause actuelle consomme cette marge)
[ ] Considérer J2 atteint et arrêter l'horloge
Commentaire libre :
```

### D2. Décisions par défaut des lots 18, C1, C2, C3 — § « Formulaire », lignes « Lot 18 » à « C3 »
24 questions, toutes déjà appliquées dans le code tel qu'il tourne, et les jalons n°5 à 7 se sont appuyés dessus. En
changer une demande de reprendre une partie du moteur.
```
D2 Valider en bloc les 24 choix pré-cochés (classement 54/6/12, texte libre, sous-chaîne d'archétype, T49/R11,
   « non couvert » effet par effet, illégal par caractéristiques imprimées, réserves en main, HORS_PERIMETRE, harnais,
   formalisee = exercée, situations J1 à part, R22 ordre libre, méthode J1, cible Wilson ≤ 20 %, verifiee après oracle,
   N01-N13, R23 obligatoire, N04 permis, N09 étendu, cartes absentes des guides, combo à une carte seule,
   8 filtres D4, J2 sous réserve)
[x] Oui, tous
[ ] Non, je précise lesquels en commentaire
Commentaire libre :
```

---

## Bloc E — organisation

```
E1 Linear : « Fini » = tickets fusionnés dans la branche d'intégration et vérifiés (In Review), sans attendre le push ;
   une session par groupe de tickets qui touchent les mêmes fichiers ; une seule session armée d'avance
[x] Valider
[ ] À revoir
Commentaire libre :

E2 TOK-91 (tier list maison) semble couvert par TOK-97 (tier list calculée à la volée)
[x] Le fermer
[ ] Le garder
Commentaire libre :

E3 Jalons Linear « File de nuit 16-17/11 » et « File du 18/11 » (l'outil ne sait pas les supprimer)
[ ] Je les supprime moi-même dans Linear
Commentaire libre :

E4 Prochain jalon (n°8), moteur en pause
[x] Jalon n°8 = mise en ligne (bloc A appliqué, release v2026.11.19, vérification de la prévisualisation), puis
    jalon n°9 = bloc B
[ ] Laisser le jalon n°8 vide
Commentaire libre :
```
