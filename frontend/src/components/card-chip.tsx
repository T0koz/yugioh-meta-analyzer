"use client";

import { useRef } from "react";
import { useHoverPreview } from "@/components/hover-preview-context";
import { apiBaseUrl } from "@/lib/api";

export function CardChip({
  name,
  subtitle,
  variant = "chip",
  className = "",
}: {
  name: string;
  subtitle?: string;
  /** `plain` : nom en texte courant (titre de ligne), même survol que la pastille. */
  variant?: "chip" | "plain";
  className?: string;
}) {
  const { setPreview } = useHoverPreview();
  const cachedImageRef = useRef<string | null | undefined>(undefined);
  const hoveredNameRef = useRef<string | null>(null);

  async function handleEnter() {
    hoveredNameRef.current = name;
    if (cachedImageRef.current !== undefined) {
      if (cachedImageRef.current) setPreview({ name, imageUrl: cachedImageRef.current, subtitle });
      return;
    }
    try {
      const res = await fetch(`${apiBaseUrl()}/cards/${encodeURIComponent(name)}`);
      const imageUrl = res.ok ? ((await res.json()).image_url_small ?? null) : null;
      cachedImageRef.current = imageUrl;
      // Ignore la réponse si la souris a déjà quitté cette carte (fetch trop lent).
      if (hoveredNameRef.current === name && imageUrl) {
        setPreview({ name, imageUrl, subtitle });
      }
    } catch {
      cachedImageRef.current = null;
    }
  }

  function handleLeave() {
    hoveredNameRef.current = null;
    setPreview(null);
  }

  return (
    <span
      onMouseEnter={() => void handleEnter()}
      onMouseLeave={handleLeave}
      className={`cursor-default transition-colors duration-200 ${
        variant === "chip"
          ? "inline-flex rounded-[4px] border border-line bg-ink-4 px-2 py-0.5 text-[14px] text-text hover:border-line-2"
          : "hover:text-signal-hi"
      } ${className}`}
    >
      {name}
    </span>
  );
}
