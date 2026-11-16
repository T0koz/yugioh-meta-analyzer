# Lighthouse — mesure de référence du 16 novembre 2026

Première mesure, prise à la fin de TOK-98 (branche `claude/refonte-front-cbe8af`), avant la nouvelle page d'accueil.
Elle sert de point de comparaison pour TOK-106 (objectifs : Performance ≥ 90, Accessibilité ≥ 95, LCP mobile ≤ 2,0 s).

**Conditions** : Lighthouse 12.8, build de production (`next build` puis `next start`), machine locale, API locale sur
`serving.db`, Chromium de Playwright. Le profil mobile simule un téléphone milieu de gamme sur une 4G lente : ses temps
sont des estimations, pas des mesures d'utilisateurs réels. Les scores bougent de quelques points d'un passage à l'autre.

Pour refaire la mesure, depuis `frontend/` : `npm run build`, `npm run start -- -p 3100`, puis
`CHROME_PATH=<chromium> npm run lighthouse -- http://localhost:3100 mobile` (ou `desktop`).

## Mobile, réseau simulé (réglage par défaut)

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

## Desktop, réseau simulé

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

## Mobile, ralentissement réel (mesure à citer pour le LCP)

Même build, après deux correctifs (entrée du titre sans fondu, `h2` après le `h1`), avec `LH_THROTTLING=devtools` :
Lighthouse ralentit vraiment le réseau et le processeur au lieu de simuler.

| Page (mobile) | Performance | Accessibilité | Bonnes pratiques | SEO | LCP | Blocage | CLS |
|---|---|---|---|---|---|---|---|
| `/` | 98 | 100 | 100 | 100 | 2061 ms | 82 ms | 0.000 |
| `/tier-list` | 98 | 100 | 100 | 100 | 2061 ms | 87 ms | 0.000 |
| `/evolution` | 90 | 100 | 100 | 100 | 2001 ms | 379 ms | 0.000 |
| `/predictions` | 98 | 100 | 100 | 100 | 1949 ms | 89 ms | 0.000 |
| `/boutique` | 98 | 100 | 100 | 100 | 2004 ms | 93 ms | 0.000 |
| `/early-signals` | 98 | 100 | 100 | 100 | 1995 ms | 89 ms | 0.000 |
| `/graph` | 73 | 100 | 100 | 100 | 1663 ms | 1566 ms | 0.000 |
| `/ban` | 98 | 100 | 100 | 100 | 1974 ms | 85 ms | 0.000 |
| `/ban?tab=impact` | 98 | 100 | 100 | 100 | 1991 ms | 93 ms | 0.000 |

## Lecture

- **Le LCP mobile réel est d'environ 2,0 s sur les 9 pages** (1,7 à 2,1 s), pour un objectif de 2,0 s dans TOK-106.
  Les 3,0 à 3,6 s des deux premiers tableaux viennent de la **simulation** de Lighthouse : pour une même page, elle a
  donné de 1,6 à 3,9 s d'un passage à l'autre. Elle reste utile pour comparer des tendances, pas pour citer un LCP.
- **Le fondu d'entrée coûtait jusqu'à 0,8 s.** Un texte qui démarre à opacité 0 n'est pas compté par le LCP tant qu'il
  n'est pas visible ; avec le fondu, `/predictions` mesurait 2,8 s en ralentissement réel et l'élément LCP changeait
  d'un passage à l'autre. L'entrée du premier écran est donc un glissement sans fondu ; le fondu reste sous le premier
  écran (`Reveal`).
- **Il reste environ 0,4 s entre le premier affichage (1,6 s) et le LCP (2,0 s).** Cause non isolée : probablement le
  remplacement de la police de secours par Inter Tight. À regarder si TOK-106 a besoin de marge.
- **Accessibilité : 100 partout** après le correctif `heading-order`.
- `/graph` (73, 1,6 s de blocage) : vis-network, remplacé dans TOK-102. `/evolution` (90, 0,4 s de blocage) : recharts,
  remplacé dans TOK-99.
- **Desktop** : 100 en performance sur les 9 pages, décalage de mise en page nul partout.
