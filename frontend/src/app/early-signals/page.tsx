import type { Metadata } from "next";
import { api } from "@/lib/api";
import { fmtDate, fmtNum } from "@/lib/format";
import { CardArt } from "@/components/card-art";
import { CardChip } from "@/components/card-chip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import { Em } from "@/components/ds/em";
import { DataFooter, Meter, Page, PageHero } from "@/components/ds/page";
import { InfoTooltip } from "@/components/ui/info-tooltip";

export const metadata: Metadata = {
  title: "Signaux précoces",
  description: "Les nouvelles cartes Yu-Gi-Oh! qui entrent dans la méta, repérées par leurs vues et leurs co-occurrences.",
};

// Colonnes : rang · vignette · carte · score (barre + valeur) · vues par semaine.
const GRID =
  "grid grid-cols-[22px_34px_minmax(0,1fr)_72px] items-center gap-3 px-3 min-[760px]:grid-cols-[28px_34px_minmax(0,1.4fr)_minmax(120px,1fr)_110px] min-[760px]:gap-4 min-[760px]:px-4";

export default async function EarlySignalsPage() {
  const { data, computed_at } = await api.earlySignals();

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <Page>
        <PageHero
          eyebrow="Boutique · Signaux précoces"
          title={
            <>
              Les cartes qui montent <Em>avant</Em> la méta.
            </>
          }
          intro={
            <>
              Nouvelles cartes qui entrent dans la méta, repérées par leurs vues, leurs co-occurrences et le tier de
              leur archétype.
              <InfoTooltip text="Score 0-100 combinant les vues par semaine, la co-occurrence avec les decks de la méta et le tier de l'archétype. Un tiers du score reprend l'alert_score des Signaux Boutique." />
            </>
          }
        />

        <div className="overflow-hidden rounded-[6px] border border-line">
          <div className={`${GRID} py-2.5 font-mono text-[11px] tracking-[0.08em] text-muted-text uppercase`}>
            <span>#</span>
            <span className="col-span-2">Carte</span>
            <span className="hidden min-[760px]:block">Score</span>
            <span className="text-right">Vues / sem.</span>
          </div>
          {data.map((signal, i) => (
            <div
              key={signal.card_name}
              className={`${GRID} border-t border-line py-3 transition-colors duration-200 hover:bg-ink-3`}
            >
              <span className="font-mono text-[12px] text-faint tabular-nums">{String(i + 1).padStart(2, "0")}</span>
              <CardArt src={signal.image_url} name={signal.card_name} eager={i < 8} />
              <span className="min-w-0">
                <CardChip name={signal.card_name} subtitle={signal.archetype ?? undefined} variant="plain" className="font-medium tracking-[-0.01em]" />
                <small className="mt-0.5 block text-[13px] text-muted-text">
                  {/* Carte sans archétype dans YGOPRODeck (ex. Fydraulis Harmonia) : on n’affirme rien. */}
                  {signal.archetype ?? "—"}
                  <span className="min-[760px]:hidden"> · score {fmtNum(signal.early_score * 100)}</span>
                </small>
              </span>
              <span className="hidden items-center gap-3 min-[760px]:flex">
                <span className="flex-1">
                  <Meter value={signal.early_score} max={1} />
                </span>
                <span className="w-7 text-right font-mono text-[13px] font-medium tabular-nums">
                  {fmtNum(signal.early_score * 100)}
                </span>
              </span>
              <span className="text-right font-mono text-[13px] tabular-nums text-soft">{fmtNum(signal.views_week)}</span>
            </div>
          ))}
        </div>
        <DataFooter
          source="vues par semaine (YGOPRODeck), co-occurrences dans les decklists de tournoi (yugiohmeta.com)"
          date={computed_at ? `calcul du ${fmtDate(computed_at)}` : "date de calcul inconnue"}
          sample={`${fmtNum(data.length)} cartes`}
        />
      </Page>
    </HoverPreviewProvider>
  );
}
