# 04 — TOK-101 : page d'archétype et transitions de vue

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front. Décision déjà prise (audit) : 10 — transitions de page en embellissement (drapeau expérimental
de Next 16), le site doit marcher sans.

**À faire** : page par archétype (depuis la tier list) : part de méta, tendance, cartes clés (`CardArt`), signal
boutique si présent, pied de données ; transition de vue depuis la tier list ; `metadata` par page.
Lis `node_modules/next/dist/docs/` sur les transitions avant d'écrire.

**Critères** : navigation correcte avec et sans prise en charge des transitions ; mouvement réduit respecté ;
LCP de la page ≤ 2,0 s ; Lighthouse Accessibilité ≥ 95 ; URL stable et partageable ; aucun chiffre sans source/date.
Pas de nouveau calcul statistique : n'affiche que ce que l'API sert déjà (sinon `data-scientist-ygo`).
