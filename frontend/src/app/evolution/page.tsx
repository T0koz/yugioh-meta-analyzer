import { api } from "@/lib/api";
import { EvolutionChart } from "./EvolutionChart";

export default async function EvolutionPage() {
  const { data } = await api.evolution();

  return (
    <main className="max-w-6xl mx-auto px-6 py-10 w-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Évolution méta</h1>
        <p className="text-slate-400 mt-1 text-sm">Score méta mensuel par archétype</p>
      </div>

      <EvolutionChart data={data} />
    </main>
  );
}
