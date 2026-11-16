# 03 — TOK-99 : dataviz maison (D3) et palette de données

Modèle : Sonnet. Décisions déjà prises (audit) : 6 (un bleu pour l'OCG, palette de 6 teintes), 8 (SVG maison + D3).

**À faire** : `/evolution` et `/predictions` en SVG avec D3 ; recharts supprimé ; palette documentée dans
`docs/design-system.md` ; pied de données (source + date) sous chaque visualisation et tableau.

**Critères** : recharts absent de `package.json` et du build ; JavaScript de `/evolution` ≤ 200 ko transférés ;
contrastes AA sur la palette (script d'audit du projet) ; 100 % des graphiques et tableaux avec source + date ;
les courbes gardent les axes ajustés de TOK-96 ; accessible au clavier, alternative tabulaire.
Le graphe de synergies (vis-network) n'est PAS dans ce ticket.
