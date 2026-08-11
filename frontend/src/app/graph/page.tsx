import { api } from "@/lib/api";
import { GraphView } from "./GraphView";

export default async function GraphPage() {
  const data = await api.graphSynergies({ limit: 200, minJaccard: 0.15 });

  return (
    <main className="max-w-6xl mx-auto px-6 py-10 w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Graphe de synergies</h1>
        <p className="text-slate-400 mt-1 text-sm">
          Co-occurrence Jaccard · top {data.nodes.length} cartes par degré pondéré
        </p>
      </div>

      <GraphView data={data} />
    </main>
  );
}
