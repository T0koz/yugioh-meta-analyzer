# 11 — TOK-35 : préparation du déploiement sur Vercel (rien d'irréversible)

Modèle : Sonnet. Sous-agent autorisé : `gardien-donnees` (base de service). Réponds en français.
**Interdits** : aucun déploiement (`vercel`, `vercel deploy`, `vercel --prod`), aucune connexion du dépôt GitHub au
projet Vercel, aucun compte créé, aucun secret dans un fichier suivi (dépôt public), pas de push. Tout ce qui
demande les identifiants de Thomas va dans le guide.

## Décisions déjà prises (16/11)
- **Vercel seul, plan gratuit** (pas de Railway). Adresse non diffusée.
- **Option A** : un seul projet Vercel qui sert le front Next.js 16 (`frontend/`) ET l'API FastAPI (`backend/`)
  en fonction Python serverless. On ne déplace pas `backend/`.
- Projet déjà créé et lié par Thomas : **`gang-5d00/yugi-gang`**, lié depuis `frontend/`
  (`frontend/.vercel/project.json`, ignoré par git), sans connexion Git. La CLI a écrit `frontend/.env.local`
  (`VERCEL_OIDC_TOKEN`, ignoré par git) : ne jamais le lire à voix haute, le copier ni le commiter.

## À faire
1. **Lire la documentation Vercel à jour** (WebFetch) : FastAPI / fonctions Python, racine de projet (Root
   Directory), monorepo avec Next.js + Python, `vercel.json`, limites de taille des fonctions, fichiers envoyés par
   la CLI (`.vercelignore` / `.gitignore`), Deployment Protection et optimisation d'images sur le plan gratuit.
   Citer les pages dans le guide.
2. **Configuration de l'option A** : déterminer comment le projet `yugi-gang` doit être réglé (racine = dépôt entier
   ou autre montage recommandé par la doc), écrire `vercel.json` et le point d'entrée Python de l'API, sans casser
   le lancement local (`uvicorn`, `npm run dev`) ni `scripts/check.py`. Si le lien doit passer de `frontend/` à la
   racine, l'écrire comme étape pour Thomas (ne pas relier soi-même).
3. **`serving.db` (10,7 Mo, hors git)** : choisir et documenter comment elle arrive dans la fonction (embarquée au
   déploiement depuis la machine de Thomas, ou Vercel Blob téléchargée au démarrage) ; ouverture en lecture seule
   (`mode=ro` ou copie dans `/tmp`). Vérifier qu'elle ne finit jamais dans git.
4. **Variables d'environnement** : `NEXT_PUBLIC_API_URL`, `YGO_DB_PATH`, et toute autre nécessaire, documentées
   dans `.env.example` (sans valeur secrète) ; ajout par Thomas avec `vercel env add`.
5. **Non-diffusion** : `noindex` (robots / en-tête) ; dire ce que la protection Vercel couvre réellement sur le plan
   gratuit.
6. **Images (TOK-92)** : état après le lot 8 ; risque de hotlinking et quotas d'optimisation d'images.
7. **Guide `docs/deploiement.md`** : pas à pas pour Thomas — réglages du projet, variables, premier déploiement de
   prévisualisation (`vercel`), puis production (`vercel --prod`) depuis `main`, mise à jour du lundi, retour arrière,
   et rappel : plan gratuit = usage non commercial.

**Critères** : configuration présente, lancement local intact, `check.py` vert ; guide suivable sans connaissance
préalable, sources citées ; aucun secret dans un fichier suivi ; aucune commande de déploiement exécutée.
