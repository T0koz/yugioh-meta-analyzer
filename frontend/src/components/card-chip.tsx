"use client";

import { useRef } from "react";
import { useHoverPreview } from "@/components/hover-preview-context";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export function CardChip({
  name,
  subtitle,
  className = "",
}: {
  name: string;
  subtitle?: string;
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
      const res = await fetch(`${API_BASE}/cards/${encodeURIComponent(name)}`);
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
      className={`px-2 py-0.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 cursor-default hover:border-indigo-500 hover:text-slate-100 transition-colors ${className}`}
    >
      {name}
    </span>
  );
}
