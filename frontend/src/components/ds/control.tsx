// Composants d'interaction (lot 8) : boutons, pills de filtre, bascules et onglets.
// Source unique. L'apparence et les états (survol, appui, focus, désactivé) sont dans
// `globals.css`, bloc « Composants d'interaction » (classe `.ctl`) ; ce fichier ne fait
// que choisir la variante. Aucun état React, aucun `"use client"` : utilisable depuis un
// composant serveur comme depuis un composant client.
import Link from "next/link";
import type { ComponentProps } from "react";

/** `primary` (un seul par écran), `secondary`, `ghost` (discret), `pill` (filtre, bascule), `tab`. */
export type ControlVariant = "primary" | "secondary" | "ghost" | "pill" | "tab";
/** Taille des boutons ; pills et onglets ont la leur. */
export type ControlSize = "sm" | "md" | "lg";

type Look = {
  variant?: ControlVariant;
  size?: ControlSize;
  /** État actif sans attribut ARIA pour le porter (ex. groupe de la nav dont une page est ouverte). */
  active?: boolean;
  className?: string;
};

/**
 * Classes d'un contrôle. À utiliser seule quand la balise n'est ni un `<button>` ni un
 * `<Link>` : `<a href="#ancre">`, `<summary>`.
 */
export function controlClass({ variant = "secondary", size = "md", active = false, className }: Look = {}) {
  return [
    "ctl",
    `ctl-${variant}`,
    size !== "md" && (variant === "primary" || variant === "secondary" || variant === "ghost") && `ctl-${size}`,
    active && "ctl-on",
    className,
  ]
    .filter(Boolean)
    .join(" ");
}

/** Bouton. `type="button"` par défaut : préciser `type="submit"` dans un formulaire. */
export function Button({ variant, size, active, className, type = "button", ...props }: Look & ComponentProps<"button">) {
  return <button type={type} className={controlClass({ variant, size, active, className })} {...props} />;
}

/** Lien qui a l'apparence d'un bouton : reste un `<a>`. */
export function ButtonLink({ variant, size, active, className, ...props }: Look & ComponentProps<typeof Link>) {
  return <Link className={controlClass({ variant, size, active, className })} {...props} />;
}

/** Pill de filtre ou bascule : un `<button>` qui porte son état dans `aria-pressed`. */
export function Pill({ pressed, className, type = "button", ...props }: { pressed: boolean } & ComponentProps<"button">) {
  return <button type={type} aria-pressed={pressed} className={controlClass({ variant: "pill", className })} {...props} />;
}

/** Pill de filtre portée par l'adresse (`?kind=`) : un lien, `aria-current="page"` quand il est actif. */
export function PillLink({ current, className, ...props }: { current: boolean } & ComponentProps<typeof Link>) {
  return (
    <Link aria-current={current ? "page" : undefined} className={controlClass({ variant: "pill", className })} {...props} />
  );
}

/** Rail d'onglets portés par l'adresse (`?tab=`) : un `<nav>` de liens. */
export function TabRail({ className, ...props }: ComponentProps<"nav">) {
  return <nav className={["ctl-rail", className].filter(Boolean).join(" ")} {...props} />;
}

/** Onglet du rail : un lien, `aria-current="page"` quand il est actif. */
export function TabLink({ current, className, ...props }: { current: boolean } & ComponentProps<typeof Link>) {
  return (
    <Link aria-current={current ? "page" : undefined} className={controlClass({ variant: "tab", className })} {...props} />
  );
}
