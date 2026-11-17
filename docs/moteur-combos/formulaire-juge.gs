/**
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

var DONNEES = {
  "title": "Relecture des règles Yu-Gi-Oh! — Branded",
  "description": "Merci de prendre ce temps.\n\nLe contexte en trois lignes. Un programme doit décider si une action est légale à partir du texte officiel des cartes (anglais, TCG) et des règles du jeu papier. Avant de l'écrire, on a rédigé des tests à la main. Ils reposent sur les 34 lectures ci-dessous, faites par une IA : certaines sont sûrement fausses, et c'est ce qu'on vous demande de repérer.\n\nComment répondre. Pour chaque question : choisissez une réponse, et ajoutez une ligne si ce n'est pas « d'accord ». « Je ne sais pas » est une réponse utile. Si vous connaissez un ruling officiel ou une source, citez-la.\n\nLe deck est un Branded de régional (novembre 2026, liste TCG d'octobre 2026) ; toutes les situations sont au tour 1 du joueur qui commence, sauf mention contraire.\n\n34 questions fermées en deux parties (les 12 premières sont les moins sûres : si le temps manque, elles suffisent), puis 4 questions ouvertes. Durée estimée, non mesurée : une à deux heures.",
  "choices": [
    "D'accord",
    "Faux",
    "Ça dépend",
    "Je ne sais pas"
  ],
  "sections": [
    {
      "title": "Partie 1 — les 12 questions prioritaires",
      "questions": [
        {
          "id": "R01",
          "question": "Peut-on activer un effet qui ne pourra rien faire à la résolution (aucune carte à chercher dans le Deck, aucune Fusion possible, aucune carte à défausser) ?",
          "lecture": "Non. L'activation est illégale. Doute : le Deck est une zone privée, et la règle exacte pour « chercher alors qu'il n'y a rien » peut différer."
        },
        {
          "id": "R07",
          "question": "Branded Fusion : « you cannot Special Summon from the Extra Deck, except Fusion Monsters, the turn you activate this card ». Si j'ai déjà fait une Invocation Synchro ce tour, puis-je l'activer ? Et Branded Opening (« for the rest of this turn after this card resolves ») ?",
          "lecture": "Branded Fusion : non (la restriction vaut pour tout le tour, passé compris). Branded Opening : oui."
        },
        {
          "id": "R08",
          "question": "Si l'effet d'une carte « You can only activate 1 per turn » est annulé (par Ash Blossom), la limite est-elle consommée et le verrou s'applique-t-il ?",
          "lecture": "Oui aux deux : l'effet est annulé, pas l'activation. Si c'est l'activation qui est annulée, la carte ne compte pas comme activée."
        },
        {
          "id": "R09",
          "question": "Un monstre Fusion envoyé au Cimetière directement depuis l'Extra Deck (par Nadir Servant) peut-il être ciblé par Guiding Quem pour être Invoqué Spécialement ?",
          "lecture": "Non : il n'a jamais été correctement invoqué. Le même monstre, invoqué par Fusion puis envoyé au Cimetière, peut revenir."
        },
        {
          "id": "R10",
          "question": "Un effet « If … : You can » dont la condition se réalise pendant la résolution d'un autre effet, ou pendant le paiement d'un coût, peut-il être activé ensuite ?",
          "lecture": "Oui, dans une nouvelle chaîne, après la chaîne en cours. Seuls les effets « When … you can » ratent leur moment."
        },
        {
          "id": "R14",
          "question": "Un effet dont le seul résultat possible est interdit par un verrou (Fusion depuis l'Extra Deck sous Nadir Servant) peut-il être activé ?",
          "lecture": "Non."
        },
        {
          "id": "R17",
          "question": "Branded Opening : « Discard 1 card, then take… » sans point-virgule. La défausse est-elle un coût ? Et faut-il une carte à défausser pour activer ? Même question pour « Reveal… and send… » de Branded in High Spirits.",
          "lecture": "Ce sont des effets, pas des coûts (ils se font à la résolution). Il faut quand même pouvoir les faire pour activer."
        },
        {
          "id": "R22",
          "question": "Deux effets facultatifs du même joueur se déclenchent en même temps (Granguignol invoqué par Fusion, Tri-Brigade Springans Kitt envoyée au Cimetière). Qui choisit l'ordre dans la chaîne ?",
          "lecture": "Le joueur, librement. Il peut aussi n'en activer qu'un."
        },
        {
          "id": "R23",
          "question": "Incredible Ecclesia : « During the End Phase, if a Fusion Monster(s) was sent to your GY this turn: Add this card from the GY to your hand » (sans « You can »). Obligatoire ? Et dans quel ordre résout-on plusieurs effets de Phase de Fin ?",
          "lecture": "Obligatoire. Le joueur du tour active ses effets de Phase de Fin un par un, dans l'ordre qu'il veut, chacun dans sa chaîne."
        },
        {
          "id": "R27",
          "question": "Cocatorium bannit Tri-Brigade Mercourier du Deck (coût) et prend son nom. (a) Compte-t-il comme monstre « Tri-Brigade » pour Tri-Brigade Springans Kitt ? (b) Le bannissement en coût depuis le Deck est-il « face visible », et déclenche-t-il Mercourier et The Golden Swordsoul ?",
          "lecture": "(a) oui ; (b) oui aux deux."
        },
        {
          "id": "R34",
          "question": "The Fallen & The Virtuous : « Send 1 monster… from your Extra Deck to the GY, then target 1 face-up card on the field; destroy it ». (a) La carte peut-elle se cibler elle-même ? (b) La cible se choisit-elle à l'activation ou à la résolution ? (c) Sans aucune carte face visible sur le terrain, peut-on l'activer ?",
          "lecture": "(a) non ; (b) je ne sais pas : la formulation « then target » est inhabituelle ; (c) non."
        },
        {
          "id": "R30",
          "question": "Est-il légal d'activer Mulcharmy Fuwalos pendant son propre tour, ou d'enchaîner son propre Ash Blossom à son propre effet ?",
          "lecture": "Oui : rien dans les textes ne l'interdit."
        }
      ]
    },
    {
      "title": "Partie 2 — les 22 autres",
      "questions": [
        {
          "id": "R03",
          "question": "Fallen of the White Dragon (« always treated as \"Fallen of Albaz\" ») compte-t-il comme « Fallen of Albaz » partout : matériel pris dans le Deck par Branded Fusion, carte cherchée par Nadir Servant, condition de Blazing Cartesia ?",
          "lecture": "Oui, dans toutes les zones."
        },
        {
          "id": "R04",
          "question": "« A card / monster that mentions \"Fallen of Albaz\" » : est-ce toute carte dont le texte contient ce nom entre guillemets ? Ecclesia and the Dark Dragon et The Three Champions of Swordsoul (Synchro) comptent-ils ? Les Magies comptent-elles quand le texte dit « card » ?",
          "lecture": "Oui aux trois."
        },
        {
          "id": "R05",
          "question": "« A Fusion Monster that mentions \"Fallen of Albaz\" as material » : faut-il que le nom soit dans la ligne de matériels ?",
          "lecture": "Oui. Granguignol (matériels : Blazing Cartesia + 1 LIGHT ou DARK) ne compte pas ; Titaniklad, Rindbrumm, Mirrorjade, Albion the Sanctifire Dragon, Sprind, The Dragon that Devours the Dogma comptent."
        },
        {
          "id": "R11",
          "question": "Appartenance à un archétype : par le nom ou par « always treated as ». Guiding Quem est-il « Dogmatika » et « Despia » ? Fallen of Albaz est-il « Dogmatika » ? Incredible Ecclesia et Dogmatika Ecclesia sont-ils des monstres « Ecclesia » ?",
          "lecture": "Quem : les deux. Fallen of Albaz : non. Les deux Ecclesia : oui. Blazing Cartesia : ni « Dogmatika » ni « Ecclesia ». The Fallen & The Virtuous (« always treated as a \"Branded\" and \"Dogmatika\" card ») : cherchable par Aluber et par Dogmatika Ecclesia."
        },
        {
          "id": "R32",
          "question": "Springans Kitt : « If you have a Fusion Monster that mentions \"Fallen of Albaz\" as material on your field or in your GY ». Un monstre Fusion envoyé au Cimetière sans avoir été invoqué suffit-il ?",
          "lecture": "Oui : la condition ne demande que sa présence."
        },
        {
          "id": "R06",
          "question": "Branded Fusion (« using 2 monsters ») peut-il invoquer The Dragon that Devours the Dogma (3 matériels) ?",
          "lecture": "Non."
        },
        {
          "id": "R20",
          "question": "Garura : « 2 monsters with the same Type and Attribute, but different names ». Blazing Cartesia + Guiding Quem conviennent-ils ?",
          "lecture": "Oui (LIGHT Spellcaster tous les deux)."
        },
        {
          "id": "R24",
          "question": "Un monstre peut-il remplir deux lignes de matériel d'une même Fusion ? Albion the Sanctifire Dragon peut-il servir de matériel ?",
          "lecture": "Non et non (« Cannot be used as Fusion Material »)."
        },
        {
          "id": "R25",
          "question": "Sprind : « 1 Effect Monster Special Summoned this turn ». Un monstre Invoqué Normalement ce tour convient-il ?",
          "lecture": "Non."
        },
        {
          "id": "R26",
          "question": "Synchro : Ecclesia and the Dark Dragon (« 1 Tuner + 1+ non-Tuners », Niveau 8) avec deux Syntoniseurs de Niveau 4 ? Verrou de Fallen of the White Dragon (« except Level 8 Fusion or Synchro Monsters ») : Despian Luluwalilith (Niveau 12) est-elle interdite ?",
          "lecture": "Deux Syntoniseurs : illégal. Luluwalilith : interdite sous ce verrou."
        },
        {
          "id": "R12",
          "question": "Nadir Servant : « ATK less than or equal to that sent monster in the GY ». On compare à l'ATK imprimée du monstre envoyé ?",
          "lecture": "Oui (au Cimetière, pas de modification)."
        },
        {
          "id": "R13",
          "question": "Un verrou « cannot Special Summon from the Extra Deck » empêche-t-il d'invoquer depuis le Deck ou le Cimetière ?",
          "lecture": "Non."
        },
        {
          "id": "R21",
          "question": "Branded in High Spirits : « Level 8 Fusion Monster … with the same Type that has 2500 ATK or DEF ». The Dragon that Devours the Dogma (3000/2500) convient-il par sa DEF ? Et la limite « 1 effect per turn » interdit-elle de reprendre la carte en Phase de Fin après l'avoir activée ?",
          "lecture": "Oui et oui."
        },
        {
          "id": "R29",
          "question": "Gold Sarcophagus activée à notre tour 1 : « your second Standby Phase after this card's activation » est-elle celle de notre tour 5 ?",
          "lecture": "Oui (tour 3 = première, tour 5 = seconde)."
        },
        {
          "id": "R02",
          "question": "Toute recherche dans le Deck est-elle suivie d'un mélange ? Une carte posée au-dessous du Deck (Springans Kitt) y reste-t-elle jusqu'au mélange suivant ?",
          "lecture": "Oui et oui."
        },
        {
          "id": "R15",
          "question": "Incredible Ecclesia (« you can Special Summon this card (from your hand) ») : invocation sans chaîne. Blazing Cartesia (« If you control … : You can Special Summon this card from your hand ») : effet activé, avec chaîne. Exact ?",
          "lecture": "Oui (la présence de « : » fait la différence)."
        },
        {
          "id": "R16",
          "question": "« If your opponent controls more monsters than you do » avec 0 contre 0 ?",
          "lecture": "Faux : pas d'invocation."
        },
        {
          "id": "R18",
          "question": "Une Magie Jeu-Rapide peut-elle être activée depuis la main pendant son propre tour, en réponse à son propre effet ? Et le tour où elle a été posée face cachée ?",
          "lecture": "Depuis la main : oui. Posée ce tour : non."
        },
        {
          "id": "R19",
          "question": "Super Polymerization : puis-je enchaîner ma propre carte à son activation ?",
          "lecture": "Non (« Neither player »)."
        },
        {
          "id": "R28",
          "question": "Mirrorjade : « banish 1 monster on the field ». Peut-elle bannir un monstre de son propre contrôleur ? L'effet cible-t-il ?",
          "lecture": "Oui ; il ne cible pas (pas de « target »)."
        },
        {
          "id": "R31",
          "question": "Le joueur qui commence ne pioche pas et n'a pas de Phase de Combat au tour 1 ?",
          "lecture": "Oui."
        },
        {
          "id": "R33",
          "question": "Tri-Brigade Springans Kitt (« Special Summon 1 of the following monsters from your GY ») : l'effet cible-t-il ? Faut-il un monstre éligible au Cimetière pour l'activer ?",
          "lecture": "Il ne cible pas ; il faut au moins un monstre éligible à l'activation."
        }
      ]
    }
  ],
  "sectionHelp": {
    "Partie 1": "Ce sont celles où la lecture est la moins sûre.",
    "Partie 2": "Même format. Vous pouvez envoyer le formulaire sans avoir tout rempli."
  },
  "open": {
    "title": "Partie 3 — quatre questions ouvertes",
    "help": "Elles ne portent pas sur une carte, mais sur la façon de représenter le jeu.",
    "questions": [
      "Un effet « une fois par tour » est-il consommé dès l'activation, même si l'effet est ensuite annulé ?",
      "L'ordre des cartes dans le Cimetière compte-t-il pour une carte jouée en TCG aujourd'hui ?",
      "La colonne où se trouve un monstre ne compte-t-elle que pour les cartes qui en parlent (Sprind the Irondash Dragon, Albion the Sanctifire Dragon) ? Peut-on placer tous les autres monstres « n'importe où » sans jamais perdre un combo ?",
      "Un monstre Fusion peut-il toujours être placé, au choix, en Zone Monstre Extra ou en Zone Monstre Principale ?"
    ]
  },
  "last": {
    "title": "Et ensuite",
    "question": "Si vous avez encore un peu de temps : quelle est, selon vous, la ligne d'ouverture la plus courante de ce deck (4 à 8 cartes jouées, dans l'ordre) ? Le programme devra la retrouver seul.",
    "deck": "Deck principal : 3 Aluber the Jester of Despia, 3 Ash Blossom & Joyous Spring, 2 Blazing Cartesia, the Virtuous, 1 Branded Fusion, 1 Branded Opening, 1 Branded in High Spirits, 1 Cocatorium the Heavy Metal Avian, 1 Dogmatika Ecclesia, the Virtuous, 1 Droll & Lock Bird, 1 Fallen of Albaz, 2 Fallen of the White Dragon, 3 Ghost Ogre & Snow Rabbit, 1 Gold Sarcophagus, 1 Guiding Quem, the Virtuous, 2 Incredible Ecclesia, the Virtuous, 3 Mulcharmy Fuwalos, 3 Nadir Servant, 1 Springans Kitt, 3 Super Polymerization, 3 The Fallen & The Virtuous, 1 The Golden Swordsoul, 1 Tri-Brigade Mercourier, 1 Tri-Brigade Springans Kitt.\n\nExtra Deck : 1 Albion the Sanctifire Dragon, 1 Despian Luluwalilith, 1 Ecclesia and the Dark Dragon, 1 Garura, Wings of Resonant Life, 1 Granguignol the Dusk Dragon, 1 Hyperinvoked Aeon, 1 Mirrorjade the Iceblade Dragon, 1 Mixousia the Confounder, 1 Predaplant Dragostapelia, 1 Rindbrumm the Striking Dragon, 1 Sprind the Irondash Dragon, 2 The Dragon that Devours the Dogma, 1 The Three Champions of Swordsoul, 1 Titaniklad the Ash Dragon."
  }
};

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
