# TOK-115 — Relecture du diagnostic du Ban Radar TCG par le data scientist (lot 15a bis, 2026-11-17)

Relecture critique de `docs/journal/ban-radar-tcg-diagnostic.md` par le sous-agent `data-scientist-ygo` (lecture seule),
demandée par Thomas avant de répondre au formulaire. Session lancée sur Sonnet 5.5 (`claude-sonnet-5-5`) ; le sous-agent
a bien été utilisé. Branche `claude/lot15a-bis-relecture-ds-48faf2`, non fusionnée. **Rien n'a été corrigé** (ni journal,
ni script, ni `context.md`, ni `WEIGHTS`) : ce document est un rapport. Les sorties de recalcul sont dans le scratchpad de
la session (hors dépôt).

## Verdict global : **valide avec réserves** — aucun point bloquant

## En clair (pour Thomas)

- **Les chiffres sont bons.** Tous les tableaux du journal se reproduisent à l'identique en relançant le script, et deux
  recalculs indépendants (un code écrit à part) retrouvent les mêmes rangs et les mêmes valeurs p. Aucune fuite de données
  n'a été trouvée qui change une conclusion.
- **La recommandation « ne rien changer » tient**, mais pour une meilleure raison que celle écrite : on ne peut pas dire
  que la régression « ne bat pas » les staples, on peut dire que 7 listes ne permettent **pas de conclure**.
- **Ce qui est à corriger, ce sont des phrases trop fortes**, pas des calculs : « nettement », « est démontré »,
  « 7 sur 7 » appliqué à un modèle qui n'est pas celui de l'option B, et surtout l'explication par les « poids
  effectifs », qui est une convention de calcul parmi d'autres (elle donne des lectures différentes selon la mesure).
- **Un résultat à ne pas sur-interpréter** : « 47 % des cartes touchées TCG sont jouées à moins de 1,5 exemplaire » vient
  pour moitié d'une seule liste (2026-10-19). Le score se dégrade surtout sur les trois dernières listes TCG, ce qui
  n'est pas la même chose qu'un défaut propre au format TCG.
- **Le verdict proposé pour la page Historique** est à reformuler : il manque l'effectif (« sur 250 places »), la réserve
  « la plupart de ces listes précèdent le choix des poids », et il affirme une infériorité (rang médian TCG) que seul
  l'AUC démontre.

## Détails (pour la data scientist)

### Points IMPORTANTS

**I1. Option B : l'argument « 7 listes sur 7 » ne vaut pas pour le modèle proposé** (journal l.35-37, l.309-311).
Le 7/7 (p = 0,016) est celui de `logit_6` (régression TCG seule). L'option B adopte la régression commune TCG + OCG, absente
de `pairs` (`scripts/diagnose_ban_radar.py` l.389-391). Calculée à partir de `par_liste.csv` : en TCG elle bat les poids
actuels en rang médian sur **5 listes sur 7** (p = 0,45 ; 12,7 % contre 17,8 % en moyenne), seule l'AUC passe 7/7 ; en OCG
elle est moins bonne que les poids actuels (médiane des rangs médians 36 contre 30). *Correction* : réécrire l'option B avec
ces chiffres ou la scinder en « TCG seul » / « commun ».

**I2. Les « poids effectifs » sont une convention, et elle contredit les propres tests du journal** (journal l.21-24,
l.125-140 ; `context.md` l.433-435 ; `diagnose_ban_radar.py` l.254-269). Le calcul est exact (16,7 / 5,4 / 39,5 / 12,6 /
23,5 / 2,2 % en TCG). Mais :
- « piloté à 64 % par exemplaires + tendance » : la somme réelle est **63,0 %** (TCG) et 62,4 % (OCG) ; 64 est la somme de
  deux arrondis.
- L'écart type est dominé par la queue lourde de `ubiquity` et `carrier`, et ignore leur corrélation (0,94 en rang, 0,79
  de Pearson). Trois mesures, trois lectures (moyennes par liste, TCG) :

  | Critère | poids × écart type (journal) | part de variance du score | poids × écart type des rangs centiles |
  |---|---|---|---|
  | ubiquity | 17 % | 15 % | 33 % |
  | carrier | 5 % | 4 % | 28 % |
  | copies | 40 % | 57 % | 21 % |
  | restriction | 13 % | 4 % | 5 % |
  | momentum | 24 % | 18 % | 10 % |
  | bridge | 2 % | 1 % | 4 % |

  Sur les rangs, ce que mesurent le rang médian et le top 25, part des decks + porteur pèsent **61 %**. Le tableau §4
  (« sans un critère ») va dans ce sens : retirer `ubiquity` est la pire variante (top 25 TCG 30 → 16, rang médian 81 → 152).
