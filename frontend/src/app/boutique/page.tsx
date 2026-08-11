import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { InfoTooltip } from "@/components/ui/info-tooltip";
import { CardChip } from "@/components/card-chip";
import { HoverPreviewProvider } from "@/components/hover-preview-context";
import { HoverPreviewPanel } from "@/components/hover-preview-panel";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { BuyLabel } from "@/types";

const LABEL_STYLE: Record<BuyLabel, string> = {
  Fort: "bg-green-600 text-white",
  Modéré: "bg-yellow-500 text-black",
  Faible: "bg-slate-600 text-white",
};

const BAN_STYLE: Record<string, string> = {
  Forbidden: "bg-red-600 text-white",
  Limited: "bg-orange-500 text-white",
  "Semi-Limited": "bg-yellow-500 text-black",
};

export default async function BoutiquePage() {
  const { data } = await api.boutiqueSignals();

  return (
    <HoverPreviewProvider>
      <HoverPreviewPanel />
      <main className="max-w-6xl mx-auto px-6 py-10 w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Signaux Boutique</h1>
        <p className="text-slate-400 mt-1 text-sm">
          Cartes à fort potentiel d&apos;achat · Banlist TCG prise en compte
        </p>
      </div>

      <div className="rounded-lg border border-slate-800 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-slate-400">Signal</TableHead>
              <TableHead className="text-slate-400 w-[200px]">Carte</TableHead>
              <TableHead className="text-slate-400">Archétype</TableHead>
              <TableHead className="text-slate-400">
                Score
                <InfoTooltip text="alert_score = meta_score OCG × log(1 + views/semaine moyen des cartes core). Signal OCG→TCG validé à 4 mois d'avance (r=0.771, p<0.0001)." />
              </TableHead>
              <TableHead className="text-slate-400">Prix CM</TableHead>
              <TableHead className="text-slate-400">Banlist TCG</TableHead>
              <TableHead className="text-slate-400">Entrée TCG est.</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((signal) => (
              <TableRow key={`${signal.archetype}-${signal.card_name}`} className="border-slate-800 hover:bg-slate-900">
                <TableCell>
                  <span
                    className={`inline-flex items-center justify-center px-2 py-0.5 rounded text-xs font-bold ${LABEL_STYLE[signal.buy_label]}`}
                  >
                    {signal.buy_label}
                  </span>
                </TableCell>
                <TableCell className="font-medium">
                  <CardChip name={signal.card_name} subtitle={signal.archetype} />
                </TableCell>
                <TableCell className="text-slate-400 text-sm">{signal.archetype}</TableCell>
                <TableCell className="tabular-nums text-sm font-semibold text-indigo-400">
                  {signal.buy_score.toFixed(1)}
                </TableCell>
                <TableCell className="tabular-nums text-sm">
                  {signal.cm_price.toFixed(2)} €
                </TableCell>
                <TableCell>
                  {signal.ban_tcg ? (
                    <span
                      className={`inline-flex items-center justify-center px-2 py-0.5 rounded text-xs font-bold ${BAN_STYLE[signal.ban_tcg] ?? "bg-slate-600 text-white"}`}
                    >
                      ⚠ {signal.ban_tcg}
                    </span>
                  ) : (
                    <span className="text-slate-600 text-xs">—</span>
                  )}
                </TableCell>
                <TableCell className="text-slate-400 text-sm">
                  {signal.tcg_entry_estimated ?? "—"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      </main>
    </HoverPreviewProvider>
  );
}
