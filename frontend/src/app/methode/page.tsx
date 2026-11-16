import type { Metadata } from "next";
import Link from "next/link";
import { api } from "@/lib/api";
import { fmtDate, fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { SITE_FACTS } from "@/lib/site-facts";
import { WEAK_MONTH_DECKS } from "@/lib/wilson";
import { Em } from "@/components/ds/em";
import { IntervalBar } from "@/components/ds/explain";
import { DataFooter, Page, PageHero } from "@/components/ds/page";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BanHistoryList } from "@/types";

// Page Méthode (lot 15, charte « ton et explication » §4) : une section par outil,
// dans l'ordre de la navigation ; sources, dates, seuils et leur origine, résultats
// des validations ÉCHECS COMPRIS, limites. Aucune formule : chaque méthode est
// décrite par ce qu'elle mesure. Les ancres sont celles des couches « Méthode »
// (MethodNote) des pages d'outil : ne pas les renommer sans les suivre.

export const metadata: Metadata = pageMetadata({
  title: "Méthode",
  description:
    "Sources, dates de collecte, seuils et résultats des validations de chaque outil, échecs compris : listes TCG de septembre et octobre 2026, signal boutique de juin 2026. Aucune formule.",
  path: "/methode",
});

const H2 = "text-[clamp(22px,2.6vw,30px)] leading-tight font-medium tracking-[-0.03em]";
const H3 = "font-mono text-[11px] uppercase tracking-[0.1em] text-muted-text";
const NUM = "text-right font-mono text-[13px] tabular-nums";

const SECTIONS = [
  { id: "sources", label: "Sources communes" },
  { id: "seuils", label: "Seuils" },
  { id: "tier-list", label: "Tier list" },
  { id: "decks", label: "Decks" },
  { id: "evolution", label: "Évolution" },
  { id: "predictions", label: "Prédictions" },
  { id: "ban-radar", label: "Ban Radar" },
  { id: "ban-historique", label: "Ban Radar, historique" },
  { id: "boutique", label: "Signaux boutique" },
  { id: "signaux-precoces", label: "Signaux précoces" },
  { id: "graphe", label: "Graphe" },
];

/** Bloc d'une section : mesure, sources, seuils, limites, en définitions. */
function Facts({ items }: { items: { term: string; text: React.ReactNode }[] }) {
  return (
    <dl className="mt-5 grid gap-px overflow-hidden rounded-[6px] border border-line bg-line min-[760px]:grid-cols-2">
      {items.map((item) => (
        <div key={item.term} className="grid content-start gap-1.5 bg-ink-2 px-4 py-3.5">
          <dt className={H3}>{item.term}</dt>
          <dd className="text-[14px] leading-[1.6] text-soft">{item.text}</dd>
        </div>
      ))}
    </dl>
  );
}

function Section({ id, title, children }: { id: string; title: React.ReactNode; children: React.ReactNode }) {
  return (
    <section id={id} aria-labelledby={`h-${id}`} className="mt-14 scroll-mt-24 border-t border-line pt-10">
      <h2 id={`h-${id}`} className={H2}>
        {title}
      </h2>
      {children}
    </section>
  );
}

function Validation({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-6">
      <h3 className="mb-3 text-[16px] font-medium tracking-[-0.01em]">{title}</h3>
      {children}
    </div>
  );
}

