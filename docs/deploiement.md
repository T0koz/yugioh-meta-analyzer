# Déploiement sur Vercel — guide pas à pas (TOK-35, option A)

Préparé le 2026-11-17 (lot 14), **rien n'est déployé, rien n'est relié**. Décision d'hébergement : Vercel plan gratuit (Hobby)
seul, un projet pour le site et l'API (`docs/decisions/0032-*.md`), projet `gang-5d00/yugi-gang`.
Toutes les commandes `vercel …` sont à lancer **par Thomas**, depuis son terminal ; aucune n'a été exécutée par l'agent.

## 0. À lire d'abord : trois points qui bloquent le premier déploiement

| # | Constat | Conséquence | Qui |
|---|---|---|---|
| 1 | **Le build du front appelle l'API** (pages pré-générées : `/decks/[archetype]`, tier list, etc. ; constaté : sans API sur le port visé, `npm run build` échoue). Or une liaison de service (`BACKEND_URL`) « ne se résout pas pendant les builds » (doc Services, *Bindings*). | Sur Vercel, le build du site ne peut pas interroger l'API du même déploiement : **le build échouera tel quel**. | Un lot de code (§ 8.1) |
| 2 | `lib/api.ts` (côté serveur) et `card-chip.tsx` (côté navigateur) lisent **la même** `NEXT_PUBLIC_API_URL`. Côté serveur il faut une adresse absolue, côté navigateur `/api/v1` suffit. | Impossible de servir les deux avec une seule valeur, surtout derrière la protection Vercel (§ 5). | Même lot (§ 8.1) |
| 3 | Les images de cartes (1,17 Go) ne tiennent ni dans le déploiement ni dans Vercel Blob gratuit (§ 6). | Il faut un stockage à part (recommandé : Cloudflare R2). | Thomas (§ 6) + formulaire § 9 |

Ce qui est prêt : `vercel.json`, `.vercelignore`, `.env.example`, base embarquée en lecture seule, ce guide. Les points 1 et 2 relèvent
du front (`lib/api.ts`, pages), que ce lot n'avait pas le droit de toucher : la modification exacte est décrite au § 8.1.

## 1. Ce qui a été préparé (fichiers)

| Fichier | Rôle |
|---|---|
| `vercel.json` (racine) | Deux **services** : `backend` (FastAPI, `backend/`, point d'entrée `app.main:app`) et `frontend` (Next.js, `frontend/`) ; `/api/*` → API, le reste → site ; liaison privée `BACKEND_URL` du site vers l'API ; la base `backend/data/serving.db` est incluse dans la fonction. |
| `.vercelignore` (racine) | Ce que la CLI **n'envoie pas** (bases complètes, 1,1 Go d'images, notebooks, docs, scripts, `node_modules`, `.env*`). Reste largement sous la limite d'envoi de 100 Mo. |
| `.env.example`, `frontend/.env.example` | Variables documentées, **aucune valeur secrète**. |
| `.gitignore` (+ `backend/data/`) | La copie de la base embarquée ne peut pas être commitée. |
| `backend/app/db.py` | Ouverture de la base en **lecture seule** (`mode=ro`) ; sur Vercel (variable système `VERCEL`), l'API lit seule `backend/data/serving.db`. Sans effet en local. |

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
| `NEXT_PUBLIC_API_URL` | Production, Preview | `/api/v1` | Adresse de l'API vue du **navigateur** (même domaine). Valable côté serveur seulement après le lot du § 8.1. |
| `NEXT_PUBLIC_SITE_URL` | Production | `https://<domaine de production>` (sans barre finale) | Liens canoniques, Open Graph, sitemap (lot 5). Preview : ne rien mettre. |
| `NEXT_PUBLIC_CARD_IMAGES_URL` | Production, Preview | adresse du stockage des images (§ 6) | Sans elle, le site cherche `/card-images/…`, qui n'existe pas en ligne. |
| `BACKEND_URL` | — | **ne pas la créer** | Injectée par Vercel (liaison de service) dans le site. |
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

## 5. Non-diffusion : ce que la protection couvre vraiment

