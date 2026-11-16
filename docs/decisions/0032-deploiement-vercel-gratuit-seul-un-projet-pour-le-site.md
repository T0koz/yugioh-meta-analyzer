# 0032 — Déploiement : Vercel gratuit seul, un projet pour le site et l'API (option A, projet yugi-gang)

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas (conversation du 2026-11-16 avec l'orchestrateur)
- Tickets : TOK-35

## Contexte
Hébergement à trancher : Vercel seul, ou Vercel + Railway (`BACKLOG.md`). La base de service pèse ≈ 10 Mo, donc l'API peut tourner en serverless à côté du front.

## Options
- Vercel seul
- Vercel (front) + Railway (API)
- Dans Vercel : option A, un seul projet pour front et API ; autre option non consignée

## Décision
Vercel, plan gratuit ; un seul projet servant le front Next.js 16 (`frontend/`) et l'API FastAPI (`backend/`) en fonction Python serverless. Projet `yugi-gang` créé et lié sous l'équipe `gang-5d00`, sans connexion au dépôt GitHub, rien en ligne ; déploiement depuis `main` après la relecture de Thomas.

## Raison
Raison de l'option A non consignée au-delà de la base de service légère (`BACKLOG.md`). Plan gratuit = usage non commercial (rappel du brief) ; adresse non diffusée.

## Conséquences
Préparation sans déploiement dans le lot 14 (`docs/deploiement.md`, `vercel.json`). Ticket Linear TOK-35 non consulté (connecteur indisponible). `NEXT_PUBLIC_SITE_URL` et les aperçus `noindex` en dépendent.

## Sources
- Conversation du 16/11 avec l'orchestrateur (confirmation de Thomas)
- `docs/planning/sprint-3/11-deploiement.md`
- `BACKLOG.md` (TOK-35)
