# Tests visuels et balises de partage (TOK-100)

Deux vérifications du front, chacune lancée par une commande. Aucune n'appelle de service externe.

## 1. Tests visuels

```bash
.venv/bin/python scripts/visual_tests.py            # compare aux références
.venv/bin/python scripts/visual_tests.py --update   # changement voulu : régénère les références
python scripts/check.py --visuel                    # la même suite, avec les autres vérifications
```

12 pages × 3 largeurs (375, 768 et 1440 px) = 36 captures de page entière, comparées pixel à pixel aux images
de `frontend/tests/visual/reference/`. Durée mesurée le 2026-11-16 : 44 à 45 s, build compris (Mac M-series).

| Capture | Adresse |
|---|---|
| accueil | `/` |
| tier-list, evolution, predictions | `/tier-list`, `/evolution`, `/predictions` |
| boutique, early-signals, graph | `/boutique`, `/early-signals`, `/graph` |
| ban-radar, ban-impact, ban-simulateur | `/ban`, `/ban?tab=impact`, `/ban?tab=simulateur` |
| archetype-tcg, archetype-boutique | `/archetype/branded`, `/archetype/raise-moon` |

### Ce qui rend les captures reproductibles

| Source de variation | Réponse |
|---|---|
| Données recalculées chaque lundi | Le site est construit contre une fausse API qui rejoue 12 réponses JSON figées (`frontend/tests/visual/fixtures/`, 268 ko). Ni base ni backend : la suite tourne sur une machine sans `yugioh.db`. |
| Build courant du développeur | Le build de test va dans `frontend/.next-visual` (variable `NEXT_DIST_DIR`), `.next` n'est pas touché. |
| Animations, récit au défilement, braises, transitions | `prefers-reduced-motion: reduce` (le site s'y plie déjà), plus une feuille de style qui neutralise animations et transitions, et `animations: "disabled"` à la capture. |
| Apparitions à l'entrée dans l'écran | Un aller-retour jusqu'en bas de page avant la capture. |
| Images de cartes (YGOPRODeck, réseau externe) | Remplacées par un aplat de la couleur `--ink-4` ; toute autre requête sortante est coupée. |
| Graphe de synergies (mise en page tirée au hasard) | Le canvas est masqué : la capture de `/graph` ne couvre que l'habillage de la page. |
| Polices | Capture après `document.fonts.ready`. |
| Langue, fuseau, densité | `fr-FR`, `Europe/Paris`, 1 pixel par point. |

### Seuil de tolérance

- Un pixel compte comme changé si un de ses canaux s'écarte de plus de **16 sur 255** de la référence.
- Une capture échoue si plus de **0,01 %** de ses pixels ont changé, ou si sa taille a changé.

Mesure du bruit (2026-11-16) : quatre passages successifs sur le même code, **0 pixel changé sur les 36 captures**.
Le seuil n'absorbe donc aucun bruit observé ; il laisse une marge de 432 pixels sur une page de 1440 × 3000
pour un écart d'anticrénelage entre deux versions de Chromium. Sensibilité mesurée : passer l'accent `--signal`
de `#ff5a3c` à `#e8503a` (23 niveaux sur le rouge) fait échouer les 36 captures, de 0,054 % (tier-list-375)
à 1,743 % (ban-simulateur-375) de pixels changés.

Preuve (images dans `docs/planning/2026-11-17/lot-05-captures/`) : avec ce changement la suite sort en code 1
et écrit l'image obtenue et l'image de différence ; changement annulé, elle repasse (36 sur 36, 44 s).

### Quand une capture échoue

`frontend/tests/visual/output/` (hors Git) reçoit `<capture>-obtenu.png` et `<capture>-diff.png` (pixels changés
en rouge). Si le changement est voulu : relire les différences, lancer `--update`, commiter les références
avec le code. Sinon : corriger le code.

### Références et données figées

- **Références** : 36 fichiers WebP sans perte, **3,4 Mo** au total (12,4 Mo en PNG), commités. Elles ont été
  produites sur macOS avec le Chromium de Playwright 1223 : sur un autre système le rendu des polices diffère,
  il faut alors comparer à des références régénérées sur la même machine avant de modifier le code.
- **Données figées** : `--refresh-fixtures` les réenregistre depuis une API réelle (`--api`, défaut
  `http://localhost:8000/api/v1`) puis régénère les références. À faire quand la forme d'une réponse change
  (champ ajouté ou retiré), pas chaque lundi. Les pages d'archétype autres que `branded` et `raise-moon`
  répondent 404 pendant ce build : elles ne sont pas capturées.

### Limites connues

- Le build télécharge les polices chez Google (`next/font`). Coupure réseau observée une fois sur cinq le
  2026-11-16 : le script réessaie trois fois, puis se déclare « ignoré » (code 3), pas « échoué ».
- C'est la raison, avec la durée, pour laquelle la suite n'est pas dans le `check.py` par défaut : elle se lance
  avec `--visuel`. Sans venv, sans Chromium (`.venv/bin/playwright install chromium`) ou sans `node_modules`,
  l'étape est « ignorée ». `check.py` rappelle la commande quand `frontend/src/` a changé.
- Les états de survol, de focus et les menus ouverts ne sont pas capturés.

## 2. Balises de partage

```bash
cd frontend && npm run build && npm run start -- -p 3100   # API lancée à côté
npm run check:meta -- http://localhost:3100
```

`frontend/scripts/check-meta.mjs` lit le HTML servi en local et sort en code 1 si une règle n'est pas tenue :

- sur les 10 pages principales et les pages d'archétype du sitemap : un titre (70 caractères au plus), une
  description (50 à 200 caractères), aucun point d'exclamation hors « Yu-Gi-Oh! », un lien canonique égal à
  l'adresse attendue, `og:url` identique, `og:title`, `og:description`, `og:type`, `og:site_name`, `og:locale`,
  `twitter:card`, et une image qui répond 200 en PNG de 1200 × 630 ;
- titres et descriptions tous différents entre les pages principales ;
- `robots.txt` renvoie au sitemap ; `sitemap.xml` contient exactement les pages principales et les archétypes
  servis par l'API ;
- une variante en majuscules d'un slug (`/archetype/BRANDED`) a pour canonique le slug servi (`/archetype/branded`) ; une adresse inconnue répond 404 en `noindex`.

Mesure du 2026-11-16 : 10 pages principales, 63 pages d'archétype, 73 adresses dans le sitemap, aucune règle
non tenue. Lighthouse (mobile, build de production) : **SEO 100 sur 12 pages** (les 10 principales et deux
pages d'archétype).

## 3. Adresse publique du site

Le domaine définitif n'est pas choisi (TOK-35). `frontend/src/lib/site.ts` lit, dans l'ordre :
`NEXT_PUBLIC_SITE_URL`, puis le domaine de production fourni par Vercel (`VERCEL_PROJECT_PRODUCTION_URL`),
puis `http://localhost:3000`. Liens canoniques, Open Graph, sitemap et robots en dépendent tous. Modèle :
`frontend/.env.example`. Un déploiement d'aperçu Vercel (`VERCEL_ENV=preview`) est servi en `noindex`.

## 4. Images de partage

Générées par le projet (`frontend/src/lib/og.tsx`, fichiers `opengraph-image.tsx`) : polices du design system
(copies WOFF sous licence OFL dans `src/assets/og-fonts/`), couleurs lues dans `globals.css`, marque du pied de
page. Aucune illustration de carte. Un chiffre n'y figure qu'avec sa période et sa source : l'accueil
(`lib/site-facts.ts`) et les pages d'archétype (API) en portent, les autres pages n'en portent pas.