- **Lot 5** : `noindex` + `robots.txt` fermé **seulement en prévisualisation** (`VERCEL_ENV=preview`, `lib/site.ts`). **La production, elle, est indexable.**
- **Protection Vercel gratuite** (doc *Deployment Protection*, relue le 2026-11-17) :
  - *Vercel Authentication* (réservée aux comptes Vercel autorisés de l'équipe) : **gratuite, tous plans**. *Standard Protection* protège tout **sauf** les domaines de production ; **« All Deployments »** protège aussi la production et l'adresse `*.vercel.app`, **tous plans**.
  - *Password Protection* : **payant, indisponible sur Hobby**. Liste d'IP : Enterprise.
- **Recommandation : « All Deployments » + Vercel Authentication.** Le site n'est alors visible que de Thomas et des membres de l'équipe `gang-5d00` connectés. Ni moteur de recherche, ni robots.txt n'y accèdent (tout est derrière la connexion).
  Pour montrer une page à quelqu'un sans compte : lien partageable temporaire (Settings → Deployment Protection → Shareable Links, à relire dans la doc avant usage).
- Réglage : **Settings → Deployment Protection → Vercel Authentication : Enabled, scope « All Deployments »**.
- Attention : un appel du site vers sa **propre adresse publique** est bloqué par cette protection ; c'est la raison de la liaison privée `BACKEND_URL` (qui, elle, saute la protection, doc *Bindings*) et du point 2 du § 0.
- Quand le site sera ouvert au public : passer en *Standard Protection* (ou aucune) et vérifier que `NEXT_PUBLIC_SITE_URL` est renseignée.

## 6. Images de cartes (TOK-92)

État : 14 084 cartes, 3 tailles (`art` 257 Mo / 13 968 fichiers, `card-sm` 190 Mo, `card-lg` 725 Mo), **1,17 Go, 42 136 fichiers**, WebP déjà aux bonnes tailles, hors Git.
`lib/card-images.ts` fabrique toutes les adresses à partir de `NEXT_PUBLIC_CARD_IMAGES_URL` : changer d'hébergement = changer cette variable, aucun code.

| Option | Verdict | Chiffres et sources |
|---|---|---|
| Embarquer dans le déploiement | **Non** | Envoi CLI limité à **100 Mo** (Hobby) ; 1,17 Go dépasse largement (doc *Limits*, « Static file uploads »). |
| **Vercel Blob (gratuit)** | **Non** | Hobby : **1 Go** de stockage (1,17 Go à stocker) et **2 000 opérations avancées** (un envoi = 1 ; il en faut 42 136). Dépassement = **plus d'accès au Blob pendant 30 jours** (doc *Blob usage and pricing*, 2026-09-23). Même en n'envoyant que `art` + `card-sm` (447 Mo, ≈ 28 000 fichiers) : bloqué par les opérations. |
| **Cloudflare R2** | **Recommandé** | Gratuit : **10 Go** de stockage, **1 M d'opérations d'écriture** (Class A), **10 M de lecture** par mois, **sortie gratuite** (doc Cloudflare R2 *Pricing*, relue le 2026-11-17). Largement suffisant (1,17 Go, 42 136 envois). |

Réserves sur R2 (non établies par la documentation lue) : la page de tarifs ne dit pas si une **carte bancaire est exigée à l'ouverture du compte** (à regarder avant de s'inscrire ; cela peut contredire la règle « rien qui engage de l'argent ») ;
l'adresse publique gratuite `r2.dev` est, à ma connaissance, limitée en débit et prévue pour les essais, une adresse sur un **domaine à soi** est la voie normale. À vérifier avec la doc R2 *Public buckets*.
Si ces conditions ne conviennent pas : tout hébergeur d'objets compatible S3 donnant ≥ 2 Go gratuits convient ; seule la variable change.

### Étapes pour Thomas (ne rien faire avant d'avoir coché le formulaire § 9)
1. Créer le compte et un *bucket* (nom suggéré : `yugi-gang-cards`), en lecture publique.
2. Envoyer le dossier `data/card-images/` (sans `_failures.jsonl` ni `_missing.json`) : `rclone` ou l'outil `wrangler r2 object put`, ou le tableau de bord (glisser-déposer : lent à 42 000 fichiers, préférer `rclone sync`). Garder la structure `art/`, `card-sm/`, `card-lg/` et `missing.webp` à la racine si présent.
3. Ajouter l'en-tête de cache `Cache-Control: public, max-age=31536000, immutable` (une illustration de carte ne change pas ; `scripts/download_card_images.py` ajoute seulement les nouvelles).
4. `vercel env add NEXT_PUBLIC_CARD_IMAGES_URL production` (et `preview`) avec l'adresse de base, **sans barre finale**, puis redéployer.
5. Contrôler : `https://<base>/art/<id>.webp` s'ouvre ; le site ne fait aucune requête vers `images.ygoprodeck.com`.
6. Chaque lundi : `python scripts/download_card_images.py` (incrémental) puis renvoyer seulement les nouveaux fichiers (`rclone copy`).

### Optimisation d'images de `next/image` (plan gratuit)
Quotas Hobby par mois : **5 000 transformations**, 300 000 lectures du cache, 100 000 écritures. Au-delà : les **nouvelles** images ne s'optimisent plus et renvoient une erreur **402** (le texte `alt` s'affiche), les déjà optimisées continuent ; **aucune facturation** (doc *Image optimization limits and pricing*, 2026-11-12).
Une liste de décks ou une tier list affiche des centaines de cartes ; avec 3 tailles × plusieurs largeurs, **5 000 transformations s'épuisent vite** (un seul visiteur curieux suffit sur 14 000 cartes).
**Recommandation : désactiver l'optimisation pour les images de cartes** (`unoptimized`), puisqu'elles sont déjà en WebP aux bonnes tailles. L'adresse du stockage les sert directement, sans quota Vercel. Ce changement touche `CardArt` / `next.config.ts` (hors de ce lot) :
décrit au § 8.2.

