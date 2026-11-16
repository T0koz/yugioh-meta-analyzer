# Design system — YGO Meta ("Ember")

> Source de vérité visuelle pour `frontend/`. À lire avant toute modification d'UI.
> Validé par Thomas le 31/10/2026 (accent rouge Ember, tier list en liste, home en bento, Ban Radar score en grand, nav flottante).
> Maquettes de référence : [`docs/design-reference.html`](design-reference.html) (ouvrir dans un navigateur ; le sélecteur d'accent y est un reste de la phase de choix, ignorer).
> Inspiration : velmax.llc (encre quasi noire, un accent, serif italique, labels mono).

## 0. Règles de travail

- **Rien n'est appliqué sans validation** : Thomas veut voir le rendu (capture de `localhost:3000`) avant de passer à la page suivante. Une page à la fois.
- **Ne pas mélanger avec les changements en cours** (jointure `<P>`, page `/graph`) : si le dépôt a des fichiers modifiés non liés au design, ne pas les inclure dans un commit design. Commits : proposer, Thomas valide. Push : jamais sans lui.
- Next.js 16 : lire `node_modules/next/dist/docs/` avant de toucher aux fonts, au cache ou au fetch (voir `frontend/AGENTS.md`).
- Réponses et textes d'interface **en français**.

## 1. Principes

1. **Un seul accent** (rouge Ember). Il signale ce qui compte : T1, score critique, bouton principal, valeur mise en avant. S'il y a du rouge partout, il ne signale plus rien.
2. **Hiérarchie par la taille, pas par des boîtes.** Un gros titre, un gros chiffre, puis du détail discret. Pas de carte autour de tout.
3. **Un seul mot en serif italique par titre** (couleur accent). Jamais deux, jamais dans le corps de texte.
4. **Les chiffres et labels sont en monospace** : scores, pourcentages, dates, étiquettes (`TIER`, `ROGUE`, `AU 9 AOÛT 2026`).
5. **Bordures fines, pas d'ombres.** Séparation par lignes à 12 % d'opacité et par changement de surface.
6. **Dense mais respirant** : lignes de tableau de 64 px max, marges généreuses autour des blocs.

## 2. Tokens

Thème **sombre uniquement** (pas de mode clair). Définir sur `:root` (pas de classe `.dark` à poser) et mapper les variables shadcn dessus.

```css
/* frontend/src/app/globals.css — remplace les blocs :root et .dark existants */
:root {
  color-scheme: dark;

  /* surfaces (encre) */
  --ink: #05070b;        /* fond de page */
  --ink-2: #090d14;      /* surface légère (frames, nav) */
  --ink-3: #0e131c;      /* cartes, tuiles sombres */
  --ink-4: #151c28;      /* survol, barres vides, vignettes */
  --line: rgba(170, 195, 235, 0.12);    /* bordure par défaut */
  --line-2: rgba(170, 195, 235, 0.22);  /* bordure appuyée (boutons, tuiles) */

  /* texte */
  --text: #e8edf5;
  --soft: #b4bfcf;       /* paragraphes */
  --muted-text: #8591a6;      /* secondaire, labels */
  --faint: #566175;      /* rangs, placeholders */
  /* NB : dans design-reference.html ce gris s'appelle --muted ; ici --muted-text car shadcn réserve --muted aux fonds */

  /* accent Ember */
  --signal: #ff5a3c;
  --signal-hi: #ff8a6b;      /* survol, focus */
  --on-signal: #1f0700;      /* texte sur fond accent */
  --signal-deep: #b3300f;    /* accent sur fond clair (tuile paper) */

  /* tuile claire de contraste */
  --paper: #eceef1;
  --paper-ink: #0b0f16;
  --paper-muted: #58606e;
  --paper-line: rgba(11, 15, 22, 0.13);

  /* sémantique (hors accent) */
  --good: #3ddc97;       /* tendance haussière uniquement */
  --warn: #f5c451;       /* restrictions de banlist uniquement */
  /* tendance baissière = --muted-text + ▼ (le rouge est réservé à l'accent) */

  /* forme */
  --r: 4px;              /* rayon par défaut (boutons, pills, lignes) */
  --r-lg: 8px;           /* tuiles, frames */
  --gutter: clamp(16px, 3.2vw, 44px);
  --maxw: 1200px;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);

  /* mapping shadcn (pour que table, badge, input, select… héritent du thème) */
  --background: var(--ink);
  --foreground: var(--text);
  --card: var(--ink-3);
  --card-foreground: var(--text);
  --popover: var(--ink-3);
  --popover-foreground: var(--text);
  --primary: var(--signal);
  --primary-foreground: var(--on-signal);
  --secondary: var(--ink-4);
  --secondary-foreground: var(--text);
  --muted: var(--ink-4);
  --muted-foreground: var(--muted-text);
  --accent: var(--ink-4);
  --accent-foreground: var(--text);
  --destructive: var(--signal);
  --border: var(--line);
  --input: var(--line-2);
  --ring: var(--signal-hi);
  --radius: 0.25rem;
  --chart-1: var(--signal);
  --chart-2: var(--soft);
  --chart-3: var(--muted-text);
  --chart-4: var(--faint);
  --chart-5: var(--ink-4);
}
```

À ajouter dans le bloc `@theme inline` pour utiliser les tokens en classes Tailwind (`bg-ink-3`, `text-signal`, `border-line`…) :

```css
@theme inline {
  --color-ink: var(--ink);  --color-ink-2: var(--ink-2);
  --color-ink-3: var(--ink-3);  --color-ink-4: var(--ink-4);
  --color-line: var(--line);  --color-line-2: var(--line-2);
  --color-text: var(--text);  --color-soft: var(--soft);
  --color-muted-text: var(--muted-text);  --color-faint: var(--faint);
  --color-signal: var(--signal);  --color-signal-hi: var(--signal-hi);
  --color-on-signal: var(--on-signal);  --color-signal-deep: var(--signal-deep);
  --color-paper: var(--paper);  --color-paper-ink: var(--paper-ink);
  --color-paper-muted: var(--paper-muted);
  --color-good: var(--good);  --color-warn: var(--warn);
  --font-sans: var(--font-inter-tight);
  --font-serif: var(--font-instrument-serif);
  --font-mono: var(--font-jetbrains-mono);
  --font-heading: var(--font-inter-tight);
}
```

Dans les composants, le texte secondaire s'écrit `text-muted-text` (ou `text-muted-foreground` côté shadcn, même valeur). `bg-muted` reste un fond (`--ink-4`).

> Attention : dans les composants existants, remplacer toutes les classes `bg-slate-*`, `text-slate-*`, `border-slate-*`, `indigo`, `emerald`, `red`, etc. par les tokens ci-dessus. Aucune couleur Tailwind brute ne doit rester dans `src/`.

## 3. Typographie

Trois familles via `next/font/google` dans `layout.tsx` (remplace Geist) :

```tsx
import { Inter_Tight, Instrument_Serif, JetBrains_Mono } from "next/font/google";

const sans = Inter_Tight({ variable: "--font-inter-tight", subsets: ["latin"], weight: ["400", "500", "600"] });
const serif = Instrument_Serif({ variable: "--font-instrument-serif", subsets: ["latin"], weight: "400", style: "italic" });
const mono = JetBrains_Mono({ variable: "--font-jetbrains-mono", subsets: ["latin"], weight: ["400", "500"] });
// <html lang="fr" className={`${sans.variable} ${serif.variable} ${mono.variable}`}>
// <body className="bg-ink text-text font-sans antialiased">
```

| Rôle | Police | Taille / graisse | Tracking | Usage |
|---|---|---|---|---|
| Hero h1 | Inter Tight 500 | `clamp(40px, 7.4vw, 92px)`, lh 0.95 | -0.05em | Une fois par page, max 14 caractères de large (`max-w-[14ch]`) |
| Titre de section h2 | Inter Tight 500 | `clamp(28px, 4vw, 44px)`, lh 1.05 | -0.035em | |
| Titre de tuile h3 | Inter Tight 500 | `clamp(22px, 2.6vw, 30px)`, lh 1.08 | -0.03em | |
| Chiffre clé | Inter Tight 500 | 24–34 px (stats), 80–148 px (tuile) | -0.03 à -0.07em | `tabular-nums` |
| Corps | Inter Tight 400 | 16 px, lh 1.55, couleur `--soft` | normal | Largeur max 65 caractères |
| Texte de liste | Inter Tight 500 | 16 px | -0.01em | Noms d'archétypes et de cartes |
| Label / eyebrow | JetBrains Mono 400 | 11 px | +0.12em, MAJUSCULES | `--muted-text`, précédé d'un point accent 6 px |
| Donnée (score, %, date) | JetBrains Mono 500 | 12–14 px | normal | `tabular-nums` |
| Mot d'accent | Instrument Serif italique | taille du titre parent | -0.01em | Couleur `--signal`. **Un mot par titre.** |

Composant utilitaire à créer : `<Em>mot</Em>` → `<em className="font-serif italic font-normal text-signal tracking-[-0.01em]">`.

## 4. Composants

Créer dans `src/components/ds/` (ou adapter l'existant) ; garder les composants shadcn pour la mécanique (select, tooltip, table) mais restyler.

### Navigation flottante (`nav.tsx`)
- Conteneur : `sticky top-3 z-40`, marge latérale `--gutter`, `max-w-[1200px] mx-auto`.
- Boîte : `bg-ink-2/85 backdrop-blur border border-line-2 rounded-[10px] p-2 pl-4`, flex, gap 16.
- Gauche : logo `YGO META` en mono 600 14 px, tracking .08em, précédé d'un glyphe accent 14 px.
- Centre : liens (Méta, Ban Center, Boutique, Graphe) en 13 px `--muted-text` ; actif = `--text` sur fond `--ink-4`, rayon 4. Masqués sous 760 px (menu à prévoir).
- Droite : champ de recherche (SmartSearch existant) : mono 12 px, bordure `--line`, placeholder « Rechercher une carte… », pastille `⌘K` à droite. Le raccourci ⌘K / Ctrl+K doit focus le champ.
- Garder les sous-menus actuels (Méta, Boutique) en dropdown restylé (même surface que la nav).

### Hero de page
Eyebrow mono (`TIER LIST · TCG · MIS À JOUR 17 JUIN 2026`) → h1 hero avec un mot `<Em>` → paragraphe `--soft` max 52 caractères de large → **bande de stats** : 4 colonnes séparées par des filets verticaux `--line`, bordures haut/bas `--line`, chiffre 24–34 px + label mono 11 px. Fond optionnel : points (`radial-gradient(rgba(170,195,235,.16) 1px, transparent 1.2px)`, maille 14 px), statique.

### Ligne de tier list (`ArchetypeCard` → `ArchetypeRow`)
Grille : `28px 40px minmax(0,1.2fr) 60px minmax(80px,1fr) 64px 92px`, gap 16, padding 10×16, bordure haute `--line`, survol `--ink-3` (transition .2 s `--ease`).
Colonnes : rang mono `01` (`--faint`) · vignette carte 34×48 (rayon 3, bordure `--line-2`, vraie image `image_url`) · nom (500) + sous-ligne mono `score 9,7` · étiquette de tier · barre · part en % (mono 500, droite) · tendance (mono 12, droite).
- La 1re ligne est teintée : `linear-gradient(90deg, color-mix(in srgb, var(--signal) 9%, var(--ink)), var(--ink) 60%)`.
- Barre : 4 px de haut, fond `--ink-4`, remplissage `--signal`, **relative au max du snapshot** (conserver `maxScore`, voir piège `meta_score` ~0.15).
- Sous 760 px : masquer étiquette de tier et barre ; colonnes `22px 34px 1fr 54px 64px`.
- Conteneur : `border border-line rounded-md overflow-hidden`.
- Le panneau de survol (`HoverPreviewPanel`) est conservé, restylé avec la surface `--ink-3`.

### Étiquette de tier (`Badge`)
Mono 500 11 px, tracking .08em, padding 3×7, rayon 3, bordure 1 px.
- `T0`/`T1` : fond `--signal`, texte `--on-signal`.
- `T2` : contour `--signal`, texte `--signal`.
- `T3` : contour `--line-2`, texte `--text`.
- `ROGUE` (et tout autre) : contour `--line-2`, texte `--soft`.
Plus aucune couleur propre à chaque tier.

### Tendance
Mono 500 12 px : `▲ Rising` en `--good`, `→ Stable` en `--muted-text`, `▼ Declining` en `--muted-text`. (Le rouge n'est pas utilisé pour une baisse.)

### Filtres (pills)
Mono 500 12 px, padding 6×10, rayon 4, bordure `--line-2`, texte `--soft`. Actif : fond `--text`, texte `--ink`. Compteur à droite en mono 11 px `--muted-text` (`8 / 47 ARCHÉTYPES`).

### Boutons
Rayon 4, 14 px / 500, padding 11×18. **Un seul bouton plein par écran.**
- Primaire : fond `--signal`, texte `--on-signal`. Secondaire : fond `--ink-3`, bordure `--line-2`. Ghost : transparent.
- Survol : `translateY(-1px)` en .25 s `--ease`. Focus visible : `outline 2px --signal-hi`, offset 2.

### Tuiles bento (home)
Grille 12 colonnes, gap 12, rayon 8, padding 22, bordure `--line-2`. Trois variantes :
- **Paper** (claire) : fond `--paper`, texte `--paper-ink`, mot d'accent en `--signal-deep`. Pour le chiffre boutique (100/100).
- **Dark** : fond `--ink-3`. Pour les listes (top Ban Radar).
- **Signal** : fond `--signal`, texte `--on-signal`. **Une seule par écran**, pour la prédiction.
Chaque tuile : tag mono en haut (`A  SIGNAL BOUTIQUE` avec la lettre encadrée), titre h3 avec un mot `<Em>`, contenu, métadonnées en pills mono. Colonnes desktop : 5 / 4 / 3, puis 7 / 5 ; une colonne sous 900 px.
Home : hero = « Le TCG suit l'OCG, `<Em>quatre mois</Em>` plus tard. » (chiffre réel : lag de 4 mois, r = 0,771).

### Ban Radar (`/ban`, onglet Radar)
- En-tête : eyebrow + h1 « Qui sera `<Em>banni</Em>` ensuite ? » à gauche ; à droite, bloc mono 11 px aligné à droite (`DONNÉES AU 9 AOÛT 2026 / 2 018 DECKS · 6 MOIS`).
- Carte-ligne : grille `110px 40px 1fr auto`, padding 20, bordure haute `--line`. Score 40–60 px Inter Tight 500 (`tabular-nums`) avec, dessous, le libellé de risque en mono 11 px MAJUSCULES couleur `--signal` (`CRITIQUE`). Puis rang `#1`, nom (20 px), méta mono (`83,4 % des decks · 1 682 decks · 82 archétypes`), **barre empilée des 6 critères**, puis statut banlist à droite.
- Barre empilée : hauteur 8, gap 2, un segment par critère dont la largeur = sa contribution en points (somme = score, sur 100). Un seul teinte (`--signal`) avec opacité décroissante par critère : ubiquité .9, porteur .75, copies .6, restriction .45, élan .3, pont .18. Légende mono 10,5 px sous la 1re ligne seulement.
- Statut : mono 500 11 px, bordure 1 px ; `Unlimited` en `--soft` ; `Limited`/`Semi-Limited` en `--warn` (contour + texte).
- L'encart « Comment lire ce score » (actuellement un pavé) passe dans une info-bulle ou un panneau repliable ouvert par un bouton `Comment lire ce score ?`.
- Les poids des critères restent **dupliqués** entre `scripts/build_ban_radar.py` (`WEIGHTS`) et `backend/app/routers/ban_radar.py` : ne pas les toucher dans un travail de design.

### Encart d'info / tooltip
Surface `--ink-3`, bordure `--line-2`, rayon 4, padding 14×16. Titre mono 11 px MAJUSCULES `--signal`, texte 14 px `--soft`. `InfoTooltip` : même surface, 12 px.

### Tableau (`boutique`, etc.)
`Table` shadcn restylé : pas de fond de ligne, filets `--line`, en-têtes mono 11 px MAJUSCULES `--muted-text`, nombres en mono `tabular-nums` alignés à droite, survol de ligne `--ink-3`. Badges de signal : `Fort` = étiquette T1 (plein accent) ; `Moyen`/`Faible` = contour. Statut banlist TCG = statut jaune `--warn`.

### Card chip (`card-chip.tsx`)
Vignette mini + nom, fond `--ink-4`, bordure `--line`, rayon 4, mono 12 px ; au survol le panneau de prévisualisation s'affiche (comportement existant).

### Graphiques (recharts)
Série principale `--signal` (trait 2 px), séries secondaires `--soft` / `--muted-text` / `--faint`, grille `--line` en pointillés, axes et légendes en mono 11 px `--muted-text`, tooltip sur surface `--ink-3`. Pas de dégradés multicolores. Point final de la série principale mis en évidence (cercle 4,5 px).

## 5. Mise en page

- Largeur max `--maxw` 1200 px, centrée ; gutter latéral `--gutter` (≥ 16 px) partout.
- Rythme vertical : 44 px entre sections, 26 px entre titre et contenu.
- Responsive : tester à 390 px. Aucun scroll horizontal de page ; un tableau large défile dans son propre conteneur (`overflow-x-auto`).
- Fond de page `--ink` ; surfaces `--ink-2`/`--ink-3` ; jamais de blanc pur hors tuile `--paper`.

## 6. Mouvement et accessibilité

- Une seule animation orchestrée au chargement par page, au plus. Survols : 200–250 ms avec `--ease`. Fond en points : statique pour l'instant (animation canvas = phase ultérieure, validation requise).
- Respecter `prefers-reduced-motion` : supprimer transitions et transformations.
- Focus clavier toujours visible (`outline 2px --signal-hi`). Contraste : texte `--soft`/`--muted-text` sur `--ink` ≥ 4.5:1 ; le texte sur fond `--signal` utilise `--on-signal`.
- L'information ne passe jamais par la couleur seule (tendances : flèche + mot ; risque : libellé + score).

## 7. Copy

- Français, phrases courtes, voix active. Nommer par ce que l'utilisateur reconnaît (« cartes à acheter », pas « buy_signals »).
- Titres : une idée, un mot `<Em>`. Exemples : « Ce que joue la méta, *maintenant*. » · « Qui sera *banni* ensuite ? » · « Le TCG suit l'OCG, *quatre mois* plus tard. »
- Pas d'emoji comme marqueur de section. Pas de numérotation 01/02/03 sauf si l'ordre est une information (les rangs le sont).
- Chiffres français : virgule décimale (`9,7`), espace insécable avant `%` seulement si le design le demande (mockups : `29,6 %`), milliers avec espace (`19 888`).

## 8. Ordre d'implémentation (une étape = une validation de Thomas)

1. **Socle** : polices dans `layout.tsx`, tokens dans `globals.css`, `<Em>`, fond `bg-ink`. Vérifier qu'aucune page ne casse (contrastes).
2. **Navigation flottante** + recherche ⌘K.
3. **Tier list** : hero + stats + lignes (maquette A).
4. **Home** en bento (maquette B) : remplace la redirection de `src/app/page.tsx`.
5. **Ban Center** : Radar (maquette C), puis onglets Cartes à impact et Simulateur.
6. **Boutique**, **Prédictions**, **Évolution**, **Early signals**, **Graphe** : appliquer le système (tableaux, graphiques, panneaux).
7. Passe finale : responsive 390 px, `prefers-reduced-motion`, nettoyage des classes Tailwind brutes restantes, mise à jour de `context.md`/`BACKLOG.md`.

À chaque étape : lancer le front, capturer les pages touchées (desktop + 390 px), les montrer à Thomas, **attendre son feu vert**, puis proposer le commit.

## 9. Interdits

- Couleurs Tailwind brutes (`slate`, `indigo`, `emerald`, `red`…) ou hex en dur dans les composants.
- Plus d'un accent, plus d'un bouton plein, plus d'une tuile `signal` par écran.
- Ombres portées, dégradés violet/bleu, coins très arrondis (> 8 px), cartes empilées dans des cartes.
- Rouge pour une baisse ou une erreur ordinaire : le rouge = signal. Les erreurs techniques s'affichent en `--warn` avec un message clair.
- Toucher à la logique des données, aux endpoints ou au scoring dans une tâche de design.
