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
  const inputRef = useRef<HTMLInputElement>(null);

  // ⌘K / Ctrl+K place le curseur dans la recherche depuis n'importe quelle page.
  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

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
    <div className="relative ml-auto min-w-0 flex-1 min-[760px]:w-60 min-[760px]:flex-none">
      <input
        ref={inputRef}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        onKeyDown={(e) => e.key === "Escape" && e.currentTarget.blur()}
        placeholder="Rechercher une carte…"
        aria-keyshortcuts="Meta+K Control+K"
        className="w-full rounded-[4px] border border-line bg-ink py-2 pl-3 pr-3 font-mono text-[12px] text-text text-ellipsis placeholder:text-faint min-[760px]:pr-12 transition-colors duration-200 focus:border-signal-hi focus:outline-none"
      />
      <kbd className="pointer-events-none absolute hidden min-[760px]:block right-2 top-1/2 -translate-y-1/2 rounded-[3px] border border-line-2 px-1.5 font-mono text-[11px] text-muted-text">
        ⌘K
      </kbd>
      {showResults && (
        <div className="absolute right-0 mt-1 w-72 max-h-96 overflow-y-auto rounded-[4px] border border-line-2 bg-ink-3 p-1 z-40">
          {results.map((r, i) => (
            <button
              key={r.name}
              type="button"
              onMouseDown={() => selectCard(r.name)}
              onMouseEnter={() => setHoveredIndex(i)}
              onMouseLeave={() => setHoveredIndex(null)}
              className="w-full flex items-center gap-3 rounded-[4px] px-3 py-2 text-left hover:bg-ink-4 transition-colors duration-200 relative"
            >
              {r.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck)
                <img src={r.image_url} alt={r.name} className="w-8 h-8 rounded-[3px] object-cover shrink-0" />
              ) : (
                <div className="w-8 h-8 rounded-[3px] bg-ink-4 shrink-0" />
              )}
              <div className="min-w-0">
                <p className="text-sm font-medium text-text truncate">{r.name}</p>
                {r.archetype && <p className="font-mono text-[11px] text-muted-text truncate">{r.archetype}</p>}
              </div>
              {hoveredIndex === i && r.image_url && (
                <span className="pointer-events-none absolute right-full top-0 mr-2 z-50">
                  {/* eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck) */}
                  <img src={r.image_url} alt={r.name} className="w-28 rounded-[4px] border border-line-2" />
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
