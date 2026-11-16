// Vérifie les balises de partage et de référencement sur le HTML servi en local (TOK-100).
// Aucun service externe : le script lit les pages, robots.txt, sitemap.xml et les images
// Open Graph d'un serveur local, et sort en code 1 à la première règle non tenue.
//
//   npm run build && npm run start -- -p 3100     (API lancée à côté)
//   npm run check:meta -- http://localhost:3100
//
// Variables lues (les mêmes que le build) : NEXT_PUBLIC_SITE_URL (adresse publique attendue
// dans les balises, défaut http://localhost:3000) et NEXT_PUBLIC_API_URL (liste des archétypes).
// `python scripts/visual_tests.py` le lance aussi, sur son propre serveur.

const base = (process.argv[2] ?? "http://localhost:3100").replace(/\/+$/, "");
const site = (process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000").replace(/\/+$/, "");
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const STATIC_PATHS = [
  "/",
  "/tier-list",
  "/decks",
  "/evolution",
  "/predictions",
  "/boutique",
  "/early-signals",
  "/graph",
  "/ban",
  "/ban?tab=historique",
  "/ban?tab=impact",
  "/ban?tab=simulateur",
];
const TITLE_MAX = 70; // au-delà, les moteurs tronquent
const DESCRIPTION_RANGE = [50, 200];
const OG_SIZE = { width: 1200, height: 630 };

const errors = [];
const fail = (where, message) => errors.push(`${where} : ${message}`);
const absolute = (path) => (path === "/" ? site : site + path);

const ENTITIES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'" };
const decode = (text) =>
  text.replace(/&(#x[0-9a-f]+|#\d+|\w+);/gi, (match, code) => {
    if (code[0] !== "#") return ENTITIES[code] ?? match;
    return String.fromCodePoint(code[1].toLowerCase() === "x" ? parseInt(code.slice(2), 16) : Number(code.slice(1)));
  });

/** Balises <meta> et <link rel=canonical> de l'en-tête, en { clé: [valeurs] }. */
function readHead(html) {
  const tags = {};
  const push = (key, value) => (tags[key] ??= []).push(decode(value));
  for (const [tag] of html.matchAll(/<(?:meta|link)\b[^>]*>/gi)) {
    const attr = (name) => tag.match(new RegExp(`\\b${name}="([^"]*)"`, "i"))?.[1];
    if (/^<meta/i.test(tag)) {
      const key = attr("property") ?? attr("name");
      if (key && attr("content") !== undefined) push(key, attr("content"));
    } else if (attr("rel") === "canonical") {
      push("canonical", attr("href") ?? "");
    }
  }
  // Le premier <title> est celui du document ; les suivants appartiennent aux SVG des graphiques.
  const title = html.match(/<title>([^<]*)<\/title>/i)?.[1];
  if (title !== undefined) push("title", title);
  tags.lang = [html.match(/<html[^>]*\blang="([^"]*)"/i)?.[1] ?? ""];
  return tags;
}

async function get(path) {
  const res = await fetch(base + path, { redirect: "manual" });
  return { status: res.status, type: res.headers.get("content-type") ?? "", body: Buffer.from(await res.arrayBuffer()) };
}

const imageCache = new Map();
async function checkImage(where, url) {
  if (!url.startsWith(site + "/")) return fail(where, `og:image hors du site : ${url}`);
  const path = url.slice(site.length);
  if (!imageCache.has(path)) imageCache.set(path, get(path));
  const { status, type, body } = await imageCache.get(path);
  if (status !== 200) return fail(where, `og:image répond ${status} (${path})`);
  if (!type.startsWith("image/png")) return fail(where, `og:image n'est pas un PNG (${type})`);
  // En-tête PNG : largeur et hauteur aux octets 16 et 20.
  const [width, height] = [body.readUInt32BE(16), body.readUInt32BE(20)];
  if (width !== OG_SIZE.width || height !== OG_SIZE.height) fail(where, `og:image mesure ${width}×${height}`);
  return body.length;
}

/** Une page publique : toutes les balises d'un aperçu de lien, cohérentes entre elles. */
async function checkPage(path, canonicalPath = path) {
  const { status, body } = await get(path);
  if (status !== 200) return fail(path, `répond ${status}`);
  const head = readHead(body.toString("utf8"));
  const one = (key) => {
    const values = head[key] ?? [];
    if (values.length !== 1) fail(path, `${key} : ${values.length} occurrence(s), 1 attendue`);
    return values[0] ?? "";
  };

  const title = one("title");
  const description = one("description");
  const canonical = one("canonical");
  if (head.lang[0] !== "fr") fail(path, `<html lang> vaut « ${head.lang[0]} »`);
  if (!title || title.length > TITLE_MAX) fail(path, `titre de ${title.length} caractères (1 à ${TITLE_MAX})`);
  if (description.length < DESCRIPTION_RANGE[0] || description.length > DESCRIPTION_RANGE[1])
    fail(path, `description de ${description.length} caractères (${DESCRIPTION_RANGE.join(" à ")})`);
  // Consigne de ton : pas de point d'exclamation, hors le nom du jeu.
  for (const [label, text] of [["titre", title], ["description", description]])
    if (text.replaceAll("Yu-Gi-Oh!", "").includes("!")) fail(path, `point d'exclamation dans ${label}`);
  if (canonical !== absolute(canonicalPath)) fail(path, `canonique « ${canonical} », attendu « ${absolute(canonicalPath)} »`);
  if ((head.robots ?? []).some((value) => value.includes("noindex"))) fail(path, "page publique en noindex");

  if (one("og:url") !== canonical) fail(path, "og:url diffère du lien canonique");
  if (!one("og:title")) fail(path, "og:title vide");
  if (one("og:description") !== description) fail(path, "og:description diffère de la description");
  if (one("og:type") !== "website") fail(path, "og:type attendu : website");
  if (one("og:site_name") !== "YGO Meta") fail(path, "og:site_name attendu : YGO Meta");
  if (one("og:locale") !== "fr_FR") fail(path, "og:locale attendu : fr_FR");
  if (one("og:image:width") !== String(OG_SIZE.width) || one("og:image:height") !== String(OG_SIZE.height))
    fail(path, "og:image:width / height attendus : 1200 × 630");
  if (!one("og:image:alt")) fail(path, "og:image:alt vide");
  if (one("twitter:card") !== "summary_large_image") fail(path, "twitter:card attendu : summary_large_image");
  if (!one("twitter:title") || one("twitter:description") !== description) fail(path, "twitter:title / description incohérents");
  const image = one("og:image");
  if (one("twitter:image") !== image) fail(path, "twitter:image diffère de og:image");
  const imageBytes = image ? await checkImage(path, image) : undefined;
  return { path, title, description, canonical, image, imageBytes };
}

async function archetypeSlugs() {
  const [tierList, boutique] = await Promise.all(
    ["/meta/tier-list", "/boutique/signals"].map(async (path) => (await fetch(apiUrl + path)).json())
  );
  return [...new Set([...tierList.data.map((e) => e.slug), ...boutique.data.map((s) => s.archetype_slug)])].sort();
}

async function deckSlugs() {
  const decks = await (await fetch(apiUrl + "/decks")).json();
  return decks.data.filter((d) => d.has_profile).map((d) => d.slug).sort();
}

// ── Pages principales ──────────────────────────────────────────────────────────
const slugs = await archetypeSlugs();
const decks = await deckSlugs();
const pages = [];
for (const path of STATIC_PATHS) pages.push(await checkPage(path));

// Deux pages ne partagent ni titre ni description.
for (const key of ["title", "description"]) {
  const seen = new Map();
  for (const page of pages.filter(Boolean)) {
    if (seen.has(page[key])) fail(page.path, `${key} identique à ${seen.get(page[key])}`);
    seen.set(page[key], page.path);
  }
}

// ── robots.txt et sitemap.xml ──────────────────────────────────────────────────
const robots = (await get("/robots.txt")).body.toString("utf8");
if (!robots.includes(`Sitemap: ${site}/sitemap.xml`)) fail("/robots.txt", "ligne Sitemap absente ou sur une autre adresse");
if (/^Disallow:\s*\/\s*$/im.test(robots)) fail("/robots.txt", "tout le site est interdit");

const sitemap = (await get("/sitemap.xml")).body.toString("utf8");
const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => decode(m[1]));
const expected = [
  ...STATIC_PATHS.map(absolute),
  ...slugs.map((slug) => absolute(`/archetype/${slug}`)),
  ...decks.map((slug) => absolute(`/decks/${slug}`)),
];
for (const url of expected) if (!locs.includes(url)) fail("/sitemap.xml", `adresse absente : ${url}`);
for (const url of locs) if (!expected.includes(url)) fail("/sitemap.xml", `adresse inattendue : ${url}`);
if (new Set(locs).size !== locs.length) fail("/sitemap.xml", "adresses en double");