- Le commentaire « testés à ±0.10 sans changer le classement » (`scripts/build_ban_radar.py` l.45) est **faux**, et le
  journal l.138-140 le « comprend » à tort. Test sur 20 listes (référence TCG 30 top 25 / 81 ; OCG 41 / 28) :
  `ubiquity` −0,10 : TCG 23 / 91,5, OCG 35 / 53 ; `ubiquity` +0,10 : TCG 35 / 73,5, OCG 44 / 26,5 ; `copies` +0,10 : TCG 28 /
  112,5, OCG 39 / 54 ; `momentum` +0,10 : TCG 21 / 137,8, OCG 24 / 88,5. Remonter `ubiquity` de 0,10 améliore tout, mais
  en échantillon (20 listes) : à ne pas adopter tel quel.
- *Correction* : présenter les poids effectifs comme « part de la dispersion du score » en nommant la convention ; retirer
  « toute retouche de `WEIGHTS` se raisonne en poids effectifs » (`context.md` l.434-435). L'explication « le TCG résiste »
  par les AUC univariées reste correcte.

**I3. « 47 % à moins de 1,5 exemplaire » est tiré par une seule liste** (journal l.26-27, l.147-157 ; `context.md` l.436-437).
La liste TCG 2026-10-19 compte 29 cartes de ce type sur 37 touchées, soit la moitié des 59. Sans elle : 33,7 % (30 sur 89).
Par liste : 3/16, 2/11, 4/5, 5/9, 29/37. Lecture plus fidèle : le score se dégrade sur les trois dernières listes TCG ;
rupture temporelle et effet de format ne sont pas distingués. Exemple faux (journal l.156-157) : *Called by the Grave* et
*Triple Tactics Talent* sont en position 5 et 10 du classement du 2026-10-19, pas « descendues » ; seules *Crossout
Designator* (224) et *Anti-Spell Fragrance* (237) illustrent le propos.

**I4. Formulations plus fortes que les valeurs p.**
- « Elle les bat **nettement** en top 25 (25 contre 13) » (l.40-41) : 5 listes pour, 1 contre, 1 égalité, p = 0,22 ; la liste
  2025-04-07 fournit 11 des 25 (sans elle : 14 contre 9).
- « Seul l'écart de top 25 en OCG (9/10, p = 0,02) **est démontré** » (`context.md` l.67) : calcul confirmé (0,0215), mais
  au moins 4 tests dans la famille (Bonferroni 0,086), fenêtres qui se chevauchent, et 9 listes OCG sur 10 antérieures au
  calage des poids (pas un test hors échantillon pour le score). Écrire « dépasse le hasard au test du signe » + la réserve.
