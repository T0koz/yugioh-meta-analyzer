"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

type Preview = { name: string; imageUrl: string; subtitle?: string } | null;

const HoverPreviewContext = createContext<{
  preview: Preview;
  setPreview: (p: Preview) => void;
} | null>(null);

export function HoverPreviewProvider({ children }: { children: ReactNode }) {
  const [preview, setPreview] = useState<Preview>(null);
  return (
    <HoverPreviewContext.Provider value={{ preview, setPreview }}>
      {children}
    </HoverPreviewContext.Provider>
  );
}

export function useHoverPreview() {
  const ctx = useContext(HoverPreviewContext);
  if (!ctx) throw new Error("useHoverPreview must be used within a HoverPreviewProvider");
  return ctx;
}
