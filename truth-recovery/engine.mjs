// Pure Fragility-Index engine EXTRACTED VERBATIM from fragility-index.html
// (functions logFact, hypergeomPMF, fisherExact, computeFI). Only ES-module
// `export` keywords were added; the algorithm bodies are unchanged so the
// truth-recovery harness measures the SHIPPED estimator.

// Log-factorial with caching
const _logfCache = [0, 0];
export function logFact(n) {
  if (n < 0) return 0;
  if (n < _logfCache.length) return _logfCache[n];
  let val = _logfCache[_logfCache.length - 1];
  for (let i = _logfCache.length; i <= n; i++) {
    val += Math.log(i);
    _logfCache.push(val);
  }
  return val;
}

// Hypergeometric probability: P(X=k | N, K, n)
export function hypergeomPMF(k, N, K, n) {
  const logP = logFact(K) - logFact(k) - logFact(K - k)
             + logFact(N - K) - logFact(n - k) - logFact(N - K - n + k)
             - logFact(N) + logFact(n) + logFact(N - n);
  return Math.exp(logP);
}

// Fisher's exact test, two-sided p-value. 2x2 table: [[a, b], [c, d]]
export function fisherExact(a, b, c, d) {
  const n1 = a + b;
  const n2 = c + d;
  const N = n1 + n2;
  const K = a + c;
  const n = n1;

  const pObs = hypergeomPMF(a, N, K, n);

  const kMin = Math.max(0, K - n2);
  const kMax = Math.min(K, n);
  let pVal = 0;
  for (let k = kMin; k <= kMax; k++) {
    const pk = hypergeomPMF(k, N, K, n);
    if (pk <= pObs + 1e-12) {
      pVal += pk;
    }
  }
  return Math.min(pVal, 1.0);
}

// Core Fragility Index (forward when significant, reverse when not).
export function computeFI(a, b, c, d, alpha, armMode) {
  alpha = alpha || 0.05;
  armMode = armMode || 'fewer';

  const totalN = a + b + c + d;
  const pOriginal = fisherExact(a, b, c, d);
  const isSignificant = pOriginal < alpha;

  let aa = a, bb = b, cc = c, dd = d;
  let fi = 0;
  const steps = [];

  if (isSignificant) {
    while (fisherExact(aa, bb, cc, dd) < alpha) {
      let modArm;
      if (armMode === 'treatment') {
        modArm = 'treatment';
      } else if (armMode === 'control') {
        modArm = 'control';
      } else {
        modArm = (aa <= cc) ? 'treatment' : 'control';
      }

      if (modArm === 'treatment') {
        aa++; bb--;
        if (bb < 0) break;
      } else {
        cc++; dd--;
        if (dd < 0) break;
      }
      fi++;
      const pStep = fisherExact(aa, bb, cc, dd);
      steps.push({ step: fi, arm: modArm, a: aa, b: bb, c: cc, d: dd, p: pStep });
    }

    const pFinal = fisherExact(aa, bb, cc, dd);
    const fq = totalN > 0 ? fi / totalN : 0;

    return {
      fi, fq, pOriginal, pFinal,
      significant: true, reverse: false, steps, totalN, alpha, armMode,
      input: { a, b, c, d }
    };
  } else {
    let bestFI = Infinity;
    let bestSteps = [];
    let bestPFinal = pOriginal;
    let bestDirection = 'treatment';

    for (let dir of ['treatment', 'control']) {
      let ta = a, tb = b, tc = c, td = d;
      let rfi = 0;
      const rSteps = [];

      while (fisherExact(ta, tb, tc, td) >= alpha) {
        if (dir === 'treatment') {
          ta++; tb--;
          if (tb < 0) break;
        } else {
          tc++; td--;
          if (td < 0) break;
        }
        rfi++;
        const pS = fisherExact(ta, tb, tc, td);
        rSteps.push({ step: rfi, arm: dir, a: ta, b: tb, c: tc, d: td, p: pS });
        if (pS < alpha) break;
      }

      const rpFinal = fisherExact(ta, tb, tc, td);
      if (rpFinal < alpha && rfi < bestFI) {
        bestFI = rfi;
        bestSteps = rSteps;
        bestPFinal = rpFinal;
        bestDirection = dir;
      }
    }

    if (bestFI === Infinity) bestFI = null;

    return {
      fi: bestFI,
      fq: (bestFI !== null && totalN > 0) ? bestFI / totalN : null,
      pOriginal, pFinal: bestPFinal,
      significant: false, reverse: true, steps: bestSteps, totalN, alpha, armMode,
      reverseDirection: bestDirection,
      input: { a, b, c, d }
    };
  }
}
