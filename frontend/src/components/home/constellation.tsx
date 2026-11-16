// Illustration du graphe de synergies : trois amas de cartes reliés par deux
// cartes « pont ». Positions calculées (aucun hasard, aucune donnée) : c'est un
// schéma, signalé comme tel dans le pied de la tuile. SVG animé en CSS seul.

const W = 640;
const H = 320;
const CLUSTERS = [
  { x: 0.2, y: 0.5, n: 9 },
  { x: 0.52, y: 0.34, n: 11 },
  { x: 0.82, y: 0.56, n: 8 },
];
const BRIDGES = [
  { x: 0.36, y: 0.43, to: [0, 9, 12] },
  { x: 0.68, y: 0.44, to: [10, 14, 20, 24] },
];

type Node = { x: number; y: number; cluster: number };

const nodes: Node[] = [];
const links: [number, number][] = [];
CLUSTERS.forEach((c, ci) => {
  const base = nodes.length;
  for (let i = 0; i < c.n; i++) {
    const angle = (i / c.n) * 6.28;
    const radius = 0.06 + (i % 3) * 0.035;
    nodes.push({ x: (c.x + Math.cos(angle) * radius) * W, y: (c.y + Math.sin(angle) * radius * 1.9) * H, cluster: ci });
  }
  for (let i = 0; i < c.n; i++)
    for (let j = i + 1; j < c.n; j++) if ((i + j) % 3 === 0 || j === i + 1) links.push([base + i, base + j]);
});

const r1 = (v: number) => Math.round(v * 10) / 10;

export function Constellation({ names }: { names: string[] }) {
  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label="Schéma : trois amas de cartes reliés entre eux par deux cartes pont, en orange."
      className="home-constellation block h-auto w-full"
    >
      {BRIDGES.map((b, bi) =>
        b.to.map((target, k) => {
          const d = `M${r1(b.x * W)} ${r1(b.y * H)} L${r1(nodes[target].x)} ${r1(nodes[target].y)}`;
          return (
            <g key={`${bi}-${target}`}>
              <path d={d} stroke="var(--signal)" strokeOpacity=".55" strokeWidth="1.4" fill="none" />
              <circle
                r="2"
                fill="var(--signal-hi)"
                className="motion-reduce:hidden [animation:travel_2.4s_linear_infinite] [offset-distance:0%]"
                style={{ offsetPath: `path("${d}")`, animationDelay: `${-(bi * 3 + k) * 0.45}s` }}
              />
            </g>
          );
        })
      )}

      {CLUSTERS.map((c, ci) => (
        <g key={ci} data-cluster>
          {/* Zone de survol : sans elle, le survol ne prendrait que sur les points. */}
          <ellipse cx={c.x * W} cy={c.y * H} rx={W * 0.15} ry={H * 0.34} fill="transparent" />
          {links
            .filter(([a]) => nodes[a].cluster === ci)
            .map(([a, b]) => (
              <line
                key={`${a}-${b}`}
                x1={r1(nodes[a].x)}
                y1={r1(nodes[a].y)}
                x2={r1(nodes[b].x)}
                y2={r1(nodes[b].y)}
                stroke="var(--line-2)"
              />
            ))}
          {nodes.map((n, i) =>
            n.cluster === ci ? (
              <circle
                key={i}
                cx={r1(n.x)}
                cy={r1(n.y)}
                r="4"
                fill={i % 4 === 0 ? "var(--text)" : "var(--soft)"}
                className="home-node"
                style={{ "--n": i % 9, "--dx": `${(i % 3) - 1}px`, "--dy": `${(i % 2 ? 1 : -1) * 2}px` } as React.CSSProperties}
              />
            ) : null
          )}
          <text
            x={c.x * W}
            y={c.y * H + H * 0.4}
            textAnchor="middle"
            fill="var(--soft)"
            className="font-mono text-[11px] tracking-[0.08em] uppercase"
          >
            {names[ci] ?? `Archétype ${ci + 1}`}
          </text>
        </g>
      ))}

      {BRIDGES.map((b, bi) => (
        <g key={bi}>
          <circle cx={b.x * W} cy={b.y * H} r="15" fill="var(--signal)" fillOpacity=".16" />
          <circle cx={b.x * W} cy={b.y * H} r="7" fill="var(--signal)" />
          <text
            x={b.x * W}
            y={b.y * H - 22}
            textAnchor="middle"
            fill="var(--signal-hi)"
            className="font-mono text-[11px] font-medium tracking-[0.08em]"
          >
            PONT
          </text>
        </g>
      ))}
    </svg>
  );
}
