"use client";

import { useHoverPreview } from "@/components/hover-preview-context";

export function HoverPreviewPanel() {
  const { preview } = useHoverPreview();
  if (!preview) return null;

  return (
    <div className="pointer-events-none fixed top-32 left-6 z-30 hidden w-56 rounded-[8px] border border-line-2 bg-ink-3 p-3 xl:block">
      {/* eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck) */}
      <img src={preview.imageUrl} alt={preview.name} className="w-full rounded-[4px]" />
      <p className="mt-3 text-center text-[14px] font-medium text-text">{preview.name}</p>
      {preview.subtitle && (
        <p className="mt-0.5 text-center font-mono text-[11px] text-muted-text">{preview.subtitle}</p>
      )}
    </div>
  );
}
