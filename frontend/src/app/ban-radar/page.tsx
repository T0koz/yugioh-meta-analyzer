import Link from "next/link";
import { api } from "@/lib/api";
import { CardChip } from "@/components/card-chip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import type { BanRadarCriteria, BanRadarEntry, RiskLabel } from "@/types";

const RISK_STYLE: Record<RiskLabel, { badge: string; score: string }> = {
  Critique: { badge: "bg-red-600 text-white", score: "text-red-400" },
  Élevé: { badge: "bg-orange-500 text-white", score: "text-orange-400" },
  Modéré: { badge: "bg-yellow-500 text-black", score: "text-yellow-400" },
  Faible: { badge: "bg-slate-600 text-white", score: "text-slate-400" },
};

const STATUS_STYLE: Record<string, string> = {
  Limited: "bg-orange-500/15 text-orange-300 border-orange-500/40",
  "Semi-Limited": "bg-yellow-500/15 text-yellow-300 border-yellow-500/40",
  Unlimited: "bg-slate-700/40 text-slate-400 border-slate-700",
};

// Ordre et libellés de la barre de décomposition, alignés sur WEIGHTS côté API.
const CRITERIA: { key: keyof BanRadarCriteria; label: string; color: string; help: string }[] = [
  { key: "ubiquity", label: "Omniprésence", color: "#6366f1", help: "Part des decks du format qui jouent la carte." },
  { key: "carrier", label: "Pièce de moteur", color: "#8b5cf6", help: "La carte est indispensable à un archétype qui pèse dans la méta." },
  { key: "copies", label: "Marge de restriction", color: "#ec4899", help: "Nombre moyen d'exemplaires joués : une carte jouée à 3 peut être limitée, une carte déjà à 1 beaucoup moins." },
  { key: "restriction", label: "Déjà touchée", color: "#f59e0b", help: "La carte est déjà Limited ou Semi-Limited : Konami y revient souvent." },
  { key: "momentum", label: "En hausse", color: "#22c55e", help: "Usage des 3 derniers mois comparé aux 3 précédents." },
  { key: "bridge", label: "Pont du graphe", color: "#38bdf8", help: "Centralité de type pont : la carte relie des paquets de cartes autrement séparés." },
];

function CriteriaBar({ criteria, score }: { criteria: BanRadarCriteria; score: number }) {
  return (
    <div className="flex h-2 w-full overflow-hidden rounded-full bg-slate-800">
      {CRITERIA.map(({ key, label, color }) => {
        const contribution = criteria[key];
        if (contribution <= 0) return null;
        return (
          <div
            key={key}
            style={{ width: `${contribution}%`, backgroundColor: color }}
            title={`${label} : ${contribution.toFixed(1)} pts sur ${score.toFixed(1)}`}
          />
        );
      })}
    </div>
  );
}

function RadarRow({ entry, rank }: { entry: BanRadarEntry; rank: number }) {
  const style = RISK_STYLE[entry.risk_label];
  const dominant = CRITERIA.reduce((best, c) =>
    entry.criteria[c.key] > entry.criteria[best.key] ? c : best
  );
  // top_archetype est nul quand la carte est jouée un peu partout sans deck
  // d'attache : c'est une staple, pas une pièce d'archétype.
  const origin = entry.top_archetype ?? "Générique";

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 px-5 py-4">
      <div className="flex items-center gap-4">
        <span className="w-6 shrink-0 text-right text-sm tabular-nums text-slate-600">{rank}</span>

        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold">
            <CardChip name={entry.card_name} subtitle={origin} />
          </p>
          <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
            <span>{origin}</span>
            <span>·</span>
            <span className="tabular-nums">{entry.deck_share.toFixed(1)}% des decks</span>
            <span>·</span>
            <span className="tabular-nums">{entry.mean_copies.toFixed(1)} ex. en moyenne</span>
            <span
              className={`rounded border px-1.5 py-0.5 ${STATUS_STYLE[entry.current_status] ?? STATUS_STYLE.Unlimited}`}
            >
              {entry.current_status}
            </span>
          </p>
        </div>

        <div className="shrink-0 text-right">
          <p className={`text-2xl font-bold tabular-nums ${style.score}`}>
            {entry.ban_risk_score.toFixed(0)}
          </p>
          <span className={`inline-block rounded px-2 py-0.5 text-[10px] font-bold ${style.badge}`}>
            {entry.risk_label}
          </span>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <CriteriaBar criteria={entry.criteria} score={entry.ban_risk_score} />
        <span className="shrink-0 text-xs text-slate-500">
          surtout : <span className="text-slate-400">{dominant.label.toLowerCase()}</span>
        </span>
      </div>
    </div>
  );
}

export default async function BanRadarPage() {
  const { data, as_of, n_decks_window } = await api.banRadar(50);

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <main className="mx-auto w-full max-w-4xl px-6 py-10">
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">Ban Radar</h1>
          <p className="mt-1 text-sm text-slate-400">
            Cartes les plus exposées à la prochaine banlist TCG
            <InfoTooltip text="Score 0-100 combinant 6 critères pondérés : omniprésence, rôle de pièce de moteur, nombre d'exemplaires joués, restriction déjà en vigueur, momentum et centralité graphe." />
            <span className="mx-2">·</span>
            {n_decks_window.toLocaleString("fr-FR")} decks sur 6 mois, arrêtés au {as_of}
          </p>
        </div>

        <div className="mb-6 rounded-lg border border-slate-800 bg-slate-900/60 px-5 py-4 text-sm text-slate-400">
          <p className="mb-2 font-semibold text-slate-300">Comment lire ce score</p>
          <p>
            C&apos;est un score de <strong className="text-slate-300">risque</strong>, pas une probabilité :
            il classe les cartes par ressemblance au profil de celles que Konami a
            historiquement touchées, il ne dit pas &laquo;&nbsp;X% de chances d&apos;être bannie&nbsp;&raquo;.
            Rejoué la veille de la banlist du 18 mai 2026, il plaçait 8 des 11 cartes
            touchées dans son quart supérieur (rang médian 128 sur 922 cartes notées).
            Une seule banlist a assez de decks en base pour être testée : à prendre
            comme un indicateur encourageant, pas comme une validation.
          </p>
          <p className="mt-2">
            La barre colorée sous chaque carte décompose le score par critère.
            {CRITERIA.map((c) => (
              <span key={c.key} className="ml-2 inline-flex items-center gap-1 whitespace-nowrap text-xs">
                <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: c.color }} />
                {c.label}
                <InfoTooltip text={c.help} />
              </span>
            ))}
          </p>
        </div>

        <div className="grid gap-3">
          {data.map((entry, index) => (
            <RadarRow key={entry.card_name} entry={entry} rank={index + 1} />
          ))}
        </div>

        <p className="mt-6 text-center text-sm text-slate-500">
          Pour mesurer l&apos;impact réel d&apos;un ban sur le graphe de synergies, passe par le{" "}
          <Link href="/ban-simulator" className="text-indigo-400 hover:text-indigo-300">
            simulateur de ban
          </Link>
          .
        </p>
      </main>
    </HoverPreviewProvider>
  );
}
