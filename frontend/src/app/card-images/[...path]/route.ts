import { readFile } from "node:fs/promises";
import path from "node:path";

// Sert en local les images de cartes téléchargées par `scripts/download_card_images.py` (TOK-92).
// Hébergement de développement seulement : au déploiement (TOK-35), NEXT_PUBLIC_CARD_IMAGES_URL
// pointe vers le stockage définitif et cette route ne reçoit plus de requête.
// Dossier : CARD_IMAGES_DIR, sinon ../data/card-images (dépôt principal, hors Git).

const DIR = path.resolve(process.env.CARD_IMAGES_DIR || path.join(process.cwd(), "..", "data", "card-images"));
const FOLDERS = new Set(["art", "card-sm", "card-lg"]);

export async function GET(_req: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path: parts } = await ctx.params;
  // Deux segments exactement, dossier connu, identifiant numérique : aucune autre lecture possible.
  if (parts.length !== 2 || !FOLDERS.has(parts[0]) || !/^\d+\.webp$/.test(parts[1])) {
    return new Response("Not found", { status: 404 });
  }
  try {
    const file = await readFile(path.join(DIR, parts[0], parts[1]));
    return new Response(new Uint8Array(file), {
      headers: { "Content-Type": "image/webp", "Cache-Control": "public, max-age=2678400, immutable" },
    });
  } catch {
    return new Response("Not found", { status: 404 });
  }
}
