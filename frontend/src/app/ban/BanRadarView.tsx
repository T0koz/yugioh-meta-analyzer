import { api } from "@/lib/api";
import { fmtDate, fmtNum, fmtPct } from "@/lib/format";
import { CardChip } from "@/components/card-chip";
import { Em } from "@/components/ds/em";
import { Explainer, PageHero } from "@/components/ds/page";
import { BanStatus } from "@/components/ds/tags";
import type { BanRadarCriteria, BanRadarEntry, BanRadarKind, RiskLabel } from "@/types";
import { KindFilterTabs } from "./kind-filter";

// Ordre et libellés de la barre de décomposition, alignés sur WEIGHTS côté API.
// Une seule teinte : l'opacité décroît avec le poids du critère (design system §4).
const CRITERIA: { key: keyof BanRadarCriteria; label: string; opacity: number; help: string }[] = [
  { key: "ubiquity", label: "Ubiquité", opacity: 0.9, help: "Part des decks du format qui jouent la carte." },
  { key: "carrier", label: "Porteur", opacity: 0.75, help: "La carte est indispensable à un archétype qui pèse dans la méta." },
  { key: "copies", label: "Copies", opacity: 0.6, help: "Nombre moyen d'exemplaires joués : une carte jouée à 3 peut être limitée, une carte déjà à 1 beaucoup moins." },
  { key: "restriction", label: "Restriction", opacity: 0.45, help: "La carte est déjà Limited ou Semi-Limited : Konami y revient souvent." },
  { key: "momentum", label: "Élan", opacity: 0.3, help: "Usage des 3 derniers mois comparé aux 3 précédents." },
  { key: "bridge", label: "Pont", opacity: 0.18, help: "Centralité de type pont : la carte relie des paquets de cartes autrement séparés." },
];

// L'accent ne marque que les risques qui comptent ; le libellé porte toujours l'information.
const RISK_TONE: Record<RiskLabel, string> = {
  Critique: "text-signal",
  Élevé: "text-signal",
  Modéré: "text-muted-text",
  Faible: "text-muted-text",
};

// Dernière colonne de largeur fixe : avec `auto`, la longueur du statut
// (UNLIMITED / SEMI-LIMITED) ferait varier celle des barres d'une ligne à l'autre.
export const ROW_GRID =
  "grid grid-cols-[84px_34px_minmax(0,1fr)] items-center gap-x-4 gap-y-3 border-t border-line px-1 py-5 min-[760px]:grid-cols-[110px_40px_minmax(0,1fr)_140px] min-[760px]:gap-x-[22px]";

export function BigScore({ value, label, tone }: { value: string; label: string; tone: string }) {
  return (
    <div className="text-[clamp(40px,5vw,60px)] leading-none font-medium tracking-[-0.05em] tabular-nums">
      {value}
      <small className={`mt-1.5 block font-mono text-[11px] font-normal tracking-[0.1em] uppercase ${tone}`}>{label}</small>
    </div>
  );
}

function CriteriaStack({ criteria, score }: { criteria: BanRadarCriteria; score: number }) {
  return (
    <div className="mt-3 flex h-2 gap-0.5 overflow-hidden rounded-[2px] bg-ink-4">
      {CRITERIA.map(({ key, label, opacity }) => {
        const contribution = criteria[key];
        if (contribution <= 0) return null;
        return (
          <i
            key={key}
            className="block h-full bg-signal"
            style={{ width: `${contribution}%`, opacity }}
            title={`${label} : ${fmtNum(contribution, 1)} pts sur ${fmtNum(score, 1)}`}
          />
        );
      })}
    </div>
  );
}

function CriteriaLegend() {
  return (
    <div className="mt-2 flex flex-wrap gap-x-3.5 gap-y-1 font-mono text-[10.5px] tracking-[0.06em] text-muted-text uppercase">
      {CRITERIA.map((c) => (
        <span key={c.key} className="inline-flex items-center gap-1.5">
          <span className="inline-block h-[7px] w-[7px] rounded-[1px] bg-signal" style={{ opacity: c.opacity }} />
          {c.label}
        </span>
      ))}
    </div>
  );
}

