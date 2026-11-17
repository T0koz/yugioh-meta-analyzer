# TOK-92 — Images de cartes hébergées par nous (2026-11-17)

- `scripts/download_card_images.py` : télécharge chaque carte une fois (carte entière + illustration), contrôle
  que ce sont des images (type, 3 Mo, 4 Mpx, format JPEG/PNG/WEBP), écrit 3 tailles en WebP dans `data/card-images/`
  (dossier ignoré, dépôt principal) : `card-lg` 421 px, `card-sm` 168 px, `art` 256 px carré.
  Reprenable : un id est sauté si ses fichiers existent ; les 404 sont notés dans `_missing.json` (`--retry-missing`),
  les échecs dans `_failures.jsonl`. ≤ 15 requêtes/s, `User-Agent` générique.
- Mesuré : 14 084 cartes, 28 068 requêtes en 1 902 s (14,8/s), 0 échec, 1,1 Go (art 257 Mo, card-sm 190 Mo,
  card-lg 725 Mo). 116 cartes n'ont pas d'illustration recadrée chez la source (404) : repli en initiales pour
  `CardArt`, image cassée possible ailleurs (lignes de tier list, pages d'archétype/deck). Second lancement : 0 téléchargement.
- Front : `lib/card-images.ts` est le seul fichier qui connaît les URL ; l'API sert encore l'URL d'origine
  (on n'en garde que l'identifiant). `NEXT_PUBLIC_CARD_IMAGES_URL` (défaut `/card-images`), route locale
  `app/card-images/[...path]/route.ts` lisant `CARD_IMAGES_DIR` (défaut `../data/card-images`). `SafeImage`
  (client) donne le repli. `remotePatterns` ne contient plus YGOPRODeck.
- `cards` : `fetch_cards.py` n'écrit qu'un JSON ; le rafraîchissement complet est `init_db.py` (`INSERT OR REPLACE`,
  écrase `views_week`), donc non ajouté à la chaîne. `fetch_new_cards.py` (garde de nom, ne supprime rien) l'est,
  en première étape de `refresh_all.py`. Essai à blanc : 0 nouvelle carte, 0 nom à corriger, 14 084 lignes avant/après,
  noms corrigés par la session combos intacts (rien écrit). Cartes du Ban Radar sans ligne dans `cards` : 10 sur 966
  (le brief en annonçait 22) ; aucune n'est gagnée : l'API TCG ne les connaît pas (cartes OCG).
- Mesure Playwright (build de production, accueil, tier-list, ban, boutique, decks, fiche deck, archétype,
  early-signals, graphe ; 1280 et 390 px) : 0 requête vers images.ygoprodeck.com côté navigateur, 0 côté serveur
  (Node espionné), 587 images servies en 200, 0 image cassée.
- Reste pour TOK-35 : choisir le stockage (Vercel Blob ou autre), y envoyer `data/card-images/`, renseigner
  `NEXT_PUBLIC_CARD_IMAGES_URL` ; la route locale devient inutile en production.
