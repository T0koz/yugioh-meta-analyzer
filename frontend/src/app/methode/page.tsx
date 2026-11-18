import type { Metadata } from "next";
import Link from "next/link";
import { api } from "@/lib/api";
import { fmtDate, fmtMonthShort, fmtNum, fmtPct } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { BAN_VERDICT } from "@/lib/ban-verdict";
import { SITE_FACTS } from "@/lib/site-facts";
import { WEAK_MONTH_DECKS } from "@/lib/wilson";
import { Em } from "@/components/ds/em";
import { IntervalBar } from "@/components/ds/explain";
import { DataFooter, Page, PageHero } from "@/components/ds/page";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BanHistoryList } from "@/types";
import { earlyTextNote } from "@/lib/early-signals";

// Page Méthode (lot 15, charte « ton et explication » §4) : une section par outil,
// dans l'ordre de la navigation ; sources, dates, seuils et leur origine, résultats
// des validations ÉCHECS COMPRIS, limites. Aucune formule : chaque méthode est
// décrite par ce qu'elle mesure. Les ancres sont celles des couches « Méthode »
// (MethodNote) des pages d'outil : ne pas les renommer sans les suivre.

export const metadata: Metadata = pageMetadata({
  title: "Méthode",
  description:
    "Sources, dates de collecte, seuils et résultats des validations de chaque outil, échecs compris. Aucune formule.",
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
            return (
              <TableRow key={`${l.format}-${l.effective_date}`}>
                <TableCell className="text-[14px] whitespace-nowrap text-soft">
                  {l.format} · {fmtDate(l.effective_date)}
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
                      color="var(--soft)"
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
  const [tierList, evolution, banHistory, boutique, prices, early] = await Promise.all([
    api.tierList(),
    api.evolution(),
    api.banHistory(),
    api.boutiqueSignals(),
    api.boutiquePrices(),
    api.earlySignals(),
  ]);

  const months = Object.entries(evolution.decks_by_month).sort(([a], [b]) => a.localeCompare(b));
  const weakMonths = months.filter(([, n]) => n < WEAK_MONTH_DECKS);
  const fullMonths = months.length - weakMonths.length;
  const firstFull = months.find(([, n]) => n >= WEAK_MONTH_DECKS)?.[0];
  const rule = boutique.label_rule;
  const retained = banHistory.lists.filter((l) => l.retained);
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
            caption="Seuils et poids appliqués sur le site, leur origine et leur date"
            head={["Réglage", "Valeur", "Origine"]}
            rows={[
              ["Mois atténué dans les séries", `moins de ${WEAK_MONTH_DECKS} decks`, "fixé à la main le 17 novembre 2026, d’après une mesure : à 100 decks, une part de 10 % est connue à ±6 points près"],
              ["Fiche de composition d’un archétype", "8 listes", "fixé à la main le 16 novembre 2026, d’après une mesure : 9 à 13 % d’étiquettes instables à 8 listes, 19 à 24 % à 5"],
              ["Carte de base / d’appoint (Decks)", "80 % / 20 % des listes", "fixés à la main le 16 novembre 2026 : seuils ronds ; 80 % donne un cœur de deck plausible, ce n’est pas un optimum"],
              ["Seuils de tier", "T0 40 %, T1 15 %, T2 7 %, T3 3 % des decks", "fixés à la main le 16 novembre 2026 : seuils ronds, conventionnels ; un classement descriptif, sans validation"],
              ["Archétype classé Rogue", "moins de 5 decks", "fixé à la main le 16 novembre 2026 : pas de part ni de tendance lisible en dessous"],
              ["Poids du Ban Radar", "part des decks 30 %, porteur 25 %, exemplaires 20 %, restriction 10 %, élan 10 %, pont 5 %", "fixés à la main le 14 août 2026, pas estimés sur les données ; 3 des 20 banlists rejouées sont postérieures à ce réglage ; le classement y est sensible"],
              ["Banlist retenue dans le backtest", "600 decks", "fixé à la main le 14 août 2026, d’après une mesure : la seule liste sous ce volume (OCG d’avril 2026, 416 decks à l’époque) tombait au niveau du hasard"],
              ["Libellé boutique Fort / Modéré", rule ? `rang ${rule.strong_max_rank} / rang ${rule.moderate_max_rank} sur ${rule.population}` : "10 % / 25 % des archétypes", "fixés à la main le 16 novembre 2026 : premiers 10 % et 25 % ; provisoires, non validés hors échantillon"],
              ["Signaux précoces", "vues 35 %, texte 35 %, OCG 30 % ; sortie TCG depuis moins de 168 jours ; moins de 3 % des decks sur 90 jours", "fixés à la main (notebook de juin 2026, filtres ajoutés le 18 novembre 2026) ; jamais validés"],
              ["Direction des prédictions", "écart dessiné d’au moins 0,3 point", "fixé à la main, repris du modèle de prévision (seuil sur la variation complète, ramené à l’échelle dessinée)"],
            ]}
          />
          <DataFooter
            source="documentation du projet et calculs des scripts"
            date="réglages en vigueur au 18 novembre 2026"
            uncertainty="aucun de ces réglages n’est estimé sur les données ni validé hors échantillon ; ceux de 100 decks, 8 listes et 600 decks s’appuient sur une mesure"
          />
        </div>
      </Section>

      <Section id="tier-list" title="Tier list">
        <Facts
          items={[
            { term: "Ce que mesure", text: "La part des decks de tournoi TCG de la fenêtre qui jouent chaque archétype, et l’écart avec la fenêtre précédente." },
            { term: "Seuils", text: "T0 dès 40 % des decks, T1 dès 15 %, T2 dès 7 %, T3 dès 3 %, Rogue en dessous ou sous 5 decks. Seuils ronds, fixés à la main." },
            { term: "Tendance", text: "Écart avec la fenêtre précédente testé archétype par archétype, puis corrigé pour le nombre de tests : en moyenne, au plus 5 % des tendances affichées seraient dues au hasard. Contrôle approché : les parts d’une même fenêtre sont liées entre elles, un effet faible vérifié par simulation." },
            { term: "À la limite", text: "Tier marqué « limite » quand l’intervalle à 95 % de la part contient un seuil : avec d’autres decks, l’archétype pourrait passer au tier d’à côté." },
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
            { term: "Seuils", text: "Carte de base dans au moins 80 % des listes, d’appoint dans au moins 20 % (seuils ronds, fixés à la main) ; fiche à partir de 8 listes." },
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
              text: "Intervalle minimal : il suppose des decks indépendants, plusieurs listes d’un même joueur ou d’un même tournoi le rendent trop étroit. Deux bandes qui se chevauchent ou non ne valent pas un test d’écart entre deux mois.",
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
            { term: "Ce que mesure", text: "Le score méta attendu le mois qui suit le dernier mois complet observé si la situation récente se prolonge, en ramenant les écarts vers la moyenne. Ce mois est en général le mois en cours au calcul : ses decks déjà relevés ne sont pas utilisés." },
            { term: "Construction", text: "Pour l’essentiel la valeur du mois observé, corrigée d’une part de retour à la moyenne apprise sur l’historique." },
            { term: "Incertitude", text: "Aucun intervalle par archétype : le modèle ne produit qu’une valeur." },
            { term: "Limites", text: "N’anticipe ni les ruptures (banlist, nouvelle extension) ni l’arrivée d’un nouvel archétype." },
          ]}
        />
        <Validation title="Erreur, rejouée mois par mois sur l’historique">
          <SimpleTable
            caption="Erreur de prévision comparée à deux références, avec intervalle à 95 %"
            head={["Comparaison", "Résultat", "Intervalle à 95 %"]}
            rows={[
              ["erreur sur la variation du score, contre « rien ne change »", "6 % de moins (0,20 point)", "0,10 à 0,30 point de moins"],
              ["classement des archétypes par score prévu, contre « rien ne change »", "aucun écart démontré (écart de corrélation de rang +0,01)", "−0,01 à +0,04"],
              ["contre le retour à la moyenne seul", "équivalente", "—"],
            ]}
          />
          <DataFooter
            source="validation glissante dans le temps, decks TCG seuls, 24 mois de test, 519 prévisions"
            date="évaluation du 16 novembre 2026"
            uncertainty="intervalles à 95 % par rééchantillonnage des mois ; points de score ×100 ; gain faible et limité à la variation : en niveau, le modèle ne classe pas mieux que la valeur du mois observé"
          >
            la part du modèle (30 %) a été choisie sur ces mêmes 24 mois
          </DataFooter>
        </Validation>
      </Section>

      <Section id="ban-radar" title="Ban Radar">
        <Facts
          items={[
            { term: "Ce que mesure", text: "La ressemblance de chaque carte avec le profil des cartes déjà touchées par Konami, sur six critères." },
            { term: "Critères", text: "Part des decks, archétype porteur, exemplaires joués, restriction en cours, élan sur 3 mois, position de pont." },
            { term: "Fenêtre", text: "Les 6 derniers mois de decks de tournoi TCG." },
            { term: "Poids", text: "Fixés à la main le 14 août 2026, pas estimés sur les données. 3 des 20 banlists rejouées sont postérieures à ce réglage ; les autres étaient connues au moment du réglage." },
            { term: "Limites", text: "Un score de risque, pas une probabilité. Le méta Genesys, exclu des données, lui échappe." },
            { term: "Résultat", text: BAN_VERDICT.measures },
          ]}
        />
      </Section>

      <Section id="ban-historique" title="Ban Radar contre l’historique">
        <Facts
          items={[
            { term: "Protocole", text: "Chaque banlist est rejouée avec les decks des 6 mois qui précèdent son entrée en vigueur, jamais avec des données postérieures. Exception : le critère « pont » vient du graphe actuel ; effet mesuré négligeable (le retirer change de 2 le nombre de cartes touchées dans le top 25 TCG)." },
            { term: "Hasard", text: "Rangs médians qu’on obtiendrait en tirant au sort autant de cartes : 90 % des tirages tombent dans la bande." },
            { term: "Base de comparaison", text: "Classer simplement les cartes par part des decks (« staples les plus jouées »)." },
            { term: "Lecture", text: BAN_VERDICT.significance },
          ]}
        />
        <Validation title="Rang médian des cartes touchées, liste par liste">
          <BanTable lists={banHistory.lists} />
          <DataFooter
            source="decks de tournoi (yugiohmeta.com), banlists (Yugipedia)"
            date={`calcul du ${fmtDate(banHistory.computed_at)}`}
            sample={`${fmtNum(retained.length)} listes retenues sur ${fmtNum(banHistory.lists.length)}`}
            uncertainty="barre pâle : 90 % des rangs médians d’un tirage au hasard ; point : rang médian des cartes touchées ; rang 1 à gauche"
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
            { term: "Arrivée en TCG", text: `De 75 à 202 jours après le premier deck OCG : délai de 8 cartes sur 10 parmi les ${fmtNum(SITE_FACTS.arrivalWindowCards)} cartes sorties en OCG de 2022 à 2025 puis en TCG. La mesure porte sur des cartes, pas sur des archétypes, et ignore les cartes jamais sorties en TCG.` },
            {
              term: "Couverture vérifiée",
              text: `Fenêtre estimée sur les cartes de 2022-2023, puis appliquée aux cartes suivantes : elle contient le délai de ${SITE_FACTS.arrivalCoverage.map((c) => `${c.pct} % des ${fmtNum(c.cards)} cartes de ${c.year}`).join(" et ")}, et non 80 %.`,
            },
            {
              term: "Comparaison naïve",
              text: `Le classement suit presque la seule part des decks OCG : corrélation de rang ${fmtNum(SITE_FACTS.ocgScoreShareRho, 2)} sur ${SITE_FACTS.ocgScoreArchetypes} archétypes (recalcul du 18 novembre 2026). Aucun test ne montre encore qu’il fait mieux.`,
            },
            { term: "Limites", text: "Rien n’est encore échu pour juger les signaux actuels." },
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
          >
            mesuré sur des archétypes déjà joués en OCG et en TCG : ce lien ne valide pas le signal boutique, qui porte sur des archétypes pas encore sortis en TCG
          </DataFooter>
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
            { term: "Ce que mesure", text: "Une note de 0 à 100 qui réunit les vues d’une carte récente sur une semaine, la proximité de son texte avec celui des cartes des 20 archétypes de la méta récente, et le poids de son archétype en OCG. Les decks où la carte est jouée n’entrent pas dans la note." },
            { term: "Cartes retenues", text: "Sorties en TCG dans les 168 jours qui précèdent le dernier deck relevé, ou pas encore sorties ; ni interdites ni limitées dans la banlist TCG en vigueur à cette date ; jouées dans moins de 3 % des decks TCG des 90 derniers jours (seuil du tier T3)." },
            { term: "Validation", text: "Aucune à ce jour : la note ordonne les cartes, elle n’a pas été confrontée à ce que les cartes sont devenues." },
            { term: "Limites", text: `${earlyTextNote(early) ?? ""} Les vues des cartes anciennes ne sont pas rafraîchies au même rythme que celles des cartes nouvelles.`.trim() },
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
