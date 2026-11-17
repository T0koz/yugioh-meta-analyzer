# Composants d'interaction « smooth » (boutons, pills, onglets, filtres)

Modèle : le plus puissant disponible (Fable, sinon Opus) — règle front. Petit lot, avant le sprint 2 pour que
toutes les pages suivantes en profitent.

**Ressenti voulu (Thomas)** : boutons qui ont l'air physiques — formes arrondies, ombres douces en plusieurs couches,
légère variation de couleur, animation au survol et à l'appui, le tout très fluide.

**À faire** : un seul composant de base décliné en bouton (principal, secondaire, discret), pill de filtre, onglet,
bascule. Rayon généreux ; ombre de contact + ombre diffuse, reflet interne subtil en haut ; survol = légère élévation,
teinte éclaircie ; appui = enfoncement (échelle ~0,97, ombre resserrée) puis retour avec un ressort court ;
transitions 120-200 ms, courbe douce ; focus clavier net ; rien ne bouge avec « réduire les animations ».
Tokens dans la feuille de style existante (palette Braise, tokens `--dur-*`). Remplacer les boutons, pills et
onglets existants du site par ces composants. Documenter dans `docs/design-system.md`.

**Critères** : un seul composant source (pas de styles de bouton dupliqués, vérifié par recherche dans le code) ;
contraste AA sur tous les états ; 0 animation en mouvement réduit ; captures des états (repos, survol, appui, focus,
désactivé) à 3 largeurs ; poids JavaScript inchangé (CSS seul, pas de nouvelle bibliothèque) ; `check.py` vert.
