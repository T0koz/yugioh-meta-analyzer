import type { Metadata } from "next";
import { Inter_Tight, Instrument_Serif, JetBrains_Mono } from "next/font/google";
import { Nav } from "@/components/nav";
import "./globals.css";

// Sans `weight` : next/font charge la version variable (un fichier, toutes les graisses).
const sans = Inter_Tight({ variable: "--font-inter-tight", subsets: ["latin"] });
const serif = Instrument_Serif({ variable: "--font-instrument-serif", subsets: ["latin"], weight: "400", style: "italic" });
const mono = JetBrains_Mono({ variable: "--font-jetbrains-mono", subsets: ["latin"], weight: ["400", "500"] });

// `template` s'applique aux pages enfants : chacune n'exporte que son titre court.
export const metadata: Metadata = {
  title: {
    default: "YGO Meta · Analyse de la méta Yu-Gi-Oh!",
    template: "%s · YGO Meta",
  },
  description:
    "Analyse de la méta Yu-Gi-Oh! TCG et OCG à partir des decklists de tournoi : tier list, prédictions, risque de ban et signaux pour les boutiques.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${sans.variable} ${serif.variable} ${mono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-ink text-text font-sans">
        <Nav />
        {children}
      </body>
    </html>
  );
}
