"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useState } from "react";
import type { EvolutionResponse } from "@/types";

const COLORS = ["#6366f1", "#f97316", "#22c55e", "#eab308", "#ec4899", "#14b8a6"];

export function EvolutionChart({ data }: { data: EvolutionResponse["data"] }) {
  const archetypes = Object.keys(data);
  const [selected, setSelected] = useState<string[]>(archetypes.slice(0, 3));

  const months = Array.from(new Set(archetypes.flatMap((a) => data[a].map((p) => p.month)))).sort();
  const chartData = months.map((month) => {
    const row: Record<string, string | number | null> = { month };
    for (const arch of archetypes) {
      const point = data[arch].find((p) => p.month === month);
      // null (pas absence de clé) pour que `connectNulls` relie les mois sans données.
      row[arch] = point ? Math.round(point.meta_score * 100) : null;
    }
    return row;
  });

  return (
    <>
      <div className="mb-6 flex flex-wrap gap-2">
        {archetypes.map((arch, i) => (
          <button
            key={arch}
            onClick={() =>
              setSelected((prev) =>
                prev.includes(arch) ? prev.filter((a) => a !== arch) : [...prev, arch]
              )
            }
            className={`px-3 py-1 rounded-full text-sm border transition-colors ${
              selected.includes(arch)
                ? "border-transparent text-white"
                : "border-slate-700 text-slate-400 bg-transparent"
            }`}
            style={selected.includes(arch) ? { backgroundColor: COLORS[i % COLORS.length] } : {}}
          >
            {arch}
          </button>
        ))}
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-900 p-6">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="month" stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 12 }} />
            <YAxis domain={[0, 100]} stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 12 }} unit="" />
            <Tooltip
              contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #1e293b", borderRadius: 8 }}
              labelStyle={{ color: "#e2e8f0" }}
            />
            <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 12 }} />
            {archetypes.filter((a) => selected.includes(a)).map((arch) => (
              <Line
                key={arch}
                type="monotone"
                dataKey={arch}
                stroke={COLORS[archetypes.indexOf(arch) % COLORS.length]}
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
