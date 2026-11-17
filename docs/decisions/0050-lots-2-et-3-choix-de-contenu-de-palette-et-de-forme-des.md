# 0050 — Lots 2 et 3 : choix de contenu, de palette et de forme des graphiques

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Lots 2 et 3, par défaut ; validée par Thomas le 2026-11-17 (revue du matin)
- Tickets : TOK-106, TOK-99

## Contexte
Registre des décisions de moindre portée prises par défaut pendant ce lot. Chaque ligne est une décision, rangée ici pour ne pas multiplier les notes d'une ligne.

## Options
- Pour chaque ligne, voir la source (question et alternatives).

## Décision

  - Titre du prototype et « 100/100 » boutique faux → **titre « La méta OCG précède la méta TCG de 2 à 6 mois. » ; tuile boutique = rang de l'archétype (3ᵉ sur 89) et libellé, pas `buy_score`** (chiffres de `SITE_FACTS` et du lot 1) — **titre remplacé le 2026-11-17** par le titre neutre « Méta Yu-Gi-Oh! TCG et OCG » (formulaire des textes du lot 16, `decisions-prises.md`) ; la tuile boutique reste valable
  - Pied de page : partout ou accueil seulement → **accueil seulement (`SiteFooter` réutilisable)** (périmètre du lot ; l'étendre au layout est une ligne)
  - Prototype : barre du radar colorée avec `--warn` et bleu OCG → **une seule teinte (accent, opacité décroissante) ; `--ocg` réservé à l'OCG** (règles du design system)
  - Tuiles « Prédictions » et « Recherche » absentes du prototype → **retirées ; bande de 4 liens sous le bento** (fidélité au prototype sans perdre l'accès aux pages)
  - Consigne de ton reçue en cours de lot → **tous les textes de l'accueil réécrits ; boutons = noms** (consigne explicite (voir la note sur le ton))
  - Date du graphe de co-occurrences → **« date de calcul non enregistrée dans la base servie »** (afficher la date d'une autre table serait faux)
  - Graphique de rangs proposé par l'audit pour `/evolution` → **courbes conservées (étiquettes directes, bande d'échantillon) ; haltères + colonne d'écart pour `/predictions`** (le brief prime ; écarts prévus ≤ 0,8 point invisibles sans colonne d'écart)
  - Où appliquer la palette de 6 teintes → **séries de `/evolution` et barre des critères du Ban Radar ; graphe de synergies non touché** (vis-network exclu du ticket)
  - Aucun script de contraste commité → **`frontend/scripts/contrast.mjs` (`npm run contrast`), seuil 4,5:1** (le critère cite « le script d'audit du projet »)
  - `--cat-1` (= `--signal`) dépasse de 0,015 la bande de luminosité du validateur → **accent conservé tel quel ; les 5 autres teintes sont dans la bande** (accent Ember validé par Thomas depuis le 31/10 ; contraste 6,5:1)
  - `/predictions` : aucun intervalle d'incertitude par archétype → **rien n'est dessiné ; le pied le dit** (ne pas inventer une mesure ; les docs divergent sur le gain du modèle (4, 5 ou 6 %), texte existant laissé tel quel)

## Raison
Une raison est donnée entre parenthèses pour chaque ligne.

## Conséquences
Relue par Thomas le 2026-11-17 : toutes les lignes acceptées, sauf le titre de l'accueil (remplacé, voir la première ligne). Pied de page : accueil seulement pour l'instant. Chacune est réversible sauf mention contraire dans la source.

## Sources
- `docs/planning/2026-11-17/decisions-prises.md` (Lots 2 et 3)
