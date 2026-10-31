import type { Tier, Trend } from "@/types";

// Étiquettes mono du design system (docs/design-system.md §4). Plus aucune
// couleur propre à chaque tier : l'accent seul marque ce qui compte.

const TAG = "inline-flex w-fit items-center rounded-[3px] border px-[7px] py-[3px] font-mono text-[11px] font-medium leading-none tracking-[0.08em] whitespace-nowrap";

/** `strong` = plein accent (T0/T1, signal Fort), `outline` = contour accent (T2), sinon neutre. */
export function Tag({
  children,
  tone = "neutral",
}: {
  children: React.ReactNode;
  tone?: "strong" | "outline" | "plain" | "neutral";
}) {
  const style = {
    strong: "border-signal bg-signal text-on-signal",
    outline: "border-signal text-signal",
    plain: "border-line-2 text-text",
    neutral: "border-line-2 text-soft",
  }[tone];
  return <span className={`${TAG} ${style}`}>{children}</span>;
}

export function TierTag({ tier }: { tier: Tier }) {
  const tone = tier === "T0" || tier === "T1" ? "strong" : tier === "T2" ? "outline" : tier === "T3" ? "plain" : "neutral";
  return <Tag tone={tone}>{tier.toUpperCase()}</Tag>;
}

const TREND = {
  Rising: { arrow: "▲", className: "text-good" },
  Stable: { arrow: "→", className: "text-muted-text" },
  // Pas de rouge pour une baisse : le rouge est réservé à l'accent.
  Declining: { arrow: "▼", className: "text-muted-text" },
} satisfies Record<Trend, { arrow: string; className: string }>;

export function TrendLabel({ trend }: { trend: Trend }) {
  const { arrow, className } = TREND[trend];
  return (
    <span className={`font-mono text-[12px] font-medium whitespace-nowrap ${className}`}>
      {arrow} {trend}
    </span>
  );
}

/** Statut banlist : restrictions en --warn (seul usage du jaune), le reste neutre. */
export function BanStatus({ status }: { status: string }) {
  const restricted = status !== "Unlimited";
  return (
    <span
      className={`inline-flex w-fit items-center rounded-[3px] border px-2 py-1 font-mono text-[11px] font-medium leading-none tracking-[0.06em] whitespace-nowrap uppercase ${
        restricted ? "border-warn/50 text-warn" : "border-line-2 text-soft"
      }`}
    >
      {status}
    </span>
  );
}
