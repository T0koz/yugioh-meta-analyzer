import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtMonthRange, fmtNum } from "@/lib/format";
import { SITE_FACTS } from "@/lib/site-facts";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { CardArt } from "@/components/card-art";
import { CardChip } from "@/components/card-chip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { Page, PageHero, StatBand } from "@/components/ds/page";
import { BanStatus, Tag } from "@/components/ds/tags";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { BuyLabel } from "@/types";

export const metadata: Metadata = {
  title: "Signaux boutique",
  description: "Les cartes des archétypes qui montent en OCG, à surveiller avant leur arrivée en TCG.",
};

// Fort = étiquette pleine (l'accent signale ce qui compte), le reste en contour.
const LABEL_TONE: Record<BuyLabel, "strong" | "outline" | "neutral"> = {
  Fort: "strong",
  Modéré: "outline",
  Faible: "neutral",
};

export default async function BoutiquePage() {
  const { data } = await api.boutiqueSignals();
  const strong = data.filter((s) => s.buy_label === "Fort").length;
  const archetypes = new Set(data.map((s) => s.archetype)).size;

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          eyebrow="Boutique · Signaux d’achat"
          title={
            <>
              Les cartes à surveiller <Em>avant</Em> le TCG.
            </>
          }
          intro={`Archétypes joués en OCG dont les cartes clés ne sont pas encore sorties en TCG. Le TCG suit souvent l’OCG ${SITE_FACTS.ocgTcgLagRange} plus tard : signal modéré, à croiser avec la banlist et le prix. La fenêtre d’arrivée est une estimation, pas une date.`}
        >
          <StatBand
            stats={[
              { value: fmtNum(strong), label: "Signaux forts" },
              // Une ligne par (archétype, carte) : une staple compte sous chaque archétype.
              { value: fmtNum(data.length), label: "Signaux en tout" },
              { value: fmtNum(archetypes), label: "Archétypes" },
              { value: fmtNum(SITE_FACTS.ocgTcgCorrelation, 2), label: "Corrélation OCG → TCG" },
            ]}
          />
        </PageHero>

        <div className="overflow-hidden rounded-[6px] border border-line">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Signal</TableHead>
                <TableHead>Carte</TableHead>
                <TableHead>Archétype</TableHead>
                <TableHead className="text-right">
                  Score
                  <InfoTooltip text="alert_score = meta_score OCG × log(1 + vues/semaine moyennes des cartes clés). Seuls les archétypes avec au moins 3 cartes clés jamais sorties en TCG sont retenus. Fort, Modéré et Faible sont relatifs au meilleur signal du moment. Signal OCG → TCG réel mais modéré : r ≈ 0,53 (IC 95 % 0,43 à 0,59), à peu près constant de 2 à 6 mois d’écart. Le signal de juin 2026 a perdu : ses cartes ont baissé de 35 % contre 1 % pour le marché." />
                </TableHead>
                <TableHead className="text-right">Prix CM</TableHead>
                <TableHead>Banlist TCG</TableHead>
                <TableHead className="text-right">
                  Arrivée TCG
                  <InfoTooltip text="Fenêtre dans laquelle l’archétype devrait arriver en TCG, 8 fois sur 10 : premier deck OCG + 75 à 202 jours, délai mesuré sur 1 897 cartes sorties de 2022 à 2025. Pas encore vérifiée sur des cas nouveaux, et certains archétypes n’arrivent jamais." />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((signal, index) => (
                <TableRow key={`${signal.archetype}-${signal.card_name}`}>
                  <TableCell>
                    <Tag tone={LABEL_TONE[signal.buy_label]}>{signal.buy_label.toUpperCase()}</Tag>
                  </TableCell>
                  <TableCell>
                    <span className="flex items-center gap-3">
                      <CardArt src={signal.image_url} name={signal.card_name} eager={index < 6} />
                      <CardChip name={signal.card_name} subtitle={signal.archetype} variant="plain" className="font-medium tracking-[-0.01em]" />
                    </span>
                  </TableCell>
                  <TableCell className="text-[14px] text-soft">{signal.archetype}</TableCell>
                  <TableCell className="text-right font-mono text-[13px] font-medium tabular-nums">
                    {fmtNum(signal.buy_score, 1)}
                  </TableCell>
                  <TableCell className="text-right font-mono text-[13px] tabular-nums">
                    {fmtNum(signal.cm_price, 2)} €
                  </TableCell>
                  <TableCell>
                    {signal.ban_tcg ? <BanStatus status={signal.ban_tcg} /> : <span className="font-mono text-[12px] text-faint">—</span>}
                  </TableCell>
                  <TableCell className="text-right font-mono text-[12px] whitespace-nowrap text-muted-text">
                    {fmtMonthRange(signal.tcg_window_start, signal.tcg_window_end) ?? "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Page>
    </HoverPreviewProvider>
  );
}
