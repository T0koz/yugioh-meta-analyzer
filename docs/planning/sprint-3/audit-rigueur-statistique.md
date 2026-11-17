# Audit de rigueur statistique de tous les scores du site

Modèle : Opus. Agent `data-scientist-ygo`. **Lecture seule, rapport seul** : aucun score, poids ou seuil modifié.

**Principe posé par Thomas (17/11)** : partout où le site affiche un score, une prédiction, un seuil ou un libellé
(Fort / Modéré, tiers, « tendance »…), il doit être **estimé à partir des données**, **validé hors échantillon dans
le temps**, **comparé à une méthode naïve** (hasard, popularité, « le mois dernier »), et **affiché avec son
incertitude**. Un réglage fixé à la main n'est acceptable que s'il est déclaré comme tel.

**À faire** : inventaire de chaque score et seuil du projet (au minimum : Ban Radar, cartes à impact et
`bridge_score`, simulateur de ban, signal boutique `alert_score` et seuils Fort / Modéré / Faible, signaux précoces,
prédictions méta, tiers de la tier list et test de tendance, seuils de la page Decks 80 % / 20 %, fenêtre d'arrivée
OCG → TCG). Pour chacun : comment il est construit, s'il est estimé ou réglé à la main, s'il est validé (et comment),
contre quelle méthode naïve, si l'incertitude est affichée, et ce qu'il faudrait pour le mettre au niveau.

**Livrable** : `docs/journal/audit-rigueur-statistique.md` — un tableau (score, état, risque, effort) et une liste de
tickets proposés, classés par impact sur la crédibilité du site. Formulaire pour Thomas.