## 7. Premier déploiement, puis production, puis mise à jour du lundi

Prérequis : §§ 2, 3, 4 faits, **lot de code du § 8.1 fait**. `vercel --version` donne la version installée (la doc exige la CLI ≥ 48.1.8 pour FastAPI).

**Prévisualisation d'abord** (jamais la production en premier : *le premier déploiement d'un nouveau projet est toujours un déploiement de production*, doc `vercel deploy` ; `yugi-gang` n'en a pas encore, donc ce premier essai l'est peut-être. Avec la protection « All Deployments » du § 5 active **avant**, il reste invisible).
```bash
cd ~/code/yugioh-meta-analyzer && git checkout main && git pull --rebase
python scripts/check.py
mkdir -p backend/data && cp data/serving.db backend/data/serving.db
vercel deploy                      # prévisualisation ; affiche une adresse *.vercel.app
vercel curl /api/v1/meta/tier-list --deployment <adresse>     # l'API répond (curl gère la protection)
```
Vérifier : la page d'accueil, `/tier-list`, `/decks`, `/ban`, une image de carte ; dans le tableau de bord, *Runtime Logs* sans erreur « unable to open database ».
Si le build échoue sur « Failed to collect page data » : c'est le point 1 du § 0.

**Production** (après avoir regardé la prévisualisation) :
```bash
vercel deploy --prod
```
Le dépôt GitHub n'étant pas connecté, « production depuis `main` » signifie : se placer sur `main` à jour, lancer `check.py`, puis `vercel deploy --prod` depuis cette copie.

**Mise à jour du lundi** (après `scripts/refresh_all.py`, qui recalcule les tables et reconstruit `data/serving.db`) :
```bash
python scripts/build_serving_db.py --check
cp data/serving.db backend/data/serving.db
python scripts/download_card_images.py      # incrémental ; renvoyer les nouveaux fichiers (§ 6, étape 6)
vercel deploy --prod
```
**Retour arrière** : `vercel rollback` (sans argument : revient au déploiement de production **précédent**). Sur Hobby, on ne peut revenir **qu'au déploiement de production immédiatement précédent** (doc *Rolling back*) ; pour un plus ancien : le redéployer (`vercel redeploy <url>`) ou passer en Pro. Contrôle : `vercel rollback status`.

## 8. Changements à planifier dans un lot suivant (non faits ici)

