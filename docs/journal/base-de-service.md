### 🗄 Base de service (déploiement, TOK-35)

`scripts/build_serving_db.py` → `data/serving.db`, **9,4 Mo au lieu de 236 Mo**.

L'API n'interroge que 12 des 36 tables : tout ce qu'elle sert est précalculé.
`deck_cards` et ses index pèsent 74% de `yugioh.db` et ne sont jamais lus en
ligne — ils ne servent qu'aux notebooks et à `build_ban_radar.py`. La base de
service est donc transportable avec le déploiement : **pas de volume persistant
à provisionner ni à sauvegarder**, le backend reste en lecture seule pure.

- Le backend lit `YGO_DB_PATH` si la variable est définie, sinon `data/yugioh.db`.
  En production : `YGO_DB_PATH=/app/data/serving.db`.
- Le script embarque une **garde anti-dérive** : il scanne les `FROM`/`JOIN` des
  routeurs et échoue si l'un d'eux référence une table absente de `SERVED_TABLES`.
  Sans ça, un nouvel endpoint partirait en production avec une table manquante et
  ne casserait qu'à la première requête. `--check` la lance sans rien écrire.
- `data/serving.db` n'est pas trackée (`data/*.db`) : elle se régénère.

Conséquence à évaluer avant de provisionner quoi que ce soit : à 9 Mo en lecture
seule, **Railway n'est peut-être plus nécessaire** — l'API pourrait tourner en
fonctions serverless à côté du front, base embarquée. Ça supprimerait la moitié
de TOK-35.
