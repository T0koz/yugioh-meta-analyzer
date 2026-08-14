"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { SearchResult } from "@/types";

const DEBOUNCE_MS = 250;
const MIN_QUERY_LENGTH = 2;

export function SmartSearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const trimmedQuery = query.trim();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (trimmedQuery.length < MIN_QUERY_LENGTH) return;

    debounceRef.current = setTimeout(async () => {
      try {
        const res = await api.searchCards(trimmedQuery);
        setResults(res.data);
        setOpen(true);
      } catch {
        setResults([]);
      }
    }, DEBOUNCE_MS);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [trimmedQuery]);

  // Dérivé plutôt que réinitialisé dans l'effet : repasser sous le seuil de
  // caractères masque le menu immédiatement, sans setState synchrone à l'entrée
  // de l'effet (ce que la règle react-hooks/set-state-in-effect signalait).
  const showResults = open && trimmedQuery.length >= MIN_QUERY_LENGTH && results.length > 0;

  function selectCard(name: string) {
    setOpen(false);
    setQuery("");
    router.push(`/ban?tab=simulateur&card=${encodeURIComponent(name)}`);
  }

  return (
    <div className="relative w-full sm:w-56 sm:ml-auto shrink-0">
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        placeholder="Rechercher une carte..."
        className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-sm text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
      />
      {showResults && (
        <div className="absolute right-0 mt-1 w-72 max-h-96 overflow-y-auto rounded-md border border-slate-700 bg-slate-900 shadow-xl z-40">
          {results.map((r, i) => (
            <button
              key={r.name}
              type="button"
              onMouseDown={() => selectCard(r.name)}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-slate-800 transition-colors relative"
            >
              {r.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck)
                <img src={r.image_url} alt={r.name} className="w-8 h-8 rounded object-cover shrink-0" />
              ) : (
                <div className="w-8 h-8 rounded bg-slate-800 shrink-0" />
              )}
              <div className="min-w-0">
                <p className="text-sm text-slate-200 truncate">{r.name}</p>
                {r.archetype && <p className="text-xs text-slate-500 truncate">{r.archetype}</p>}
              </div>
              {hoveredIndex === i && r.image_url && (
                <span className="pointer-events-none absolute right-full top-0 mr-2 z-50">
                  {/* eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck) */}
                  <img src={r.image_url} alt={r.name} className="w-28 rounded-md shadow-xl border border-slate-700" />
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