### 8.1 Rendre le build indépendant de l'API et séparer les deux adresses (bloquant)
- `frontend/src/lib/api.ts` (serveur) : lire, dans l'ordre, `API_URL` (build local ou adresse choisie), puis `BACKEND_URL` + `/api/v1` (Vercel, à l'exécution), puis `NEXT_PUBLIC_API_URL`. `card-chip.tsx` (navigateur) garde `NEXT_PUBLIC_API_URL=/api/v1`.
- Le build ne pouvant pas joindre l'API sur Vercel, deux voies à départager au premier essai :
  1. **Pages dynamiques ou à génération à la demande** (pas de `generateStaticParams` ni de fetch au build), l'API étant interrogée à l'exécution par `BACKEND_URL` ; c'est la voie propre, mais elle change des pages (lots 11 et 12 y travaillent) ;
  2. **Build local puis envoi du résultat** : API locale lancée sur `data/serving.db`, `API_URL=http://localhost:8000/api/v1 vercel build`, puis `vercel deploy --prebuilt` ; les données du site sont alors figées au build (cohérent avec une mise à jour hebdomadaire). **Non vérifié** que `vercel build` gère les Services (à essayer en prévisualisation).
- À vérifier aussi à l'essai : le service FastAPI reçoit le chemin d'origine (`/api/v1/…`), conformément à la doc *Services routing* ; les routes existent déjà sous `/api/v1`, aucune réécriture de chemin n'est donc prévue.

### 8.2 Images de cartes sans optimisation
Dans `CardArt` (ou globalement `images: { unoptimized: true }` dans `next.config.ts`) : ne pas passer les images de cartes par `/_next/image` (§ 6). `lib/card-images.ts` n'a **pas** à changer.

### 8.3 Autres suites
`context.md` : « adresse du stockage définitif » (TOK-35 / TOK-92) se règle avec `NEXT_PUBLIC_CARD_IMAGES_URL` ; `scripts/check.py` ne connaît pas Vercel (un contrôle « `vercel.json` valide » pourrait s'ajouter).

## 9. Formulaire à copier-coller (décisions de Thomas)

**A. Stockage définitif des images de cartes**
- [x] Cloudflare R2 (10 Go gratuits, 1 M d'écritures, sortie gratuite) — *recommandé*, sous réserve du point carte bancaire à vérifier
- [ ] Autre hébergeur d'objets gratuit (précise lequel) : …
- [ ] Ne pas héberger : laisser les images cassées en ligne pour l'instant
- Commentaire libre : …

**B. Protection de l'adresse**
- [x] « All Deployments » + Vercel Authentication (visible seulement par les comptes de l'équipe) — *recommandé*
- [ ] Standard Protection (production publique, indexable) — à ne prendre qu'à l'ouverture du site
- [ ] Aucune protection
- Commentaire libre : …

**C. Voie du build (§ 8.1)**
- [x] Voie 2 d'abord (build local + `--prebuilt`), à tenter en prévisualisation ; voie 1 si elle ne fonctionne pas — *recommandé : change le moins de code, données figées chaque lundi*
- [ ] Voie 1 directement (pages dynamiques)
- Commentaire libre : …

## 10. Rappels

- **Plan gratuit (Hobby) = usage personnel, non commercial.** Les pages de documentation lues ne reprennent pas la formulation exacte : la relire dans les conditions d'utilisation de Vercel (section *Fair use*) avant toute offre payante. Le projet vise la vente aux boutiques (150 €/mois) : à ce moment-là, le plan Pro est nécessaire (et l'adresse sera diffusée).
- Quotas Hobby utiles (doc *Fair use guidelines*) : 100 Go de transfert rapide, 1 M d'invocations de fonctions, 4 h de CPU actif, par mois ; 100 déploiements par jour ; durée maximale d'une fonction 300 s (réglée à 30 s dans `vercel.json`) ; mémoire 2 Go ; corps de réponse 4,5 Mo.
- Jamais de `.env`, de base ou de jeton dans Git (dépôt public) ; `frontend/.env.local` (jeton OIDC de la CLI) reste ignoré.

## Points non vérifiés (à lever au premier essai)
- Comportement exact de la CLI vis-à-vis de `.gitignore` quand un `.vercelignore` existe (la page de documentation consultée a répondu 404) ; garde-fou : la vérification de `vercel inspect` du § 3.
- Prise en charge de `vercel build` + `--prebuilt` avec les Services ; poids des fichiers de la fonction (`includeFiles` dans un service Python).
- Conditions d'ouverture d'un compte Cloudflare R2 (carte bancaire) et limites de `r2.dev`.
- Comportement des Services (bêta) en prévisualisation avec la protection activée.

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
