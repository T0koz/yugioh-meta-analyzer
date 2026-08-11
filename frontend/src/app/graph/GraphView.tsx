"use client";

import { useEffect, useRef, useState } from "react";
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
type VisNetwork = { destroy: () => void; fit: () => void };

export function GraphView({ data }: { data: GraphResponse }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const networkRef = useRef<VisNetwork | null>(null);
  const nodesDataRef = useRef<VisDataSet<{ id: string; hidden: boolean }> | null>(null);
  const edgesDataRef = useRef<VisDataSet<{ id: number; hidden: boolean }> | null>(null);
  const [ready, setReady] = useState(false);
  const [archetypeFilter, setArchetypeFilter] = useState("all");

  const archetypes = Array.from(new Set(data.nodes.map((n) => n.group).filter((g): g is string => !!g))).sort();

  useEffect(() => {
    let disposed = false;

    (async () => {
      const { Network, DataSet } = await import("vis-network/standalone");
      if (disposed || !containerRef.current) return;

      const nodes = new DataSet(
        data.nodes.map((n) => ({
          id: n.id,
          label: n.id,
          title: n.group ? `${n.id}\n${n.group}` : n.id,
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
          interaction: { hover: true, tooltipDelay: 100 },
        }
      );

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
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  useEffect(() => {
    if (!ready || !nodesDataRef.current || !edgesDataRef.current) return;

    const nodeById = new Map(data.nodes.map((n) => [n.id, n]));
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
  }, [archetypeFilter, ready, data]);

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
      <div ref={containerRef} className="w-full h-[600px] rounded-md bg-slate-950" />
      <p className="mt-3 text-xs text-slate-500">
        {data.nodes.length} cartes · {data.edges.length} arêtes (Jaccard ≥ seuil) · survol pour l&apos;archétype
      </p>
    </div>
  );
}
