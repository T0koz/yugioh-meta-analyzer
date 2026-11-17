"""Génère docs/moteur-combos/formulaire-juge.gs (Google Apps Script) depuis dossier-juge.md.

Usage : python scripts/build_judge_form.py   (lecture seule sur le dossier, aucune base touchée)
"""
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
src = (root / "docs/moteur-combos/dossier-juge.md").read_text(encoding="utf-8")
deck = json.loads((root / "docs/moteur-combos/deck-branded-source.json").read_text(encoding="utf-8"))


def plain(text: str) -> str:
    """Google Forms n'affiche pas le Markdown : on retire gras et accents graves."""
    text = text.replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


judge = src[src.index("## Pour le juge"):]
parts = re.split(r"^## ", judge, flags=re.M)
sections = []
for part in parts:
    if not part.startswith("Partie 1") and not part.startswith("Partie 2"):
        continue
    title = part.splitlines()[0].strip()
    questions = []
    for block in re.split(r"^### ", part, flags=re.M)[1:]:
        rid = block.splitlines()[0].strip()
        m = re.search(r"\*\*Question\.\*\*(.*?)\*\*Lecture supposée\.\*\*(.*?)```", block, flags=re.S)
        if not m:
            raise SystemExit(f"Question illisible : {rid}")
        questions.append({"id": rid, "question": plain(m.group(1)), "lecture": plain(m.group(2))})
    sections.append({"title": title, "questions": questions})

p3 = next(p for p in parts if p.startswith("Partie 3"))
body = p3.split("```")[0]
open_qs = [plain(q) for q in re.split(r"^\d+\.\s", body, flags=re.M)[1:]]

total = sum(len(s["questions"]) for s in sections)
assert total == 34, total
assert [len(s["questions"]) for s in sections] == [12, 22], sections
assert len(open_qs) == 4, open_qs
ids = [q["id"] for s in sections for q in s["questions"]]
assert len(set(ids)) == 34


def zone(name: str) -> str:
    return ", ".join(f"{c['amount']} {c['name']}" for c in deck["cards"] if c["zone"] == name)


data = {
    "title": "Relecture des règles Yu-Gi-Oh! — Branded",
    "description": (
        "Merci de prendre ce temps.\n\n"
        "Le contexte en trois lignes. Un programme doit décider si une action est légale à partir du texte "
        "officiel des cartes (anglais, TCG) et des règles du jeu papier. Avant de l'écrire, on a rédigé des "
        "tests à la main. Ils reposent sur les 34 lectures ci-dessous, faites par une IA : certaines sont "
        "sûrement fausses, et c'est ce qu'on vous demande de repérer.\n\n"
        "Comment répondre. Pour chaque question : choisissez une réponse, et ajoutez une ligne si ce n'est "
        "pas « d'accord ». « Je ne sais pas » est une réponse utile. Si vous connaissez un ruling officiel "
        "ou une source, citez-la.\n\n"
        "Le deck est un Branded de régional (novembre 2026, liste TCG d'octobre 2026) ; toutes les "
        "situations sont au tour 1 du joueur qui commence, sauf mention contraire.\n\n"
        "34 questions fermées en deux parties (les 12 premières sont les moins sûres : si le temps manque, "
        "elles suffisent), puis 4 questions ouvertes. Durée estimée, non mesurée : une à deux heures."
    ),
    "choices": ["D'accord", "Faux", "Ça dépend", "Je ne sais pas"],
    "sections": sections,
    "sectionHelp": {
        "Partie 1": "Ce sont celles où la lecture est la moins sûre.",
        "Partie 2": "Même format. Vous pouvez envoyer le formulaire sans avoir tout rempli.",
    },
    "open": {
        "title": "Partie 3 — quatre questions ouvertes",
        "help": "Elles ne portent pas sur une carte, mais sur la façon de représenter le jeu.",
        "questions": open_qs,
    },
    "last": {
        "title": "Et ensuite",
        "question": (
            "Si vous avez encore un peu de temps : quelle est, selon vous, la ligne d'ouverture la plus "
            "courante de ce deck (4 à 8 cartes jouées, dans l'ordre) ? Le programme devra la retrouver seul."
        ),
        "deck": f"Deck principal : {zone('main')}.\n\nExtra Deck : {zone('extra')}.",
    },
}

script = """/**
 * Formulaire Google du juge (TOK-89) — généré depuis docs/moteur-combos/dossier-juge.md.
 * Ne pas modifier à la main : corriger le dossier, puis relancer python scripts/build_judge_form.py.
 *
 * Mode d'emploi :
 *   1. Ouvrir https://script.google.com , « Nouveau projet ».
 *   2. Remplacer tout le contenu par ce fichier, enregistrer.
 *   3. Lancer la fonction creerFormulaireJuge (bouton « Exécuter ») et accepter l'autorisation demandée.
 *   4. Les deux liens (à envoyer / à modifier) s'affichent dans le « Journal d'exécution ».
 * Chaque exécution crée un nouveau formulaire dans Google Drive.
 */

var DONNEES = __DATA__;

function creerFormulaireJuge() {
  var d = DONNEES;
  var form = FormApp.create(d.title);
  form.setDescription(d.description);
  form.setCollectEmail(false);
  form.setProgressBar(true);

  form.addTextItem()
    .setTitle('Votre nom ou pseudo')
    .setHelpText('Facultatif. Il sert à noter qui a tranché chaque point, avec la date.');
  form.addMultipleChoiceItem()
    .setTitle('Votre pratique du jeu')
    .setChoiceValues(['Arbitre (juge certifié)', 'Joueur de tournoi régulier', 'Joueur occasionnel ou Master Duel']);

  d.sections.forEach(function (section) {
    var page = form.addPageBreakItem().setTitle(section.title);
    var aide = d.sectionHelp[section.title.slice(0, 8)];
    if (aide) page.setHelpText(aide);
    section.questions.forEach(function (q) {
      form.addMultipleChoiceItem()
        .setTitle(q.id + ' — ' + q.question)
        .setHelpText('Lecture supposée : ' + q.lecture)
        .setChoiceValues(d.choices);
      form.addParagraphTextItem().setTitle(q.id + ' — commentaire ou source');
    });
  });

  form.addPageBreakItem().setTitle(d.open.title).setHelpText(d.open.help);
  d.open.questions.forEach(function (question, i) {
    form.addParagraphTextItem().setTitle((i + 1) + '. ' + question);
  });

  form.addPageBreakItem().setTitle(d.last.title).setHelpText(d.last.deck);
  form.addParagraphTextItem().setTitle(d.last.question);

  form.setConfirmationMessage('Merci. Vos réponses sont enregistrées.');
  try {
    form.setPublished(true);
  } catch (e) {
    Logger.log('Publication à faire à la main (bouton « Publier » du formulaire) : ' + e);
  }

  Logger.log('Lien à envoyer : ' + form.getPublishedUrl());
  Logger.log('Lien pour modifier et lire les réponses : ' + form.getEditUrl());
}
""".replace("__DATA__", json.dumps(data, ensure_ascii=False, indent=2))

out = root / "docs/moteur-combos/formulaire-juge.gs"
out.write_text(script, encoding="utf-8")
print(f"{out} : {total} questions fermées, {len(open_qs)} ouvertes, {len(script)} caractères")
