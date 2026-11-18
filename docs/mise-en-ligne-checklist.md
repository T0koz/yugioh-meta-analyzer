# Mise en ligne — check-list à cocher (release v2026.11.18)

Version courte de `docs/deploiement.md`, à suivre dans l'ordre, dans ton terminal. Durée estimée : environ 1 h, dont
≈ 30 min d'envoi des images. Rien de cette liste ne peut être fait par un agent (tes comptes, tes clés).
Une case = une commande ou un écran. En cas d'écart, le paragraphe du guide est indiqué entre crochets.

## A. Pousser la release (5 min)
- [ ] `cd ~/code/yugioh-meta-analyzer && git checkout main`
- [ ] `python scripts/check.py` → « Tout est bon »
- [ ] `git push origin main --follow-tags` (pousse aussi le tag `v2026.11.18`)
- [ ] `git checkout claude/moteur-18-11` (la branche de travail des sessions)

## B. Relier le projet Vercel depuis la racine (5 min) [§ 2]
- [ ] `vercel link --project yugi-gang --scope gang-5d00`
- [ ] Tableau de bord → projet `yugi-gang` → Settings → General : **Root Directory vide**, **Framework Preset : Services**
- [ ] Settings → Git : **ne pas** connecter GitHub

## C. Images sur Cloudflare R2 (≈ 40 min) [§ 6]
- [ ] Cloudflare → R2 Object Storage → activer (lire l'écran : une carte bancaire peut être demandée)
- [ ] Create bucket `yugi-gang-cards`
- [ ] Bucket → Settings → Public Development URL → Enable (taper `allow`) ; noter l'adresse `https://pub-….r2.dev`
- [ ] R2 → Manage API Tokens → Create, permission **Object Read & Write** limitée à `yugi-gang-cards` ; ranger les deux clés dans ton gestionnaire de mots de passe
- [ ] `brew install rclone && rclone config` : remote `r2`, *Amazon S3 compliant* → *Cloudflare R2*, les deux clés, point d'accès `https://<id du compte>.r2.cloudflarestorage.com`, `no_check_bucket = true`
- [ ] Essai à blanc :
  ```bash
  rclone copy data/card-images r2:yugi-gang-cards --exclude "_*" --header-upload "Cache-Control: public, max-age=31536000, immutable" --transfers 16 --dry-run
  ```
- [ ] Envoi réel (même commande avec `--progress` à la place de `--dry-run`)
- [ ] `curl -I https://pub-….r2.dev/art/89392810.webp` → `200`, `content-type: image/webp`

## D. Variables (5 min) [§ 4]
Chaque commande demande la valeur (elle n'apparaît pas dans l'historique).
- [ ] `vercel env add NEXT_PUBLIC_API_URL production` → `/api/v1`
- [ ] `vercel env add NEXT_PUBLIC_API_URL preview` → `/api/v1`
- [ ] `vercel env add NEXT_PUBLIC_CARD_IMAGES_URL production` → l'adresse `https://pub-….r2.dev` (sans barre finale)
- [ ] `vercel env add NEXT_PUBLIC_CARD_IMAGES_URL preview` → la même
- [ ] `vercel env add NEXT_PUBLIC_SITE_URL production` → l'adresse de production (`https://yugi-gang.vercel.app` ou ton domaine, sans barre finale)
- [ ] Ne **jamais** créer `API_URL`, `BACKEND_URL` ni `YGO_DB_PATH` sur Vercel
- [ ] `vercel env ls` → les 5 lignes ci-dessus

## E. Prévisualisation (10 min) [§ 7.2]
- [ ] Terminal 2 : `cd backend && YGO_DB_PATH=../data/serving.db ../.venv/bin/uvicorn app.main:app --port 8000`
- [ ] Terminal 1 : `python scripts/deploy_prebuilt.py` → tout en ✓
- [ ] `python scripts/deploy_prebuilt.py --execute preview` → noter l'adresse du déploiement
- [ ] **Envoie-moi cette adresse** : je vérifie les pages, les images (aucune vers `images.ygoprodeck.com`), l'API et la console

## F. Production (5 min) [§ 7.3]
- [ ] Après mon retour sur la prévisualisation : `python scripts/deploy_prebuilt.py --execute prod`
- [ ] En cas de problème : tableau de bord → Deployments → déploiement précédent → *Promote* (retour arrière, seul le précédent sur Hobby)

## Chaque lundi ensuite
- [ ] Le job tourne ; puis `python scripts/download_card_images.py` et la même commande `rclone copy` (seuls les fichiers nouveaux partent)
- [ ] API sur `serving.db`, puis `python scripts/deploy_prebuilt.py --execute prod` (la base embarquée part avec le déploiement)
