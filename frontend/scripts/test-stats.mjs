// Test du module src/lib/wilson.ts (lot 15). Sans dépendance : le fichier TypeScript
// est transpilé à la volée par le compilateur déjà installé, puis importé.
// Valeurs de référence calculées indépendamment (statsmodels proportion_confint,
// method="wilson", alpha=0.05), arrondies à 4 décimales.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import ts from "typescript";

const source = readFileSync(fileURLToPath(new URL("../src/lib/wilson.ts", import.meta.url)), "utf8");
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2020 },
});
const { wilsonInterval } = await import(`data:text/javascript,${encodeURIComponent(outputText)}`);

const cases = [
  // k, n, basse, haute
  [2, 156, 0.0035, 0.0455],
  [6, 156, 0.0177, 0.0814],
  [38, 412, 0.0679, 0.1241],
  [15, 16, 0.7167, 0.9889],
  [10, 100, 0.0552, 0.1744],
  [50, 100, 0.4038, 0.5962],
  [0, 50, 0, 0.0713],
  [50, 50, 0.9287, 1],
  [1, 1, 0.2065, 1],
];

let failures = 0;
for (const [k, n, lo, hi] of cases) {
  const [a, b] = wilsonInterval(k, n);
  try {
    assert.ok(Math.abs(a - lo) < 5e-4, `basse ${a.toFixed(4)} ≠ ${lo}`);
    assert.ok(Math.abs(b - hi) < 5e-4, `haute ${b.toFixed(4)} ≠ ${hi}`);
    assert.ok(a <= k / n && k / n <= b, "la part observée doit être dans l'intervalle");
  } catch (error) {
    failures += 1;
    console.error(`✗ Wilson(${k}, ${n}) : ${error.message}`);
  }
}

// Bords et cas dégénérés.
assert.deepEqual(wilsonInterval(0, 0), [0, 1]);
assert.deepEqual(wilsonInterval(3, -1), [0, 1]);
const [clampLo, clampHi] = wilsonInterval(12, 10); // k > n ramené à n
assert.equal(clampHi, 1);
assert.ok(Math.abs(clampLo - 0.7225) < 5e-4);
// La largeur diminue quand n augmente à part égale.
const width = (k, n) => wilsonInterval(k, n)[1] - wilsonInterval(k, n)[0];
assert.ok(width(10, 100) > width(100, 1000));

if (failures) {
  console.error(`${failures} cas en échec sur ${cases.length}`);
  process.exit(1);
}
console.log(`✓ Wilson : ${cases.length} cas de référence et 5 contrôles de bord`);
