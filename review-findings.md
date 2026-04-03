# FragilityIndex Code Review Findings

**Date:** 2026-04-03
**Reviewer:** Code Audit (Claude)
**File:** fragility-index.html (1,344 lines)

## P0 (Critical — must fix before ship)

### P0-1: Missing Content-Security-Policy meta tag
**Location:** `<head>` section (lines 2-8)
**Issue:** No CSP header present. Other tools in the portfolio include inline CSP.
While `escapeHtml()` is used consistently, defense-in-depth requires CSP.
**Fix:** Add CSP meta tag.

### P0-2: Missing skip-to-content link for accessibility
**Location:** After `<body>` tag (line 359)
**Issue:** No skip navigation link. WCAG 2.1 AA requires bypass mechanism
(Success Criterion 2.4.1). All other tools in the portfolio have this.
**Fix:** Add skip-to-content anchor.

## P1 (Important — fix before submission)

### P1-1: Fragility Index modifies correct arm per Walsh et al.
**Location:** `computeFI()` (~line 697-803)
**Status:** Algorithm correctly modifies the arm with fewer events (default `armMode='fewer'`),
matching Walsh et al. 2014. Also provides `treatment`/`control` only modes.
Fisher exact test implementation uses log-factorial with caching -- correct.
**Verdict:** No issue with formulas. Algorithm is sound.

### P1-2: Reverse FI tries both directions -- correct
**Location:** `computeFI()` (~line 751-803)
**Status:** When trial is non-significant, tries adding events to both treatment and
control arms, picks the direction requiring fewer changes. This is a sound approach.

### P1-3: Icon array scaling with fi=0 correctly handled
**Location:** `renderIconArray()` (~line 1032-1078)
**Issue:** When `fi === 0`, `dotsFI` is set to 0 at line 1047. However, if scaling is
applied AND `fi > 0`, `dotsFI = Math.max(1, ...)` ensures at least 1 dot is shown,
which could slightly misrepresent FI=1 at scale. Minor visual issue only.

## P2 (Minor — nice to have)

### P2-1: `csvSafe()` properly implemented
**Location:** Line 601-609
**Status:** Correctly guards `=+@\t\r` prefixes. Does not include `-`. Good.

### P2-2: `escapeHtml()` uses DOM-based approach
**Location:** Line 594-598
**Status:** Safe. No issue.

### P2-3: Blob URLs properly revoked
**Location:** `downloadBlob()` (~line 1236-1246)
**Status:** Correctly revokes. No issue.

### P2-4: Theme persistence uses correct unique key
**Location:** Line 1294
**Status:** Uses `fragilityindex-theme` -- unique key. No issue.

### P2-5: Scrollbar CSS syntax error
**Location:** Line 321
**Issue:** `scrollbar-color: var(--color-border-strong) var(--surface-bg);` is at the
root level outside any selector block. This is a CSS syntax error -- it will be ignored
by browsers but is technically invalid.
**Recommendation:** Move inside a selector (e.g., `html { scrollbar-color: ...; }`).

## Summary

| Severity | Count | Fixed |
|----------|-------|-------|
| P0       | 2     | Yes   |
| P1       | 1     | No    |
| P2       | 1     | No    |
| **Total**| **4** |       |
