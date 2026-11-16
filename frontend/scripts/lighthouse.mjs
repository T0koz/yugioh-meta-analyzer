// Mesure Lighthouse des pages du site sur un build de production.
//
//   npm run build && npm run start -- -p 3100     (API lancée à côté)
//   CHROME_PATH=<chromium> npm run lighthouse -- http://localhost:3100 mobile
//
// Écrit un tableau Markdown sur la sortie standard. Les scores varient de
// quelques points d'un passage à l'autre : comparer des tendances, pas des unités.
import lighthouse from "lighthouse";
import desktopConfig from "lighthouse/core/config/desktop-config.js";
import * as chromeLauncher from "chrome-launcher";

const base = process.argv[2] ?? "http://localhost:3100";
const formFactor = process.argv[3] === "desktop" ? "desktop" : "mobile";
const PAGES = [
  "/",
  "/tier-list",
  "/evolution",
  "/predictions",
  "/boutique",
  "/early-signals",
  "/graph",
  "/ban",
  "/ban?tab=impact",
];

const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless=new"] });
const pct = (category) => Math.round((category?.score ?? 0) * 100);
const ms = (audit) => `${Math.round(audit.numericValue)} ms`;

console.log(`| Page (${formFactor}) | Performance | Accessibilité | Bonnes pratiques | SEO | LCP | Blocage | CLS |`);
console.log("|---|---|---|---|---|---|---|---|");
try {
  for (const path of PAGES) {
    const { lhr } = await lighthouse(
      base + path,
      { port: chrome.port, output: "json", logLevel: "error" },
      formFactor === "desktop" ? desktopConfig : undefined
    );
    const c = lhr.categories;
    const a = lhr.audits;
    console.log(
      `| \`${path}\` | ${pct(c.performance)} | ${pct(c.accessibility)} | ${pct(c["best-practices"])} | ${pct(c.seo)} | ${ms(a["largest-contentful-paint"])} | ${ms(a["total-blocking-time"])} | ${a["cumulative-layout-shift"].numericValue.toFixed(3)} |`
    );
    const failed = Object.values(c.accessibility.auditRefs)
      .map((ref) => a[ref.id])
      .filter((audit) => audit.score !== null && audit.score < 1)
      .map((audit) => audit.id);
    if (failed.length) console.error(`  ${path} — accessibilité à corriger : ${failed.join(", ")}`);
  }
} finally {
  await chrome.kill();
}
