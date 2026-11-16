"use client";

import Image, { type ImageProps } from "next/image";
import { useState, type ReactNode } from "react";

/** `next/image` avec repli : si le fichier de la carte manque chez nous (404), on affiche `fallback`, jamais une image cassée. */
export function SafeImage({ fallback, ...props }: ImageProps & { fallback: ReactNode }) {
  const [failed, setFailed] = useState(false);
  if (failed) return <>{fallback}</>;
  // eslint-disable-next-line jsx-a11y/alt-text -- `alt` est transmis par l'appelant
  return <Image {...props} onError={() => setFailed(true)} />;
}
