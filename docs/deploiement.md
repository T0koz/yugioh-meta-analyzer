# Déploiement sur Vercel — guide pas à pas (TOK-35, option A)

Préparé le 2026-11-17 (lot 14), code de déploiement le 2026-11-17 (lot 14 bis) ; **rien n'est déployé, rien n'est relié**. Décision d'hébergement : Vercel plan gratuit (Hobby)
seul, un projet pour le site et l'API (`docs/decisions/0032-*.md`), projet `gang-5d00/yugi-gang`.
Toutes les commandes `vercel …` sont à lancer **par Thomas**, depuis son terminal ; aucune n'a été exécutée par l'agent.

## 0. À lire d'abord : état des trois points bloquants

Décisions de Thomas du 17/11 (formulaire § 9) : images sur **Cloudflare R2**, site **public mais non diffusé** (aucune protection
Vercel, production indexable), **construction sur sa machine puis envoi** (voie 2).

| # | Constat | État au 17/11 (lot 14 bis) |
|---|---|---|
| 1 | **Le build du front appelle l'API** (pages pré-générées), et la liaison `BACKEND_URL` « ne se résout pas pendant les builds » (doc *Service bindings*). Un build lancé par Vercel échouerait. | **Contourné par la voie 2** : le site est construit sur la machine de Thomas contre l'API locale (`API_URL`), puis le résultat est envoyé (`vercel deploy --prebuilt`). Script : `scripts/deploy_prebuilt.py` (§ 7). |
| 2 | Le serveur et le navigateur lisaient la même `NEXT_PUBLIC_API_URL`. | **Réglé** : `lib/api.ts` (`apiBaseUrl()`) lit côté serveur `API_URL`, puis `BACKEND_URL` + `/api/v1`, puis `NEXT_PUBLIC_API_URL` ; côté navigateur `NEXT_PUBLIC_API_URL` (`/api/v1` en ligne). Sans variable, rien ne change en local (`http://localhost:8000/api/v1`). |
| 3 | Les images de cartes (1,17 Go) ne tiennent ni dans le déploiement ni dans Vercel Blob gratuit. | **À faire par Thomas** : envoi vers R2 (§ 6). Côté code, les images de cartes ne passent plus par `/_next/image` (quota gratuit épargné, § 6). |

Reste à Thomas, dans l'ordre : § 2 (relier le projet depuis la racine), § 6 (R2), § 4 (variables), § 7 (prévisualisation, puis production).

## 1. Ce qui a été préparé (fichiers)

| Fichier | Rôle |
|---|---|
| `vercel.json` (racine) | Deux **services** : `backend` (FastAPI, `backend/`, point d'entrée `app.main:app`) et `frontend` (Next.js, `frontend/`) ; `/api/*` → API, le reste → site ; liaison privée `BACKEND_URL` du site vers l'API ; la base `backend/data/serving.db` est incluse dans la fonction. |
| `.vercelignore` (racine) | Ce que la CLI **n'envoie pas** (bases complètes, 1,1 Go d'images, notebooks, docs, scripts, `node_modules`, `.env*`). Reste largement sous la limite d'envoi de 100 Mo. |
| `.env.example`, `frontend/.env.example` | Variables documentées, **aucune valeur secrète**. |
| `.gitignore` (+ `backend/data/`) | La copie de la base embarquée ne peut pas être commitée. |
| `backend/app/db.py` | Ouverture de la base en **lecture seule** (`mode=ro`) ; sur Vercel (variable système `VERCEL`), l'API lit seule `backend/data/serving.db`. Sans effet en local. |

| `frontend/src/lib/api.ts`, `card-chip.tsx` *(lot 14 bis)* | Adresse de l'API séparée serveur / navigateur (§ 0, point 2). |
| `frontend/src/components/card-art.tsx`, `safe-image.tsx` *(lot 14 bis)* | Images de cartes en `unoptimized` (`CardImage`, `SafeImage`) : demandées telles quelles à `NEXT_PUBLIC_CARD_IMAGES_URL`. |
| `scripts/deploy_prebuilt.py` *(lot 14 bis)* | Voie 2 : vérifie les prérequis, prépare la base embarquée, **affiche** les commandes Vercel ; ne les lance qu'avec `--execute`. |
| `.gitignore` (+ `.vercel/`) *(lot 14 bis)* | `vercel pull` écrit les variables du projet dans `.vercel/` à la racine : jamais commité. |

