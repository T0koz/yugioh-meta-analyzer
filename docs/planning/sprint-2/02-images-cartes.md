# 02 — TOK-92 : images de cartes hébergées + `cards` à jour

Modèle : Sonnet. Sous-agent autorisé : `gardien-donnees`.

**À faire**
1. Rafraîchir `cards` : ajouter `fetch_cards.py` (et `fetch_new_cards.py`) à la chaîne du lundi. Vérifier que le
   nom de carte corrigé par la session combos n'est pas écrasé (le noter dans le compte rendu). Mesurer combien des
   22 cartes du radar sans image en ont une après.
2. Télécharger chaque image une seule fois (~14 000, ≤ 20 requêtes/s avec pause), puis seulement les nouvelles
   cartes. Stockage **hors git** (dossier ignoré), URL de base configurable par variable d'environnement ;
   `lib/card-images.ts` reste le seul fichier qui connaît la forme des URL. La destination finale (Vercel Blob ou
   autre) se décidera avec TOK-35 : ne rien héberger à l'extérieur.
3. Trois tailles pré-générées (décision 7 de l'audit).

**Critères** : 0 requête vers `images.ygoprodeck.com` depuis le serveur et le navigateur (mesure Playwright) ;
aucune image dans un commit ; un second lancement ne télécharge rien ; `check.py` vert.
