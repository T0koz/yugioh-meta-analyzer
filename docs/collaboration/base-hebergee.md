# Base de données hébergée : comparaison (TOK-110)

> Note de comparaison, **aucune migration**. Rédigée le 2026-11-16. Les tarifs viennent des pages
> publiques à cette date et changent souvent : les revérifier au moment de choisir.

## Le vrai problème à résoudre

Le ticket part de : « deux copies de SQLite qui divergent ». Mais regardons **qui écrit quoi** :

| Données | Écrites par | Reproductibles ? |
|---|---|---|
| Brutes (`tournament_decks`, `deck_cards`, `banlist_history`, `cards`, prix) | Le job du lundi + le snapshot quotidien des prix, **sur le Mac de Thomas** | **Non** pour les prix (un snapshot manqué est perdu) ; à peu près pour les decks (l'API yugiohmeta peut disparaître) |
| Dérivées (scores, prédictions, Ban Radar, graphe…) | `refresh_all.py`, à partir des brutes | **Oui** : c'est du code versionné, rejoué chaque lundi |
| Journal des prédictions | `log_predictions.py` → `data/prediction_log.jsonl` (versionné) | Non : c'est une preuve datée |

Conséquence : **il n'y a qu'un écrivain légitime** (le job du lundi). Les tables dérivées n'ont pas
besoin d'être partagées : elles se recalculent depuis le code. Ce qu'il faut partager, c'est **une
copie de référence des données brutes**, en lecture. Deux personnes qui écrivent en même temps dans
la même base, c'est justement ce qu'on veut éviter (un recalcul expérimental écraserait la table que
sert le site).

Une base hébergée devient vraiment utile quand : (1) le job du lundi quitte le Mac de Thomas
(TOK-35, TOK-111) ; (2) plusieurs personnes doivent écrire des données brutes ; (3) l'API B2B doit
écrire en ligne (comptes, clés d'API, TOK-67). Aucun des trois n'est vrai aujourd'hui.

## Contraintes du projet

- **270 Mo** dont 74 % pour `deck_cards` (850 000 lignes) ; la base de service ne fait que 10 Mo.
- **SQLite partout** : 60 appels `sqlite3.connect` (scripts, notebooks, backend), 14 notebooks,
  ~20 constructions propres à SQLite (`INSERT OR REPLACE`, `PRAGMA`, triggers append-only du journal,
  l'astuce `= +col` pour l'index d'expression de TOK-83…).
- **Privé obligatoire** : données de tiers + ≈ 15 000 pseudos de joueurs (donnée personnelle).
- **Coût zéro** et **aucun identifiant dans Git** (dépôt public) : tout passe par un `.env`, désormais
  exclu par `.gitignore`.

## Les options

| | A. Copie de référence partagée *(recommandée)* | B. Fichier SQLite sur stockage objet (R2, B2) | C. Turso (SQLite hébergé, libSQL) | D. Postgres managé (Neon, Supabase) |
|---|---|---|---|---|
| **Principe** | Le job du lundi exporte un instantané (`export_db_snapshot.py`) dans un dossier Drive partagé avec elle | Même chose, mais dans un « bucket » privé, téléchargé par script | Vraie base distante, compatible SQLite, avec réplique locale synchronisée | Vraie base distante, autre moteur |
| **Coût** | 0 € | 0 € sous 10 Go (R2), sortie gratuite ; moyen de paiement probablement demandé à l’ouverture (à vérifier) | 0 € : 5 Go, 500 M lignes lues/mois, 10 M lignes écrites/mois | Neon : 0 €, 1 Go ; Supabase : 0 €, 500 Mo (**trop petit**), pause après 1 semaine sans activité |
| **Effort de migration** | ~1 h : une étape en fin de job | ~½ jour : script d'envoi + script de récupération | **Plusieurs jours** : remplacer `sqlite3` par le client libSQL dans 60 endroits, revoir les notebooks | **1 à 2 semaines** : dialecte SQL, types, triggers, `to_sql`, index d'expression, tous les notebooks |
| **Scripts et notebooks existants** | Inchangés | Inchangés | À adapter (client différent ; la réplique locale reste un fichier SQLite) | À réécrire en partie |
| **Confidentialité** | Partage nominatif Google | Bucket privé + clés d'accès dans `.env` | Jeton d'accès dans `.env` | Mot de passe dans `.env`, rôles lecture seule possibles |
| **Écritures concurrentes** | Impossible par construction (c'est voulu) | Idem | Possible | Possible, et c'est son point fort |
| **Sauvegardes** | Historique de versions Drive + les `backup_*.db` locaux | Versionnage du bucket | Restauration à un instant donné : 1 jour en gratuit (selon les sources) | Neon : historique court ; Supabase : pas en gratuit |
| **Job du lundi** | + 1 étape (export) | + 1 étape (export + envoi) | Il écrit dans Turso au lieu du fichier local : **à la limite du quota** de 10 M lignes écrites/mois : le fetch réécrit chaque lundi les ~850 000 lignes de `deck_cards` (suppression + insertion ≈ 1,7 M écritures), soit ≈ 7 M par mois avant même les prix et les tables dérivées | Il écrit dans Postgres ; le volume dépasse probablement 500 Mo une fois indexé |
| **Dépendance** | Google | Cloudflare / Backblaze | Turso (annonce de rapprochement avec Supabase en 2026 : avenir du gratuit incertain) | Neon / Supabase |

### Pourquoi pas tout de suite C ou D

- **Turso** est le plus naturel techniquement (même dialecte), mais le quota d'écritures gratuit est
  presque entièrement consommé par le fetch hebdomadaire complet, et l'offre gratuite est mouvante. À revoir si le
  pipeline devient incrémental.
- **Postgres** est la bonne cible **le jour où le produit devient un service B2B** avec des comptes et
  des écritures en ligne. Pas avant : le coût de migration est élevé et n'apporte rien au travail
  d'analyse, qui est mono-écrivain.

## Recommandation

1. **Maintenant : option A.** Le job du lundi, après `build_serving_db.py`, exporte un instantané
   dans le dossier Drive partagé (aujourd'hui à la main, cf. [`transmission-base.md`](transmission-base.md)).
   Elle travaille sur sa copie comme bac à sable ; tout ce qui devient officiel passe par du code
   commité.
2. **Si le job quitte le Mac** (déploiement TOK-35, ou machine toujours allumée) : passer à **B**,
   qui s'automatise sans compte Google sur un serveur.
3. **Quand le produit B2B a besoin d'écrire en ligne** : réévaluer **D (Neon)** pour la partie service
   uniquement (comptes, clés d'API), en gardant SQLite pour l'analyse. Ce n'est pas l'un ou l'autre.

## Si on va plus loin un jour : règles déjà posées

- Identifiants dans `.env` (exclu de Git depuis ce chantier), un `.env.example` sans valeurs commité.
- `scripts/check.py` refuse un push contenant un `.env` ou une URL de base avec mot de passe ; la
  protection de push de GitHub (activée sur le dépôt) bloque en plus les clés des grands fournisseurs.
- Une base hébergée est **privée** : jamais d'accès public, même en lecture.
- Envisager de ne pas y mettre `tournament_decks.author` (aucune analyse ne le lit).

## Sources (tarifs au 2026-11-16)

- Turso : [turso.tech/pricing](https://turso.tech/pricing), [costbench.com](https://costbench.com/software/database-as-service/turso/free-plan)
- Neon : [neon.com — free tier](https://neon.com/faqs/managed-postgres-databases-free-tier)
- Supabase : [activepieces.com — limites du gratuit](https://www.activepieces.com/blog/supabase-pricing-free-tier-limits-pro-costs-egress)
- Cloudflare R2 : [developers.cloudflare.com/r2/pricing](https://developers.cloudflare.com/r2/pricing/index.md)