Lancement local intact : `uvicorn` (port 8114 essayé), `npm run build` (le build réussit quand l'API tourne), 44 tests de l'API verts sur `serving.db`,
sur `yugioh.db` et en simulant Vercel (`VERCEL=1` + base embarquée).

## 2. Réglages du projet `yugi-gang` (à faire par Thomas)

Source : doc *Services* et guide *Python backend with Next.js* (§ 11). Les Services sont en **bêta, sur tous les plans**.

1. **Relier depuis la racine du dépôt**, pas depuis `frontend/` (le `vercel.json` est à la racine) :
   ```bash
   cd ~/code/yugioh-meta-analyzer
   vercel link --project yugi-gang --scope gang-5d00
   ```
   Le lien de `frontend/.vercel/` devient inutile (il n'est jamais commité, ne pas y toucher ; `frontend/.env.local` contient un jeton, ne pas l'ouvrir).
2. Tableau de bord → projet → **Settings → General → Root Directory** : **vide** (racine du dépôt), et **Framework Preset : Services**
   (ou `vercel project update --framework services`). Si le dossier racine reste `frontend`, seul le site se construit (dépannage du guide Vercel).
3. **Settings → Git** : **ne pas connecter GitHub** (décision du 16/11). Conséquence : pas de déploiement automatique à chaque push, et
   c'est voulu : la base n'est pas dans Git, donc tout déploiement part de la machine de Thomas (§ 3).
4. **Settings → Functions** : région par défaut `iad1` (Washington). Laisser, ou choisir une région européenne proche (Hobby : une seule région).

## 3. La base `serving.db` : embarquée dans l'API

**Choix recommandé : embarquer.** `data/serving.db` fait 11,6 Mo ; la fonction Python peut peser 500 Mo décompressée (limite Hobby, doc *Functions limits*)
et l'envoi par la CLI 100 Mo. La base part donc **avec le code**, depuis la machine de Thomas, à chaque déploiement : pas de stockage externe, pas de téléchargement au démarrage,
pas de démarrage à froid supplémentaire. Contrepartie : mettre à jour les données = redéployer (§ 7), ce qui convient à un recalcul hebdomadaire.
Vercel Blob au démarrage a été écarté : plus de pièces mobiles, et il faudrait un jeton dans la fonction.

Avant chaque déploiement :
```bash
python scripts/build_serving_db.py --check        # la base de service est cohérente avec les endpoints
mkdir -p backend/data && cp data/serving.db backend/data/serving.db
```
- **Elle ne peut pas finir dans Git** : `git check-ignore -v backend/data/serving.db` répond `.gitignore:…:backend/data/` (vérifié le 2026-11-17) ; `data/*.db` couvre déjà l'original ;
  `scripts/check.py` refuse en plus tout `.db` suivi.
- La CLI envoie le fichier malgré `.gitignore` : un `.vercelignore` est présent et lui seul compte pour la CLI (doc *Deploying from the CLI* ; non relu en détail, voir « Points non vérifiés »).
  Si un déploiement de prévisualisation dit « base introuvable », ouvrir `vercel inspect <url>` et vérifier que `backend/data/serving.db` figure dans les fichiers de la fonction.
- Lecture seule : `db.py` ouvre la base en `mode=ro` ; le système de fichiers de la fonction est de toute façon non modifiable.

## 4. Variables d'environnement

À ajouter **par Thomas** (aucune ne se commite). `NEXT_PUBLIC_*` sont **publiques** et figées **au build** : redéployer après changement.

| Variable | Environnement | Valeur | Rôle |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | Production, Preview | `/api/v1` | Adresse de l'API vue du **navigateur** (même domaine). Le serveur ne l'utilise que si `API_URL` et `BACKEND_URL` manquent. |
| `API_URL` | — | **ne jamais la créer sur Vercel** | Adresse absolue de l'API pour le **build local** (`http://localhost:8000/api/v1`), passée par le script. Sur Vercel, elle prendrait le pas sur `BACKEND_URL` et pointerait vers une machine absente. |
| `NEXT_PUBLIC_SITE_URL` | Production | `https://<domaine de production>` (sans barre finale) | Liens canoniques, Open Graph, sitemap (lot 5). Preview : ne rien mettre. **Obligatoire avec la voie 2** : avec `--prebuilt`, la variable système `VERCEL_PROJECT_PRODUCTION_URL` manque au build (doc `vercel deploy`), les liens canoniques retomberaient sur `http://localhost:3000`. Le script le vérifie avant un `--execute prod`. |
| `NEXT_PUBLIC_CARD_IMAGES_URL` | Production, Preview | adresse du stockage des images (§ 6) | Sans elle, le site cherche `/card-images/…`, qui n'existe pas en ligne. |
| `BACKEND_URL` | — | **ne pas la créer** | Injectée par Vercel (liaison de service) dans le site, **à l'exécution seulement** : sert au rafraîchissement des pages (toutes les 5 min, `revalidate: 300`). |
| `YGO_DB_PATH` | — | **inutile** | L'API lit seule `backend/data/serving.db` sur Vercel. |

```bash
vercel env add NEXT_PUBLIC_API_URL production        # Vercel demande la valeur : /api/v1
vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_SITE_URL production
vercel env add NEXT_PUBLIC_CARD_IMAGES_URL production
vercel env add NEXT_PUBLIC_CARD_IMAGES_URL preview
vercel env ls
```
(`vercel env add` ouvre une saisie interactive : la valeur n'apparaît pas dans l'historique de commandes.)

## 5. Site public mais non diffusé (choix du 17/11)

**Choix de Thomas : aucune protection Vercel.** Le site est en ligne, ouvert à qui connaît l'adresse, et l'adresse n'est publiée nulle part.

Ce que cela implique :
- **Tout le monde peut l'ouvrir** avec l'adresse : pas de connexion, pas de mot de passe. « Non diffusé » n'est pas « privé ».
- **L'adresse se découvre sans qu'on la donne** : les certificats HTTPS sont inscrits dans des journaux publics (*Certificate Transparency*) que des robots lisent, un lien collé dans une messagerie peut être visité par son aperçu, une capture peut circuler.
- **La production est indexable** : lot 5, `noindex` et `robots.txt` fermé **seulement** quand `VERCEL_ENV=preview` (`lib/site.ts`). Avec la voie 2, cette valeur est figée **au build** : le script passe `VERCEL_ENV=preview` aux prévisualisations et `VERCEL_ENV=production` à la production (les variables système manquent au build avec `--prebuilt`, doc `vercel deploy`).
- L'API est publique aussi (`/api/v1/…`), en lecture seule ; elle ne sert que des agrégats déjà affichés par le site.
- Coût : aucun. Un passage de robots consomme des invocations de fonctions (quota Hobby : 1 M par mois, § 10), les pages étant surtout statiques.

**Recommandation (non appliquée, elle contredit le choix « production indexable ») : garder `noindex` en production tant que le site n'est pas ouvert.**
Un moteur qui indexe maintenant garde des pages provisoires (textes non relus, seuils « provisoires ») dans ses résultats pendant des semaines.
Mise en œuvre si Thomas la retient (formulaire § 9, point D) : une variable de build, par exemple `SITE_INDEXABLE=0`, lue par `INDEXABLE` dans
`lib/site.ts` (quelques lignes, pas de changement de page), retirée à l'ouverture du site.

Pour fermer le site plus tard (doc *Deployment Protection*) : *Vercel Authentication*, portée « All Deployments », est **gratuite sur tous les plans** ;
*Password Protection* est payante. Réglage : Settings → Deployment Protection. La liaison `BACKEND_URL` n'est pas concernée (les appels entre services
sautent la protection, doc *Service bindings*).

