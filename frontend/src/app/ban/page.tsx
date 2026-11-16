import type { Metadata } from "next";
import Link from "next/link";
import { api } from "@/lib/api";
import { fmtDate, fmtNum } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
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

// Un titre, une description et une adresse canonique par onglet : les trois vues
// partagent la même route, mais pas le même contenu.
export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}): Promise<Metadata> {
  const tab = parseTab((await searchParams).tab);
  if (tab === "simulateur") {
    return pageMetadata({
      title: "Simulateur de ban",
      description: `Archétypes et decks de tournoi Yu-Gi-Oh! TCG reliés à une carte dans le graphe de co-occurrences, et cohésion du graphe sans elle. Source : ${DECK_SOURCE}, date de calcul non enregistrée.`,
      path: "/ban?tab=simulateur",
    });
  }
  if (tab === "impact") {
    const { as_of, n_decks_window } = await api.cardImpact();
    return pageMetadata({
      title: "Cartes à impact",
      description: `Cartes Yu-Gi-Oh! TCG classées par nombre d’archétypes et de decks qui les jouent, sur ${fmtNum(n_decks_window)} decks de tournoi, relevé du ${fmtDate(as_of)}. Source : ${DECK_SOURCE}.`,
      path: "/ban?tab=impact",
    });
  }
  const { as_of, n_decks_window } = await api.banRadar();
  return pageMetadata({
    title: "Ban Radar",
    description: `Cartes Yu-Gi-Oh! TCG notées de 0 à 100 sur six critères de risque de restriction, sur ${fmtNum(n_decks_window)} decks de tournoi, relevé du ${fmtDate(as_of)}. Source : ${DECK_SOURCE}.`,
    path: "/ban",
  });
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
        {tab === "radar" && <BanRadarView view={parseKind(params.kind, "radar")} tabs={tabs} />}
        {tab === "impact" && <CardImpactView view={parseKind(params.kind, "impact")} tabs={tabs} />}
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
