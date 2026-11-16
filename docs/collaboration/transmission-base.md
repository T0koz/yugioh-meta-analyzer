# Transmettre la base à la collaboratrice (TOK-109)

> Court terme, en attendant une éventuelle base hébergée (voir [`base-hebergee.md`](base-hebergee.md)).
> **Jamais par Git** : le dépôt est public. C'est Thomas qui envoie.

## Ce qu'il y a dans la base, et pourquoi c'est privé

`data/yugioh.db` (~270 Mo) contient :

- des données **récupérées chez des tiers** (yugiohmeta, Yugipedia, YGOPRODeck) : on peut les
  utiliser, pas les republier ;
- **≈ 15 000 pseudos de joueurs** (`tournament_decks.author`) : c'est une **donnée personnelle**
  au sens du RGPD. Aucune analyse ne la lit (seuls les scripts de fetch l'écrivent), d'où l'option
  `--sans-auteurs` ci-dessous.

`data/serving.db` (~10 Mo) suffit pour lancer l'API et le site, **pas** pour les notebooks ni
pour `build_ban_radar.py` (il n'y a pas `deck_cards`). Elle ne contient aucun pseudo.

## Méthode recommandée : Google Drive, partage nominatif

1. **Préparer la copie** (Thomas, 10 secondes) :

   ```bash
   python scripts/export_db_snapshot.py --sans-auteurs
   ```

   Produit sur le Bureau `yugioh-AAAA-MM-JJ.db.gz` (~51 Mo) et `yugioh-AAAA-MM-JJ.json` (date du
   dernier tournoi, dernière banlist, empreinte SHA-256). La base source est ouverte en lecture
   seule ; la copie est faite par `VACUUM INTO`, qui reste cohérente même si le job du lundi
   écrit au même moment (un simple `cp` ne l'est pas).

2. **Déposer les deux fichiers** dans un dossier Drive `yugioh-base` et le **partager avec son
   adresse Google uniquement**, en lecture. Ne **pas** activer « Tous les utilisateurs disposant
   du lien ».

3. **Elle installe** la copie :

   ```bash
   cd yugioh-meta-analyzer
   shasum -a 256 ~/Downloads/yugioh-AAAA-MM-JJ.db.gz   # doit égaler "sha256" du .json
   gunzip -c ~/Downloads/yugioh-AAAA-MM-JJ.db.gz > data/yugioh.db
   python scripts/build_serving_db.py                   # régénère serving.db pour l'API
   python scripts/check.py --all                        # tout doit être vert
   ```

### Pourquoi celle-ci

| Option | Privé | Effort | Pour |
|---|---|---|---|
| **Drive, partage nominatif** *(recommandée)* | ✅ accès lié à son compte Google | faible | Un compte Google suffit ; on peut retirer l'accès ; les mises à jour remplacent le fichier au même endroit |
| AirDrop / clé USB, en personne | ✅ aucun intermédiaire | nul | Parfait pour la première fois si vous vous voyez ; pas pour les mises à jour |
| WeTransfer et équivalents | ⚠ quiconque a le lien | faible | À éviter : le lien circule dans un e-mail |
| Serveur dédié (SFTP) | ✅ | élevé | Démesuré pour 50 Mo par semaine |
| Git LFS / release GitHub | ❌ **public** | — | Exclu : le dépôt est public |

Chiffrer l'archive (zip à mot de passe, 7-Zip) n'apporte pas grand-chose de plus qu'un partage
nominatif, et le mot de passe devrait transiter par un autre canal. À reconsidérer seulement si
la copie doit passer par un canal non nominatif.

## De quand date sa copie, et comment la mettre à jour

- **La date est dans le `.json`** livré avec la copie (`dernier_tournoi_tcg`, `derniere_banlist`).
  Pour la retrouver plus tard : `sqlite3 data/yugioh.db "SELECT MAX(created) FROM tournament_decks"`.
- **Les deux copies divergent dès qu'un recalcul a lieu.** Le job du lundi (8 h 30, sur le Mac de
  Thomas) récupère les nouveaux decks et recalcule tout : sa copie à elle est périmée dès le lundi
  suivant.
- **Mise à jour** : Thomas relance `export_db_snapshot.py` après le job du lundi et remplace les
  deux fichiers dans le dossier Drive ; elle refait l'étape 3. Rythme suggéré : à la demande, ou
  chaque lundi si elle travaille sur des chiffres récents.
- Elle peut aussi rafraîchir elle-même (`scripts/refresh_decks.py` puis `scripts/refresh_all.py`),
  mais elle obtiendra alors des chiffres légèrement différents de ceux de Thomas (decks
  soumis entre-temps, horaire différent). **La référence reste la base de Thomas.**

## Règle qui en découle

Sa base locale est un **bac à sable** : elle peut tout y recalculer, tout y casser. Ce qui devient
officiel passe par le **code** (un script ou un notebook commité), que le job du lundi rejoue sur la
base de référence. On ne s'échange jamais de tables recalculées à la main.
