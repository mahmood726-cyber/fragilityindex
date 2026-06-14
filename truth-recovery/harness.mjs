// Truth-recovery harness for the SHIPPED Fragility Index (engine.mjs, extracted
// verbatim from fragility-index.html). Question (single-trial 2x2 FI):
//
//   Among SIGNIFICANT trials, does a higher Fragility Index mean the result is
//   more likely a TRUE positive (real effect) vs a FALSE positive (chance)?
//
// We feed a seeded known-truth corpus (dgp.mjs: half true-null, half true-effect),
// run the repo's computeFI, keep the SIGNIFICANT trials (p<0.05), and measure:
//   * AUROC of FI for separating true vs false positives.
//   * P(true | FI bucket) calibration.
//   * Honest nuance: FI correlates with sample size, so an ABSOLUTE FI threshold
//     conflates "big trial" with "true effect". We also report AUROC of the
//     Fragility QUOTIENT (FI / N) as a size-adjusted comparator.

import { computeFI } from './engine.mjs';
import { makeCorpus } from './dgp.mjs';

export function auroc(scores, labels) {
  // Mann-Whitney AUROC with tie handling. scores/labels are arrays.
  const idx = scores.map((s, i) => [s, labels[i]]).sort((x, y) => x[0] - y[0]);
  const ranks = new Array(idx.length);
  let i = 0;
  while (i < idx.length) {
    let j = i;
    while (j + 1 < idx.length && idx[j + 1][0] === idx[i][0]) j++;
    const avg = (i + 1 + j + 1) / 2; // average rank (1-based)
    for (let k = i; k <= j; k++) ranks[k] = avg;
    i = j + 1;
  }
  let sumPos = 0, nPos = 0, nNeg = 0;
  for (let k = 0; k < idx.length; k++) {
    if (idx[k][1] === 1) { sumPos += ranks[k]; nPos++; } else nNeg++;
  }
  if (nPos === 0 || nNeg === 0) return NaN;
  return (sumPos - (nPos * (nPos + 1)) / 2) / (nPos * nNeg);
}

function pearson(x, y) {
  const n = x.length;
  const mx = x.reduce((a, b) => a + b, 0) / n;
  const my = y.reduce((a, b) => a + b, 0) / n;
  let sxy = 0, sxx = 0, syy = 0;
  for (let i = 0; i < n; i++) {
    sxy += (x[i] - mx) * (y[i] - my);
    sxx += (x[i] - mx) ** 2;
    syy += (y[i] - my) ** 2;
  }
  return sxy / Math.sqrt(sxx * syy);
}

export function run(opts = {}) {
  const corpus = makeCorpus(opts);
  const sig = []; // significant trials only
  for (const t of corpus) {
    const r = computeFI(t.a, t.b, t.c, t.d, 0.05, 'fewer');
    if (r.significant) {
      sig.push({ truth: t.truth, fi: r.fi, fq: r.fq, n: t.totalN ?? r.totalN });
    }
  }

  const fi = sig.map((s) => s.fi);
  const fq = sig.map((s) => s.fq);
  const N = sig.map((s) => s.n);
  const truth = sig.map((s) => s.truth);

  const nTrue = truth.filter((t) => t === 1).length;
  const nFalse = truth.length - nTrue;

  // Discrimination of FI (and FQ) for true vs false positives.
  const aucFI = auroc(fi, truth);
  const aucFQ = auroc(fq, truth);

  // Honest nuance: how strongly does FI track N (vs effect)?
  const corrFI_N = pearson(fi, N);

  // Calibration: P(true | FI bucket).
  const buckets = [
    [1, 1], [2, 3], [4, 7], [8, 15], [16, 1e9],
  ];
  const calib = buckets.map(([lo, hi]) => {
    const inb = sig.filter((s) => s.fi >= lo && s.fi <= hi);
    const pt = inb.length ? inb.filter((s) => s.truth === 1).length / inb.length : NaN;
    return { range: hi >= 1e9 ? `${lo}+` : `${lo}-${hi}`, n: inb.length, pTrue: pt };
  });

  // Mean FI / FQ by truth class (among significant).
  const mean = (arr, mask) => {
    const v = arr.filter((_, i) => truth[i] === mask);
    return v.length ? v.reduce((a, b) => a + b, 0) / v.length : NaN;
  };

  return {
    nSignificant: sig.length,
    nTruePos: nTrue,
    nFalsePos: nFalse,
    falseDiscoveryRate: nFalse / sig.length,
    aucFI, aucFQ,
    corrFI_sampleSize: corrFI_N,
    meanFI_true: mean(fi, 1),
    meanFI_false: mean(fi, 0),
    meanFQ_true: mean(fq, 1),
    meanFQ_false: mean(fq, 0),
    calibration: calib,
  };
}

// CLI
const _entry = process.argv[1] ? process.argv[1].replace(/\\/g, '/') : '';
if (_entry && import.meta.url.endsWith(_entry.split('/').pop())) {
  const m = run({ nEach: 4000, p0: 0.20, effect: 0.10, nMin: 50, nMax: 800, seed: 2026 });
  const f = (x) => (Number.isFinite(x) ? x.toFixed(3) : 'NaN');
  console.log('='.repeat(64));
  console.log('FRAGILITY INDEX -- TRUTH-RECOVERY HARNESS (single-trial 2x2)');
  console.log('='.repeat(64));
  console.log(`Significant trials (p<0.05)      : ${m.nSignificant}`);
  console.log(`  true positives                 : ${m.nTruePos}`);
  console.log(`  false positives (true null)    : ${m.nFalsePos}`);
  console.log(`  false-discovery rate           : ${f(m.falseDiscoveryRate)}`);
  console.log('-'.repeat(64));
  console.log('Does FI track TRUTH among significant trials?');
  console.log(`  AUROC  Fragility Index (FI)     : ${f(m.aucFI)}`);
  console.log(`  AUROC  Fragility Quotient (FI/N): ${f(m.aucFQ)}`);
  console.log('-'.repeat(64));
  console.log('Honest nuance: FI scales with sample size');
  console.log(`  corr(FI, N)                     : ${f(m.corrFI_sampleSize)}`);
  console.log(`  mean FI  true / false           : ${f(m.meanFI_true)} / ${f(m.meanFI_false)}`);
  console.log(`  mean FQ  true / false           : ${f(m.meanFQ_true)} / ${f(m.meanFQ_false)}`);
  console.log('-'.repeat(64));
  console.log('Calibration  P(true | FI bucket)');
  for (const b of m.calibration) {
    console.log(`  FI ${b.range.padEnd(6)} n=${String(b.n).padStart(5)}  P(true)=${f(b.pTrue)}`);
  }
  console.log('='.repeat(64));
}
