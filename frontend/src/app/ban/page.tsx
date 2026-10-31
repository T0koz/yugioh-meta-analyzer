import Link from "next/link";
import { api } from "@/lib/api";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Page } from "@/components/ds/page";
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

// Même grammaire que la nav : texte doux, onglet actif en clair sur --ink-4.
function TabNav({ active }: { active: Tab }) {
  return (
    <nav aria-label="Ban Center" className="mt-8 inline-flex flex-wrap gap-1 rounded-[8px] border border-line-2 bg-ink-2 p-1">
      {TABS.map((t) => (
        <Link
          key={t.id}
          href={`/ban?tab=${t.id}`}
          aria-current={active === t.id ? "page" : undefined}
          className={`rounded-[4px] px-3 py-1.5 text-[13px] transition-colors duration-200 ${
            active === t.id ? "bg-ink-4 text-text" : "text-muted-text hover:text-text"
          }`}
        >
          {t.label}
        </Link>
      ))}
    </nav>
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

  const tabs = <TabNav active={tab} />;

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        {tab === "radar" && <BanRadarView kind={kind} tabs={tabs} />}
        {tab === "impact" && <CardImpactView kind={kind} tabs={tabs} />}
        {tab === "simulateur" && (
          <BanSimulatorView
            key={cardParam ?? ""}
            initialCard={cardParam}
            initialResult={initialResult}
            tabs={tabs}
          />
        )}
      </Page>
    </HoverPreviewProvider>
  );
}
