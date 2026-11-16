# Compte rendu — file front du 2026-11-16 (soir)

Branche d'intégration : `claude/front-nuit-17-11` (depuis `main` local `cb2e9fb`). Rien fusionné dans `main`, rien poussé.
Décisions prises par défaut : [`decisions-prises.md`](decisions-prises.md).

| Lot | Ticket | Modèle réel | Résultat | Critères | `check.py` après fusion | Reste |
|---|---|---|---|---|---|---|
| 01 | Seuil boutique (suite TOK-113) | Sonnet 5.5 (demandé : `claude-sonnet-5-5`) | ✅ Fusionné (`69de94c`) | Plus de libellé relatif : `signal_label` (Fort / Modéré / Faible / null) = rang de l'archétype parmi les 89 archétypes OCG (Fort ≤ rang 8, Modéré ≤ rang 22), `archetype_rank`, `label_rule` ; au 16/11 : 3 Fort, 9 Modéré, 0 Faible sur 12 signaux. Méthode : `docs/journal/seuils-signal-boutique.md`. Seuils = quantiles ronds, **non validables** aujourd'hui (première échéance mars 2027). Tuile d'accueil : à lire au lot 02. | ✓ vert, aucune étape ignorée (29 tests sur `yugioh.db` et `serving.db`) | `serving.db` reconstruite par l'orchestrateur (sauvegarde `data/backup_serving_avant_lot01_20261116.db`) ; `buy_label` retiré de l'API (colonne gardée en base) |
| 02 | TOK-106 accueil | Fable 5.2 (hérité) | ✅ Fusionné (`730a15b`, `31de5a0`) | Mesures de la session, non refaites par l'orchestrateur : hauteur 7,73 / 5,62 / 8,86 écrans (1440 / 768 / 375 px) ; LCP mobile 1 792 à 1 879 ms (3 passages, devtools) ; JS transféré 180 ko ; Lighthouse mobile Perf 98, Access. 100 ; pied de données 6/6 ; sans JS et mouvement réduit OK ; captures avant/après à 3 largeurs (`docs/audit-front/captures/tok-106/`, non suivies). Consigne de ton appliquée (vérif. orchestrateur : aucun appel à l'action ni point d'exclamation au grep). Tous les textes : `docs/journal/accueil-tok-106.md`. | ✓ vert, aucune étape ignorée | À relire par Thomas : verbe « précède » du titre, « 63 communautés » non recalculé, mention légale du pied de page. Données Kewl Tune figées dans `proof-data.ts`. `app/loading.tsx` déplacé dans `app/ban/` (touche toutes les pages). Journal : un bloc de textes dupliqué. Non vérifié : Safari, Firefox, lecteur d'écran, téléphone réel. |
| 03 | TOK-99 dataviz | Fable 5.2 (hérité) | ✅ Fusionné (`0f093d3`) | Vérifié par l'orchestrateur : recharts absent de `package.json` et de `src/` ; `npm run contrast` passe (toutes les paires ≥ 4,5:1). Mesures de la session, non refaites : JS de `/evolution` 190,6 ko (avant 274,1, cible ≤ 200) ; Access. 100 ; LCP mobile 1,76 s ; palette `--cat-1` à `--cat-6` ≥ 5,1:1, documentée dans `docs/design-system.md` ; pied source + date sur 9 vues, **2 sans date servie** (graphe, simulateur : le pied l'écrit) ; alternative tabulaire en `<details>`. Détail : `docs/journal/dataviz-tok-99.md`. | ✓ vert, aucune étape ignorée | Critère « 100 % avec source + date » atteint à 9/11 : il manque une date de calcul du graphe de co-occurrences dans la base. Champs ajoutés à l'API (`decks_by_month`, `data_month`, `computed_at`). Pas d'intervalle d'incertitude par archétype dans `/predictions` (non dessiné). Marge de 9,4 ko sur le budget JS. Les docs divergent sur le gain du modèle (4, 5 ou 6 %). |
| 04 | TOK-101 page d'archétype | Fable 5.2 (hérité) | ✅ Fusionné (`9d69c55`) | Vérifié par l'orchestrateur : `GET /archetypes/{slug}` répond 200 sur `serving.db` pour `branded`, `Branded`, `harpie-amazoness`, `raise-moon`, et 404 pour un slug inconnu. Mesures de la session, non refaites : LCP mobile 1,72 à 1,84 s sur 9 pages (cible ≤ 2,0) ; Accessibilité 100 ; CLS 0 ; URL `/archetype/{slug}` (slug calculé par l'API, 231 archétypes, 0 collision) ; transitions tier list ↔ archétype seulement, mouvement réduit couvert par une règle dédiée ; un `DataFooter` par bloc. Détail : `docs/journal/archetype-tok-101.md`. | ✓ vert, aucune étape ignorée (37 tests sur chaque base) | Lien canonique à poser au lot 05 (toute casse rend la même page). Prédiction du mois suivant non affichée (`data_month` différents selon l'archétype, à trancher avec le data scientist). Deux fenêtres sur la même page (396 decks tier list, 1 883 decks Ban Radar). Les 3 archétypes à signal boutique n'ont ni graphique ni cartes clés (pas encore en TCG). |
| 05 | TOK-100 SEO et tests visuels | Fable 5.2 (hérité) | ✅ Fusionné (`088247b`, `d140f99`) | Vérifié par l'orchestrateur après fusion : `python scripts/check.py --visuel` vert, 36 captures (12 pages × 3 largeurs) identiques aux références en 46 s. Mesures de la session, non refaites : Lighthouse SEO 100 sur 12 pages ; balises vérifiées par `npm run check:meta` ; bruit mesuré 0 pixel ; preuve du diff sur changement de style volontaire (`docs/journal/seo-tests-tok-100.md`) ; accueil inchangé (LCP mobile 1,80 s, JS 182 ko) ; références WebP 3,4 Mo commitées. Doc : `docs/tests-visuels.md`. | ✓ vert, aucune étape ignorée, tests visuels inclus | Tests visuels hors du `check.py` par défaut (option `--visuel` : 45 s, build dépendant du réseau). Ils rejouent des réponses d'API figées (`--refresh-fixtures` si un contrat change). Canvas du graphe masqué (non déterministe). Références produites sur macOS. `NEXT_PUBLIC_SITE_URL` à renseigner au déploiement, sinon canoniques et sitemap pointent en local. Sitemap : 63 pages d'archétype sur 231. |