## 6. Images de cartes (TOK-92)

État : 14 084 cartes, 3 tailles (`art` 257 Mo / 13 968 fichiers, `card-sm` 190 Mo, `card-lg` 725 Mo), **1,17 Go, 42 136 fichiers**, WebP déjà aux bonnes tailles, hors Git.
`lib/card-images.ts` fabrique toutes les adresses à partir de `NEXT_PUBLIC_CARD_IMAGES_URL` : changer d'hébergement = changer cette variable, aucun code.

| Option | Verdict | Chiffres et sources |
|---|---|---|
| Embarquer dans le déploiement | **Non** | Envoi CLI limité à **100 Mo** (Hobby) ; 1,17 Go dépasse largement (doc *Limits*, « Static file uploads »). |
| **Vercel Blob (gratuit)** | **Non** | Hobby : **1 Go** de stockage (1,17 Go à stocker) et **2 000 opérations avancées** (un envoi = 1 ; il en faut 42 136). Dépassement = **plus d'accès au Blob pendant 30 jours** (doc *Blob usage and pricing*, 2026-09-23). Même en n'envoyant que `art` + `card-sm` (447 Mo, ≈ 28 000 fichiers) : bloqué par les opérations. |
| **Cloudflare R2** | **Recommandé** | Gratuit : **10 Go** de stockage, **1 M d'opérations d'écriture** (Class A), **10 M de lecture** par mois, **sortie gratuite** (doc Cloudflare R2 *Pricing*, relue le 2026-11-17). Largement suffisant (1,17 Go, 42 136 envois). |

