// Formats français de l'interface (docs/design-system.md §7) : virgule
// décimale, espace pour les milliers, mois en toutes lettres.

const numberFormats = new Map<number, Intl.NumberFormat>();

export function fmtNum(value: number, digits = 0): string {
  let format = numberFormats.get(digits);
  if (!format) {
    format = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
    numberFormats.set(digits, format);
  }
  return format.format(value);
}

/** `value` déjà exprimé en pourcentage (29.56 → « 29,6 % »). */
export function fmtPct(value: number, digits = 1): string {
  return `${fmtNum(value, digits)} %`;
}

/** `value` signé, avec un vrai signe moins typographique. */
export function fmtSigned(value: number, digits = 1): string {
  const abs = fmtNum(Math.abs(value), digits);
  if (value > 0) return `+${abs}`;
  if (value < 0) return `−${abs}`;
  return abs;
}

/** « 2026-06-17 » → « 17 juin 2026 ». Date invalide : renvoyée telle quelle. */
export function fmtDate(iso: string): string {
  const date = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

/** « October 2026 » (format de l'API) → « oct. 2026 ». Valeur non reconnue : renvoyée telle quelle. */
export function fmtMonthYear(label: string): string {
  const date = new Date(`1 ${label}`);
  if (Number.isNaN(date.getTime())) return label;
  return date.toLocaleDateString("fr-FR", { month: "short", year: "numeric" });
}

/** Fenêtre entre deux dates ISO → « nov. 26 à mars 27 » ; nul si une borne manque. */
export function fmtMonthRange(startIso: string | null, endIso: string | null): string | null {
  if (!startIso || !endIso) return null;
  const start = fmtMonthShort(startIso.slice(0, 7));
  const end = fmtMonthShort(endIso.slice(0, 7));
  return start === end ? start : `${start} à ${end}`;
}

/** « 2026-01 » → « janv. 26 » (axes de graphique). Valeur non reconnue : renvoyée telle quelle. */
export function fmtMonthShort(yearMonth: string): string {
  const date = new Date(`${yearMonth}-01T00:00:00`);
  if (Number.isNaN(date.getTime())) return yearMonth;
  return date.toLocaleDateString("fr-FR", { month: "short", year: "2-digit" });
}

/** Rang ordinal : 1 → « 1er », 18 → « 18ᵉ ». */
export function fmtRank(rank: number): string {
  return rank === 1 ? "1er" : `${rank}ᵉ`;
}

/** Fenêtre de mois « AAAA-MM » → « oct. 26 à nov. 26 » (un seul mois : « nov. 26 »). */
export function fmtWindow(window: { start: string; end: string }): string {
  return window.start === window.end
    ? fmtMonthShort(window.end)
    : `${fmtMonthShort(window.start)} à ${fmtMonthShort(window.end)}`;
}

/** Résultat de tournoi : 1 → « Vainqueur », 2 → « Finaliste », 3,5 → « Top 4 », 8 → « Top 8 ». */
export function fmtPlacement(placement: number): string {
  if (placement <= 1) return "Vainqueur";
  if (placement <= 2) return "Finaliste";
  return `Top ${Math.ceil(placement)}`;
}

/** Médiane d'exemplaires : « 3 », ou « 2,5 » quand elle tombe entre deux valeurs. */
export function fmtCopies(copies: number): string {
  return fmtNum(copies, Number.isInteger(copies) ? 0 : 1);
}
