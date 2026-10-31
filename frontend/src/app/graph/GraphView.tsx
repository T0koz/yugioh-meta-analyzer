"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useHoverPreview } from "@/components/hover-preview-context";
import type { GraphResponse } from "@/types";

const PALETTE = [
  "#6366f1", "#f97316", "#22c55e", "#eab308", "#ec4899",
  "#14b8a6", "#a855f7", "#f43f5e", "#0ea5e9", "#84cc16",
];

function colorFor(group: string | null): string {
  if (!group) return "#64748b";
  let hash = 0;
  for (let i = 0; i < group.length; i++) hash = (hash * 31 + group.charCodeAt(i)) >>> 0;
  return PALETTE[hash % PALETTE.length];
}

// vis-network's types don't need to leak beyond this file; the network/dataset
// instances only ever get called through their documented methods below.
type VisDataSet<T> = { update: (items: (Partial<T> & { id: string | number })[]) => void };
type FitOptions = {
  nodes?: (string | number)[];
  maxZoomLevel?: number;
};
type VisNetwork = {
  destroy: () => void;
  fit: (options?: FitOptions) => void;
  once: (event: "stabilizationIterationsDone", callback: () => void) => void;
  on: (event: "hoverNode" | "blurNode", callback: (params: { node: string }) => void) => void;
};

export function GraphView({ data }: { data: GraphResponse }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<VisNetwork | null>(null);
  const nodesDataRef = useRef<VisDataSet<{ id: string; hidden: boolean }> | null>(null);
  const edgesDataRef = useRef<VisDataSet<{ id: number; hidden: boolean }> | null>(null);
  const [ready, setReady] = useState(false);
  const [archetypeFilter, setArchetypeFilter] = useState("all");
  const { setPreview } = useHoverPreview();

  const archetypes = Array.from(new Set(data.nodes.map((n) => n.group).filter((g): g is string => !!g))).sort();
  const nodeById = useMemo(() => new Map(data.nodes.map((n) => [n.id, n])), [data]);

  useEffect(() => {
    let disposed = false;

    (async () => {
      const { Network, DataSet } = await import("vis-network/standalone");
      if (disposed || !containerRef.current) return;

      const nodes = new DataSet(
        data.nodes.map((n) => ({
          id: n.id,
          label: n.id,
          value: n.size,
          color: colorFor(n.group),
          group: n.group ?? undefined,
        }))
      );
      const edges = new DataSet(
        data.edges.map((e, i) => ({
          id: i,
          from: e.source,
          to: e.target,
          value: e.weight,
        }))
      );

      const network = new Network(
        containerRef.current,
        { nodes, edges },
        {
          nodes: {
            shape: "dot",
            scaling: { min: 6, max: 26 },
            font: { color: "#cbd5e1", size: 11, strokeWidth: 0 },
          },
          edges: { color: { color: "#334155", opacity: 0.4 }, smooth: false },
          physics: {
            stabilization: { iterations: 200 },
            barnesHut: { gravitationalConstant: -6000, springLength: 90, springConstant: 0.02 },
          },
          // hover: true déclenche hoverNode/blurNode ci-dessous, qui pilotent
          // le panneau de survol partagé (pas de tooltip natif vis-network).
          interaction: { hover: true },
        }
      );

      // Le layout physique place les nœuds à un cadrage arbitraire, souvent à
      // moitié hors champ : les co-occurrences Jaccard forment surtout des
      // cliques denses par archétype, peu reliées entre elles, et barnesHut
      // les repousse aux quatre coins d'un immense canvas. Sans ce fit(), la
      // vue au chargement ne montre qu'une fraction des cartes par hasard.
      //
      // Pas d'animation sur les fit() : quand deux fit animés s'enchaînent sans
      // frame entre eux (celui de fin de stabilisation puis celui-ci),
      // vis-network 10 écrase sa viewFunction sans désabonner l'ancienne, qui
      // reste branchée sur initRedraw et ramène la caméra au cadrage précédent
      // à chaque redessin — le recentrage du filtre avait un temps de retard.
      network.once("stabilizationIterationsDone", () => network.fit());

      // Panneau de survol partagé avec le reste du site (tier-list, boutique,
      // ban-radar...) plutôt qu'un tooltip vis-network natif : celui-ci reste
      // une bulle blanche par défaut, hors thème, et redouble l'information
      // une fois le panneau introduit.
      network.on("hoverNode", ({ node }) => {
        const card = nodeById.get(node);
        if (!card?.image_url) return;
        setPreview({ name: card.id, imageUrl: card.image_url, subtitle: card.group ?? "Staple générique" });
      });
      network.on("blurNode", () => setPreview(null));

      networkRef.current = network;
      nodesDataRef.current = nodes;
      edgesDataRef.current = edges;
      setReady(true);
    })();

    return () => {
      disposed = true;
      networkRef.current?.destroy();
      networkRef.current = null;
      setReady(false);
      setPreview(null);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  useEffect(() => {
    if (!ready || !nodesDataRef.current || !edgesDataRef.current || !networkRef.current) return;

    const visibleIds = data.nodes
      .filter((n) => archetypeFilter === "all" || n.group === archetypeFilter)
      .map((n) => n.id);

    nodesDataRef.current.update(
      data.nodes.map((n) => ({
        id: n.id,
        hidden: archetypeFilter !== "all" && n.group !== archetypeFilter,
      }))
    );
    edgesDataRef.current.update(
      data.edges.map((e, i) => {
        if (archetypeFilter === "all") return { id: i, hidden: false };
        const a = nodeById.get(e.source);
        const b = nodeById.get(e.target);
        const hidden = a?.group !== archetypeFilter && b?.group !== archetypeFilter;
        return { id: i, hidden };
      })
    );

    // Le filtre masque des nœuds mais ne déplace jamais la caméra : sans ce
    // recentrage, sélectionner un archétype dont la clique physique est loin
    // du cadrage courant affiche un canvas vide. fit() plafonne le zoom à 1 par
    // défaut, échelle à laquelle la vue complète est déjà : sans relever ce
    // plafond, la clique d'un archétype resterait minuscule au centre.
    networkRef.current.fit({ nodes: visibleIds, maxZoomLevel: 4 });
  }, [archetypeFilter, ready, data, nodeById]);

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="mb-3 flex items-center gap-3">
        <label className="text-sm text-slate-400">Filtrer par archétype</label>
        <select
          value={archetypeFilter}
          onChange={(e) => setArchetypeFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-md px-2 py-1"
        >
          <option value="all">Tous ({data.nodes.length} cartes)</option>
          {archetypes.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
      </div>
      {/* vis-network n'émet pas blurNode quand la souris quitte le canvas
          directement depuis un nœud : sans ce handler, le panneau reste figé. */}
      <div
        ref={containerRef}
        onMouseLeave={() => setPreview(null)}
        className="w-full h-[600px] rounded-md bg-slate-950"
      />
      <p className="mt-3 text-xs text-slate-500">
        {data.nodes.length} cartes · {data.edges.length} arêtes (Jaccard ≥ seuil) · survol pour l’archétype
      </p>
    </div>
  );
}
