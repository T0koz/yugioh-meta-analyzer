# 0028 — Transmission de la base à la collaboratrice : Drive nominatif, sans pseudos

- Date : 2026-11-16
- Statut : acceptée
- Décidé par : Claude (méthode recommandée) ; envoi par Thomas
- Tickets : TOK-109

## Contexte
`yugioh.db` (~270 Mo) contient des données de tiers et ≈ 15 000 pseudos de joueurs (donnée personnelle). Le dépôt est public : la base ne peut pas passer par Git.

## Options
- Google Drive en partage nominatif (recommandée)
- AirDrop / clé USB (première fois seulement)
- WeTransfer (à éviter : lien qui circule)
- SFTP (démesuré)
- Git LFS / release GitHub (exclu : public)

## Décision
Drive, partage nominatif en lecture, via `scripts/export_db_snapshot.py --sans-auteurs` (~51 Mo, avec un `.json` contenant dates et SHA-256).

## Raison
Aucune analyse ne lit `tournament_decks.author` ; un partage nominatif suffit et peut être retiré. Chiffrer l'archive n'apporte pas grand-chose de plus.

## Conséquences
Sa copie est périmée dès le lundi suivant ; mise à jour à la demande. L'envoi reste à faire par Thomas (`BACKLOG.md`, TOK-109).

## Sources
- `docs/collaboration/transmission-base.md`
