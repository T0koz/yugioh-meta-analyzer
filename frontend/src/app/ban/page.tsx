import Link from "next/link";
import { api } from "@/lib/api";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { BanRadarView } from "./BanRadarView";
import { CardImpactView } from "./CardImpactView";
import { BanSimulatorView } from "./BanSimulatorView";
import { parseKind } from "./kind-filter";
import type { BanSimResult } from "@/types";

type Tab = "radar" | "impact" | "simulateur";

const TABS: { id: Tab; label: string }[] = [
  { id: "radar", label: "Ban Radar" },
  { id: "impact", label: "Cartes à impact" },
  { id: "simulateur", label: "Simulateur" },
];

function parseTab(raw: string | string[] | undefined): Tab {
  return TABS.some((t) => t.id === raw) ? (raw as Tab) : "radar";
}

function TabNav({ active }: { active: Tab }) {
  return (
    <div className="mb-8 flex gap-1 border-b border-slate-800">
      {TABS.map((t) => (
        <Link
          key={t.id}
          href={`/ban?tab=${t.id}`}
          aria-current={active === t.id ? "page" : undefined}
          className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
            active === t.id
              ? "border-indigo-500 text-white"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          {t.label}
        </Link>
      ))}
    </div>
  );
}

export default async function BanPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const tab = parseTab(params.tab);
  const kind = parseKind(params.kind);
  const cardParam = typeof params.card === "string" ? params.card : undefined;

  // Arrivée directe sur l'onglet simulateur via ?card= (recherche globale ou
  // "simuler le ban →" de l'onglet impact) : on résout côté serveur pour ne
  // pas faire attendre un aller-retour client avant d'afficher le résultat.
  let initialResult: BanSimResult | null = null;
  if (tab === "simulateur" && cardParam) {
    initialResult = await api.simulateBan(cardParam);
  }

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <main className="mx-auto w-full max-w-4xl px-6 py-10">
        <div className="mb-2">
          <h1 className="text-3xl font-bold tracking-tight">Ban Center</h1>
          <p className="mt-1 text-sm text-slate-400">
            Risque de ban, impact sur la méta, simulation carte par carte
          </p>
        </div>

        <TabNav active={tab} />

        {tab === "radar" && <BanRadarView kind={kind} />}
        {tab === "impact" && <CardImpactView kind={kind} />}
        {tab === "simulateur" && (
          <BanSimulatorView initialCard={cardParam} initialResult={initialResult} />
        )}
      </main>
    </HoverPreviewProvider>
  );
}
