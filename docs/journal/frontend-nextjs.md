### ✅ Frontend Next.js — Branché sur l'API réelle (2026-08-05)

**Stack :** Next.js 16.2.12 + TypeScript + Tailwind CSS + shadcn/ui + recharts + vis-network (^10)
**Dossier :** `frontend/`
**Dev :** lancé via le tool preview (config `"frontend"` dans `.claude/launch.json`, `autoPort: true`) → `http://localhost:3000`
**⚠ `frontend/AGENTS.md`** : Next 16 a un nouveau modèle de cache (`'use cache'` + Cache Components, opt-in via `cacheComponents: true` dans `next.config.ts` — **pas activé ici**, donc l'ancien `fetch(url, { next: { revalidate } })` utilisé dans `lib/api.ts` reste valide). Vérifier `node_modules/next/dist/docs/` si un changement touche au caching/fetch.
**⚠ Cache disque `.next/cache`** : persiste entre redémarrages du serveur dev (contrairement au cache mémoire). Si une donnée fraîchement ajoutée côté API n'apparaît pas côté front malgré un redémarrage du serveur, faire `rm -rf frontend/.next` avant de conclure à un bug.

**Structure :**
```
frontend/src/
├── app/
│   ├── layout.tsx          # Layout global + navigation top bar
│   ├── page.tsx            # Home en bento (5 tuiles branchées sur l'API), plus de redirection
│   ├── tier-list/          # Server component + TierList.tsx (filtres) + ArchetypeRow.tsx (liste dense)
│   ├── evolution/          # page.tsx (server, fetch) + EvolutionChart.tsx (client, recharts, connectNulls)
│   ├── predictions/        # Server component, api.predictions(), barre recalibrée au max
│   ├── boutique/           # Server component, api.boutiqueSignals(), key=archetype+card_name, CardChip
│   ├── early-signals/      # Server component, api.earlySignals(), CardChip
│   ├── graph/              # page.tsx (server, api.graphSynergies) + GraphView.tsx (client, vis-network, filtre par archétype)
│   └── ban-simulator/      # Client component (Suspense + useSearchParams pour ?card=...), api.simulateBan(), photo de la carte affichée
├── components/
│   ├── nav.tsx             # Navigation top bar (flex-wrap : recherche passe à la ligne si l'espace manque)
│   ├── smart-search.tsx    # Autocomplete debounced → GET /cards/search, clic → /ban-simulator?card=...
│   ├── card-chip.tsx       # Chip carte réutilisable, déclenche le hover-preview-context (pas de tooltip flottant local)
│   ├── hover-preview-context.tsx  # Provider React Context (preview: {name, imageUrl, subtitle}) — un seul par page
│   ├── hover-preview-panel.tsx    # Panneau fixe à gauche (`fixed left-6 top-32`, visible dès xl/1280px), affiche l'image en grand au survol
│   ├── ds/                 # Design system Ember : em.tsx (<Em>), page.tsx (Page, PageHero, StatBand, Toolbar, pillClass, Callout, Explainer, Meter), tags.tsx (TierTag, TrendLabel, BanStatus, Tag)
│   └── ui/                 # shadcn/ui restylés sur les tokens : table, input, info-tooltip (badge, button, card, select inutilisés)
├── lib/
│   └── api.ts              # Client fetch → NEXT_PUBLIC_API_URL (défaut http://localhost:8000/api/v1)
└── types/index.ts          # TypeScript types (TierEntry, BoutiqueSignal, GraphResponse, SearchResult, etc.)
```

`lib/mock.ts` supprimé (plus aucune page ne l'utilise).

**Design system « Ember » (2026-10-31) :** source de vérité visuelle dans `docs/design-system.md` (maquettes : `docs/design-reference.html`). Toutes les pages l'appliquent : thème sombre uniquement, un seul accent `--signal`, tokens en classes Tailwind (`bg-ink-3`, `text-signal`, `border-line`…), **aucune couleur Tailwind brute ni hex dans `src/`**. Tier list en liste dense (l'ancienne grille de cartes est abandonnée), home en bento, Ban Radar avec score en grand et barre empilée des critères.

Pièges rencontrés pendant la refonte :
- **Espace perdu dans un texte JSX multi-ligne qui contient une entité** (`&apos;`, `&amp;`…) : la compilation supprime l'espace initial du texte qui suit une balise ou une expression (« génériques</strong> trustent » rendu « génériquestrustent »). Écrire l'apostrophe typographique `’` plutôt que `&apos;`, ou construire la phrase dans une chaîne JS.
- **Canvas (vis-network) et `var()`** : le canvas ne résout pas les variables CSS. `GraphView` lit les tokens au runtime (`getComputedStyle`), police comprise. Les SVG (home, recharts) acceptent `var(--…)` directement.
- **Chiffres de vitrine** (19 888 decklists, 13 797 cartes, r = 0,771, 4 mois, 63 communautés) : aucun endpoint ne les expose, ils sont dans `src/lib/site-facts.ts`, à mettre à jour à la main quand la base est rafraîchie.
- `prefers-reduced-motion` coupe transitions et animations, mais **pas** `transform` (il casserait les centrages en `-translate-y-1/2`) : les déplacements au survol s'écrivent en `motion-safe:`.
- Formats français centralisés dans `src/lib/format.ts` (`fmtNum`, `fmtPct`, `fmtDate`…) : ne plus utiliser `toFixed` pour l'affichage.
- `--faint` (rangs, placeholders) est à 3,2:1 de contraste sur `--ink` : à réserver au décoratif, jamais à une information seule.

`HoverPreviewProvider`/`HoverPreviewPanel` remplacent l'ancien tooltip flottant par carte (`bottom-full` dans un conteneur `overflow-hidden` → invisible, clippé). Toute nouvelle page qui utilise `CardChip` doit être enveloppée dans un `<HoverPreviewProvider>` avec un `<HoverPreviewPanel />`, sinon `useHoverPreview()` lève une erreur.

**`InfoTooltip`** (`components/ui/info-tooltip.tsx`) : bulle ⓘ ouverte vers le **bas** (`top-full`, pas `bottom-full`) — sinon coupée par un ancêtre `overflow-hidden` (ex: conteneur de tableau). Ne pas revenir à `bottom-full` sans vérifier qu'aucun ancêtre ne clippe.

**`/graph` (vis-network 10) — pièges corrigés le 2026-10-31 :**
- **Pas de `fit()` animé.** Deux `fit` animés enchaînés sans frame entre eux (celui de fin de stabilisation + le nôtre) laissent une `viewFunction` orpheline branchée sur `initRedraw` : la caméra revient au cadrage précédent à chaque redessin (le filtre recentrait avec un changement de retard). Les `fit` sont donc instantanés.
- `fit()` plafonne le zoom à 1 par défaut : le recentrage sur un archétype passe `maxZoomLevel: 4`, sinon la clique reste minuscule.
- `blurNode` n'est pas émis quand la souris quitte le canvas depuis un nœud : le conteneur vide le panneau de survol sur `onMouseLeave`.
- Jointure `cards` ↔ noms issus de `deck_cards` : `cards.name` porte `<P>`/`<C>`/`<Q>` (« Maliss <P> March Hare »), pas `deck_cards` → joindre sur `REPLACE(REPLACE(c.name,'<',''),'>','')` (graph, ban_radar, card_impact). Les ~19 nœuds encore sans image sont des cartes récentes absentes de `cards` (relancer `fetch_cards.py`).
