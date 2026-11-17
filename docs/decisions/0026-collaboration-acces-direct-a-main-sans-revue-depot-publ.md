# 0026 — Collaboration : accès direct à main sans revue, dépôt public, garde-fous par outillage

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Thomas
- Tickets : TOK-107, TOK-78

## Contexte
Une collaboratrice data scientist rejoint le projet et pousse directement sur `main`, sans revue, sur un dépôt public.

## Options
- A : pull requests obligatoires
- B : accès direct + garde-fous (non bloquants)

## Décision
Accès direct à `main` sans revue (choix de Thomas), compensé par `scripts/check.py` avant tout push, un hook pre-push optionnel et une CI GitHub gratuite qui ne bloque rien.

## Raison
Choix de Thomas (`avis-stack.md` : « c'est un choix de Thomas »). La CI et le hook rattrapent l'essentiel sans ralentir. Perdu : aucune relecture ; une erreur poussée est publique tout de suite.

## Conséquences
À reconsidérer si une erreur passe en production. Protection de `main` (interdire force-push et suppression) à poser par Thomas (TOK-108). Jamais d'identifiants, de `.env` ni de base dans un commit (dépôt public).

## Sources
- `docs/collaboration/avis-stack.md` (« Ce qu'il ne faut pas changer »)
- `docs/journal/collaboration.md`
- `CLAUDE.md`
