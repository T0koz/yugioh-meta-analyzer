# 05 — TOK-100 : SEO de partage et tests visuels (EN DERNIER)

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front. À lancer après 02, 03, 04 : les images de référence reflètent l'interface finale.

**À faire** : Open Graph + images de partage (sans reproduire d'illustration de carte protégée au-delà de ce que
le site affiche déjà), sitemap, robots ; suite Playwright de tests visuels sur 9+ pages × 3 largeurs, avec seuil de
tolérance documenté, lancée par une commande unique ; documenter dans `docs/`.

**Critères** : Lighthouse SEO = 100 sur les pages publiques ; aperçu de lien valide (balises vérifiées par script) ;
suite verte, et un changement de style volontaire produit un diff d'images (preuve fournie) ; intégrée à
`scripts/check.py` ou documentée comme étape manuelle si trop lente.