// Chaque adresse du sitemap répond 200 et se désigne elle-même comme canonique.
let archetypePages = 0;
for (const slug of slugs) {
  const page = await checkPage(`/archetype/${slug}`);
  if (page) archetypePages++;
}
let deckPages = 0;
for (const slug of decks) {
  const page = await checkPage(`/decks/${slug}`);
  if (page) deckPages++;
}

// ── Canonique d'une variante de casse, et page absente ─────────────────────────
if (slugs.length) await checkPage(`/archetype/${slugs[0].toUpperCase()}`, `/archetype/${slugs[0]}`);
const missing = await get("/archetype/cet-archetype-n-existe-pas");
if (missing.status !== 404) fail("page absente", `répond ${missing.status}, 404 attendu`);
else if (!(readHead(missing.body.toString("utf8")).robots ?? []).some((v) => v.includes("noindex")))
  fail("page absente", "la 404 n'est pas en noindex");

// ── Compte rendu ───────────────────────────────────────────────────────────────
console.log(`Balises de partage — serveur ${base}, adresse publique ${site}`);
console.log("| Page | Titre | Description (car.) | Image (ko) |");
console.log("|---|---|---|---|");
for (const page of pages.filter(Boolean))
  console.log(`| \`${page.path}\` | ${page.title} | ${page.description.length} | ${page.imageBytes ? Math.round(page.imageBytes / 1000) : "?"} |`);
console.log(`\n${pages.filter(Boolean).length} pages principales, ${archetypePages} pages d'archétype, ${deckPages} fiches de deck, ${locs.length} adresses dans le sitemap.`);

if (errors.length) {
  console.error(`\n✗ ${errors.length} règle(s) non tenue(s) :`);
  for (const error of errors) console.error(`  - ${error}`);
  process.exit(1);
}
console.log("✓ Titre, description, canonique, Open Graph, Twitter, image 1200 × 630, robots.txt et sitemap.xml cohérents.");