function SimpleTable({ caption, head, rows }: { caption: string; head: string[]; rows: React.ReactNode[][] }) {
  return (
    <div className="overflow-x-auto rounded-[6px] border border-line">
      <Table>
        <caption className="sr-only">{caption}</caption>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            {head.map((h, i) => (
              <TableHead key={h} className={i ? "text-right" : ""}>
                {h}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, r) => (
            <TableRow key={r}>
              {row.map((cell, i) => (
                <TableCell key={i} className={i ? NUM : "text-[14px] text-soft"}>
                  {cell}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

/** Septembre et octobre 2026 en TCG : les deux échecs nommés par la charte. */
const isRecentFailure = (l: BanHistoryList) =>
  l.format === "TCG" && (l.effective_date.startsWith("2026-09") || l.effective_date.startsWith("2026-10"));

function BanTable({ lists }: { lists: BanHistoryList[] }) {
  return (
    <div className="overflow-x-auto rounded-[6px] border border-line">
      <Table>
        <caption className="sr-only">
          Rang médian des cartes touchées, bande du hasard à 90 % et base « staples les plus jouées », par banlist rejouée
        </caption>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead>Liste</TableHead>
            <TableHead className="text-right">Decks</TableHead>
            <TableHead className="text-right">Rang médian</TableHead>
            <TableHead className="min-w-[180px]">Face au hasard (90 %)</TableHead>
            <TableHead className="text-right">Staples les plus jouées</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {lists.map((l) => {
            const ranked = l.retained && l.median_rank != null && l.n_cards != null;
            const beat = ranked && l.random_low != null && l.median_rank! < l.random_low;
            return (
              <TableRow key={`${l.format}-${l.effective_date}`}>
                <TableCell className="text-[14px] whitespace-nowrap text-soft">
                  {l.format} · {fmtDate(l.effective_date)}
                  {isRecentFailure(l) && ranked && <span className="ml-2 font-mono text-[12px] text-warn">échec</span>}
                </TableCell>
                <TableCell className={NUM}>{fmtNum(l.n_decks)}</TableCell>
                <TableCell className={NUM}>
                  {ranked ? `${fmtNum(l.median_rank!)} sur ${fmtNum(l.n_cards!)}` : (
                    <span className="text-muted-text">écartée ({l.skip_reason === "decks" ? "decks" : "cartes touchées"})</span>
                  )}
                </TableCell>
                <TableCell>
                  {ranked && l.random_low != null && l.random_high != null ? (
                    <IntervalBar
                      value={l.median_rank!}
                      lo={l.random_low}
                      hi={l.random_high}
                      min={1}
                      max={l.n_cards!}
                      color={beat ? "var(--cat-1)" : "var(--soft)"}
                      label={`Rang médian ${fmtNum(l.median_rank!)} ; hasard de ${fmtNum(l.random_low)} à ${fmtNum(l.random_high)} sur ${fmtNum(l.n_cards!)}`}
                    />
                  ) : (
                    <span className="font-mono text-[12px] text-faint">—</span>
                  )}
                </TableCell>
                <TableCell className={NUM}>{ranked && l.baseline_median_rank != null ? fmtNum(l.baseline_median_rank) : "—"}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

export default async function MethodePage() {
  const [tierList, evolution, banHistory, boutique, prices] = await Promise.all([
    api.tierList(),
    api.evolution(),
    api.banHistory(),
    api.boutiqueSignals(),
    api.boutiquePrices(),
  ]);

  const months = Object.entries(evolution.decks_by_month).sort(([a], [b]) => a.localeCompare(b));
  const weakMonths = months.filter(([, n]) => n < WEAK_MONTH_DECKS);
  const fullMonths = months.length - weakMonths.length;
  const firstFull = months.find(([, n]) => n >= WEAK_MONTH_DECKS)?.[0];
  const rule = boutique.label_rule;
  const retained = banHistory.lists.filter((l) => l.retained);
  const tcgBaselineWins = retained.filter(
    (l) => l.format === "TCG" && l.baseline_median_rank != null && l.median_rank != null && l.baseline_median_rank < l.median_rank
  ).length;
  const tcgRetained = retained.filter((l) => l.format === "TCG").length;
  const [ciLow, ciHigh] = SITE_FACTS.ocgTcgCorrelationCi;

  return (
    <Page>
      <PageHero
        eyebrow="Méthode"
        title={
          <>
            Sources, seuils et résultats des <Em>validations</Em>.
          </>
        }
        intro="Une section par outil, dans l’ordre de la navigation. Chaque méthode est décrite par ce qu’elle mesure ; les résultats mauvais restent dans les tableaux."
      />

      <nav aria-label="Sections de la page" className="flex flex-wrap gap-x-5 gap-y-2 font-mono text-[12px] text-muted-text">
        {SECTIONS.map((s) => (
          <a key={s.id} href={`#${s.id}`} className="underline decoration-line-2 underline-offset-4 hover:text-text">
            {s.label}
          </a>
        ))}
      </nav>

      <Section id="sources" title="Sources communes">
        <Facts
          items={[
            {
              term: "Decks de tournoi",
              text: `${DECK_SOURCE} : ${fmtNum(SITE_FACTS.decklistsTcg)} listes TCG et ${fmtNum(SITE_FACTS.decklistsOcg)} listes OCG au 14 novembre 2026, collectées chaque lundi. Seules les listes légales à la date de leur tournoi sont comptées.`,
            },
            { term: "Banlists", text: "Yugipedia, TCG et OCG, reconstituées à chaque collecte ; une nouvelle liste devient automatiquement un point de validation." },
            {
              term: "Cartes, vues et prix",
              text: `YGOPRODeck (fiches, vues par semaine, prix Cardmarket). ${fmtNum(prices.snapshot_count)} relevés de prix servis${prices.period_start && prices.period_end ? `, du ${fmtDate(prices.period_start)} au ${fmtDate(prices.period_end)}` : ""}.`,
            },
            {
              term: "Fenêtre de la tier list",
              text: `${fmtMonthShort(tierList.window_start)} à ${fmtMonthShort(tierList.window_end)}, ${fmtNum(tierList.n_decks)} decks TCG.`,
            },
          ]}
        />
      </Section>

      <Section id="seuils" title="Seuils et leur origine">
        <div className="mt-5">
          <SimpleTable
            caption="Seuils appliqués sur le site et leur origine"
            head={["Seuil", "Valeur", "Origine"]}
            rows={[
              ["Mois atténué dans les séries", `moins de ${WEAK_MONTH_DECKS} decks`, "à 100 decks, une part de 10 % est connue à ±6 points près"],
              ["Fiche de composition d’un archétype", "8 listes", "9 à 13 % d’étiquettes instables à 8 listes, 19 à 24 % à 5"],
              ["Banlist retenue dans le backtest", "600 decks", "mesure du 14 août 2026 : la seule liste sous ce volume (OCG d’avril 2026, 416 decks à l’époque) tombait au niveau du hasard"],
              ["Archétype classé Rogue", "moins de 5 decks", "pas de part ni de tendance lisible en dessous"],
              ["Libellé boutique Fort / Modéré", rule ? `rang ${rule.strong_max_rank} / rang ${rule.moderate_max_rank} sur ${rule.population}` : "10 % / 25 % des archétypes", "premiers 10 % et 25 % ; provisoires, non validés hors échantillon"],
            ]}
          />
          <DataFooter
            source="documentation du projet et calculs des scripts"
            date="seuils en vigueur au 17 novembre 2026"
            uncertainty="les seuils de 8 listes et 600 decks viennent de mesures ; ceux du libellé boutique n’ont pas pu être validés (une seule série datée)"
          />
        </div>
      </Section>

      <Section id="tier-list" title="Tier list">
        <Facts
          items={[
            { term: "Ce que mesure", text: "La part des decks de tournoi TCG de la fenêtre qui jouent chaque archétype, et l’écart avec la fenêtre précédente." },
            { term: "Seuils", text: "T0 dès 40 % des decks, T1 dès 15 %, T2 dès 7 %, T3 dès 3 %, Rogue en dessous ou sous 5 decks." },
            { term: "Tendance", text: "Affichée seulement si l’écart avec la fenêtre précédente dépasse le bruit d’échantillonnage, testé archétype par archétype." },
            { term: "Limites", text: "La fenêtre courante compte quelques centaines de decks : un archétype à 2 % repose sur une dizaine de listes." },
          ]}
        />
        <Validation title="Tendances dues au hasard">
          <SimpleTable
            caption="Nombre de tendances attendues par hasard"
            head={["Archétypes comparés", "Niveau du test", "Fausses tendances attendues"]}
            rows={[["environ 60", "5 %", "environ 3"]]}
          />
          <DataFooter
            source="tier list"
            date={`fenêtre ${fmtMonthShort(tierList.window_start)} à ${fmtMonthShort(tierList.window_end)}`}
            uncertainty="ordre de grandeur, pas une mesure : il suppose des archétypes indépendants"
          />
        </Validation>
      </Section>

      <Section id="decks" title="Decks">
        <Facts
          items={[
            { term: "Ce que mesure", text: "Pour chaque archétype, la part de ses listes qui jouent chaque carte, et le nombre médian d’exemplaires." },
            { term: "Seuils", text: "Carte de base dans au moins 80 % des listes, d’appoint dans au moins 20 % ; fiche à partir de 8 listes." },
            { term: "Fenêtre", text: "La même que la tier list : les effectifs des deux pages sont égaux." },
            { term: "Limites", text: "Pas d’intervalle affiché : à 8 listes il serait trop large pour être lu ; chaque part est donnée avec son effectif." },
          ]}
        />
        <Validation title="Stabilité des étiquettes selon le nombre de listes">
          <SimpleTable
            caption="Part des étiquettes de base ou d’appoint qui changent d’un tirage de listes à l’autre"
            head={["Listes par archétype", "Étiquettes qui changent"]}
            rows={[
              ["5", "19 à 24 %"],
              ["8", "9 à 13 %"],
            ]}
          />
          <DataFooter
            source="rééchantillonnage des listes d’Elfnote et d’Angelechy"
            date="mesure du 16 novembre 2026"
            uncertainty="deux archétypes seulement ; l’écart entre 5 et 8 listes est net, sa valeur exacte ne l’est pas"
          />
        </Validation>
      </Section>

      <Section id="evolution" title="Évolution et parts mensuelles">
        <Facts
          items={[
            { term: "Ce que mesure", text: "Chaque mois, la part des decks de tournoi TCG relevés qui jouent l’archétype." },
            {
              term: "Incertitude",
              text: "Une bande à 95 % entoure chaque part. Elle s’élargit quand le mois compte peu de decks ou quand la part est proche de 50 %.",
            },
            { term: "Mois atténués", text: `Moins de ${WEAK_MONTH_DECKS} decks dans le mois, ou mois en cours de relevé : point et segment en pointillé, plus pâles.` },
            {
              term: "Limites",
              text: "La bande suppose des decks indépendants ; plusieurs listes d’un même joueur ou d’un même tournoi la rendent trop étroite.",
            },
          ]}
        />
        <div id="part-mensuelle" className="scroll-mt-24">
          <Validation title="Mois relevés selon leur nombre de decks">
            <SimpleTable
              caption="Nombre de mois relevés au-dessus et en dessous de 100 decks"
              head={["Mois", "Nombre", "Période"]}
              rows={[
                [
                  `au moins ${WEAK_MONTH_DECKS} decks`,
                  fmtNum(fullMonths),
                  firstFull ? `${fmtMonthShort(firstFull)} à ${fmtMonthShort(months[months.length - 1][0])}` : "—",
                ],
                [
                  `moins de ${WEAK_MONTH_DECKS} decks`,
                  fmtNum(weakMonths.length),
                  weakMonths.length ? weakMonths.map(([m, n]) => `${fmtMonthShort(m)} (${fmtNum(n)})`).join(", ") : "aucun",
                ],
              ]}
            />
            <DataFooter
              source={`decks de tournoi TCG, ${DECK_SOURCE}`}
              date={months.length ? `${fmtMonthShort(months[0][0])} à ${fmtMonthShort(months[months.length - 1][0])}` : "aucun mois"}
              sample={`${fmtNum(months.reduce((sum, [, n]) => sum + n, 0))} decks`}
              uncertainty="comptes exacts ; le dernier mois est incomplet tant qu’il n’est pas terminé"
            />
          </Validation>
        </div>
      </Section>

      <Section id="predictions" title="Prédictions">
        <Facts
          items={[
            { term: "Ce que mesure", text: "Le score méta attendu le mois suivant si la situation récente se prolonge, en ramenant les écarts vers la moyenne." },
            { term: "Construction", text: "Pour l’essentiel la valeur du mois observé, corrigée d’une part de retour à la moyenne apprise sur l’historique." },
            { term: "Incertitude", text: "Aucun intervalle par archétype : le modèle ne produit qu’une valeur." },
            { term: "Limites", text: "N’anticipe ni les ruptures (banlist, nouvelle extension) ni l’arrivée d’un nouvel archétype." },
          ]}
        />
        <Validation title="Erreur, rejouée mois par mois sur l’historique">
          <SimpleTable
            caption="Erreur de prévision comparée à deux références"
            head={["Référence", "Erreur du modèle"]}
            rows={[
              ["« rien ne change » (valeur du mois observé)", "environ 5 % de moins"],
              ["retour à la moyenne seul", "équivalente"],
            ]}
          />
          <DataFooter
            source="validation glissante dans le temps (notebook 05)"
            date="dernier calcul du modèle"
            uncertainty="gain faible : le modèle fait à peine mieux que la valeur du mois observé"
          />
        </Validation>
      </Section>

      <Section id="ban-radar" title="Ban Radar">
        <Facts
          items={[
            { term: "Ce que mesure", text: "La ressemblance de chaque carte avec le profil des cartes déjà touchées par Konami, sur six critères." },
            { term: "Critère décisif", text: "Le nombre moyen d’exemplaires joués : 2,5 chez les cartes touchées contre 1,1 chez les autres (mesure d’août 2026)." },
            { term: "Fenêtre", text: "Les 6 derniers mois de decks de tournoi TCG." },
            { term: "Limites", text: "Un score de risque, pas une probabilité. Le méta Genesys, exclu des données, lui échappe." },
          ]}
        />
      </Section>

      <Section id="ban-historique" title="Ban Radar contre l’historique">
        <Facts
          items={[
            { term: "Protocole", text: "Chaque banlist est rejouée avec les decks des 6 mois qui précèdent son entrée en vigueur, jamais avec des données postérieures." },
            { term: "Hasard", text: "Rangs médians qu’on obtiendrait en tirant au sort autant de cartes : 90 % des tirages tombent dans la bande." },
            { term: "Base de comparaison", text: "Classer simplement les cartes par part des decks (« staples les plus jouées »)." },
            {
              term: "Résultat défavorable",
              text: `En TCG, cette base bat le score en rang médian sur ${fmtNum(tcgBaselineWins)} listes sur ${fmtNum(tcgRetained)}. Les listes de septembre et octobre 2026 sont proches du hasard.`,
            },
          ]}
        />
        <Validation title="Rang médian des cartes touchées, liste par liste">
          <BanTable lists={banHistory.lists} />
          <DataFooter
            source="decks de tournoi (yugiohmeta.com), banlists (Yugipedia)"
            date={`calcul du ${fmtDate(banHistory.computed_at)}`}
            sample={`${fmtNum(retained.length)} listes retenues sur ${fmtNum(banHistory.lists.length)}`}
            uncertainty="barre pâle : 90 % des rangs médians d’un tirage au hasard ; point en couleur : rang médian meilleur que le hasard ; rang 1 à gauche"
          >
            seules les listes postérieures au 14 août 2026 sont indépendantes du réglage du score ;{" "}
            <Link href="/ban?tab=historique" className="underline decoration-line-2 underline-offset-4 hover:text-text">
              détail par liste
            </Link>
          </DataFooter>
        </Validation>
      </Section>

      <Section id="boutique" title="Signaux boutique">
        <Facts
          items={[
            { term: "Ce que mesure", text: "Les archétypes joués en OCG dont au moins 3 cartes clés ne sont pas encore sorties en TCG, classés par leur poids en OCG." },
            {
              term: "Libellé",
              text: rule
                ? `Rang parmi les ${rule.population} archétypes OCG suivis : Fort jusqu’au rang ${rule.strong_max_rank}, Modéré jusqu’au rang ${rule.moderate_max_rank}. Seuils provisoires.`
                : "Rang parmi les archétypes OCG suivis. Seuils provisoires.",
            },
            { term: "Arrivée en TCG", text: "Période où 8 archétypes sur 10 sont arrivés en TCG par le passé : 75 à 202 jours après le premier deck OCG, mesurée sur 1 897 cartes sorties de 2022 à 2025." },
            { term: "Limites", text: "Rien n’est encore échu pour juger les signaux actuels ; la fenêtre d’arrivée n’a pas été vérifiée sur des cas nouveaux." },
          ]}
        />
        <Validation title="Lien entre OCG et TCG">
          <div className="grid max-w-[560px] gap-2 rounded-[6px] border border-line bg-ink-2 px-4 py-4">
            <p className="flex items-baseline justify-between font-mono text-[12px] text-muted-text">
              <span>corrélation, {SITE_FACTS.ocgTcgArchetypes} archétypes</span>
              <span className="text-[14px] font-medium text-text tabular-nums">{fmtNum(SITE_FACTS.ocgTcgCorrelation, 2)}</span>
            </p>
            <IntervalBar
              value={SITE_FACTS.ocgTcgCorrelation}
              lo={ciLow}
              hi={ciHigh}
              max={1}
              label={`Corrélation ${fmtNum(SITE_FACTS.ocgTcgCorrelation, 2)}, intervalle à 95 % de ${fmtNum(ciLow, 2)} à ${fmtNum(ciHigh, 2)}`}
            />
            <p className="flex justify-between font-mono text-[12px] text-muted-text tabular-nums">
              <span>0</span>
              <span>
                95 % : {fmtNum(ciLow, 2)} à {fmtNum(ciHigh, 2)}
              </span>
              <span>1</span>
            </p>
          </div>
          <DataFooter
            source="parts OCG et TCG des archétypes, decks de tournoi"
            date={`décalage de ${SITE_FACTS.ocgTcgLagRange}, recalcul du 16 novembre 2026`}
            sample={`${SITE_FACTS.ocgTcgArchetypes} archétypes`}
            uncertainty="segment : intervalle à 95 % ; l’ancienne valeur affichée (0,77 sur 43 archétypes) n’est plus reproductible"
          />
        </Validation>
        <Validation title="Signal de juin 2026">
          <SimpleTable
            caption="Évolution des prix des cartes du signal de juin 2026 comparée au marché"
            head={["Groupe", "Évolution du prix"]}
            rows={[
              ["cartes du signal de juin 2026", fmtPct(-35, 0)],
              ["marché (toutes cartes suivies)", fmtPct(-1, 0)],
            ]}
          />
          <DataFooter
            source="prix Cardmarket (YGOPRODeck)"
            date="signal de juin 2026"
            uncertainty="une seule série datée : un échec net, mais pas une mesure de la fiabilité générale"
          />
        </Validation>
      </Section>

      <Section id="signaux-precoces" title="Signaux précoces">
        <Facts
          items={[
            { term: "Ce que mesure", text: "Une note de 0 à 100 qui réunit les vues d’une carte récente sur une semaine, sa présence dans les decks de la méta et le niveau de son archétype." },
            { term: "Validation", text: "Aucune à ce jour : la note ordonne les cartes, elle n’a pas été confrontée à ce que les cartes sont devenues." },
            { term: "Limites", text: "Les vues des cartes anciennes ne sont pas rafraîchies au même rythme que celles des cartes nouvelles." },
          ]}
        />
      </Section>

      <Section id="graphe" title="Graphe de synergies">
        <Facts
          items={[
            { term: "Ce que mesure", text: "Deux cartes sont reliées quand, parmi les decks qui jouent l’une ou l’autre, au moins 15 % jouent les deux." },
            { term: "Affichage", text: `Les 200 cartes les plus connectées ; ${SITE_FACTS.graphCommunities} communautés de cartes détectées.` },
            { term: "Cartes pont", text: "Cartes qui relient des groupes de cartes qui, sans elles, se jouent rarement ensemble." },
            { term: "Limites", text: "La date du calcul n’est pas enregistrée dans la base servie ; un lien proche du seuil peut changer d’un calcul à l’autre." },
          ]}
        />
      </Section>
    </Page>
  );
}