function RadarRow({ entry, rank }: { entry: BanRadarEntry; rank: number }) {
  // top_archetype est nul quand la carte est jouée un peu partout sans deck
  // d'attache : c'est une staple, pas une pièce d'archétype.
  const origin = entry.top_archetype ?? "Générique";
  const score = entry.ban_risk_score;

  return (
    <div className={ROW_GRID}>
      <BigScore value={fmtNum(score, Number.isInteger(score) ? 0 : 1)} label={entry.risk_label} tone={RISK_TONE[entry.risk_label]} />
      <span className="font-mono text-[12px] text-faint">#{rank}</span>
      <div className="min-w-0">
        <h3 className="text-[20px] leading-tight font-medium tracking-[-0.02em] [overflow-wrap:anywhere]">
          <CardChip name={entry.card_name} subtitle={origin} variant="plain" />
        </h3>
        <p className="mt-1 font-mono text-[12px] text-muted-text">
          {[
            origin,
            `${fmtPct(entry.deck_share)} des decks`,
            `${fmtNum(entry.mean_copies, 1)} ex. en moyenne`,
            `${fmtNum(entry.n_archetypes)} archétypes`,
          ].join(" · ")}
        </p>
        <CriteriaStack criteria={entry.criteria} score={score} />
        {rank === 1 && <CriteriaLegend />}
      </div>
      <div className="col-start-3 min-[760px]:col-start-auto min-[760px]:justify-self-end">
        <BanStatus status={entry.current_status} />
      </div>
    </div>
  );
}

export async function BanRadarView({ kind, tabs }: { kind?: BanRadarKind; tabs: React.ReactNode }) {
  const { data, as_of, n_decks_window } = await api.banRadar({ limit: 50, kind });

  return (
    <>
      <PageHero
        eyebrow="Ban Center · Radar"
        title={
          <>
            Qui sera <Em>banni</Em> ensuite ?
          </>
        }
        aside={
          <>
            Données au {fmtDate(as_of)}
            <br />
            {fmtNum(n_decks_window)} decks · 6 mois
          </>
        }
        intro="Les cartes les plus exposées à la prochaine banlist TCG, notées sur six critères."
      >
        {tabs}
      </PageHero>

      <Explainer label="Comment lire ce score ?" title="Lecture du score">
        <p>
          C’est un score de <strong className="font-medium text-text">risque</strong>, pas une probabilité : il
          classe les cartes par ressemblance au profil de celles que Konami a historiquement touchées. Il ne dit pas
          « X % de chances d’être bannie ».
        </p>
        <p>Rejoué la veille des banlists passées (listes dont la fenêtre compte au moins 600 decks : dix en TCG, dix en OCG) :</p>
        <ul className="grid gap-1.5">
          <li>
            <strong className="font-medium text-text">TCG, 18 mai 2026</strong> : rang médian 84 sur 889 cartes notées
            pour les cartes réellement touchées (le hasard donnerait environ 445).
          </li>
          <li>
            <strong className="font-medium text-text">OCG, 1er juillet 2026</strong> : rang médian 19 sur 1 236. Le
            score n’a jamais été calibré sur l’OCG : c’est un test hors distribution, et il y réussit mieux qu’en TCG.
          </li>
          <li>
            <strong className="font-medium text-text">TCG, 21 septembre et 19 octobre 2026</strong> : les deux listes
            les plus récentes sont mauvaises (rang médian 206 sur 981, puis 308 sur 905, proche du hasard). Le haut du
            classement tient, mais la liste d’octobre touche 43 cartes dont beaucoup de marginales, et le méta
            Genesys, exclu des données, échappe au score.
          </li>
        </ul>
        <p>Résultats mitigés selon les listes : c’est encourageant, ce n’est pas une validation.</p>
        <p>
          Les <strong className="font-medium text-text">staples génériques</strong> trustent le haut du classement parce
          qu’elles sont jouées partout à 3 exemplaires, mais Konami frappe surtout les pièces de moteur des decks qui
          gagnent. Le filtre « Pièces d’archétype » isole ces dernières.
        </p>
        <p>La barre sous chaque carte décompose le score : un segment par critère, en points sur 100.</p>
        <dl className="grid gap-1 font-mono text-[12px]">
          {CRITERIA.map((c) => (
            <div key={c.key} className="flex gap-2">
              <dt className="flex shrink-0 items-center gap-1.5 text-text uppercase">
                <span className="inline-block h-[7px] w-[7px] rounded-[1px] bg-signal" style={{ opacity: c.opacity }} />
                {c.label}
              </dt>
              <dd className="font-sans text-[13px]">{c.help}</dd>
            </div>
          ))}
        </dl>
      </Explainer>

      <KindFilterTabs basePath="/ban?tab=radar" active={kind} count={`Top ${data.length}`} />

      <div className="border-b border-line">
        {data.map((entry, index) => (
          <RadarRow key={entry.card_name} entry={entry} rank={index + 1} />
        ))}
      </div>
    </>
  );
}