- Les « deux écarts à p = 0,016 » (l.219) sont tirés de 24 tests TCG : ≈ 1 faux positif attendu ; à dire à côté du résultat
  (le journal ne le dit qu'en l.273).
- « Il faudrait 7 sur 7 pour conclure à 5 % » (l.222) est faux avec des égalités : 6 sur 6 donne p = 0,031 (cas du top 25 OCG).
- Argument à ajouter (plus fort que l.272) : sur les deux seules listes TCG postérieures au calage, les poids actuels sont les
  derniers des trois méthodes (rang médian en % : 0,210 / 0,340, contre 0,154 / 0,263 pour la régression et 0,101 / 0,142
  pour les staples).

**I5. La règle d'adoption est ambiguë et le journal la présente comme tranchée** (journal l.38-41, l.307-308). Le brief ne
nomme ni la mesure ni le seuil. Sur les deux mesures de la page, la régression TCG seule gagne en descriptif (rang médian 51
contre 84 et 98 ; top 25 de 25 contre 24 et 13) ; elle perd en AUC contre les staples et le rang médian moyen en % la place
derrière (14,4 % contre 11,7 %). Résultat **non concluant**, pas « ne bat pas les staples ». « Ne rien changer » reste juste :
aucune comparaison avec les staples n'est significative sur 7 listes, 44 % du top 25 vient d'une liste, et les poids estimés
mettent 0,79 sur le porteur (revient à remplacer le score par un autre produit).

**I6. La page publique ne mentionne pas la fuite `bridge`** (`frontend/src/app/ban/BanHistoryView.tsx` l.547-570, bloc
« Méthode »). Elle cite le calage et l'écart annonce / entrée en vigueur, pas le fait que la centralité de pont vient du
graphe actuel. Effet mesuré négligeable (coefficient négatif, retrait neutre, top 25 TCG 30 → 28). *Correction* : une ligne
dans la méthode, ou retirer le critère au prochain changement. (Je n'ai pas touché `frontend/`.)

### Points MINEURS

- **M1.** « 64 % » (journal l.140) → 63 %.
- **M2.** « 0,79 en brut ≈ influence de la tendance à 0,04 » (l.242-243) : rapport des coefficients standardisés 0,76 / 0,47 =
  1,6 ; écrire « du même ordre ». Le 0,04 vaut 0,045.
- **M3.** « AUC plus basse sur les 10 listes » (l.44) : vrai en moyenne ; par liste, le score est plus bas sur 9 sur 10
  (p = 0,021), 2024-09-02 fait exception. Cet écart d'AUC TCG dépasse donc aussi le hasard : « seul l'écart de top 25 OCG »
  (`context.md` l.440) est trop restrictif.
- **M4.** « poids d'environ 70 » (l.68-70) : poids sklearn 33 pour les touchées, 0,5 pour les autres, rapport ≈ 66. Écrire
  « environ 70 fois plus qu'une carte non touchée ».
- **M5.** Top 25 poids actuels 29 contre 30 : départage des égalités (ordinal contre rang moyen), total identique avec le
  rang moyen (29 TCG, 41 OCG). La note l.171 est correcte.
- **M6.** Entraînement `effective < as_of` pour le modèle commun : correct, légèrement conservateur (aucune fuite).
- **M7.** Rangs centiles « les plus prometteuses » (l.299, question 2) : test rapide à une spécification, TCG médiane 83 et
  top 25 de 18 contre 51 et 25 avec les critères bruts. Garder le ticket, retirer « prometteuses ».
- **M8.** `context.md` l.72 « chiffres de la v1, non recalculés » : le §4 du journal les recalcule (sans exemplaires, top 25
  30 → 19 en TCG, 41 → 19 en OCG).
- **M9.** Non signalé : retirer `momentum` améliore le top 25 (TCG 33 contre 30 ; OCG 46 contre 41) mais dégrade le rang
  médian TCG (119 contre 81). À noter dans le ticket.
- **M10.** Verdict Q5 : « 29 contre 16 » sans effectif ; écrire « sur 250 places » comme `context.md` l.66.

## Fuites de données : examen

Propre pour l'essentiel. Cible = gain de sévérité par rapport à la liste précédente, jamais calculée à partir de la liste
testée ; entraînement sur `effective < as_of` (`diagnose_ban_radar.py` l.153-154) ; `StandardScaler` ajusté sur
l'entraînement seul (réplique indépendante : mêmes résultats) ; statut de restriction = veille (`end_date` exact) ; univers
identique pour toutes les méthodes (11 cartes TCG hors univers, toutes sous 5 decks). Réserves déjà connues : `bridge`
(graphe actuel, négligeable, I6), écart annonce / entrée en vigueur (non quantifiable sans dates d'annonce), poids actuels
calés en août (avantage indu sur 5 des 7 listes TCG, qui joue **contre** la régression).

## Chiffres recalculés (journal contre recalcul)

Tous identiques, sauf mention. Le script relancé deux fois (le mien et celui du sous-agent, 54 s) redonne les tableaux §1 à §6.

| Chiffre | Journal | Recalcul indépendant | Écart |
|---|---|---|---|
| Jeu de données | 18 600 lignes, 225 touchées (126 TCG, 99 OCG) | idem | aucun |
| Test du signe 7/10 ; 7/7 ; 9/10 ; 6/7 (3 égalités) | 0,34 ; 0,016 ; 0,02 ; 0,13 | 0,344 ; 0,0156 ; 0,0215 ; 0,125 | arrondi |
| AUC univariée `ubiquity` / `carrier` TCG | 0,827 / 0,823 | 0,8275 / 0,8231 | aucun |
| AUC score actuel TCG / OCG | 0,773 / 0,887 | 0,7726 / 0,8872 | aucun |
| Touchées < 1,5 exemplaire TCG / OCG | 47 % / 22 % | 46,8 % (59/126) / 22,2 % (22/99) | aucun |
| Poids effectifs TCG | 17/5/40/13/24/2 % | 16,7/5,4/39,5/12,6/23,5/2,2 % | arrondi |
| Somme exemplaires + tendance | 64 % | 63,0 % (TCG), 62,4 % (OCG) | **1 point** |
| Top 25 total, poids actuels / staples, TCG | 29 / 16 | 29 / 16 | aucun |
| Top 25 total, poids actuels / staples, OCG | 41 / 18 | 41 / 18 | aucun |
| Rang médian, 7 listes tenues à l'écart (staples / poids actuels) | 98 / 84 | 98,25 / 84,0 | aucun |
| Idem en % moyen | 11,7 % / 17,8 % | 11,67 % / 17,84 % | aucun |
| Régression TCG seule : médiane, % moyen, top 25 | 51, 14,4 %, 25 | 51, 14,4 %, 25 (code indépendant) | aucun |
| Régression commune − poids actuels, rang médian TCG | non calculé | 5/7, p = 0,45 | **nouveau** |
| Critère porteur seul, 7 listes TCG | non calculé | rang 97,5, 13,9 %, top 25 de 21 | **nouveau** |
| Poids estimés TCG (porteur / part des decks / tendance) | 0,79 / 0,07 / 0,04 | 0,789 / 0,070 / 0,045 | arrondi |
| Poids négatif de `ubiquity` TCG (bootstrap) | 23 % | 22,6 % | aucun |

## Les 5 questions du formulaire

1. **Poids (`WEIGHTS`)** : **A confirmée, justification à corriger** (« non concluant » et non « ne bat pas les staples »,
   I5). **B contredite sous sa forme actuelle** (I1).
2. **Suite technique** : **nuancée**. Ouvrir le ticket, sans « prometteuses » (M7), avec une mesure primaire et un seuil écrits
   d'avance, rangs centiles testés séparément du logit conditionnel.
3. **`bridge`** : **nuancée**. Le laisser jusqu'au prochain changement, mais ajouter une ligne dans la méthode de la page
   Historique (I6).
4. **Dates d'annonce** : **confirmée** (seul moyen de quantifier l'écart, jusqu'à 10 % des decks de la fenêtre).
5. **Verdict court** : **nuancée**. Texte proposé par le data scientist : « Sur les 10 banlists TCG d'avril 2024 à octobre
   2026, le Ban Radar place 29 cartes touchées dans son top 25 (sur 250 places) contre 16 pour le classement par part des
   decks ; l'écart n'est pas établi (6 listes pour, 1 contre, 3 égalités). Son rang médian est meilleur sur 3 listes sur
   10. En OCG, il place 41 cartes contre 18 dans son top 25 (9 listes sur 10 ; la plupart de ces listes précèdent le choix
   des poids) et a un meilleur rang médian sur 8 listes sur 10 (écart non établi). » À soumettre à la charte
   (`docs/charte-ton-et-explication.md`) avant reprise sur la page.

## Phrases de `context.md` citant le diagnostic

- l.64-67 : « 7 sur 10 », « p = 0,34 », « 29 sur 250 contre 16 », « 41 contre 18 », « 9 sur 10, p = 0,02 » exacts ; seul
  « est démontré » (l.67) est trop fort (I4).
- l.433-435 : à reformuler (I2). l.436-437 : 47 % exact mais tiré par une liste (I3). l.438-439 : « pas les staples (4/7) »
  exact mais incomplet (I5). l.440 : à nuancer (M3). l.72 : à mettre à jour (M8).

## Non vérifié

Dates d'annonce des banlists (absentes de la base) ; version « porteur seul » en validation temporelle stricte (post hoc) ;
interactions format × critère et logit conditionnel par liste (non testés) ; la page `/ban?tab=historique` n'a pas été ouverte
dans un navigateur (code de la section « Méthode » relu seulement) ; base de référence du 2026-11-16 seulement.
