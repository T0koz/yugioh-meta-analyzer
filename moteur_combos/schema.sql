-- Moteur de combos — schéma de données (TOK-85, implémenté au lot 18, 2026-11-18).
--
-- Base À PART : data/combos.db (ignorée par Git, comme toutes les bases). Jamais dans yugioh.db,
-- qui n'est lue qu'en lecture seule (mode=ro) pour les textes des cartes.
-- Référence : docs/moteur-combos/definitions-et-schema.md (§ 2 définitions, § 3 schéma).
-- Préfixe cb_ (combos). Toutes les instructions sont idempotentes (IF NOT EXISTS) : le harnais
-- applique ce fichier à chaque lancement. Version du schéma : PRAGMA user_version (moteur_combos/base.py).
--
-- Ce schéma ne contient AUCUNE règle de jeu : il dit ce qui peut être enregistré, pas ce qui est légal.

-- ── Cartes ───────────────────────────────────────────────────────────────────────────────────

-- Une carte, avec le texte figé au moment de la lecture (détection d'errata par l'empreinte).
-- Le texte reste local : la base est ignorée par Git, le texte appartient à Konami.
CREATE TABLE IF NOT EXISTS cb_card (
    card_id        INTEGER PRIMARY KEY,                 -- = cards.id (YGOPRODeck)
    name           TEXT NOT NULL UNIQUE,                -- nom imprimé (sans <P>/<C>/<Q>)
    text           TEXT NOT NULL,                       -- texte lu dans yugioh.db (mode=ro)
    text_sha256    TEXT NOT NULL,                       -- empreinte de `text`
    text_fetched   TEXT NOT NULL,                       -- date de lecture (ISO 8601)
    text_source    TEXT NOT NULL DEFAULT 'ygoprodeck',
    frame_type     TEXT,                                -- effect, fusion, synchro, spell, trap…
    card_type      TEXT,                                -- « Effect Monster », « Spell Card »…
    attribute      TEXT,
    race           TEXT,                                -- Type de monstre, ou sous-type de Magie/Piège
    level          INTEGER,
    atk            INTEGER,
    def            INTEGER,
    reads_position INTEGER NOT NULL DEFAULT 0 CHECK (reads_position IN (0, 1)),  -- D3 : lit la case
    status         TEXT NOT NULL DEFAULT 'non_traitee' CHECK (status IN
        ('non_traitee', 'brouillon', 'formalisee', 'verifiee', 'non_formalisable')),
    status_reason  TEXT,
    verified_by    TEXT CHECK (verified_by IS NULL OR verified_by IN ('oracle', 'juge', 'oracle+juge')),
    updated_at     TEXT NOT NULL,
    CHECK ((status = 'verifiee') = (verified_by IS NOT NULL)),
    CHECK (status <> 'non_formalisable' OR status_reason IS NOT NULL)
);

-- Noms et archétypes d'une carte, calculés depuis le NOM imprimé et les clauses « always treated as »,
-- jamais depuis cards.archetype (definitions-et-schema.md § 3.5).
--   kind = 'nom'       : la carte porte ce nom (nom imprimé, ou « always treated as "X" »).
--                        Sert à la limite de 3 exemplaires par nom (§ 2.6).
--   kind = 'archetype' : la carte appartient à cet archétype (le nom contient le mot, ou
--                        « always treated as a "X" card »).
CREATE TABLE IF NOT EXISTS cb_card_name_tag (
    card_id   INTEGER NOT NULL REFERENCES cb_card(card_id) ON DELETE CASCADE,
    tag       TEXT NOT NULL,
    kind      TEXT NOT NULL CHECK (kind IN ('nom', 'archetype')),
    origin    TEXT NOT NULL CHECK (origin IN ('nom_imprime', 'traite_comme')),
    PRIMARY KEY (card_id, tag, kind)
);
CREATE INDEX IF NOT EXISTS idx_cb_card_name_tag_tag ON cb_card_name_tag (kind, tag);

