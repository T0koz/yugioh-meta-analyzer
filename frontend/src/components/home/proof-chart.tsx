import type { Proof } from "@/lib/proof-data";
import { fmtMonthShort, fmtNum } from "@/lib/format";

// Graphique « la preuve » : SVG rendu côté serveur dans son état final (les
// deux courbes tracées, les deux pics et l'écart annotés). Le tracé progressif
// est un embellissement piloté par ProofScroll via des variables CSS.

const W = 720;
const H = 380;
const X0 = 44;
const X1 = 700;
const Y0 = 330;
const Y1 = 24;
const MAX = 35;

const sy = (v: number) => Y0 - (v / MAX) * (Y0 - Y1);

export function ProofChart({ proof }: { proof: Proof }) {
  const { ocg, tcg, ocgPeak, tcgPeak, archetype, firstMonth } = proof;
  const N = ocg.length;
  const STEP = (X1 - X0) / (N - 1);
  const sx = (i: number) => X0 + i * STEP;
  const path = (values: readonly number[]) =>
    values.map((v, i) => `${i ? "L" : "M"}${sx(i).toFixed(1)} ${sy(v).toFixed(1)}`).join(" ");
  const monthAt = (index: number) => {
    const [year, month] = firstMonth.split("-").map(Number);
    return new Date(year, month - 1 + index, 1);
  };
  const monthName = (index: number) => monthAt(index).toLocaleDateString("fr-FR", { month: "long" });
  const axisLabel = (index: number) => {
    const d = monthAt(index);
    return fmtMonthShort(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`);
  };
  const lag = tcgPeak - ocgPeak;
  const lagY = sy(Math.max(ocg[ocgPeak], tcg[tcgPeak])) - 26;
  const text = "font-mono text-[11px]";

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label={`Part de ${archetype} dans les decks de tournoi, par mois, de ${axisLabel(0)} à ${axisLabel(N - 1)}. En OCG, pic à ${fmtNum(ocg[ocgPeak], 1)} % en ${monthName(ocgPeak)}. En TCG, pic à ${fmtNum(tcg[tcgPeak], 1)} % en ${monthName(tcgPeak)}, ${lag} mois plus tard.`}
      className="block h-auto w-full overflow-visible"
      style={{ "--lag-shift": `${(lag * STEP).toFixed(1)}px` } as React.CSSProperties}
    >
      <defs>
        <clipPath id="proof-plot">
          <rect x={X0} y="0" width={X1 - X0 + 8} height={Y0 + 2} />
        </clipPath>
      </defs>

      {[0, 10, 20, 30].map((v) => (
        <g key={v}>
          <line x1={X0} x2={X1} y1={sy(v)} y2={sy(v)} stroke="var(--line)" strokeDasharray="3 5" />
          <text x={X0 - 8} y={sy(v) + 4} textAnchor="end" fill="var(--muted-text)" className={text}>
            {v} %
          </text>
        </g>
      ))}
      {ocg.map((_, i) =>
        i % 2 === 0 ? (
          <text key={i} x={sx(i)} y={Y0 + 22} textAnchor="middle" fill="var(--muted-text)" className={text}>
            {axisLabel(i)}
          </text>
        ) : null
      )}

      <g clipPath="url(#proof-plot)">
        <g className="home-ocg-group">
          <path
            d={path(ocg)}
            pathLength={1}
            strokeDasharray="1"
            className="home-curve-ocg"
            fill="none"
            stroke="var(--ocg)"
            strokeWidth="2.5"
            strokeLinejoin="round"
          />
          <circle cx={sx(ocgPeak)} cy={sy(ocg[ocgPeak])} r="5" fill="var(--ocg)" className="home-mark home-mark-ocg-dot" />
          <text
            x={sx(ocgPeak)}
            y={sy(ocg[ocgPeak]) - 12}
            textAnchor="middle"
            fill="var(--ocg)"
            className={`home-mark home-mark-ocg-label ${text}`}
          >
            {fmtNum(ocg[ocgPeak], 1)} % · {monthName(ocgPeak)}
          </text>
        </g>
      </g>

      <path
        d={path(tcg)}
        pathLength={1}
        strokeDasharray="1"
        className="home-curve-tcg"
        fill="none"
        stroke="var(--signal)"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      <g className="home-mark home-mark-tcg">
        <circle cx={sx(tcgPeak)} cy={sy(tcg[tcgPeak])} r="5.5" fill="var(--signal)" />
        <text x={sx(tcgPeak) + 12} y={sy(tcg[tcgPeak]) + 4} fill="var(--signal-hi)" className={text}>
          {fmtNum(tcg[tcgPeak], 1)} % · {monthName(tcgPeak)}
        </text>
      </g>
      <g className="home-mark home-mark-lag">
        <path
          d={`M${sx(ocgPeak)} ${lagY + 6} V${lagY} H${sx(tcgPeak)} V${lagY + 6}`}
          fill="none"
          stroke="var(--text)"
          strokeWidth="1.5"
        />
        <text
          x={(sx(ocgPeak) + sx(tcgPeak)) / 2}
          y={lagY - 8}
          textAnchor="middle"
          fill="var(--text)"
          className={`${text} font-medium`}
        >
          {lag} mois
        </text>
      </g>
    </svg>
  );
}
