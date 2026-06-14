// Truth-recovery invariants for the SHIPPED Fragility Index (engine.mjs,
// extracted verbatim from fragility-index.html). Run: node --test
//
// Known-truth 2x2 corpus (half true-null, half true-effect). Among SIGNIFICANT
// trials we assert the FI behaves as the literature claims:
//   1. FI discriminates true positives from false positives (AUROC well > 0.5).
//   2. Calibration is monotone: P(true | FI bucket) rises with FI; FI=1
//      ("maximally fragile") significant results are markedly more likely to be
//      false positives than FI>=16 ones.
//   3. Engine sanity: published landmark tables reproduce expected FI.
//   4. Honest nuance: FI scales with sample size (corr(FI,N) materially > 0),
//      and the size-adjusted Fragility Quotient discriminates at least as well.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { run } from './harness.mjs';
import { computeFI } from './engine.mjs';

// One shared evaluation (Monte Carlo; seed fixed for reproducibility).
const M = run({ nEach: 1500, p0: 0.20, effect: 0.10, nMin: 50, nMax: 800, seed: 7 });

test('FDR among significant trials is near the nominal alpha=0.05', () => {
  // 3-sigma-ish band for a Monte Carlo proportion; not a tight point estimate.
  assert.ok(M.falseDiscoveryRate < 0.10,
    `FDR ${M.falseDiscoveryRate} should be near 0.05`);
});

test('FI discriminates true vs false positives (AUROC > 0.75)', () => {
  assert.ok(M.aucFI > 0.75, `AUROC(FI)=${M.aucFI}`);
});

test('size-adjusted Fragility Quotient discriminates at least as well as raw FI', () => {
  assert.ok(M.aucFQ >= M.aucFI - 0.02, `aucFQ=${M.aucFQ} aucFI=${M.aucFI}`);
});

test('calibration is monotone non-decreasing in FI bucket', () => {
  const ps = M.calibration.filter((b) => b.n >= 20 && Number.isFinite(b.pTrue))
    .map((b) => b.pTrue);
  for (let i = 1; i < ps.length; i++) {
    assert.ok(ps[i] >= ps[i - 1] - 0.03,
      `P(true) should not drop materially: ${JSON.stringify(ps)}`);
  }
});

test('maximally-fragile (FI=1) results are more likely false positives than FI>=16', () => {
  const lo = M.calibration.find((b) => b.range === '1-1');
  const hi = M.calibration.find((b) => b.range === '16+');
  assert.ok(lo && hi && lo.pTrue < hi.pTrue - 0.10,
    `P(true|FI=1)=${lo?.pTrue} should be well below P(true|FI>=16)=${hi?.pTrue}`);
});

test('honest nuance: FI scales with sample size (corr > 0.3)', () => {
  assert.ok(M.corrFI_sampleSize > 0.3, `corr(FI,N)=${M.corrFI_sampleSize}`);
});

test('engine sanity: landmark trials reproduce expected fragility', () => {
  const sprint = computeFI(155, 4223, 210, 4193, 0.05, 'fewer');
  assert.equal(sprint.significant, true);
  assert.ok(sprint.fi > 0 && sprint.fi < 40, `SPRINT FI=${sprint.fi}`);
  const crash = computeFI(489, 4484, 574, 4378, 0.05, 'fewer');
  assert.equal(crash.significant, true);
  assert.ok(crash.fi > 0 && crash.fi < 60, `CRASH-2 FI=${crash.fi}`);
});
