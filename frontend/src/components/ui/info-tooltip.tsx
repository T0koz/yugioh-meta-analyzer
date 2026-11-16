"use client";

import { useEffect, useId, useRef, useState } from "react";

/**
 * Infobulle de définition (charte « ton et explication » §2, étage 5) : une phrase
 * qui fait comprendre un mot, jamais une formule, un seuil en série ni un résultat.
 *
 * S'ouvre au survol, au focus clavier et au toucher (le bouton bascule) ; Échap ou
 * un toucher ailleurs la ferme. Le texte est relié au bouton par `aria-describedby` :
 * un lecteur d'écran le lit dès que le bouton reçoit le focus, ouvert ou non.
 * La bulle s'ouvre vers le BAS (`top-full`) : vers le haut, un ancêtre
 * `overflow-hidden` (tableau) la coupe.
 */
export function InfoTooltip({ term, text }: { term: string; text: string }) {
  const [pinned, setPinned] = useState(false);
  const id = useId();
  const root = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!pinned) return;
    const close = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node)) setPinned(false);
    };
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, [pinned]);

  return (
    <span
      ref={root}
      className="group/tip relative ml-0.5 inline-flex items-center align-middle normal-case tracking-normal"
      onKeyDown={(event) => event.key === "Escape" && setPinned(false)}
    >
      <button
        type="button"
        aria-label={`Définition : ${term}`}
        aria-describedby={id}
        aria-expanded={pinned}
        onClick={() => setPinned((open) => !open)}
        // Zone de toucher de 24 px autour d'un rond de 16 px.
        className="peer inline-flex h-6 w-6 cursor-help items-center justify-center rounded-full text-muted-text transition-colors duration-200 hover:text-text focus-visible:text-text"
      >
        <span
          aria-hidden
          className="inline-flex h-4 w-4 items-center justify-center rounded-full border border-line-2 font-sans text-[10px] leading-none"
        >
          i
        </span>
      </button>
      <span
        id={id}
        role="tooltip"
        className={`absolute top-full left-1/2 z-50 mt-1 w-60 -translate-x-1/2 rounded-[4px] border border-line-2 bg-ink-3 px-3 py-2.5 font-sans text-[13px] leading-[1.5] font-normal whitespace-normal text-soft shadow-none ${
          pinned ? "block" : "hidden group-hover/tip:block peer-focus-visible:block"
        }`}
      >
        {text}
      </span>
    </span>
  );
}