-- Un effet = un morceau du texte, avec sa forme formelle. Rempli à la formalisation (tranche 0 et
-- suivantes), vide au lot 18.
CREATE TABLE IF NOT EXISTS cb_effect (
    effect_id      INTEGER PRIMARY KEY,
    card_id        INTEGER NOT NULL REFERENCES cb_card(card_id),
    position       INTEGER NOT NULL CHECK (position >= 1),   -- 1er, 2e… effet du texte
    kind           TEXT NOT NULL CHECK (kind IN
        ('invocation_inherente', 'declenche', 'ignition', 'rapide', 'continu',
         'activation_carte', 'condition_invocation', 'restriction')),
    speed          INTEGER CHECK (speed IS NULL OR speed IN (1, 2, 3)),
    optional       INTEGER NOT NULL CHECK (optional IN (0, 1)),   -- 1 « You can », 0 obligatoire
    timing         TEXT CHECK (timing IS NULL OR timing IN ('if', 'when')),
    text_span      TEXT NOT NULL,                             -- extrait exact du texte officiel
    formal_json    TEXT,                                      -- condition, coût, cibles, résolution
    text_sha256    TEXT NOT NULL,                             -- empreinte du texte de la carte formalisé
    status         TEXT NOT NULL CHECK (status IN
        ('non_traitee', 'brouillon', 'formalisee', 'verifiee', 'non_formalisable')),
    UNIQUE (card_id, position)
);