## Bilan (2026-11-16, fin de file)

Les 5 lots sont fusionnés dans `claude/front-nuit-17-11` (merges `--no-ff`). Dernier `python scripts/check.py --visuel` sur la branche : vert, aucune étape ignorée. Aucun arrêt, aucun `check.py` en échec. Rien dans `main`, rien poussé.

**Tokens** : non disponibles depuis l'orchestrateur.

**Critères non atteints ou partiels**
- Lot 03 : source + date sous 9 vues sur 11 (graphe et simulateur : aucune date de calcul du graphe de co-occurrences en base).
- Lot 01 : seuils écrits et justifiés, mais non validables avant mars 2027 (quantiles ronds).

**Non vérifié** : Safari, Firefox, lecteur d'écran, téléphone réel ; les mesures Lighthouse sont celles des sessions (Chromium, build local), non refaites par l'orchestrateur.

**À relire en priorité**
- Textes de l'accueil (`docs/journal/accueil-tok-106.md`) : verbe « précède » du titre, « 63 communautés » non recalculé, mention légale du pied de page.
- `app/loading.tsx` déplacé dans `app/ban/` : touche toutes les pages statiques.
- Champs ajoutés à l'API (lots 01, 03, 04) ; `buy_label` retiré de `/boutique/signals`.
- `data/serving.db` reconstruite (sauvegarde `data/backup_serving_avant_lot01_20261116.db`).

**À trancher avec la collaboratrice** : gain du modèle de prédiction (4, 5 ou 6 % selon le fichier) ; `data_month` différents selon l'archétype dans `meta_predictions` ; date de calcul du graphe à enregistrer en base.

**Hors file** : `regles.md` modifié et plusieurs fichiers non suivis dans `docs/planning/` et `docs/decisions/` sont apparus pendant la nuit dans le dépôt principal ; ils ne viennent pas de l'orchestrateur et ne sont dans aucun commit.

**Formulaire**

```
Fusion de claude/front-nuit-17-11 dans main
[x] Oui, après ma relecture (merge --no-ff)
[ ] Oui, tout de suite
[ ] Non, corrections d'abord (préciser en commentaire)

Push de main
[ ] Oui, dès la fusion (check.py vert)
[x] Non, pas encore

Linear (MCP à reconnecter) : passer TOK-106, 99, 101, 100 en Done, commenter TOK-113 (seuils)
[x] Oui, après la fusion
[ ] Non

Branches des lots (claude/seuil-boutique-…, tok-106-…, tok-99-…, tok-101-…, tok-100-…) et worktree .claude/worktrees/seuil-boutique-b07cfa
[x] Supprimer après la fusion dans main
[ ] Garder

Commentaire libre :
```
