// Audit de contraste des couleurs de données (TOK-99) : lit les tokens de
// src/app/globals.css et vérifie le rapport WCAG de chaque teinte sur les quatre
// surfaces sombres. Seuil : 4,5:1 (AA pour du texte ; un tracé n'exige que 3:1).
//
//   npm run contrast        → tableau Markdown, code de sortie 1 si une paire échoue
import { readFileSync } from "node:fs";

const css = readFileSync(new URL("../src/app/globals.css", import.meta.url), "utf8");
const tokens = Object.fromEntries([...css.matchAll(/^\s*(--[\w-]+):\s*([^;]+);/gm)].map((m) => [m[1], m[2].trim()]));

function resolve(name) {
  let value = tokens[name];
  for (let i = 0; i < 5 && value?.startsWith("var("); i++) value = tokens[value.slice(4, -1).trim()];
  if (!/^#[0-9a-f]{6}$/i.test(value ?? "")) throw new Error(`${name} : valeur hexadécimale attendue, lu « ${value} »`);
  return value;
}

function luminance(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

const SURFACES = ["--ink", "--ink-2", "--ink-3", "--ink-4"];
const COLORS = ["--cat-1", "--cat-2", "--cat-3", "--cat-4", "--cat-5", "--cat-6", "--ocg", "--good", "--warn", "--soft", "--muted-text", "--faint"];
const MIN = 4.5;

let failed = 0;
console.log(`| Token | Valeur | ${SURFACES.join(" | ")} |`);
console.log(`|---|---|${SURFACES.map(() => "---").join("|")}|`);
for (const name of COLORS) {
  const hex = resolve(name);
  const cells = SURFACES.map((surface) => {
    const ratio = contrast(hex, resolve(surface));
    if (ratio < MIN) failed += 1;
    return `${ratio.toFixed(2).replace(".", ",")}${ratio < MIN ? " ✗" : ""}`;
  });
  console.log(`| \`${name}\` | \`${hex}\` | ${cells.join(" | ")} |`);
}
console.log(failed ? `\n${failed} paire(s) sous ${MIN}:1.` : `\nToutes les paires atteignent ${MIN}:1 (WCAG AA).`);
process.exit(failed ? 1 : 0);
