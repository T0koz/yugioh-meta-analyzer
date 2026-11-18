# Audit de rigueur statistique des scores du site (lot 19, 2026-11-17)

Lecture seule, rapport seul : aucun score, poids, seuil, script, endpoint ni texte du site n'a été modifié. Session sur
Opus 5.5 (`claude-opus-5-5`). Le sous-agent `data-scientist-ygo` a audité le signal boutique, les signaux précoces,
les prédictions méta et les courbes de prix (lecture seule, trois recalculs dans le scratchpad). La session a audité
le reste et a contrôlé trois de ses constats sur la base. Base lue : `data/yugioh.db` et `data/serving.db` du dépôt
principal, en `mode=ro`. Branche `claude/lot19-audit-rigueur-e3bee6`.

**Principe de référence (Thomas, 17/11).** Tout score, prédiction, seuil ou libellé affiché doit remplir quatre conditions :
1. être estimé à partir des données ;
2. être validé hors échantillon dans le temps ;
3. être comparé à une méthode naïve ;
4. être affiché avec son incertitude.

Un réglage posé à la main n'est acceptable que s'il est déclaré comme tel.

## En clair (pour Thomas, 10 lignes)

1. Aucun score du site ne remplit les quatre conditions. Le Ban Radar et les prédictions méta s'en approchent le plus : on les a rejoués sur le passé et comparés à une méthode simple.
2. **Le plus grave : la page « signaux précoces » met en tête des cartes déjà au cœur de la méta, dont une interdite en TCG depuis septembre** (Kewl Tune Rotary, 4e sur 50). Ce score n'a jamais été vérifié.
3. **La fenêtre d'arrivée en TCG « à 80 % » n'en vaut qu'environ 62 à 67 %** quand on la vérifie sur 2024 et 2025. De plus, la page dit « 8 archétypes sur 10 » alors que la mesure porte sur des cartes.
4. Le score boutique classe presque exactement comme la seule popularité en OCG (corrélation de rang 0,94). Aucun test ne montre qu'il fait mieux. Le seul résultat daté est un échec, et il est affiché.
5. Le chiffre r ≈ 0,53, affiché sur la page boutique, montre que l'OCG annonce le TCG pour des archétypes déjà présents dans les deux formats. Il ne valide pas le signal boutique, qui porte sur des archétypes pas encore sortis en TCG.
6. Le Ban Radar a été rejoué sur 20 banlists. Il bat le hasard, et il bat la popularité pour désigner les premières cartes visées, mais cet écart n'est démontré qu'en OCG. Ses poids sont réglés à la main, et 3 listes seulement sont postérieures à ce réglage.
7. Les prédictions méta font à peine mieux que « le mois dernier » : le gain n'est pas démontré sur les données TCG pures. De plus, le mois « prédit » est en réalité le mois en cours, déjà à moitié observé.
8. Les tiers (T1, T3…) reposent sur des seuils ronds choisis à la main : l'intervalle de 5 des 6 archétypes classés chevauche un seuil. La tendance passe par un vrai test, mais pas de correction pour les 60 tests faits en même temps.
9. Le « score de pont » et le simulateur de ban sont des formules posées à la main, jamais confrontées à un vrai ban. Le simulateur affirme « recalculer le graphe sans la carte », ce que le code ne fait pas.
10. Bonne nouvelle : la plupart des pages déclarent déjà honnêtement « aucun intervalle » ou « seuils provisoires ». Les défauts graves tiennent en 4 tickets courts. Le formulaire est en fin de document.

## Tableau de synthèse

Légende des colonnes :
- **Estimé** : estimé sur les données (oui), réglé à la main (main), ou les deux (mixte).
- **Validé HE** : validé hors échantillon, dans le temps.
- **Naïf** : comparé à une méthode naïve.
- **Incert.** : incertitude affichée sur la page.
- **Risque** : risque pour la crédibilité, de 1 (le plus fort) à 4.
- **Effort** : S = moins d'une demi-journée, M = 1 à 2 jours, L = plus de 2 jours ou dépend de données à venir.

