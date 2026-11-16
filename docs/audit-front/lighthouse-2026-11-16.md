# Lighthouse — mesure de référence du 16 novembre 2026

Première mesure, prise à la fin de TOK-98 (branche `claude/refonte-front-cbe8af`), avant la nouvelle page d'accueil.
Elle sert de point de comparaison pour TOK-106 (objectifs : Performance ≥ 90, Accessibilité ≥ 95, LCP mobile ≤ 2,0 s).

**Conditions** : Lighthouse 12.8, build de production (`next build` puis `next start`), machine locale, API locale sur
`serving.db`, Chromium de Playwright. Le profil mobile simule un téléphone milieu de gamme sur une 4G lente : ses temps
sont des estimations, pas des mesures d'utilisateurs réels. Les scores bougent de quelques points d'un passage à l'autre.

Pour refaire la mesure, depuis `frontend/` : `npm run build`, `npm run start -- -p 3100`, puis
`CHROME_PATH=<chromium> npm run lighthouse -- http://localhost:3100 mobile` (ou `desktop`).

## Mobile

| Page (mobile) | Performance | Accessibilité | Bonnes pratiques | SEO | LCP | Blocage | CLS |
|---|---|---|---|---|---|---|---|
| `/` | 77 | 98 | 100 | 100 | 3569 ms | 543 ms | 0.000 |
| `/tier-list` | 100 | 100 | 100 | 100 | 1589 ms | 9 ms | 0.000 |
| `/evolution` | 92 | 100 | 100 | 100 | 3314 ms | 52 ms | 0.000 |
| `/predictions` | 92 | 100 | 100 | 100 | 3345 ms | 21 ms | 0.000 |
| `/boutique` | 94 | 100 | 100 | 100 | 3041 ms | 14 ms | 0.000 |
| `/early-signals` | 92 | 100 | 100 | 100 | 3338 ms | 8 ms | 0.000 |
| `/graph` | 71 | 100 | 100 | 100 | 2948 ms | 1192 ms | 0.000 |
| `/ban` | 93 | 98 | 100 | 100 | 3261 ms | 20 ms | 0.000 |
| `/ban?tab=impact` | 91 | 98 | 100 | 100 | 3501 ms | 20 ms | 0.000 |

## Desktop

| Page (desktop) | Performance | Accessibilité | Bonnes pratiques | SEO | LCP | Blocage | CLS |
|---|---|---|---|---|---|---|---|
| `/` | 100 | 98 | 100 | 100 | 597 ms | 0 ms | 0.000 |
| `/tier-list` | 100 | 100 | 100 | 100 | 746 ms | 0 ms | 0.000 |
| `/evolution` | 100 | 100 | 100 | 100 | 620 ms | 0 ms | 0.000 |
| `/predictions` | 100 | 100 | 100 | 100 | 675 ms | 0 ms | 0.000 |
| `/boutique` | 100 | 100 | 100 | 100 | 632 ms | 0 ms | 0.000 |
| `/early-signals` | 100 | 100 | 100 | 100 | 591 ms | 0 ms | 0.000 |
| `/graph` | 100 | 100 | 100 | 100 | 590 ms | 82 ms | 0.000 |
| `/ban` | 100 | 98 | 100 | 100 | 693 ms | 0 ms | 0.000 |
| `/ban?tab=impact` | 100 | 98 | 100 | 100 | 710 ms | 0 ms | 0.000 |

## Lecture

- **Desktop** : 100 en performance sur les 9 pages, décalage de mise en page nul partout.
- **Mobile** : 7 pages sur 9 à 91 ou plus. Deux pages sous l'objectif :
  - `/` (77) : 543 ms de blocage et un LCP de 3,6 s. À traiter dans TOK-106, qui refait la page.
  - `/graph` (71) : 1,2 s de blocage, dû à vis-network. Attendu, remplacé dans TOK-102.
- **LCP mobile entre 3,0 et 3,6 s sur 8 pages** : au-dessus de l'objectif de 2,0 s. Seule `/tier-list` y est (1,6 s).
  Cause non isolée : à chercher avant TOK-106 (polices, JavaScript du socle, animation d'entrée du titre).
- **Accessibilité** : le seul défaut relevé (`heading-order`, des `h3` juste après le `h1` sur `/` et `/ban`) a été
  corrigé après cette mesure ; les 98 du tableau datent d'avant le correctif.
