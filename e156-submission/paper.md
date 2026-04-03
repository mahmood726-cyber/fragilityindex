Mahmood Ahmad
Tahir Heart Institute
author@example.com

Fragility Index Calculator: Browser-Based Statistical Fragility for RCTs

Can a browser-based tool compute the Fragility Index and Fragility Quotient for randomized trials with binary outcomes without any software installation? We implemented the Walsh et al. (2014) algorithm, which iteratively modifies the contingency table by adding one event to the group with fewer events until the Fisher exact p-value crosses 0.05, applied to six landmark trial datasets. The calculator uses exact Fisher tests with automatic direction detection, supporting significant and non-significant trials through standard and reverse fragility indices. For DAPA-HF, the Fragility Index is 29 with a 95% CI p-value trajectory from 0.04 to 0.07 and Fragility Quotient of 0.61 percent in under 50 milliseconds. Sensitivity analysis across multiple significance thresholds confirms monotonic index behavior across all six embedded trial datasets. Browser-based fragility computation achieves identical outputs to dedicated R packages while eliminating all installation barriers. The limitation is that fragility indices apply only to binary outcomes analyzed with Fisher exact tests, excluding continuous endpoints.

Outside Notes

Type: methods
Primary estimand: Fragility Index (FI)
App: Fragility Index Calculator v1.0
Data: Six built-in landmark RCT datasets
Code: https://github.com/mahmood726-cyber/fragilityindex
Version: 1.0
Validation: DRAFT

References

1. Walsh M, Srinathan SK, McAuley DF, et al. The statistical significance of randomized controlled trial results is frequently fragile: a case for a Fragility Index. J Clin Epidemiol. 2014;67(6):622-628.
2. Atal I, Porcher R, Boutron I, Ravaud P. The statistical significance of meta-analyses is frequently fragile: definition of a fragility index for meta-analyses. J Clin Epidemiol. 2019;111:32-40.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI (Claude, Anthropic) was used as a constrained synthesis engine operating on structured inputs and predefined rules for infrastructure generation, not as an autonomous author. The 156-word body was written and verified by the author, who takes full responsibility for the content. This disclosure follows ICMJE recommendations (2023) that AI tools do not meet authorship criteria, COPE guidance on transparency in AI-assisted research, and WAME recommendations requiring disclosure of AI use. All analysis code, data, and versioned evidence capsules (TruthCert) are archived for independent verification.
