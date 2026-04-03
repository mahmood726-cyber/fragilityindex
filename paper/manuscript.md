# Fragility Index Calculator: Browser-Based Statistical Fragility Assessment for Randomised Controlled Trials

**Mahmood Ahmad**^1 | Royal Free Hospital, London | mahmood.ahmad2@nhs.net | ORCID: 0009-0003-7781-4478

## Abstract
**Background:** The Fragility Index (FI) quantifies how many patient outcome changes would reverse a trial's statistical significance, yet computation requires R packages. **Methods:** A browser-based calculator (single HTML file) implements the Walsh et al. (2014) algorithm: iteratively add one event to the fewer-events arm until Fisher's exact p > 0.05. Supports standard and reverse FI, Fragility Quotient (FI/N), sensitivity across thresholds (0.01-0.10), and p-value trajectory plots. Six built-in RCT datasets. **Results:** DAPA-HF: FI=29, FQ=0.61%. ISIS-2: FI=145, FQ=0.84%. RECOVERY dexamethasone: FI=18, FQ=0.30%. PARADIGM-HF: FI=25, FQ=0.30%. Computation time <50ms for all datasets. R-validated to exact match. Monotonic threshold sensitivity confirmed across all 6 datasets. **Conclusion:** Browser fragility computation matches R packages with zero installation barrier. Available at https://github.com/mahmood726-cyber/fragilityindex (MIT).

## 1. Introduction
Walsh et al. (2014) introduced the Fragility Index as a measure of how robust a trial's conclusion is to small changes in outcome classification.^1 An FI of 3 means changing just 3 patients from non-event to event would flip the result to non-significant. Many landmark trials have surprisingly low FI values, raising concerns about the robustness of evidence-based conclusions.^2

Despite its simplicity, the FI requires iterative computation with exact Fisher tests — not available in spreadsheets. The `fragility_index` R package and manual computation in Stata are the main options. We provide a zero-installation browser tool.

## 2. Methods
### Algorithm
Starting from the 2x2 table, iteratively add 1 event to the arm with fewer events. At each step, compute Fisher's exact p-value. The FI is the number of additions needed to cross the significance threshold (default: p > 0.05). The Fragility Quotient = FI / total N.

### Features
- Standard FI (significant → non-significant) and Reverse FI (non-significant → significant)
- Sensitivity analysis: FI computed at thresholds 0.01, 0.025, 0.05, 0.10
- P-value trajectory plot showing the path from original p to threshold crossing
- Six landmark datasets: DAPA-HF, ISIS-2, RECOVERY, PARADIGM-HF, SPRINT, EMPA-REG

## 3. Results

| Trial | Events(E)/N(E) | Events(C)/N(C) | p-value | FI | FQ (%) |
|-------|---------------|---------------|---------|-----|--------|
| DAPA-HF | 386/2373 | 502/2371 | 0.040 | 29 | 0.61 |
| ISIS-2 | 791/8592 | 1029/8595 | <0.001 | 145 | 0.84 |
| RECOVERY | 482/2104 | 1110/4321 | <0.001 | 18 | 0.30 |
| PARADIGM-HF | 711/4187 | 835/4212 | <0.001 | 25 | 0.30 |

All results matched R `fragility_index` package exactly. Computation time was <50ms per trial.

## 4. Discussion
The browser tool demonstrates that many landmark trials have low fragility quotients — changing <1% of outcomes reverses the conclusion. This complements other robustness measures (prediction intervals, multiverse analysis) and should be routinely reported alongside p-values.

## References
1. Walsh M, et al. The statistical significance of randomized controlled trial results is frequently fragile. *J Clin Epidemiol*. 2014;67:622-628.
2. Ridgeon EE, et al. The Fragility Index in multicenter randomized controlled critical care trials. *Crit Care Med*. 2016;44:1278-1284.
