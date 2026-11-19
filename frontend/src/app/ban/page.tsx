import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtDate, fmtNum } from "@/lib/format";
import { pageMetadata } from "@/lib/seo";
import { DECK_SOURCE } from "@/lib/site";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { TabLink, TabRail } from "@/components/ds/control";
import { Page } from "@/components/ds/page";
import { BanRadarView } from "./BanRadarView";
import { CardDiffusionView } from "./CardDiffusionView";
import { BanSimulatorView } from "./BanSimulatorView";
import { BanHistoryView } from "./BanHistoryView";
import { parseKind } from "./kind-filter";
import type { BanSimResult } from "@/types";

type Tab = "radar" | "historique" | "diffusion" | "simulateur";

const TABS: { id: Tab; label: string }[] = [
  { id: "radar", label: "Ban Radar" },
  { id: "historique", label: "Historique" },
  { id: "diffusion", label: "Diffusion" },
  { id: "simulateur", label: "Simulateur" },
];

// Ancien nom de l'onglet « Diffusion » (« Cartes à impact » jusqu'au jalon n°8, TOK-132) : `next.config.ts` redirige
// (308) /ban?tab=impact vers la nouvelle adresse, filtre `kind` compris ; l'alias reste ici par sécurité.
const LEGACY_TABS: Record<string, Tab> = { impact: "diffusion" };

function parseTab(raw: string | string[] | undefined): Tab {
  if (typeof raw === "string" && raw in LEGACY_TABS) return LEGACY_TABS[raw];
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
      description: `Position d’une carte Yu-Gi-Oh! TCG dans le graphe de co-occurrences déjà calculé, sans prévision de l’effet d’un ban, et archétypes de deck qui la jouent. Source : ${DECK_SOURCE}.`,
      path: "/ban?tab=simulateur",
    });
  }
  if (tab === "historique") {
    const { lists, computed_at } = await api.banHistory();
    const retained = lists.filter((l) => l.retained).length;
    return pageMetadata({
      title: "Ban Radar : historique des banlists",
      description: `Classement du Ban Radar recalculé la veille de ${fmtNum(retained)} banlists Yu-Gi-Oh! TCG et OCG, face aux cartes réellement restreintes, comparé au hasard et aux staples les plus jouées. Calcul du ${fmtDate(computed_at)}. Sources : ${DECK_SOURCE}, Yugipedia.`,
      path: "/ban?tab=historique",
    });
  }
  if (tab === "diffusion") {
    const { as_of, n_decks_window } = await api.cardImpact();
    return pageMetadata({
      title: "Diffusion des cartes",
      description: `Cartes Yu-Gi-Oh! TCG classées par nombre d’archétypes et de decks qui les jouent, sur ${fmtNum(n_decks_window)} decks de tournoi, relevé du ${fmtDate(as_of)}. Source : ${DECK_SOURCE}.`,
      path: "/ban?tab=diffusion",
    });
  }
  const { as_of, n_decks_window } = await api.banRadar();
  return pageMetadata({
    title: "Ban Radar",
    description: `Cartes Yu-Gi-Oh! TCG notées de 0 à 100 sur six critères de risque de restriction, sur ${fmtNum(n_decks_window)} decks de tournoi, relevé du ${fmtDate(as_of)}. Source : ${DECK_SOURCE}.`,
    path: "/ban",
  });
}

// Même grammaire que la nav : onglet actif en relief dans son rail.
function TabNav({ active }: { active: Tab }) {
  return (
    <TabRail aria-label="Ban Center" className="mt-8">
      {TABS.map((t) => (
        <TabLink key={t.id} href={`/ban?tab=${t.id}`} current={active === t.id}>
          {t.label}
        </TabLink>
      ))}
    </TabRail>
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
  // « position dans le graphe → » de l'onglet Diffusion) : on résout côté serveur pour ne
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
        {tab === "historique" && (
          <BanHistoryView selected={typeof params.liste === "string" ? params.liste : undefined} tabs={tabs} />
        )}
        {tab === "diffusion" && <CardDiffusionView view={parseKind(params.kind, "diffusion")} tabs={tabs} />}
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
