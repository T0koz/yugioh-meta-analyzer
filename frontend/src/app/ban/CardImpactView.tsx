import Link from "next/link";
import { api } from "@/lib/api";
import { CardChip } from "@/components/card-chip";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import type { BanRadarKind, CardImpactEntry } from "@/types";
import { KindFilterTabs } from "./kind-filter";

function ImpactRow({ entry, rank }: { entry: CardImpactEntry; rank: number }) {
  // top_archetype est nul quand la carte est jouée un peu partout sans deck
  // d'attache : c'est une staple, pas une pièce d'archétype.
  const origin = entry.top_archetype ?? "Générique";

  return (
    <div className="flex items-center gap-4 rounded-lg border border-slate-800 bg-slate-900 px-5 py-4">
      <span className="w-6 shrink-0 text-right text-sm tabular-nums text-slate-600">{rank}</span>

      <div className="min-w-0 flex-1">
        <p className="truncate font-semibold">
          <CardChip name={entry.card_name} subtitle={origin} />
        </p>
        <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
          <span>{origin}</span>
          <span>·</span>
          <span className="tabular-nums">{entry.n_archetypes} archétypes</span>
          <span>·</span>
          <span className="tabular-nums">{entry.decks.toLocaleString("fr-FR")} decks</span>
        </p>
      </div>

      <div className="shrink-0 text-right">
        <p className="text-2xl font-bold tabular-nums text-sky-400">
          {entry.bridge_score.toFixed(0)}
        </p>
        <Link
          href={`/ban?tab=simulateur&card=${encodeURIComponent(entry.card_name)}`}
          className="text-xs text-indigo-400 hover:text-indigo-300"
        >
          simuler le ban →
        </Link>
      </div>
    </div>
  );
}

export async function CardImpactView({ kind }: { kind?: BanRadarKind }) {
  const { data, as_of, n_decks_window } = await api.cardImpact({ limit: 50, kind });

  return (
    <>
      <p className="mb-6 text-sm text-slate-400">
        Classement des cartes dont le retrait fragmenterait le plus la méta
        <InfoTooltip text="Bridge score = nombre d'archétypes qui jouent la carte × log(1 + nombre de decks). Une carte adoptée par beaucoup d'archétypes en volume est une pièce de connexion : la retirer touche plusieurs decks à la fois, pas un seul." />
        <span className="mx-2">·</span>
        {n_decks_window.toLocaleString("fr-FR")} decks sur 6 mois, arrêtés au {as_of}
      </p>

      <div className="mb-6 rounded-lg border border-slate-800 bg-slate-900/60 px-5 py-4 text-sm text-slate-400">
        <p className="mb-2 font-semibold text-slate-300">Comment lire ce score</p>
        <p>
          Ce n&apos;est pas un score de risque de ban (voir l&apos;onglet{" "}
          <Link href="/ban?tab=radar" className="text-indigo-400 hover:text-indigo-300">
            Ban Radar
          </Link>{" "}
          pour ça) mais une mesure d&apos;<strong className="text-slate-300">impact</strong> :
          si Konami retire cette carte demain, combien d&apos;archétypes et de decks
          sont concernés. Les{" "}
          <strong className="text-slate-300">staples génériques</strong> trustent
          le haut du classement parce qu&apos;elles sont jouées par le plus d&apos;archétypes
          à la fois — le filtre &laquo;&nbsp;pièces d&apos;archétype&nbsp;&raquo; isole les
          cartes rattachées à un deck précis.
        </p>
      </div>

      <KindFilterTabs basePath="/ban?tab=impact" active={kind} />

      <div className="grid gap-3">
        {data.map((entry, index) => (
          <ImpactRow key={entry.card_name} entry={entry} rank={index + 1} />
        ))}
      </div>
    </>
  );
}
