// Seeded known-truth DGP for 2x2 trials, for Fragility-Index validation.
//
// Each trial: n per arm; control event prob p0; treatment event prob p1.
//   NULL  trials: p1 == p0           (truth = 0, RR = 1, no real effect)
//   EFFECT trials: p1 != p0          (truth = 1, a genuine effect)
//
// We draw event counts from Binomial(n, p) and assemble the 2x2 table
// a = treatment events, b = treatment non-events, c = control events, d = control non-events.

// --- deterministic PRNG (mulberry32) ---
export function mulberry32(seed) {
  let s = seed >>> 0;
  return function () {
    s |= 0; s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function rbinom(rng, n, p) {
  let x = 0;
  for (let i = 0; i < n; i++) if (rng() < p) x++;
  return x;
}

// Generate one trial table given truth and parameters.
export function makeTrial(rng, { n, p0, effect, truth }) {
  const pc = p0;
  const pt = truth === 1 ? clamp01(p0 + effect) : p0;
  const cEvents = rbinom(rng, n, pc);
  const tEvents = rbinom(rng, n, pt);
  return {
    a: tEvents, b: n - tEvents,
    c: cEvents, d: n - cEvents,
    n, truth,
  };
}

function clamp01(x) { return Math.max(0, Math.min(1, x)); }

// Build a corpus: half NULL, half EFFECT. n varies across a range so we can
// study how FI scales with sample size (the honest nuance).
export function makeCorpus({
  seed = 2026,
  nEach = 4000,
  p0 = 0.20,
  effect = 0.10,          // absolute risk increase in treatment arm for EFFECT trials
  nMin = 50,
  nMax = 800,
} = {}) {
  const rng = mulberry32(seed);
  const trials = [];
  for (let i = 0; i < nEach; i++) {
    const n = Math.round(nMin + (nMax - nMin) * rng());
    trials.push(makeTrial(rng, { n, p0, effect, truth: 1 }));
  }
  for (let i = 0; i < nEach; i++) {
    const n = Math.round(nMin + (nMax - nMin) * rng());
    trials.push(makeTrial(rng, { n, p0, effect, truth: 0 }));
  }
  return trials;
}
