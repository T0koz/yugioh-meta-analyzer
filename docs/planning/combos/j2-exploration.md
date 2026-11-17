# Combos — J2 : le moteur retrouve seul les combos des guides

Modèle : Opus. Après J1. Même interdit Project Ignis.

**But (jalon J2, échéance de la règle d'arrêt : 13/01/2027)** : depuis des mains de départ réalistes, le moteur
explore les suites d'actions légales (filtres d'exploration DÉCLARÉS, décision D4 ; propagation du « non couvert »,
D5) et retrouve **les 5 à 10 combos décrits par les guides publics** du deck Branded.
1. Relever ces combos dans des guides publics (séquences factuelles de cartes, source et date citées ; ne pas
   recopier les textes des guides) dans `docs/moteur-combos/combos-guides.md`.
2. Exploration bornée (profondeur, temps), résultats enregistrés comme combos et micro-combos (schéma de TOK-85),
   interrogeables « A puis directement B » et « tous les combos qui passent par X ».
3. Rapport : combos retrouvés / manqués et pourquoi, temps de calcul, et tout combo trouvé hors guides (piste J3,
   à faire vérifier).

**Critères** : taux de combos de guides retrouvés ; chaque manque expliqué (règle, carte non couverte, borne) ;
`check.py` vert ; temps noté. Formulaire pour Thomas sur la suite (J3, extension à un deuxième deck, interface).

## Contexte au lancement (orchestrateur, 18/11)
- **Fusionnés** dans `claude/moteur-18-11` : lot 18, tranche 0 (C1), J1 (C2 : 37 cartes formalisées, 173 tests) et
  l'oracle sur les situations J1 (C2 bis : section « J1 (18/11) » de `docs/moteur-combos/reponses-oracle.md`).
- **Étape 0, avant l'exploration : réconcilier la formalisation avec ces réponses** (lecture de `reponses-oracle.md`
  seulement ; jamais son code ni `~/code/oracle-ignis/`) :
  - **N09, désaccord ferme** : un effet sans cible qui « choisit » à la résolution (`Mirrorjade`, `Luluwalilith`,
    `Aeon`) peut choisir un monstre insensible ; l'effet est alors sans effet sur lui. La formalisation l'exclut :
    à corriger (c'est la lecture générale des règles, pas un texte OCG), test à l'appui ;
  - **N04, litige** : l'oracle interdit de déclarer un Attribut que tous les autres monstres ont déjà ; tranche par
    le **texte TCG** de notre base et écris la raison ; DIVIN est déclarable (oracle) ;
  - N01 (non), N02 (non aux deux), N03, N05 à N08, N10, N11, N13 : adopter les réponses de l'oracle là où la
    formalisation répondait « non couvert » ou autrement, en le déclarant ; N12 reste non testable (hors pilote) ;
  - mettre à jour `docs/moteur-combos/j1-rapport.md` § 4 et § 5 : volet oracle de la mesure J1 (effets dont un chemin
    contredit l'oracle, avant et après correction). Le volet humain (20 effets) attend un relecteur : ne le remplis pas.
- R23 / T37 : le texte TCG fait foi (effet obligatoire), désaccord de texte avec l'oracle, inchangé.
- Décisions par défaut des lots 18, C1, C2 dans `docs/planning/2026-11-18/decisions-prises.md`, non encore validées :
  appuie-toi dessus, ajoute les tiennes au même endroit avec formulaire.
- Guides publics : relever des **séquences factuelles** (cartes, ordre), source et date ; ne jamais recopier leur
  texte (dépôt public). Si aucun guide n'est accessible (sites bloqués), dis-le et propose une liste de combos à
  faire confirmer par un joueur, sans l'inventer.
- Lot long : commite souvent sur ta branche ; si tu approches de ta limite d'usage, commite et écris où tu en es.
  Ne pousse pas, ne fusionne pas ; ne lance ni session ni sous-agent, sauf `gardien-donnees` (schéma) et
  `data-scientist-ygo` (méthode du taux de combos retrouvés).