Réserves sur R2 (non établies par la documentation lue) : la page de tarifs ne dit pas si une **carte bancaire est exigée à l'ouverture du compte** (à regarder avant de s'inscrire ; cela peut contredire la règle « rien qui engage de l'argent ») ;
l'adresse publique gratuite `r2.dev` est « limitée en débit », réservée au développement et sans cache Cloudflare (doc R2 *Public buckets*, relue le 17/11) ; une adresse sur un **domaine à soi**, géré par Cloudflare, est la voie normale pour un site ouvert.
Si ces conditions ne conviennent pas : tout hébergeur d'objets compatible S3 donnant ≥ 2 Go gratuits convient ; seule la variable change.

### Étapes R2 pour Thomas (décision du 17/11 ; aucune n'a été faite par l'agent)
1. **Compte** : Thomas a créé le compte Cloudflare. Dans le tableau de bord : **R2 Object Storage** → activer R2 (l'offre gratuite s'affiche ;
   lire l'écran avant de valider, c'est là qu'une carte bancaire peut être demandée).
2. **Bucket** : R2 → *Create bucket*, nom suggéré `yugi-gang-cards`, emplacement automatique. Un bucket n'est **jamais public par défaut** (doc *Public buckets*).
3. **Adresse publique** (doc *Public buckets*) :
   - **pour l'essai** : bucket → *Settings* → *Public Development URL* → *Enable* (taper `allow`). Adresse en `https://pub-….r2.dev`.
     La doc la dit « limitée en débit » et réservée au développement, **sans cache Cloudflare** : suffisante pour la prévisualisation.
   - **pour un site ouvert** : *Custom Domains* → un sous-domaine (ex. `cards.<domaine>`) ; le domaine doit être géré par Cloudflare
     dans le **même compte**. Cette adresse profite du cache Cloudflare. À faire quand un domaine sera choisi.
4. **Clé d'accès pour l'envoi** (doc *R2 API tokens*) : R2 → *Overview* → *Manage API Tokens* → *Create* ; permission **Object Read & Write**,
   limitée au bucket `yugi-gang-cards`. Copier l'*Access Key ID* et le *Secret Access Key* (affiché **une seule fois**) dans un gestionnaire
   de mots de passe, jamais dans le dépôt.
5. **Outil d'envoi** : `rclone` ≥ 1.59 (doc R2 *rclone* : « Cloudflare R2 » comme fournisseur). `brew install rclone`, puis `rclone config` :
   nouveau remote `r2`, type *Amazon S3 compliant*, fournisseur *Cloudflare R2*, les deux clés, point d'accès
   `https://<id du compte>.r2.cloudflarestorage.com`. Ajouter `no_check_bucket = true` si la clé est limitée au bucket (même doc).
   La configuration va dans `~/.config/rclone/rclone.conf`, hors du dépôt.
6. **Envoi** (1,17 Go, 42 136 fichiers ; structure `art/`, `card-sm/`, `card-lg/` conservée), avec l'en-tête de cache posé sur chaque fichier
   (`--header-upload`, doc rclone) ; d'abord à blanc (`--dry-run`), puis pour de vrai :
   ```bash
   cd ~/code/yugioh-meta-analyzer
   rclone copy data/card-images r2:yugi-gang-cards --exclude "_*" \
     --header-upload "Cache-Control: public, max-age=31536000, immutable" --transfers 16 --dry-run
   rclone copy data/card-images r2:yugi-gang-cards --exclude "_*" \
     --header-upload "Cache-Control: public, max-age=31536000, immutable" --transfers 16 --progress
   ```
   `--exclude "_*"` laisse de côté `_failures.jsonl` et `_missing.json`. `copy` n'efface jamais rien côté R2 (contrairement à `sync`).
   Le cache d'un an est sûr : une illustration de carte ne change pas, et `download_card_images.py` n'ajoute que des fichiers nouveaux.
7. **Contrôle** : `curl -I https://<adresse publique>/art/<id>.webp` répond `200`, `content-type: image/webp` et l'en-tête `cache-control` ci-dessus.
8. **Variable** : `vercel env add NEXT_PUBLIC_CARD_IMAGES_URL production` (et `preview`), valeur = adresse publique **sans barre finale**, puis
   reconstruire (variable figée au build). Contrôle en ligne : les images de cartes viennent de cette adresse, aucune de `images.ygoprodeck.com`
   ni de `/_next/image`.
9. **Chaque lundi** : `python scripts/download_card_images.py` (incrémental), puis la même commande `rclone copy` (seuls les fichiers nouveaux partent).

### Optimisation d'images de `next/image` (plan gratuit) — réglé au lot 14 bis
Quotas Hobby par mois : **5 000 transformations**, 300 000 lectures du cache, 100 000 écritures ; au-delà, les nouvelles images renvoient une
erreur **402** (doc *Image optimization limits and pricing*). Les images de cartes sont donc en **`unoptimized`** : `CardArt`, `CardArtFill`,
`ArtDot` (via `SafeImage` / `CardImage`) et les bandeaux d'archétype (`CardImage`). Elles sont déjà en WebP aux tailles d'affichage et partent
directement de `NEXT_PUBLIC_CARD_IMAGES_URL`. Mesuré le 17/11 (build de production, 10 pages × 2 largeurs, Playwright) : **0 requête vers
`/_next/image`**, 657 images de cartes servies directement (toutes en 200), 0 vers YGOPRODeck. Les 45 captures des tests visuels sont identiques.

## 7. Voie 2 : construire sur la machine de Thomas, puis envoyer

Prérequis : § 2 fait (projet relié **depuis la racine**), § 4 (variables), § 6 pour les images. CLI Vercel ≥ 48.1.8 (65.16.0 installée le 17/11).

### 7.1 Ce que fait le script
`python scripts/deploy_prebuilt.py` **ne lance aucune commande Vercel** par défaut. Il vérifie `vercel.json`, la CLI, le lien du projet à la racine
et que `.vercel/` est ignoré par Git ; vérifie `data/serving.db` (toutes les tables de `SERVED_TABLES`, plus récente que `yugioh.db`) ; la copie dans
`backend/data/serving.db` après avoir vérifié que Git ignore ce chemin ; vérifie que l'API locale répond **et qu'elle sert les mêmes
valeurs témoins que `data/serving.db`** (`as_of` et `n_decks_window` du Ban Radar, `computed_at` des signaux boutique ; écart =
échec bloquant, `--execute` refusé, TOK-148) ; puis **affiche** les commandes. Le témoin repère une API lancée sur une base
différente ou plus ancienne ; sur `yugioh.db` du même jour, les tables servies sont identiques et le témoin concorde, à raison.
`--execute preview` ou `--execute prod` les lance, seulement si tout est vert. Sortie réelle du 17/11, dans un worktree non relié :
```
1. Configuration Vercel
  ✓ vercel.json (mode Services) à la racine
  ✓ CLI Vercel 65.16.0
  ✗ projet non relié depuis la racine
      → cd <dépôt> && vercel link --project yugi-gang --scope gang-5d00 (guide §2)
  ✓ .vercel/ ignoré par Git (vercel pull y écrit des variables)
2. Base de service
  ✓ …/data/serving.db (11.7 Mo, construite le 2026-11-17 00:55)
  ✓ toutes les tables de SERVED_TABLES sont présentes
  ✓ serving.db plus récente que yugioh.db
3. Copie embarquée dans l'API
  ✓ backend/data/serving.db ignoré par Git
  ✓ backend/data/serving.db copiée depuis …/data/serving.db
4. API locale (interrogée par le build du site)
  ✓ http://localhost:8115/api/v1/meta/tier-list → 200
  ✓ l'API locale sert les mêmes valeurs témoins que serving.db (as_of, n_decks_window, computed_at)   ← depuis TOK-148
5. Commandes (depuis la racine du dépôt)
  # Prévisualisation (toujours d'abord)
  vercel pull --yes --environment=preview
  env API_URL=http://localhost:8115/api/v1 VERCEL_ENV=preview vercel build
  vercel deploy --prebuilt --archive=tgz
  # Production
  vercel pull --yes --environment=production
  env API_URL=http://localhost:8115/api/v1 VERCEL_ENV=production vercel build --prod
  vercel deploy --prebuilt --archive=tgz --prod
✗ 1 vérification(s) en échec : corriger avant de déployer.
Aucune commande Vercel lancée (mode par défaut).
```
(Port 8115 : celui de l'essai ; par défaut le script vise `http://localhost:8000/api/v1`, ou `--api-url`.)

### 7.2 Premier déploiement (prévisualisation)
```bash
cd ~/code/yugioh-meta-analyzer && git checkout main && git pull --rebase
python scripts/check.py
# terminal 2 : l'API sur la base qui part en ligne
cd backend && YGO_DB_PATH=../data/serving.db ../.venv/bin/uvicorn app.main:app --port 8000
# terminal 1
python scripts/deploy_prebuilt.py                     # tout doit être ✓
python scripts/deploy_prebuilt.py --execute preview
```
- `vercel pull` télécharge les réglages et variables du projet dans `.vercel/` (ignoré par Git) ; `vercel build` construit les deux services dans
  `.vercel/output/` ; `vercel deploy --prebuilt --archive=tgz` envoie ce résultat (une archive plutôt que des milliers de fichiers, doc `vercel deploy`).
- **Le premier déploiement d'un projet est toujours un déploiement de production**, même sans `--prod` (doc `vercel deploy`). Il est construit avec
  `VERCEL_ENV=preview`, donc en `noindex` : sans danger, mais à remplacer ensuite par un vrai `--execute prod`.
- Vérifier : la page d'accueil, `/tier-list`, `/decks`, `/ban`, une image de carte ; `vercel curl /api/v1/meta/tier-list --deployment <adresse>` ;
  dans le tableau de bord, *Runtime Logs* sans « unable to open database », et `vercel inspect <adresse>` montre `backend/data/serving.db` dans la fonction.
- Si le build dit « Failed to collect page data » : l'API locale ne répond pas, ou `vercel build` n'a pas transmis `API_URL` à Next (§ 8, point non vérifié).

### 7.3 Production
```bash
vercel env ls        # NEXT_PUBLIC_SITE_URL, NEXT_PUBLIC_API_URL, NEXT_PUBLIC_CARD_IMAGES_URL présentes en Production
python scripts/deploy_prebuilt.py --execute prod
```
Le dépôt GitHub n'étant pas connecté, « production depuis `main` » signifie : `main` à jour, `check.py` vert, puis le script depuis cette copie.

### 7.4 Mise à jour du lundi
Après `scripts/refresh_all.py` (recalcul des tables, reconstruction de `data/serving.db`, images nouvelles) :
```bash
cd backend && YGO_DB_PATH=../data/serving.db ../.venv/bin/uvicorn app.main:app --port 8000   # terminal 2
rclone copy data/card-images r2:yugi-gang-cards --exclude "_*" \
  --header-upload "Cache-Control: public, max-age=31536000, immutable" --transfers 16   # § 6, étape 9
python scripts/deploy_prebuilt.py --execute preview    # coup d'œil à l'adresse affichée
python scripts/deploy_prebuilt.py --execute prod
```
Les pages et la base partent ensemble : le site construit et l'API déployée montrent la même semaine de données. Les pages se rafraîchissent
ensuite au plus toutes les 5 minutes depuis l'API en ligne (même base), donc sans écart.

### 7.5 Retour arrière
`vercel rollback` (sans argument : revient au déploiement de production **précédent**). Sur Hobby, on ne peut revenir **qu'au déploiement de production
immédiatement précédent** (doc *Rolling back*) ; pour un plus ancien : `vercel redeploy <url>` (un déploiement `--prebuilt` est redéployé à partir de
sa sortie, sans reconstruction, doc `vercel deploy`) ou `vercel promote <url>`. Contrôle : `vercel rollback status`. La base voyage avec chaque
déploiement : revenir en arrière ramène aussi les données de la semaine d'avant.

## 8. Compatibilité de `vercel build` + `--prebuilt` avec les Services

**Ce que dit la documentation (lue le 17/11)** :
- *Build Output API → Services* : un déploiement à plusieurs services est décrit dans `.vercel/output/config.json` (tableau `services`), chaque service
  étant émis sous `.vercel/output/services/<nom>/` comme un arbre de sortie complet (fonctions, fichiers statiques).
- *`vercel build`* : la commande écrit dans `.vercel/output` selon la Build Output API, et sa section *Schedule configuration* traite des fonctions
  « dans un service » (`.vercel/output/services/worker/functions/index.func`) : `vercel build` produit donc bien la sortie par services.
- *`vercel deploy`* : `--prebuilt` envoie le contenu de `.vercel/output` produit par `vercel build`.
- Contraintes d'un service (*Build Output API → Services*) : pas de middleware, pas de runtime Edge. Le site n'a ni `middleware.ts` ni `proxy.ts`.

**Verdict : compatible selon la documentation, mais aucune page ne décrit explicitement un `--prebuilt` en mode Services (bêta).** C'est très probable,
pas démontré ; le premier `--execute preview` le tranchera.

**Points à observer au premier essai** :
- `vercel build` doit transmettre `API_URL` (passée dans l'environnement) au build de Next. Sinon, voie de contournement : créer
  `frontend/.env.production.local` (ignoré par Git) contenant `API_URL=http://localhost:8000/api/v1` le temps du build, puis le supprimer.
  **Jamais** `API_URL` dans les variables du projet Vercel (§ 4).
- Le service Python construit en local : la CLI installe les dépendances de `backend/requirements.txt` sur la machine de Thomas ; une erreur de
  version de Python s'afficherait à ce moment.
- `includeFiles: data/serving.db` : vérifier avec `vercel inspect` que la base est dans la fonction.

**Voie de repli si `--prebuilt` échoue avec les Services** (voie 1) : laisser Vercel construire (`vercel deploy` sans `--prebuilt`), en rendant le
build indépendant de l'API. Les pages qui interrogent l'API au build (`generateStaticParams` de `/archetype/[slug]` et `/decks/[archetype]`, pages
statiques à `revalidate: 300`) deviennent générées à la demande : `generateStaticParams` renvoie une liste vide et les pages sont rendues à la
première visite via `BACKEND_URL`, puis mises en cache. Lot de code à part, à faire après les lots qui touchent ces pages.
Repli intermédiaire, sans code : deux projets Vercel (API seule, puis site avec `API_URL` = adresse publique de l'API au build), au prix d'une
seconde adresse et de la fin du domaine unique.

## 9. Formulaire (réponses de Thomas du 17/11)

**A. Stockage définitif des images de cartes** — répondu le 17/11
- [x] Cloudflare R2 (10 Go gratuits, 1 M d'écritures, sortie gratuite) — compte créé par Thomas
- [ ] Autre hébergeur d'objets gratuit
- [ ] Ne pas héberger
- Commentaire libre : étapes au § 6.

**B. Protection de l'adresse** — répondu le 17/11
- [ ] « All Deployments » + Vercel Authentication (visible seulement par les comptes de l'équipe)
- [x] Aucune protection : site public mais non diffusé, production indexable
- Commentaire libre : conséquences et recommandation `noindex` au § 5.

**C. Voie du build** — répondu le 17/11
- [x] Voie 2 : construction sur la machine de Thomas puis envoi (`vercel build` + `vercel deploy --prebuilt`)
- [ ] Voie 1 : pages générées à la demande, build par Vercel
- Commentaire libre : script `scripts/deploy_prebuilt.py` (§ 7) ; repli au § 8.

**D. `noindex` en production tant que le site n'est pas ouvert** — question nouvelle (lot 14 bis), à cocher
- [x] Oui : variable de build `SITE_INDEXABLE=0` lue par `lib/site.ts`, retirée à l'ouverture — *recommandé (§ 5)*
- [ ] Non : production indexable dès maintenant (choix du 17/11 inchangé)
- Commentaire libre : …

## 10. Rappels

- **Plan gratuit (Hobby) = usage personnel, non commercial.** Les pages de documentation lues ne reprennent pas la formulation exacte : la relire dans les conditions d'utilisation de Vercel (section *Fair use*) avant toute offre payante. Le projet vise la vente aux boutiques (150 €/mois) : à ce moment-là, le plan Pro est nécessaire (et l'adresse sera diffusée).
- Quotas Hobby utiles (doc *Fair use guidelines*) : 100 Go de transfert rapide, 1 M d'invocations de fonctions, 4 h de CPU actif, par mois ; 100 déploiements par jour ; durée maximale d'une fonction 300 s (réglée à 30 s dans `vercel.json`) ; mémoire 2 Go ; corps de réponse 4,5 Mo.
- Jamais de `.env`, de base ou de jeton dans Git (dépôt public) ; `frontend/.env.local` (jeton OIDC de la CLI) reste ignoré.

## Points non vérifiés (à lever au premier essai)
- `vercel build` + `--prebuilt` avec les Services (bêta) : cohérent avec la documentation, non décrit explicitement (§ 8).
- Transmission de `API_URL` par `vercel build` au build de Next (§ 8, contournement prévu).
- Poids et contenu de la fonction Python (`includeFiles` dans un service) : `vercel inspect`.
- Comportement de la CLI vis-à-vis de `.gitignore` quand un `.vercelignore` existe (sans objet avec `--prebuilt` : seule `.vercel/output` part).
- Écran d'activation de R2 (carte bancaire demandée ou non) : à lire par Thomas avant de valider.

## Sources (lues le 2026-11-17)
- FastAPI sur Vercel : https://vercel.com/docs/frameworks/backend/fastapi
- Services : https://vercel.com/docs/services ; routage : https://vercel.com/docs/services/routing ; liaisons : https://vercel.com/docs/services/bindings ; référence : https://vercel.com/docs/services/config-reference ; tarifs : https://vercel.com/docs/services/pricing
- Guide Next.js + FastAPI : https://vercel.com/kb/guide/python-backend-on-vercel
- `vercel.json` : https://vercel.com/docs/project-configuration/vercel-json
- Limites des fonctions : https://vercel.com/docs/functions/limitations ; limites générales : https://vercel.com/docs/limits ; usage équitable : https://vercel.com/docs/limits/fair-use-guidelines
- Optimisation d'images : https://vercel.com/docs/image-optimization/limits-and-pricing
- Vercel Blob : https://vercel.com/docs/vercel-blob/usage-and-pricing
- Deployment Protection : https://vercel.com/docs/deployment-protection
- `vercel deploy` : https://vercel.com/docs/cli/deploy ; retour arrière : https://vercel.com/docs/deployments/rollback-production-deployment
- Cloudflare R2 : https://developers.cloudflare.com/r2/pricing/
- *(lot 14 bis)* `vercel build` : https://vercel.com/docs/cli/build ; Build Output API, services : https://vercel.com/docs/build-output-api/services
- *(lot 14 bis)* R2, accès public (`r2.dev`, domaine personnalisé) : https://developers.cloudflare.com/r2/buckets/public-buckets/ ; clés d'API : https://developers.cloudflare.com/r2/api/tokens/ ; rclone : https://developers.cloudflare.com/r2/examples/rclone/ ; options rclone (`--header-upload`, `--dry-run`, `--transfers`) : https://rclone.org/docs/