| # | Score | Estimé | Validé HE | Naïf | Incert. | État | Risque | Effort pour le mettre au niveau |
|---|---|---|---|---|---|---|---|---|
| 1 | Signaux précoces (`early_score`) | main | non | non | non, déclaré | défaut de méthode, texte faux | **1** | S (filtre, texte) puis M (backtest) |
| 2 | Fenêtre d'arrivée OCG → TCG « 80 % » | oui (quantiles) | non (recalcul : 62-67 %) | sans objet | oui (segment), mais faux | défaut de méthode, texte faux | **1** | S (texte) puis M (survie) |
| 3 | Signal boutique (`alert_score`, `buy_score`) | main | non (rien d'échu, 1 série négative) | non | non, déclaré | non démontré ; r ≈ 0,53 mal placé | **1** | S (texte) puis L (séries datées) |
| 4 | Libellés Fort / Modéré / Faible | main (10 % / 25 % de rang) | non | non | déclaré « provisoires » | réglage déclaré ; journal sur le mauvais champ | 2 | S |
| 5 | Prédictions méta (70 % naïf + 30 % Ridge) | mixte (Ridge estimé, mélange réglé sur le test) | oui (walk-forward, 24 mois) | oui (persistance) | non par archétype, déclaré | cible mal libellée, gain fragile | 2 | S puis S/M (intervalles) |
| 6 | Ban Radar (score 0-100) | main (`WEIGHTS`) | partiel (20 listes, 3 après le réglage) | oui (hasard, staples) | non, déclaré ; bande du hasard sur l'Historique | réglage non déclaré comme tel ; commentaire faux | 2 | S (déclaration), M (TOK-115) |
| 7 | Tiers de la tier list (40/15/7/3 %) | main | sans objet (descriptif) | sans objet | oui (Wilson) | réglage non déclaré comme tel | 3 | S |
| 8 | Tendance (test z de deux proportions) | oui (test) | sans objet | sans objet | partiel | pas de correction multiple | 3 | S |
| 9 | Score de pont (`bridge_score`) | main (formule) | non | non | non, déclaré | jamais confronté à un ban | 2 | M |
| 10 | Simulateur de ban | main (approximations) | non | non | non, déclaré | le texte décrit un calcul absent | 2 | S (texte) ou M (vrai calcul) |
| 11 | Decks : seuils 80 % / 20 %, fiche dès 8 listes | mixte (choix étayés par bootstrap) | stabilité seulement | sans objet | effectifs « k sur n » | conforme, réglage déclaré | 4 | — |
| 12 | Courbes de prix (trou au-delà de 10 jours, 3 relevés minimum) | main (convention d'affichage) | sans objet | sans objet | relevés bruts | conforme, déclaré | 4 | — |
| 13 | Graphe de co-occurrences (seuil de lien) | main | non | non | déclaré « pas d'intervalle » | hors périmètre prédictif | 4 | — |

## Les 5 risques de crédibilité les plus forts

1. **Signaux précoces : une carte interdite et des cartes déjà dominantes en tête.** Un client boutique qui achète sur cette page achète des cartes déjà chères, ou une carte interdite.
2. **Fenêtre d'arrivée annoncée à 80 %, observée à 62-67 %.** C'est le seul chiffre de la boutique présenté comme un intervalle mesuré, et il est faux d'environ 15 points. La phrase « 8 archétypes sur 10 » est fausse dans son unité.
3. **Le r ≈ 0,53 sert de caution au signal boutique.** Il mesure autre chose, sur une population sélectionnée par la cible. Le signal lui-même revient à la popularité OCG (ρ = 0,94), sans démonstration qu'il fait mieux.
4. **Le simulateur de ban décrit un calcul qu'il ne fait pas.** De plus, le score de pont et la « fragmentation » ne sont pas validés.
5. **Ban Radar : poids réglés à la main, peu de listes postérieures au réglage, un commentaire de code faux.** Le score est réellement comparé au hasard et à la popularité, mais son statut de réglage manuel n'est pas déclaré à l'écran. L'avance sur la popularité n'est démontrée qu'en OCG, en tête de classement.

## Détail par score (pour la collaboratrice)

Notation : HE = hors échantillon ; « [recalcul] » = calcul refait dans ce lot, hors dépôt, méthode indiquée.

### 1. Signaux précoces : `early_card_signals`, page `/early-signals`

- **Construction** (notebook 11, cellule 9) : `0,35·vues + 0,35·synergie textuelle + 0,30·force OCG`, normalisé sur le maximum.
- **Constantes posées à la main** :
  - les poids 0,35 / 0,35 / 0,30 ;
  - les fenêtres de 168, 380 et 200 jours (cellule 1) ;
  - `text_synergy_score >= 0.1` (cellule 5) ;
  - le top 20 des archétypes méta ;
  - les 50 cartes affichées (`backend/app/routers/boutique.py:24`).
- **Validation** : aucune, ce que `/methode` déclare (« Aucune à ce jour »). `scripts/validate_predictions.py` est descriptif.
- **Méthode naïve** : aucune. La base évidente serait le classement par vues seules.
- **Incertitude** : aucune. C'est déclaré (`early-signals/page.tsx:93`).
- **Défauts de méthode** :
  - **Filtre de banlist périmé.** Le notebook filtre sur `cards.ban_tcg`, figé au 13 juin. Vérifié par la session : Kewl Tune Rotary est au rang 4 sur 50, alors qu'elle est Forbidden dans `banlist_history` (TCG, listes du 2026-09-21 et du 2026-10-19). Les cartes classées 1, 4, 5 et 20 sont toutes sorties en TCG le 2026-05-07, donc ne « montent » plus « avant la méta ».
  - `REF = date.today()` : le calcul n'est pas reproductible.
  - Les vues datent de jours différents selon les cartes : figées au 13 juin pour les anciennes, du jour pour les nouvelles.
- **Texte faux** : la page et `/methode` parlent de « co-occurrences » et de « tier ». Le calcul utilise une similarité de texte (positive pour 11 cartes sur 426 seulement) et la force OCG.
- **Pour le mettre au niveau** :
  - (S) Lire la banlist dans `banlist_history`, exclure les cartes déjà sorties en TCG depuis plus de N mois, fixer `REF` au dernier deck, corriger le texte.
  - (M) Backtest à des dates passées : part de decks TCG à +3 mois, contre le classement par vues seules. Critère : precision@20 au-dessus de cette base, avec un IC bootstrap par date qui exclut 0.

### 2. Fenêtre d'arrivée OCG → TCG : `tcg_window_start`, `tcg_window_end`

- **Construction** : quantiles P10 et P90 du délai OCG → TCG par carte, soit `DELAI_P10/P90 = 75/202` jours (notebook 10). La fenêtre est ancrée sur la médiane du premier deck OCG de l'archétype.
- **Défauts de méthode** :
  - **Biais du survivant.** `cards` ne contient que des cartes sorties en TCG (`fetch_cards.py`, `format=tcg`) : le délai n'est mesuré que sur les cartes arrivées. Or 37 % des archétypes ne sont jamais arrivés (journal `signal-boutique-v3.md`).
  - **[recalcul, sous-agent]** P10-P90 estimés sur les cartes OCG 2022-2023 (n = 1 078) : de 89 à 202 jours. Cet intervalle couvre **67 %** des cartes de 2024 (n = 367) et **62 %** de celles de 2025 (n = 470), au lieu des 80 % annoncés.
  - **Changement d'unité** : le délai est mesuré par carte, mais appliqué à un archétype.
- **Texte faux** :
  - `frontend/src/app/methode/page.tsx:407` dit « 8 archétypes sur 10 » (vérifié). La mesure porte sur des cartes, et seulement celles qui sont arrivées.
  - `ArrivalTimeline.tsx:129-132` dit « 8 fois sur 10 par le passé ».
- **Incertitude** : affichée (segment), mais sa couverture est surévaluée.
- **Pour le mettre au niveau** :
  - (S) Texte « cartes, parmi celles sorties en TCG », avec la couverture observée.
  - (M) Analyse de survie par archétype (Kaplan-Meier avec les cas censurés), validée par origine glissante. Critère : couverture annoncée = couverture observée ± 5 points sur 2024-2025.

### 3. Signal boutique : `alert_score` et `buy_score`, page `/boutique`

- **Construction** :
  - `meta_score_ocg = sqrt(part × placement normalisé)` ; sans placement, `fillna(part)`, une règle posée à la main ;
  - `alert_score = meta_score_ocg × log1p(vues moyennes)`, normalisé sur le maximum ;
  - `buy_score = 0,7·alert_norm + 0,3·100·price_opp` (`scripts/build_buy_signals.py:63-67`).
- **Constantes posées à la main** :
  - notebook 10, cellule 1 : `FENETRE_OCG_MOIS=3`, `MIN_OCG_DECKS=5`, `MIN_CARTES_INEDITES=3`, `FREQ_CARTE_CLE=0.3`, `SEUIL_STAPLE=0.20`, `MIN_ARCH_STAPLE=30`, `FENETRE_STAPLES_MOIS=12` ;
  - les poids 0,7 / 0,3.
- **Méthode naïve. [recalcul, sous-agent]** Spearman entre `ocg_score` et la seule part des decks OCG : **0,94** (n = 89). Les rangs des 3 archétypes retenus bougent d'une place au plus. Le facteur vues est figé au 2026-06-13 et vaut zéro pour les cartes inédites.
- **Validation HE du score** : aucune, première échéance en mars 2027. Seule série datée : TOK-74, signal de juin, −34,8 % sur 34 cartes contre −0,8 % pour le marché. C'est un échec, affiché sur `/methode`, mais il porte sur la v1.
- **Le r ≈ 0,53** (`docs/evaluation-prediction.md` B1/B5) :
  - Pearson poolé à un décalage de 4 mois, 652 paires, 105 archétypes, IC 95 % bootstrap par archétype [0,43 ; 0,59].
  - La jointure ne garde que les archétypes présents dans les deux formats : c'est une sélection sur la cible.
  - Le walk-forward B3 (20 mois de test) donne R² 0,347 pour AR + OCG contre 0,107 pour AR seul ; l'IC de ΔMSE exclut 0. Le lien OCG → TCG est donc réel.
  - Ce chiffre ne dit rien des archétypes absents du TCG ni d'`alert_score`. Le StatBand de `/boutique` le présente pourtant comme une caution du signal.
- **Pour le mettre au niveau** :
  - (S) Sortir le r du bandeau du signal, ou écrire sur quelle population il porte.
  - (L) Valider sur des séries datées contre la base « part OCG ». Critère : arrivée en TCG et variation de prix meilleures que cette base, sur au moins 10 lots journalisés.

### 4. Libellés Fort / Modéré / Faible

- **Règle** (`backend/app/signal_label.py:20-21`) : rang de l'archétype parmi les 89 de `ocg_archetype_scores` ; Fort au rang 10 % ou mieux, Modéré à 25 % ou mieux. Réglage à la main, déclaré « provisoires, non validés hors échantillon » sur la page.
- **Défauts** :
  - Le dénominateur compte des archétypes déjà sortis en TCG et 53 archétypes à moins de 5 decks. La sensibilité est documentée dans `seuils-signal-boutique.md` : à n = 36, seul Raise Moon reste Fort.
  - **`scripts/log_predictions.py:163` journalise `buy_label`**, l'ancien libellé relatif. Le libellé affiché (`signal_label`) ne pourra donc jamais être évalué.
- **Pour le mettre au niveau** : (S) journaliser `signal_label` et `archetype_rank` ; restreindre la population aux archétypes à au moins 5 decks, ou la déclarer.

### 5. Prédictions méta : page `/predictions`

- **Construction** (notebook 05) :
  - Ridge (α = 50) sur la variation (delta), 20 variables, fenêtre glissante de 9 mois ;
  - `prévision = niveau + 0,3·delta` ;
  - le mélange `W_MODEL = 0,3` a été choisi sur les mêmes plis de test. `evaluation-prediction.md` le décrit comme un plateau, pas un optimum.
- **Validation HE : oui**, walk-forward strict, 24 mois de test, bootstrap par mois (`docs/evaluation-prediction.md`, A) :
  - MAE du delta : −4 % par rapport à la persistance, IC [−0,00116 ; −0,00051] ;
  - ρ du delta : 0,347 [0,264 ; 0,434] ;
  - Ridge contre une régression linéaire sur le seul niveau : aucun écart (ρ +0,009 [−0,057 ; +0,085]) ;
  - **TCG pur (519 lignes)** : écart ensemble − naïf en niveau de +0,012 [−0,014 ; +0,041], indistinguable de 0.
- **Méthode naïve** : oui, affichée sur `/methode` (« à peine mieux que la valeur du mois observé »), sans l'IC.
- **Défauts** :
  - `meta_predictions.data_month = 2026-10` (vérifié) : la cible est novembre 2026, déjà à moitié observé et non utilisé.
  - La flèche porte sur le delta complet, l'haltère sur 0,3·delta : les deux peuvent se contredire.
  - En production, `last_banl` lit le dernier statut de banlist, qui peut être postérieur à `data_month`.
  - Les sorties du notebook sont périmées : son en-tête donne ρ naïf = 0,508, contre 0,672 aujourd'hui.
- **Incertitude** : aucune par archétype, ce que déclare `predictions/page.tsx:65`.
- **Pour le mettre au niveau** :
  - (S) Libellé « mois en cours, partiel » ou cible décalée ; flèche calculée sur l'écart dessiné ; IC du gain sur `/methode`.
  - (S/M) Intervalles par archétype à partir des résidus du walk-forward (méthode conforme). Critère : couverture observée de 80 % ± 5 points sur 24 mois.

### 6. Ban Radar

- **Construction** : score 0-100, somme pondérée de 6 critères normalisés (`scripts/build_ban_radar.py:46`, `WEIGHTS`, dupliqués dans `backend/app/routers/ban_radar.py:23`). Réglages posés à la main : `WINDOW_MONTHS=6`, `MOMENTUM_SPLIT_MONTHS=3`, `MIN_DECKS=5`, `GENERIC_CONCENTRATION_THRESHOLD=0.5`, `BACKTEST_MIN_DECKS=600`. Le seuil de 600 est étayé, la liste d'avril 2026 tombant au niveau du hasard.
- **Validation** : 20 banlists rejouées (`docs/journal/ban-historique-tok-55.md`, `ban-radar-tcg-diagnostic.md`, relecture `ban-radar-tcg-relecture.md` jugée « valide avec réserves »).
  - Les poids ont été calés le 2026-08-14 en voyant les listes jusqu'à juillet. Seules **3 listes sont postérieures** au calage (TCG 2026-09-21, TCG 2026-10-19, OCG 2026-10-01), et les deux listes TCG récentes sont mauvaises (rang 206 sur 981, 308 sur 905).
  - Le reste est un rejeu en partie dans l'échantillon. Le diagnostic le chiffre : il y voit un « avantage indu des poids actuels ».
- **Méthode naïve : oui**, hasard (bande à 90 %) et « staples les plus jouées ».
  - En rang médian, les staples font mieux sur 7 listes TCG sur 10 : tendance non démontrée, test du signe p = 0,34.
  - Top 25 de la veille : 29 cartes touchées contre 16 aux staples en TCG, 41 contre 18 en OCG. Seul l'écart OCG est démontré (9 listes sur 10, p = 0,02), avec environ un faux positif attendu sur 20 tests et des fenêtres de 6 mois qui se chevauchent.
- **Incertitude** :
  - « aucun intervalle : un score de risque classe les cartes, ce n'est pas une probabilité » (`BanRadarView.tsx:198`) ;
  - l'onglet Historique dessine la bande du hasard ;
  - le caractère manuel des poids n'est pas dit sur la page.
- **Défauts annexes** :
  - Le commentaire « Testés à ±0.10 sans changer le classement » (`scripts/build_ban_radar.py:45`) est faux : `ubiquity` −0,10 fait passer le top 25 TCG de 30 à 23 (relecture, I2).
  - Le critère « pont » utilise un graphe calculé sur toutes les données, une fuite d'au plus 7 rangs (diagnostic, l. 269).
- **Pour le mettre au niveau** :
  - (S) Déclarer « poids fixés à la main le 2026-08-14, 3 listes postérieures » ; corriger le commentaire.
  - (M) Formulaire TOK-115 : figer une règle d'adoption et accumuler les listes postérieures ; calculer le pont par date.

### 7 et 8. Tier list : tiers et tendance (`backend/app/tiering.py`)

- **Tiers** : seuils sur la part de decks de la fenêtre, T0 40 %, T1 15 %, T2 7 %, T3 3 % (`tiering.py:20`), Rogue sous 5 decks (`:22`). Seuils ronds, réglés à la main. C'est descriptif, donc la validation HE ne s'applique pas, mais le caractère conventionnel n'est pas déclaré.
- **[recalcul, session]** Fenêtre de 396 decks, `compute_tier_list` sur `serving.db`, intervalles de Wilson à 95 %. Sur les 6 archétypes classés T1 à T3, **5 ont un intervalle qui chevauche un seuil de tier** :

  | Archétype | Tier | Part et intervalle | Seuil chevauché |
  |---|---|---|---|
  | Angelechy | T1 | 16,4 % [13,1 ; 20,4] | 15 % |
  | Radiant Typhoon | T3 | [3,9 ; 8,6] | 7 % |
  | Artmage | T3 | [3,7 ; 8,3] | 7 % |
  | Dark Magician Chaos Ritual | T3 | [3,1 ; 7,4] | 7 % |
  | Branded | T3 | [2,5 ; 6,5] | 3 % |

  Seul Elfnote (T1, [17,0 ; 25,0]) est net. La barre d'intervalle est affichée (`tier-list/page.tsx:70`), mais le tier lui-même est présenté comme certain.
- **Tendance** : test z de deux proportions à 5 % (`tiering.py:24-57`), Stable sous 10 decks. **[recalcul]** 10 signaux sur 60 archétypes (4 en hausse, 6 en baisse), là où le hasard seul en donnerait environ 3. Pas de correction pour comparaisons multiples : la docstring le reconnaît, la page non.
- **Pour le mettre au niveau** : (S) déclarer « seuils conventionnels » et marquer « à la limite » un tier dont l'intervalle chevauche un seuil ; (S) correction de Benjamini-Hochberg sur la tendance, ou mention « environ 3 signaux sur 60 attendus par hasard ».

### 9. Score de pont : `bridge_score`, onglet « Impact »

- **Construction** : `n_archetypes × log(1 + decks)` (`scripts/build_card_impact.py:51`), formule posée à la main, sans paramètre estimé.
- **Validation** : aucune. On ne sait pas si un ban sur une carte à fort score de pont a fragmenté davantage la méta. Le score est présenté comme « Impact » (`CardImpactView.tsx:19`).
- **Méthode naïve** : aucune. Le score est quasi monotone en `decks` × `n_archetypes`, donc proche de la popularité.
- **Incertitude** : « comptes exacts », déclaré. Exact sur les comptes, mais rien n'est dit sur ce que le score prédit.
- **Pour le mettre au niveau** : (M) mesure a posteriori sur les 20 listes. Mesure : variation de la part de méta des archétypes porteurs à +3 mois du ban, selon le score de pont de la carte touchée, comparée à la seule part des decks. À défaut, renommer en « diffusion » et déclarer la formule.

### 10. Simulateur de ban (`POST /simulate-ban`)

- **Construction** (`backend/app/routers/cards.py:64-131`) :
  - `fragmentation = betweenness / max(betweenness)`, une approximation commentée dans le code ;
  - « archétypes impactés » : archétypes des 15 voisins de plus fort Jaccard, plus l'archétype porteur ;
  - `community_id` : premier `LIKE` sur `top_archetypes`.
- **Texte faux** : le pied de page dit « la simulation recalcule le graphe sans la carte » (`BanSimulatorView.tsx:131`). Le code lit une betweenness précalculée et ne recalcule rien.
- **Validation et méthode naïve** : aucune. L'appariement de communauté par `LIKE` est fragile : un nom contenu dans un autre suffit à se tromper de communauté.
- **Pour le mettre au niveau** : (S) corriger le texte (« estimation à partir de la position de la carte dans le graphe ») ; (M) recalculer réellement la composante sans la carte, puis valider comme au point 9.

### 11 à 13. Conformes, ou hors périmètre prédictif

- **Decks** (`backend/app/deck_profile.py:13-20`) :
  - 80 % et 20 % sont des seuils ronds, mais justifiés par mesure : stabilité bootstrap, 9,3 % d'étiquettes changées, sans meilleur couple mesurable ;
  - fiche dès 8 listes, l'erreur est divisée par deux entre 5 et 8 listes (`docs/journal/decks-tok-114.md`) ;
  - chaque part s'affiche en « k sur n ». Conforme. Écart mineur : le journal dit « seuils ronds », la page ne le dit pas.
- **Courbes de prix** (`backend/app/price_history.py:16,20`) : convention d'affichage déclarée, rien n'est interpolé. Seule limite : une variation « depuis juin » repose parfois sur 2 relevés.
- **Graphe** : seuil de lien posé à la main, déclaré (`graph/page.tsx:42`). Descriptif.

## Défauts de méthode, et défauts seulement d'affichage

- **Défauts de méthode** :
  - filtre de banlist des signaux précoces ;
  - fenêtre d'arrivée biaisée par le survivant, et changement d'unité carte → archétype ;
  - aucune base naïve pour le score boutique ni pour les signaux précoces ;
  - mauvais libellé journalisé ;
  - `W_MODEL` choisi sur le test ;
  - cible de prédiction partielle ;
  - poids du Ban Radar calés en voyant presque toutes les listes rejouées ;
  - pont du Ban Radar calculé avec des données futures ;
  - tendance sans correction multiple ;
  - score de pont et simulateur jamais confrontés à un ban.
- **Seulement non déclaré, ou faux à l'écran** :
  - « 8 archétypes sur 10 » ;
  - « co-occurrences » et « tier » sur `/early-signals` ;
  - « recalcule le graphe » dans le simulateur ;
  - r ≈ 0,53 présenté comme caution du signal ;
  - « mois prochain » au lieu du mois en cours ;
  - poids du Ban Radar et seuils de tier non déclarés comme réglages manuels ;
  - tier présenté comme certain près d'un seuil ;
  - IC du gain de prévision absent.

## Tickets proposés (numérotation provisoire, non créés dans Linear)

Classés par impact sur la crédibilité, puis par effort.

| # | Titre | Pourquoi | Critère de fin | Effort |
|---|---|---|---|---|
| A1 | Signaux précoces : banlist à date, cartes déjà en méta exclues, texte juste | Une carte interdite et des cartes dominantes en tête ; le texte décrit un autre calcul | 0 carte Forbidden ou Limited à la date du calcul ; `REF` = dernier deck ; texte = calcul réel | S |
| A2 | Fenêtre d'arrivée : textes corrigés et couverture observée affichée | Annoncée à 80 %, observée à 62-67 % ; unité fausse | « cartes sorties en TCG », couverture 2024-2025 écrite sur `/methode` et dans `ArrivalTimeline` | S |
| A3 | Boutique : r ≈ 0,53 hors du bandeau du signal, ou population précisée | Le chiffre ne valide pas le signal affiché | Le StatBand ne présente plus ce r comme une mesure du signal | S |
| A4 | Simulateur : texte conforme au calcul | Il décrit un recalcul absent | Pied et libellés décrivent l'approximation par la betweenness | S |
| A5 | Journal des prédictions : enregistrer `signal_label` et `archetype_rank` | Sinon le libellé affiché ne sera jamais évalué en mars 2027 | Champs présents dans `prediction_log.jsonl` au prochain recalcul | S |
| A6 | Prédictions : « mois en cours, partiel », flèche sur l'écart dessiné, IC du gain sur `/methode` | Cible mal nommée ; flèche et haltère peuvent se contredire | Libellé et flèche cohérents ; IC [−0,00116 ; −0,00051] et résultat TCG pur affichés | S |
| A7 | Déclarer les réglages manuels : poids du Ban Radar, seuils de tier, seuils ronds de Decks ; corriger le commentaire ±0,10 | Le principe l'exige ; un commentaire faux dans le code | Chaque réglage dit « fixé à la main » sur `/methode` avec sa date ; commentaire corrigé | S |
| A8 | Tier list : tier « à la limite » quand l'intervalle chevauche un seuil ; correction multiple de la tendance | 5 tiers sur 6 sont à la limite ; 10 signaux pour environ 3 attendus | Marquage visible ; tendance après Benjamini-Hochberg, ou nombre attendu affiché | S |
| B1 | Fenêtre d'arrivée par analyse de survie, par archétype, censure incluse | Biais du survivant | Couverture annoncée = observée ± 5 points en validation à origine glissante, 2024-2025 | M |
| B2 | Backtest des signaux précoces contre « vues seules » | Aucune validation, aucune base | precision@20 meilleure que la base, IC bootstrap par date qui exclut 0 | M |
| B3 | Score de pont et simulateur confrontés aux 20 banlists | « Impact » jamais mesuré | Lien score → variation de méta à +3 mois estimé avec IC, contre la part des decks seule ; sinon renommer | M |
| B4 | Intervalles de prévision par archétype (conformes, sur les résidus du walk-forward) | Aucune incertitude par archétype | Couverture observée de 80 % ± 5 points sur 24 mois | S/M |
| B5 | Ban Radar : pont calculé par date, règle d'adoption figée, suivi des listes postérieures au calage | Fuite légère ; 3 listes réellement hors échantillon | Pont daté ; tableau « listes postérieures au calage » tenu à jour sur l'Historique | M |
| C1 | Score boutique validé contre la base « part OCG » sur séries datées | ρ = 0,94 avec la popularité ; aucun gain démontré | Gain sur l'arrivée en TCG et sur le prix, au moins 10 lots, IC qui exclut 0 ; sinon afficher la part OCG seule | L (données à venir) |

## Formulaire pour Thomas

```
1. Quels tickets lancer en premier ?
[x] A1 à A4 (les quatre textes ou filtres faux, tous S), puis A5 à A8
[ ] A1 à A8 dans l'ordre, d'une seule traite
[ ] D'abord les tickets de méthode (B1, B2)
Commentaire libre :

2. Signaux précoces, en attendant A1 :
[x] Garder la page, avec A1 fait en priorité (une demi-journée)
[ ] Masquer /early-signals jusqu'au backtest B2
[ ] Ne rien changer
Commentaire libre :

3. Fenêtre d'arrivée en TCG : que faire du « 80 % » ?
[x] Afficher la couverture observée (environ 62-67 %) tout de suite (A2), puis B1
[ ] Élargir la fenêtre pour qu'elle couvre vraiment 80 % (même méthode, quantiles recalés)
[ ] Retirer la fenêtre jusqu'à B1
Commentaire libre :

4. Score boutique, à peu près égal à la popularité OCG (ρ = 0,94) :
[x] Garder le score, déclarer « proche de la seule part OCG », lancer C1 dès qu'il y a des lots échus
[ ] Remplacer dès maintenant le score par la part OCG seule (plus simple, même classement)
[ ] Ne rien changer
Commentaire libre :

5. Réglages manuels à garder en les déclarant (A7) :
[x] Poids du Ban Radar
[x] Seuils de tier 40/15/7/3 %
[x] Seuils Decks 80/20 % et fiche dès 8 listes
[x] Seuils Fort / Modéré 10/25 %
[ ] Aucun : tout doit être estimé avant affichage
Commentaire libre :

6. Score de pont et simulateur :
[x] Corriger le texte maintenant (A4), puis valider (B3) ; renommer en « diffusion » si B3 échoue
[ ] Retirer l'onglet Impact et le simulateur jusqu'à B3
[ ] Ne rien changer
Commentaire libre :

7. Tier list :
[x] Marquer « à la limite » et corriger la tendance (A8)
[ ] Remplacer les tiers par un classement de parts avec intervalles, sans tiers
[ ] Ne rien changer
Commentaire libre :

8. Relecture par la collaboratrice :
[x] Lui faire relire les recalculs de ce rapport (couverture de 62-67 %, ρ = 0,94, chevauchements de tiers) avant tout ticket de méthode
[ ] Pas de relecture
Commentaire libre :
```

## Limites de cet audit

- Les recalculs du sous-agent (couverture de la fenêtre, ρ = 0,94) n'ont pas été refaits par la session. Trois constats ont été contrôlés sur la base : le rang et le statut de Kewl Tune Rotary, la valeur de `data_month`, la phrase de `methode/page.tsx:407`.
- Le recalcul des tiers porte sur un seul instant (fenêtre de 396 decks, `serving.db` du dépôt principal).
- Aucun ticket n'est créé dans Linear (connecteur déconnecté).

## Correctifs A1 à A8 (lot 20, TOK-122, 2026-11-18)

Branche `claude/lot20-audit-a1-a8-cbc82f`, un commit par ticket. Session sur Opus 5.5 ; `data-scientist-ygo` a relu
A1, A5, A6 et A8, `gardien-donnees` les champs servis (A1, A6, A8). Aucun `WEIGHTS` modifié, `BACKTEST_MIN_DECKS`
inchangé, aucune écriture dans la base de référence (calculs vérifiés sur une copie dans le scratchpad).

| Ticket | Fait | Critère de fin, mesuré | Écart à l'audit |
|---|---|---|---|
| A1 | Calcul extrait du notebook 11 dans `scripts/build_early_signals.py` (le notebook n'écrit plus) : référence = dernier deck TCG (2026-11-14), banlist TCG à cette date, cartes sorties en TCG avant la fenêtre de 168 jours exclues, cartes jouées dans ≥ 3 % des decks TCG légaux des 90 derniers jours exclues (seuil T3, 70 cartes). API : `as_of`, `cards_scored`, `text_signal_cards`. Textes alignés sur le calcul réel. | 0 carte Forbidden ou Limited sur 263 (3 exclues) ; deux exécutions identiques ; Kewl Tune absente. | Constat nouveau : la proximité de texte vaut 0 pour les 263 cartes retenues (`text_synergies`, produite par le notebook 07 hors chaîne, n'atteint 0,1 pour aucune) : le score revient à 54 % vues, 46 % OCG. Dit sur la page, poids inchangés. |
| A2 | « 8 archétypes sur 10 » et « 8 fois sur 10 » remplacés : délai de 8 cartes sur 10 parmi celles sorties en TCG ; couverture vérifiée écrite sur `/methode`, `ArrivalTimeline`, `/boutique`, page d'archétype, accueil. | Recalcul refait : P10-P90 2022-2023 (n = 1 078, 89 à 202 j) couvrent 67 % des cartes de 2024 (n = 367) et 62 % de 2025 (n = 470). | Aucun. Note : la fenêtre affichée (75-202, estimée sur 2022-2025) couvre 89 % des cartes de 2024 en échantillon, 62 % en 2025. |
| A3 | r ≈ 0,53 retiré du StatBand de `/boutique` ; population dite (archétypes déjà joués dans les deux formats) ; « proche de la seule part OCG » déclaré (question 4). | Le bandeau ne présente plus le r comme mesure du signal. ρ recalculé : 0,9396 (n = 89). | Aucun. Bloc OCG → TCG de l'accueil non touché (formulaire). |
| A4 | Simulateur : titre, introduction, libellés (« Centralité de pont, part du maximum », « Archétypes voisins ») et pied décrivent l'approximation par la betweenness précalculée ; « jamais confrontée à un ban réel ». | Plus aucune mention d'un recalcul du graphe. | Aucun. |
| A5 | `log_predictions.py` : `predicted_label` = `signal_label` affiché ; payload `archetype_rank`, `rank_population`, `ocg_score`, `rank_computed_at`, `label_rule`, `label_source` ; `buy_label` gardé dans le payload. Script non lancé. | Vérifié par `collect()` en lecture seule : 12 + 3 lignes, mêmes libellés et rangs que l'API. Champs présents au prochain recalcul (Thomas). | `BOUTIQUE_MODEL` inchangé (une nouvelle version doublerait les prédictions déjà journalisées). |
| A6 | Mois prévu dit « mois en cours, déjà en partie relevé » quand c'est le cas ; flèche calculée par l'API sur l'écart dessiné (seuil 0,003 = 0,3 × 0,01, servi et déclaré) ; tableau du gain avec intervalles sur `/methode`. | 0 archétype sur 19 ne change de direction. Gain TCG seuls : −6 % (0,10 à 0,30 point de score ×100), niveau +0,012 [−0,014 ; +0,041]. | **L'IC [−0,00116 ; −0,00051] (−4 %) cité par le critère vient de l'ancienne table TCG + OCG d'avant TOK-80, plus reproductible** (sur la `meta_scores` actuelle : −0,00186 [−0,00295 ; −0,00071]). Non affiché ; seul le résultat TCG seul (évaluation du 16/11, recompté) l'est. Formulaire. |
| A7 | `/methode` : chaque réglage « fixé à la main » avec sa date (10 lignes) ; Ban Radar : 3 listes sur 20 postérieures au réglage ; commentaire « ±0,10 » corrigé dans `build_ban_radar.py`. | Chaque réglage de la question 5 daté sur `/methode`. | Aucun. |
| A8 | Tendance : Benjamini-Hochberg (q = 0,05) sur les archétypes testés, dans `compute_tier_list` (tier list, archétype, decks) ; « limite » quand l'intervalle de Wilson à 95 % contient un seuil de tier (seuils servis par l'API, Wilson côté front), à partir de 5 decks. | Marquage visible : 13 archétypes (T1 1, T3 4, Rogue 8). Tendance après correction : 10 sur 10 gardées (plus grande p retenue 0,018). | **Seuls 20 archétypes sont testés (≥ 10 decks cumulés sur les deux fenêtres), pas 60** : sans correction, ≈ 1 fausse tendance attendue, pas ≈ 3. Le tableau « environ 60 / environ 3 » de `/methode` est laissé tel quel en attendant le formulaire. BH tient malgré la dépendance (somme à 1) : 3,75 % de tirages avec au moins une fausse tendance sous l'hypothèse nulle (simulation, 4 000 tirages). |

### Après fusion, sur la base de référence (orchestrateur, après sauvegarde)

```bash
python scripts/build_early_signals.py   # réécrit early_card_signals (colonne as_of, noms sans <P>/<C>/<Q>)
python scripts/build_serving_db.py      # sinon l'API sert as_of = None et l'ancienne table
```

Aucune autre table à recalculer : A2 à A8 ne touchent que des textes, des constantes et des calculs à la volée de l'API.
`scripts/log_predictions.py` (A5) prendra les nouveaux champs au prochain recalcul, lancé par Thomas.

### À relire par la collaboratrice

- A1 : règle « déjà en méta » (3 % des decks TCG légaux sur 90 jours, seuil T3) et sa réserve : la part sur 90 jours
  sous-estime une carte sortie en cours de fenêtre (Verre, the Maid of Endymion : 3,1 % des 386 decks depuis sa sortie,
  1,2 % sur 90 jours, donc gardée). Proposé pour B2 : part depuis max(début de fenêtre, sortie TCG), avec un plancher.
- A1 : la première carte du classement (Elfnotes: Quatrain of Succession) est en TCG depuis juillet et n'est jouée dans
  aucun des 1 019 decks des 90 derniers jours ; elle ne passe que par la fenêtre de 168 jours. Signal plutôt contraire (B2).
- A2 : recalcul de la couverture (67 % / 62 %), identique à l'audit.
- A6 : passage de l'IC « mélangé » au résultat TCG seul ; « 6 % » = 0,00198 / 0,03233 (MAE de la persistance, TCG seuls).
- A8 : choix de BH plutôt que Benjamini-Yekutieli (BY ne garderait que 6 signaux sur 10) ; marquage des Rogue proches de T3.
