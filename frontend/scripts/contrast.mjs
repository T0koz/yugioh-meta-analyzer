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

// ---------- Composants d'interaction (lot 8) ----------
// Texte de chaque variante sur son fond, pour chaque état. Le fond porte un dégradé
// (--ctl-sheen-top en haut, --ctl-sheen-bottom en bas) : on mesure la couleur nue et ses
// deux extrêmes, et on retient le pire rapport. `sheen: false` = état sans dégradé.
function rgba(name) {
  const m = /^rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)$/.exec(tokens[name] ?? "");
  if (!m) throw new Error(`${name} : rgba() attendu, lu « ${tokens[name]} »`);
  return m.slice(1).map(Number);
}
function over(hex, [r, g, b, a]) {
  const mix = [1, 3, 5].map((i, k) => Math.round(parseInt(hex.slice(i, i + 2), 16) * (1 - a) + [r, g, b][k] * a));
  return `#${mix.map((c) => c.toString(16).padStart(2, "0")).join("")}`;
}
const SHEEN = [rgba("--ctl-sheen-top"), rgba("--ctl-sheen-bottom")];
const CONTROLS = [
  // [variante, état, texte, fond, dégradé]
  ["principal", "repos", "--on-signal", "--signal", true],
  ["principal", "survol", "--on-signal", "--signal-hi", true],
  ["principal", "appui", "--on-signal", "--ctl-primary-lo", true],
  ["secondaire", "repos", "--text", "--ink-3", true],
  ["secondaire", "survol", "--text", "--ink-4", true],
  ["secondaire", "appui", "--text", "--ink-3", true],
  ["discret", "repos", "--soft", "--ink", false],
  ["discret", "repos (sur tuile)", "--soft", "--ink-3", false],
  ["discret", "survol, appui", "--text", "--ink-4", false],
  ["pill", "repos", "--soft", "--ink-3", true],
  ["pill", "survol", "--text", "--ink-4", true],
  ["pill active", "repos", "--ink", "--text", true],
  ["pill active", "survol", "--ink", "--ctl-on-hi", true],
  ["pill active", "appui", "--ink", "--ctl-on-lo", true],
  ["onglet", "repos (rail)", "--muted-text", "--ink-2", false],
  ["onglet", "survol", "--text", "--ink-3", false],
  ["onglet", "appui", "--text", "--ink-4", false],
  ["onglet actif", "repos", "--text", "--ink-4", true],
  ["onglet actif", "survol", "--text", "--ctl-raise", true],
  ["tous", "désactivé", "--faint", "--ink-4", false],
];
console.log(`\n| Contrôle | État | Texte | Fond | Pire rapport |`);
console.log("|---|---|---|---|---|");
for (const [variant, state, fg, bg, sheen] of CONTROLS) {
  const base = resolve(bg);
  const fonds = sheen ? [base, ...SHEEN.map((layer) => over(base, layer))] : [base];
  const ratio = Math.min(...fonds.map((fond) => contrast(resolve(fg), fond)));
  if (ratio < MIN) failed += 1;
  console.log(`| ${variant} | ${state} | \`${fg}\` | \`${bg}\` | ${ratio.toFixed(2).replace(".", ",")}${ratio < MIN ? " ✗" : ""} |`);
}
// Anneau de focus : élément graphique, seuil WCAG 1.4.11 de 3:1 sur les surfaces voisines.
const RING_MIN = 3;
const ring = SURFACES.map((surface) => contrast(resolve("--signal-hi"), resolve(surface)));
if (Math.min(...ring) < RING_MIN) failed += 1;
console.log(`\nAnneau de focus \`--signal-hi\` sur ${SURFACES.join(", ")} : ${ring.map((r) => r.toFixed(2).replace(".", ",")).join(" / ")} (seuil ${RING_MIN}:1).`);

console.log(failed ? `\n${failed} paire(s) sous ${MIN}:1.` : `\nToutes les paires atteignent ${MIN}:1 (WCAG AA).`);
process.exit(failed ? 1 : 0);
