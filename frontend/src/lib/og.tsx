import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { DECK_SOURCE, SITE_NAME } from "@/lib/site";

// Images de partage (Open Graph) : typographie, tokens et formes du design system.
// Aucune illustration de carte n'y est reproduite. Un chiffre n'est dessiné qu'avec
// sa période et sa source ; les pages sans chiffre daté n'en montrent aucun.
// Les réseaux gardent un aperçu en cache plusieurs jours : une image datée reste juste.

export const OG_SIZE = { width: 1200, height: 630 };
export const OG_CONTENT_TYPE = "image/png";

const FONT_DIR = join(process.cwd(), "src/assets/og-fonts");
const font = (file: string) => readFile(join(FONT_DIR, file));

/** Tokens de globals.css : seule source des couleurs, comme scripts/contrast.mjs. */
async function loadTokens(): Promise<(name: string) => string> {
  const css = await readFile(join(process.cwd(), "src/app/globals.css"), "utf8");
  const tokens = new Map([...css.matchAll(/^\s*(--[\w-]+):\s*([^;]+);/gm)].map((m) => [m[1], m[2].trim()]));
  return (name) => {
    let value = tokens.get(name);
    for (let i = 0; i < 5 && value?.startsWith("var("); i++) value = tokens.get(value.slice(4, -1).trim());
    if (!value) throw new Error(`Token ${name} introuvable dans globals.css`);
    return value;
  };
}

export interface OgSpec {
  /** Surtitre en capitales : « Tier list · TCG ». */
  eyebrow: string;
  title: string;
  /** Mot du titre mis en italique d'accent (grammaire `Em` du design system). */
  emphasis?: string;
  /** Grand chiffre et sa légende (unité, population, période). */
  figure?: { value: string; legend: string[] };
  /** Série dessinée à droite ; `caption` donne la mesure et la période. */
  series?: { values: number[]; caption: string };
  /** Lignes de pied : ce qui est mesuré et la source. */
  footer: string[];
}

/** « Mesure · population · source » pour une page sans chiffre daté. */
export const sourceLine = (measure: string) => [measure, `Source : ${DECK_SOURCE}`];

// Marque du site : même tracé que le pied de page (clip-path de SiteFooter).
const FLAME = "0,100 30,0 50,60 70,0 100,100 80,100 70,45 50,100 30,45 20,100";

function Flame({ size, color, opacity = 1 }: { size: number; color: string; opacity?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" style={{ opacity }}>
      <polygon points={FLAME} fill={color} />
    </svg>
  );
}

function Sparkline({ values, stroke, fill }: { values: number[]; stroke: string; fill: string }) {
  const width = 320;
  const height = 150;
  const max = Math.max(...values, 1e-9);
  const step = width / Math.max(values.length - 1, 1);
  const points = values.map((v, i) => `${(i * step).toFixed(1)},${(height - 6 - (v / max) * (height - 12)).toFixed(1)}`);
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polygon points={`0,${height} ${points.join(" ")} ${width},${height}`} fill={fill} />
      <polyline points={points.join(" ")} fill="none" stroke={stroke} strokeWidth={3} strokeLinejoin="round" />
    </svg>
  );
}

export async function ogImage(spec: OgSpec): Promise<ImageResponse> {
  const [token, sans, mono, serif] = await Promise.all([
    loadTokens(),
    font("inter-tight-latin-500-normal.woff"),
    font("jetbrains-mono-latin-500-normal.woff"),
    font("instrument-serif-latin-400-italic.woff"),
  ]);
  const titleSize = spec.title.length > 44 ? 62 : spec.title.length > 26 ? 76 : 96;
  // Satori ne fait pas couler du texte autour d'un <span> : le titre est posé mot à mot.
  const emphasized = new Set(spec.emphasis?.split(" "));
  const emphasisStart = spec.emphasis ? spec.title.indexOf(spec.emphasis) : -1;
  let offset = 0;
  const words = spec.title.split(" ").map((word) => {
    const start = offset;
    offset += word.length + 1;
    const inEmphasis = emphasisStart >= 0 && start >= emphasisStart && start < emphasisStart + spec.emphasis!.length;
    return { word, accent: inEmphasis && emphasized.has(word) };
  });
  const monoStyle = { fontFamily: "JetBrains Mono", fontSize: 19, letterSpacing: 0.8 } as const;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "56px 64px",
          backgroundColor: token("--ink"),
          backgroundImage: `radial-gradient(circle at 88% 108%, ${token("--glow")}, transparent 58%)`,
          color: token("--text"),
          fontFamily: "Inter Tight",
        }}
      >
        {!spec.series && (
          <div style={{ position: "absolute", right: -40, top: 130, display: "flex" }}>
            <Flame size={430} color={token("--ink-3")} />
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <Flame size={30} color={token("--signal")} />
            <span style={{ ...monoStyle, fontSize: 26, letterSpacing: 3 }}>{SITE_NAME.toUpperCase()}</span>
          </div>
          <span style={{ ...monoStyle, color: token("--muted-text") }}>{spec.eyebrow.toUpperCase()}</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 30 }}>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              alignItems: "baseline",
              columnGap: titleSize * 0.22,
              maxWidth: spec.series ? 1072 : 940,
              fontSize: titleSize,
              lineHeight: 1.04,
              letterSpacing: titleSize * -0.04,
            }}
          >
            {words.map(({ word, accent }, i) =>
              accent ? (
                <span
                  key={i}
                  style={{ fontFamily: "Instrument Serif", fontStyle: "italic", color: token("--signal"), letterSpacing: titleSize * -0.02 }}
                >
                  {word}
                </span>
              ) : (
                <span key={i}>{word}</span>
              )
            )}
          </div>

          {(spec.figure || spec.series) && (
            <div style={{ display: "flex", width: "100%", alignItems: "flex-end", justifyContent: "space-between", gap: 32 }}>
              {spec.figure ? (
                <div style={{ display: "flex", alignItems: "flex-end", gap: 24 }}>
                  <span style={{ fontSize: 100, lineHeight: 0.9, letterSpacing: -4, color: token("--signal") }}>
                    {spec.figure.value}
                  </span>
                  <div style={{ display: "flex", flexDirection: "column", gap: 6, ...monoStyle, color: token("--soft") }}>
                    {spec.figure.legend.map((line) => (
                      <span key={line}>{line}</span>
                    ))}
                  </div>
                </div>
              ) : (
                <span />
              )}
              {spec.series && spec.series.values.length > 1 && (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 10 }}>
                  <Sparkline values={spec.series.values} stroke={token("--signal")} fill={token("--tile-glow")} />
                  <span style={{ ...monoStyle, fontSize: 16, letterSpacing: 0, color: token("--muted-text") }}>{spec.series.caption}</span>
                </div>
              )}
            </div>
          )}
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 32,
            paddingTop: 22,
            borderTop: `1px solid ${token("--line-2")}`,
            ...monoStyle,
            color: token("--soft"),
          }}
        >
          {spec.footer.map((line) => (
            <span key={line}>{line}</span>
          ))}
        </div>
      </div>
    ),
    {
      ...OG_SIZE,
      fonts: [
        { name: "Inter Tight", data: sans, weight: 500, style: "normal" },
        { name: "JetBrains Mono", data: mono, weight: 500, style: "normal" },
        { name: "Instrument Serif", data: serif, weight: 400, style: "italic" },
      ],
    }
  );
}
