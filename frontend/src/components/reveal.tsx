"use client";

import { useEffect, useRef } from "react";

/**
 * Apparition à l'entrée dans l'écran, une seule fois.
 * Le HTML serveur est visible : c'est ce composant qui cache l'élément, et
 * seulement s'il est encore sous l'écran et que le mouvement est autorisé.
 * Sans JavaScript ou en mouvement réduit, rien n'est jamais caché.
 */
export function Reveal({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    // Déjà à l'écran au chargement : on ne le fait pas clignoter.
    if (el.getBoundingClientRect().top < window.innerHeight) return;

    el.classList.add("reveal-pending");
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        el.classList.replace("reveal-pending", "reveal-in");
        observer.disconnect();
      },
      { rootMargin: "0px 0px -10% 0px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
