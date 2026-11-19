# Décisions prises par défaut — 2026-11-19

Jalon n°8 (mise en ligne, bloc A de `formulaires-a-trancher.md`, décision 0056). Une ligne par décision imprévue :
ticket, question, choix, raison. À valider par Thomas avant de rejoindre `docs/decisions/`. Formulaire à copier-coller
en fin de fichier (seulement pour ce qui touche l'affichage).

| Ticket | Question | Choix | Raison |
|---|---|---|---|
| TOK-82 (A1) | Le commit `f485ca1` dit « en attente du formulaire » dans son message. | Repris tel quel par `git cherry-pick` (consigne de l'orchestrateur) ; le texte appliqué correspond aux cases pré-cochées de A1, validées le 19/11. | Ne pas réécrire un commit déjà relu ; le message est seulement daté. |
| TOK-116 (A3) | Bornes de la légende Kewl Tune : quelle série ? | `total_decks` de `ocg_history` (tous archétypes OCG, par mois) sur la fenêtre fixe : **145 à 574 decks**, calculés à chaque build. Si un mois de la fenêtre manque, la légende dit seulement « Incertitude non dessinée. » | La spécification demande l'OCG ; l'historique TCG servi de Kewl Tune ne commence qu'en décembre 2025, ses effectifs ne couvrent pas la fenêtre. |
| TOK-130 (A4) | Le libellé long (« arrivée dans la fenêtre pour 27 archétypes sur 36 (2024-2026) ; 12 sur 18 pour 2026 ») ne tient pas dans un en-tête de colonne. | Deux formes tirées des mêmes chiffres (`SITE_FACTS.arrivalCoverage`) : longue (`ARRIVAL_COVERAGE`) dans les pieds, légendes, infobulles, page d'archétype et `/methode` ; courte (`ARRIVAL_COVERAGE_SHORT`, « juste pour 27 archétypes sur 36 ») dans l'en-tête du tableau boutique et la ligne de chaque groupe. Sur la page d'archétype, l'intitulé devient « Arrivée en TCG » et la phrase longue passe sous la date. | Une seule source de chiffres ; la forme longue reste visible sur chaque page qui montre la fenêtre. |
| TOK-130 (A4) | `/methode` : garder la couverture par carte (62-67 %) à côté ? | Non, remplacée. Ajout : « les archétypes de 2024 et 2025 sont en partie dans les données d'estimation ; ceux de 2026, postérieurs au calcul, sont le seul contrôle hors échantillon » (journal TOK-130). | Spécification littérale ; la précision hors échantillon vient du même journal. |
| TOK-132 (A5) | L'intervalle du +6,5 est-il à 95 % ? | **Non, à 90 %** (bootstrap par liste, journal Q3 bis). Écrit « intervalle à 90 % de +4,5 à +8,6 ». | Chiffre vérifié dans `docs/journal/pont-simulateur-tok-132.md` avant écriture. |
| TOK-132 (A5) | Où mettre la phrase sur ce que mesure le score ? | Paragraphe visible sous l'en-tête de l'onglet Diffusion (pas dans l'encart replié) ; l'encart garde la méthode et dit l'ancien nom. Libellé du gros chiffre : « Diffusion ». Pied de page du site : « Diffusion des cartes ». | La charte veut l'annotation avant la méthode repliée. |
| TOK-132 (A5) | Ancienne adresse `/ban?tab=impact` ? | Redirection permanente (308) vers `/ban?tab=diffusion`, filtre `kind` gardé ; canonique et sitemap sur la nouvelle. Captures `ban-impact-*` renommées `ban-diffusion-*`. | Une seule adresse par contenu (règle de `kind-filter.tsx`) ; les liens déjà partagés continuent de marcher. |
| TOK-132 (A5) | Textes du simulateur qui parlent encore de simuler. | Bouton « Simuler le ban » → **« Afficher la position »** ; lien des lignes Diffusion « Simuler le ban → » → **« Position dans le graphe → »** ; surtitre « Carte retirée » → « Carte » ; « Score de pont » → « Score de diffusion » (même champ que l'onglet). Onglet « Simulateur » et titre de page « Simulateur de ban » gardés (adresses inchangées). | La décision A5.2 décrit le simulateur sans prévision ; « simuler » promettait l'inverse. Renommer l'onglet n'était pas demandé. |
| TOK-132 (A5) | Quels archétypes de deck, dans quel ordre, combien ? | `archetype_card_profile` (fenêtre et listes de la tier list : 2 mois, 396 decks), Main et Extra Deck seulement (le Side Deck ne compte pas comme « jouer »), triés par nombre de listes qui jouent la carte ; 12 affichés, le reste replié ; chaque archétype avec « k sur n listes » et un lien vers sa page. Le pied dit que cette fenêtre diffère de celle du graphe. | Ash Blossom est jouée par 56 archétypes ; trier par k montre d'abord les decks les plus touchés, l'effectif dit le reste. |
| TOK-132 (A5) | Changement d'API. | Additif : `deck_archetypes`, `deck_window_start`, `deck_window_end`, `deck_window_decks` dans `POST /simulate-ban` ; `affected_archetypes` gardé (plus affiché). Relu par `gardien-donnees` : OK (0 carte en Main et Extra pour un même archétype, k ≤ n partout, 0,25 à 0,64 ms). Ses deux suggestions appliquées (invariant de test, erreur SQL non avalée). | Spécification : additif seulement, test de fumée, `api-contracts.md`. |
| TOK-149 | Échappement des jokers ailleurs que dans la recherche ? | Aussi dans la recherche de communauté de `/simulate-ban` (`top_archetypes LIKE`), qui prend un nom d'archétype de la base. `meta.py` (motif construit sur des noms de la base, sans saisie) non touché. | Même défaut, même correctif, une ligne. |
| TOK-149 | Repli du slug vide ? | « x- » + 10 caractères de l'empreinte SHA-1 du nom (stable, déjà normalisé, retrouvé par `resolve`). Nom vide ou blanc : slug vide, comme avant. | Correctif proposé par la revue (« identifiant stable ») ; aucun archétype concerné aujourd'hui. |
| TOK-148 | Quelle valeur témoin ? | `as_of` et `n_decks_window` de `/ban-radar`, `computed_at` de `/boutique/signals`, comparés à la même requête que le routeur sur `serving.db`. Champ absent = échec. | Deux tables recalculées par deux chaînes différentes (Ban Radar, notebook 10). Limite : une API lancée sur `yugioh.db` du même jour concorde (tables servies identiques), ce qui est juste, puisque les données le sont. |

## Suites repérées (non traitées, hors périmètre)

- `affected_archetypes` de `/simulate-ban` cherche le porteur dans `card_impact` par le nom avec marques (`Maliss <P> …`) :
  il ne le trouve pas pour les cartes à marque (défaut ancien, champ plus affiché). À corriger ou retirer le champ.
- Les graduations de l'axe de corrélation de l'accueil (bloc « Le signal OCG → TCG ») sont en 11 px dans un SVG (règle
  « texte de graphique ≥ 12 px »), défaut antérieur au jalon.

## Formulaire (affichage)

```
J8.1 Textes du simulateur
[x] « Afficher la position », « Position dans le graphe → », « Carte », « Score de diffusion » ; onglet « Simulateur » gardé
[ ] Renommer aussi l'onglet (ex. « Position ») avec redirection de ?tab=simulateur
[ ] Revenir à « Simuler le ban »
Commentaire libre :

J8.2 Archétypes de deck du simulateur
[x] Main et Extra Deck, tri par listes qui jouent la carte, 12 affichés puis repli, « k sur n listes », lien vers la page
[ ] Seulement les archétypes à fiche (≥ 8 listes)
[ ] Compter aussi le Side Deck
Commentaire libre :

J8.3 Fenêtre d'arrivée, forme courte
[x] « juste pour 27 archétypes sur 36 » dans l'en-tête du tableau boutique et la ligne des groupes ; forme longue ailleurs
[ ] Forme longue partout (en-tête de colonne sur deux lignes)
[ ] Pas de qualificatif dans l'en-tête, forme longue dans le pied seulement
Commentaire libre :

J8.4 Onglet Diffusion
[x] Phrase de mesure visible sous l'en-tête, intervalle écrit « à 90 % » ; ancien nom rappelé dans l'encart replié
[ ] Phrase dans l'encart replié seulement
Commentaire libre :
```