-- Limites « une fois par tour » d'un effet (relecture 1 : trois formes, plus deux variantes lues
-- dans les textes du deck). Un effet peut en porter plusieurs. La CONSOMMATION est de la tranche 0.
--   activation_par_nom  « You can only activate 1 "X" per turn »                 (clé : nom)
--   par_nom_effet       « You can only use this effect of "X" once per turn »    (clé : nom, effet)
--   par_nom_carte       « You can only use 1 "X" effect per turn, and only once that turn » (clé : nom)
--   invocation_par_nom  « You can only Special Summon "X" once per turn this way » (clé : nom)
--   par_exemplaire      « Once per turn »                                         (clé : l'exemplaire)
CREATE TABLE IF NOT EXISTS cb_effect_limit (
    effect_id  INTEGER NOT NULL REFERENCES cb_effect(effect_id) ON DELETE CASCADE,
    form       TEXT NOT NULL CHECK (form IN
        ('activation_par_nom', 'par_nom_effet', 'par_nom_carte', 'invocation_par_nom', 'par_exemplaire')),
    name_key   TEXT,                       -- nom cité par la clause (peut différer du nom imprimé)
    text_span  TEXT NOT NULL,
    PRIMARY KEY (effect_id, form),
    CHECK ((form = 'par_exemplaire') = (name_key IS NULL))
);

-- ── Decks ────────────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS cb_deck (
    deck_ref       TEXT PRIMARY KEY,                    -- tournament_decks.id
    label          TEXT NOT NULL,
    format         TEXT,
    list_name      TEXT,                                -- banlist en vigueur à la date du tournoi
    source_file    TEXT NOT NULL,                       -- docs/moteur-combos/deck-branded-source.json
    source_sha256  TEXT NOT NULL,                       -- empreinte du fichier source
    loaded_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cb_deck_card (
    deck_ref   TEXT NOT NULL REFERENCES cb_deck(deck_ref) ON DELETE CASCADE,
    card_id    INTEGER NOT NULL REFERENCES cb_card(card_id),
    zone       TEXT NOT NULL CHECK (zone IN ('main', 'extra', 'side')),
    amount     INTEGER NOT NULL CHECK (amount >= 1),    -- la limite de 3 est contrôlée par le code (§ 2.6)
    ban_tcg    TEXT,                                    -- statut au jour de l'extraction
    PRIMARY KEY (deck_ref, card_id, zone)
);
CREATE INDEX IF NOT EXISTS idx_cb_deck_card_card ON cb_deck_card (card_id);

-- ── États ────────────────────────────────────────────────────────────────────────────────────

-- États : identifiés par l'empreinte de leur forme canonique (§ 2.3). Contenu adressé : un état
-- n'est jamais modifié, on n'ajoute que des états nouveaux.
CREATE TABLE IF NOT EXISTS cb_state (
    state_id       TEXT PRIMARY KEY CHECK (length(state_id) = 64 AND state_id NOT GLOB '*[^0-9a-f]*'),   -- SHA-256 de canonical_json
    canonical_json TEXT NOT NULL,                                   -- blocs A, B, C, D
    turn           INTEGER NOT NULL CHECK (turn >= 1),
    active_player  INTEGER NOT NULL CHECK (active_player IN (0, 1)), -- 0 = nous
    phase          TEXT NOT NULL CHECK (phase IN
        ('pioche', 'standby', 'principale_1', 'combat', 'principale_2', 'fin')),
    is_stable      INTEGER NOT NULL CHECK (is_stable IN (0, 1)),
    board_id       TEXT                                             -- empreinte du « plateau final »
);
CREATE INDEX IF NOT EXISTS idx_cb_state_board ON cb_state (board_id);

-- Cible d'exploration (relecture 1) : le plateau final visé. Conditions en JSON :
-- [{"zone": "terrain"|"main"|"cimetiere"|"bannies", "carte": "<nom imprimé>", "minimum": 1}, …]
CREATE TABLE IF NOT EXISTS cb_target (
    target_id       INTEGER PRIMARY KEY,
    description     TEXT NOT NULL,
    conditions_json TEXT NOT NULL CHECK (json_valid(conditions_json)),
    created_at      TEXT NOT NULL
);

-- ── Explorations ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS cb_run (
    run_id            INTEGER PRIMARY KEY,
    mode              TEXT NOT NULL CHECK (mode IN ('absolu', 'decklist')),
    deck_ref          TEXT REFERENCES cb_deck(deck_ref),
    start_state       TEXT NOT NULL REFERENCES cb_state(state_id),
    target_id         INTEGER REFERENCES cb_target(target_id),       -- NULL = exploration exhaustive
    max_depth         INTEGER NOT NULL CHECK (max_depth >= 1),
    columns_enumerated INTEGER NOT NULL CHECK (columns_enumerated IN (0, 1)),  -- D3 révisée
    filters_json      TEXT NOT NULL CHECK (json_valid(filters_json)),  -- filtres déclarés (D4)
    rules_version     TEXT NOT NULL,
    engine_version    TEXT NOT NULL,
    complete          INTEGER NOT NULL CHECK (complete IN (0, 1)),
    started_at        TEXT NOT NULL,
    CHECK (mode = 'absolu' OR deck_ref IS NOT NULL)
);

-- Transitions : d'un état stable à un état stable.
CREATE TABLE IF NOT EXISTS cb_transition (
    transition_id  INTEGER PRIMARY KEY,
    run_id         INTEGER NOT NULL REFERENCES cb_run(run_id),
    from_state     TEXT NOT NULL REFERENCES cb_state(state_id),
    to_state       TEXT NOT NULL REFERENCES cb_state(state_id),
    action_type    TEXT NOT NULL,
    actor_card_id  INTEGER REFERENCES cb_card(card_id),
    actor_effect   INTEGER REFERENCES cb_effect(effect_id),
    is_random      INTEGER NOT NULL DEFAULT 0 CHECK (is_random IN (0, 1)),
    stop_reason    TEXT CHECK (stop_reason IS NULL OR stop_reason IN
        ('fin_forcee', 'fin_volontaire', 'tronque_profondeur', 'retour_etat_connu',
         'boucle', 'cible_atteinte', 'non_couvert', 'hors_perimetre')),
    verified       INTEGER NOT NULL CHECK (verified IN (0, 1))
);
CREATE INDEX IF NOT EXISTS idx_cb_transition_from ON cb_transition (run_id, from_state);
CREATE INDEX IF NOT EXISTS idx_cb_transition_actor ON cb_transition (actor_card_id);
CREATE INDEX IF NOT EXISTS idx_cb_transition_to ON cb_transition (to_state);

-- Pas : les décisions élémentaires à l'intérieur d'une transition (niveau oracle, D2).
-- `option` porte le choix d'une décision à options, dont le placement d'une Invocation depuis
-- l'Extra Deck (D3 révisée) : 'zone_monstre_extra' ou 'zone_principale'.
CREATE TABLE IF NOT EXISTS cb_step (
    step_id        INTEGER PRIMARY KEY,
    transition_id  INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    position       INTEGER NOT NULL CHECK (position >= 1),
    step_type      TEXT NOT NULL CHECK (step_type IN
        ('declarer', 'cout', 'cible', 'enchainer', 'resoudre', 'choisir', 'placer', 'ordonner', 'hasard')),
    chain_link     INTEGER,
    effect_id      INTEGER REFERENCES cb_effect(effect_id),
    option         TEXT,
    UNIQUE (transition_id, position)
);
CREATE INDEX IF NOT EXISTS idx_cb_step_effect ON cb_step (effect_id);

-- Toutes les cartes qu'un pas nomme, avec leur rôle et leur case d'arrivée sur le terrain.
-- `copy_index` distingue deux exemplaires de même nom et de même rôle dans un pas (deux matériels
-- homonymes, l'un pris en main, l'autre sur le terrain).
CREATE TABLE IF NOT EXISTS cb_step_card (
    step_id    INTEGER NOT NULL REFERENCES cb_step(step_id),
    card_id    INTEGER NOT NULL REFERENCES cb_card(card_id),
    copy_index INTEGER NOT NULL DEFAULT 1 CHECK (copy_index >= 1),
    role       TEXT NOT NULL CHECK (role IN
        ('acteur', 'cout', 'materiel', 'cible', 'choisie', 'deplacee', 'revelee', 'condition')),
    from_zone  TEXT,
    to_zone    TEXT,
    to_cell    TEXT CHECK (to_cell IS NULL OR to_cell IN
        ('M1', 'M2', 'M3', 'M4', 'M5', 'ZME_G', 'ZME_D', 'S1', 'S2', 'S3', 'S4', 'S5', 'TERRAIN')),
    PRIMARY KEY (step_id, card_id, role, copy_index)
);
CREATE INDEX IF NOT EXISTS idx_cb_step_card_card ON cb_step_card (card_id, step_id);

-- Fenêtres d'interruption adverse : réservées, sans réponse dans le pilote (§ 2.5).
CREATE TABLE IF NOT EXISTS cb_window (
    window_id   INTEGER PRIMARY KEY,
    step_id     INTEGER NOT NULL REFERENCES cb_step(step_id),
    window_type TEXT NOT NULL CHECK (window_type IN ('reponse_activation', 'reponse_invocation')),
    response    TEXT NOT NULL DEFAULT 'aucune'
);
CREATE INDEX IF NOT EXISTS idx_cb_window_step ON cb_window (step_id);

-- Conditions : rattachées aux transitions, hors du combo.
CREATE TABLE IF NOT EXISTS cb_condition (
    condition_id INTEGER PRIMARY KEY,
    kind         TEXT NOT NULL CHECK (kind IN
        ('etat', 'hasard', 'adverse', 'verrou_absent', 'limite_disponible', 'zone_libre', 'hypothese')),
    expression   TEXT NOT NULL,
    UNIQUE (kind, expression)
);
CREATE TABLE IF NOT EXISTS cb_transition_condition (
    transition_id INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    condition_id  INTEGER NOT NULL REFERENCES cb_condition(condition_id),
    PRIMARY KEY (transition_id, condition_id)
);

-- Relations entre deux cartes, dérivées des pas (§ 3.3).
CREATE TABLE IF NOT EXISTS cb_relation (
    relation_id   INTEGER PRIMARY KEY,
    transition_id INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    source_card   INTEGER NOT NULL REFERENCES cb_card(card_id),
    target_card   INTEGER NOT NULL REFERENCES cb_card(card_id),
    family        TEXT NOT NULL CHECK (family IN
        ('deplace', 'materiel_ou_cout', 'conditionne', 'interagit_adverse')),
    detail        TEXT,
    UNIQUE (transition_id, source_card, target_card, family)
);
CREATE INDEX IF NOT EXISTS idx_cb_relation_transition ON cb_relation (transition_id);
CREATE INDEX IF NOT EXISTS idx_cb_relation_pair ON cb_relation (source_card, target_card, family);

-- Combos : un chemin, enregistré dans son ordre réel.
CREATE TABLE IF NOT EXISTS cb_combo (
    combo_id     INTEGER PRIMARY KEY,
    run_id       INTEGER NOT NULL REFERENCES cb_run(run_id),
    final_state  TEXT NOT NULL REFERENCES cb_state(state_id),
    length       INTEGER NOT NULL CHECK (length >= 0),
    label        TEXT NOT NULL CHECK (label IN ('demontre', 'non_verifie')),
    stop_reason  TEXT NOT NULL CHECK (stop_reason IN
        ('fin_forcee', 'fin_volontaire', 'tronque_profondeur', 'retour_etat_connu',
         'boucle', 'cible_atteinte', 'non_couvert', 'hors_perimetre'))
);
CREATE INDEX IF NOT EXISTS idx_cb_combo_run ON cb_combo (run_id);
-- actor_card_id est recopié de cb_transition pour la requête « A puis B » ; l'écrivain (moteur) garde
-- les deux égaux. Pas de déclencheur au lot 18 : aucune écriture de combo n'existe encore.
CREATE TABLE IF NOT EXISTS cb_combo_step (
    combo_id      INTEGER NOT NULL REFERENCES cb_combo(combo_id),
    position      INTEGER NOT NULL CHECK (position >= 1),
    transition_id INTEGER NOT NULL REFERENCES cb_transition(transition_id),
    actor_card_id INTEGER REFERENCES cb_card(card_id),
    PRIMARY KEY (combo_id, position)
);
CREATE INDEX IF NOT EXISTS idx_cb_combo_step_actor ON cb_combo_step (actor_card_id, combo_id, position);
CREATE INDEX IF NOT EXISTS idx_cb_combo_step_transition ON cb_combo_step (transition_id, combo_id);

-- ── Jeu de tests (harnais du lot 18) ─────────────────────────────────────────────────────────

-- Une ligne par situation de tests-branded.yaml, réécrite à chaque lancement du harnais.
CREATE TABLE IF NOT EXISTS cb_test_situation (
    test_id         TEXT PRIMARY KEY CHECK (test_id GLOB 'T[0-9][0-9]*'),
    yaml_sha256     TEXT NOT NULL,                     -- empreinte du fichier de tests lu
    deck_ref        TEXT NOT NULL REFERENCES cb_deck(deck_ref),
    perimetre       TEXT NOT NULL CHECK (perimetre IN ('pilote', 'hors_pilote')),
    rules_json      TEXT NOT NULL CHECK (json_valid(rules_json)),   -- points de règle (R27a/R27b précisés)
    classe          TEXT NOT NULL CHECK (classe IN
        ('regles_confirmees', 'un_seul_avis', 'non_executable_sans_regles')),
    start_state     TEXT REFERENCES cb_state(state_id),             -- NULL si le départ est invalide
    start_complete  INTEGER NOT NULL CHECK (start_complete IN (0, 1)),  -- 0 : faits en texte libre
    free_facts_json TEXT NOT NULL CHECK (json_valid(free_facts_json)),
    expected        TEXT NOT NULL CHECK (expected IN ('legal', 'illegal', 'non_couvert')),
    status          TEXT NOT NULL CHECK (status IN
        ('verifie', 'en_attente_tranche_0', 'depart_invalide', 'echec')),
    updated_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cb_test_situation_state ON cb_test_situation (start_state);
