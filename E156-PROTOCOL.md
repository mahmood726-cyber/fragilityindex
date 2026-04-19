# E156 Protocol — `FragilityIndex`

This repository is the source code and dashboard backing an E156 micro-paper on the [E156 Student Board](https://mahmood726-cyber.github.io/e156/students.html).

---

## `[61]` Fragility Index Calculator: Browser-Based Statistical Fragility for RCTs

**Type:** methods  |  ESTIMAND: Fragility Index (FI)  
**Data:** Six built-in landmark RCT datasets

### 156-word body

Can a browser-based tool compute the Fragility Index and Fragility Quotient for randomized trials with binary outcomes without any software installation? We implemented the Walsh et al. (2014) algorithm, which iteratively modifies the contingency table by adding one event to the group with fewer events until the Fisher exact p-value crosses 0.05, applied to six landmark trial datasets. The calculator uses exact Fisher tests with automatic direction detection, supporting significant and non-significant trials through standard and reverse fragility indices. For DAPA-HF, the Fragility Index is 29 with a 95% CI p-value trajectory from 0.04 to 0.07 and Fragility Quotient of 0.61 percent in under 50 milliseconds. Sensitivity analysis across multiple significance thresholds confirms monotonic index behavior across all six embedded trial datasets. Browser-based fragility computation achieves identical outputs to dedicated R packages while eliminating all installation barriers. The limitation is that fragility indices apply only to binary outcomes analyzed with Fisher exact tests, excluding continuous endpoints.

### Submission metadata

```
Corresponding author: Mahmood Ahmad <mahmood.ahmad2@nhs.net>
ORCID: 0000-0001-9107-3704
Affiliation: Tahir Heart Institute, Rabwah, Pakistan

Links:
  Code:      https://github.com/mahmood726-cyber/FragilityIndex
  Protocol:  https://github.com/mahmood726-cyber/FragilityIndex/blob/main/E156-PROTOCOL.md
  Dashboard: https://mahmood726-cyber.github.io/fragilityindex/

References (topic pack: fragility index):
  1. Walsh M, Srinathan SK, McAuley DF, et al. 2014. The statistical significance of randomized controlled trial results is frequently fragile: a case for a Fragility Index. J Clin Epidemiol. 67(6):622-628. doi:10.1016/j.jclinepi.2013.10.019
  2. Atal I, Porcher R, Boutron I, Ravaud P. 2019. The statistical significance of meta-analyses is frequently fragile: definition of a fragility index for meta-analyses. J Clin Epidemiol. 111:32-40. doi:10.1016/j.jclinepi.2019.03.012

Data availability: No patient-level data used. Analysis derived exclusively
  from publicly available aggregate records. All source identifiers are in
  the protocol document linked above.

Ethics: Not required. Study uses only publicly available aggregate data; no
  human participants; no patient-identifiable information; no individual-
  participant data. No institutional review board approval sought or required
  under standard research-ethics guidelines for secondary methodological
  research on published literature.

Funding: None.

Competing interests: MA serves on the editorial board of Synthēsis (the
  target journal); MA had no role in editorial decisions on this
  manuscript, which was handled by an independent editor of the journal.

Author contributions (CRediT):
  [STUDENT REWRITER, first author] — Writing – original draft, Writing –
    review & editing, Validation.
  [SUPERVISING FACULTY, last/senior author] — Supervision, Validation,
    Writing – review & editing.
  Mahmood Ahmad (middle author, NOT first or last) — Conceptualization,
    Methodology, Software, Data curation, Formal analysis, Resources.

AI disclosure: Computational tooling (including AI-assisted coding via
  Claude Code [Anthropic]) was used to develop analysis scripts and assist
  with data extraction. The final manuscript was human-written, reviewed,
  and approved by the author; the submitted text is not AI-generated. All
  quantitative claims were verified against source data; cross-validation
  was performed where applicable. The author retains full responsibility for
  the final content.

Preprint: Not preprinted.

Reporting checklist: PRISMA 2020 (methods-paper variant — reports on review corpus).

Target journal: ◆ Synthēsis (https://www.synthesis-medicine.org/index.php/journal)
  Section: Methods Note — submit the 156-word E156 body verbatim as the main text.
  The journal caps main text at ≤400 words; E156's 156-word, 7-sentence
  contract sits well inside that ceiling. Do NOT pad to 400 — the
  micro-paper length is the point of the format.

Manuscript license: CC-BY-4.0.
Code license: MIT.

SUBMITTED: [ ]
```


---

_Auto-generated from the workbook by `C:/E156/scripts/create_missing_protocols.py`. If something is wrong, edit `rewrite-workbook.txt` and re-run the script — it will overwrite this file via the GitHub API._