"use client";

import { useHoverPreview } from "@/components/hover-preview-context";

export function HoverPreviewPanel() {
  const { preview } = useHoverPreview();
  if (!preview) return null;

  return (
    <div className="hidden xl:block fixed left-6 top-32 w-56 z-30">
      {/* eslint-disable-next-line @next/next/no-img-element -- preview externe (YGOPRODeck) */}
      <img
        src={preview.imageUrl}
        alt={preview.name}
        className="w-full rounded-lg shadow-2xl border border-slate-700"
      />
      <p className="mt-3 text-sm font-medium text-slate-200 text-center">{preview.name}</p>
      {preview.subtitle && (
        <p className="text-xs text-slate-500 text-center mt-0.5">{preview.subtitle}</p>
      )}
    </div>
  );
}
