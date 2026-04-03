"""
Selenium test suite for Fragility Index Calculator (fragility-index.html).
15 tests covering:
  - Page load and title
  - Loading built-in examples (CRASH-2, SPRINT, ISCHEMIA)
  - DAPA-HF FI = 62 (via _computeFI API, Walsh fewer-events method)
  - ISIS-2 FI = 156 (via _computeFI API, Walsh fewer-events method)
  - Computed FI values are positive integers
  - Fragility Quotient is a percentage in [0, 100]
  - Sensitivity analysis across alpha thresholds
  - Theme toggle (dark/light)
  - Reverse FI for non-significant trials
  - UI: compute button triggers results tab
  - p-value trajectory monotonicity
"""

import sys
import io
import os
import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HTML_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'fragility-index.html'
)
FILE_URL = 'file:///' + HTML_FILE.replace('\\', '/')


@pytest.fixture(scope="module")
def driver():
    """Create a headless Chrome driver shared across all tests in this module."""
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1280,900')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    drv = webdriver.Chrome(options=opts)
    drv.set_page_load_timeout(30)
    # Override window.confirm to always return True (avoids blocking dialogs)
    drv.get(FILE_URL)
    drv.execute_script("window.confirm = function() { return true; };")
    time.sleep(0.5)
    yield drv
    drv.quit()


def js(driver, script):
    """Shorthand for execute_script."""
    return driver.execute_script(script)


def fresh_page(driver):
    """Reload the page and override confirm dialogs."""
    driver.get(FILE_URL)
    driver.execute_script("window.confirm = function() { return true; };")
    time.sleep(0.5)


# ─────────────────────────────────────────────────
# Test 1: Page loads with correct title
# ─────────────────────────────────────────────────
def test_01_page_loads(driver):
    fresh_page(driver)
    title = driver.title
    assert 'Fragility' in title, f"Expected 'Fragility' in title, got: {title}"
    # Verify no severe JS errors
    logs = driver.get_log('browser')
    severe = [l for l in logs if l.get('level') == 'SEVERE']
    assert len(severe) == 0, f"Severe JS errors on load: {severe}"


# ─────────────────────────────────────────────────
# Test 2: Load CRASH-2 example fills inputs correctly
# ─────────────────────────────────────────────────
def test_02_load_crash2_example(driver):
    fresh_page(driver)
    js(driver, "FI.loadExample('crash2');")
    time.sleep(0.3)
    a = driver.find_element(By.ID, 'inp-a').get_attribute('value')
    b = driver.find_element(By.ID, 'inp-b').get_attribute('value')
    c = driver.find_element(By.ID, 'inp-c').get_attribute('value')
    d = driver.find_element(By.ID, 'inp-d').get_attribute('value')
    assert a == '489', f"Expected a=489, got {a}"
    assert b == '4484', f"Expected b=4484, got {b}"
    assert c == '574', f"Expected c=574, got {c}"
    assert d == '4378', f"Expected d=4378, got {d}"


# ─────────────────────────────────────────────────
# Test 3: Load SPRINT example fills inputs correctly
# ─────────────────────────────────────────────────
def test_03_load_sprint_example(driver):
    fresh_page(driver)
    js(driver, "FI.loadExample('sprint');")
    time.sleep(0.3)
    a = driver.find_element(By.ID, 'inp-a').get_attribute('value')
    b = driver.find_element(By.ID, 'inp-b').get_attribute('value')
    assert a == '155', f"Expected a=155, got {a}"
    assert b == '4223', f"Expected b=4223, got {b}"


# ─────────────────────────────────────────────────
# Test 4: Load ISCHEMIA example fills inputs correctly
# ─────────────────────────────────────────────────
def test_04_load_ischemia_example(driver):
    fresh_page(driver)
    js(driver, "FI.loadExample('ischemia');")
    time.sleep(0.3)
    a = driver.find_element(By.ID, 'inp-a').get_attribute('value')
    c = driver.find_element(By.ID, 'inp-c').get_attribute('value')
    assert a == '318', f"Expected a=318, got {a}"
    assert c == '352', f"Expected c=352, got {c}"


# ─────────────────────────────────────────────────
# Test 5: DAPA-HF Fragility Index
# DAPA-HF primary endpoint: dapagliflozin vs placebo in HFrEF
#   Treatment: 386 events / 2373 total  => a=386, b=1987
#   Control:   502 events / 2371 total  => c=502, d=1869
# Walsh method (fewer-events arm): FI = 62
# ─────────────────────────────────────────────────
def test_05_dapa_hf_fi(driver):
    r = js(driver, "return FI._computeFI(386, 1987, 502, 1869, 0.05, 'fewer');")
    assert r is not None, "computeFI returned null"
    assert r['significant'] is True, "DAPA-HF should be significant"
    assert r['reverse'] is False, "Should be forward FI"
    fi = r['fi']
    assert isinstance(fi, int), f"FI should be integer, got {type(fi)}"
    assert fi == 62, f"Expected DAPA-HF FI=62, got {fi}"


# ─────────────────────────────────────────────────
# Test 6: ISIS-2 Fragility Index
# ISIS-2: streptokinase vs placebo in acute MI
#   Treatment: 791 deaths / 8592 total  => a=791, b=7801
#   Control:  1029 deaths / 8595 total  => c=1029, d=7566
# Walsh method (fewer-events arm): FI = 156
# ─────────────────────────────────────────────────
def test_06_isis2_fi(driver):
    r = js(driver, "return FI._computeFI(791, 7801, 1029, 7566, 0.05, 'fewer');")
    assert r is not None, "computeFI returned null"
    assert r['significant'] is True, "ISIS-2 should be significant"
    fi = r['fi']
    assert isinstance(fi, int), f"FI should be integer, got {type(fi)}"
    assert fi == 156, f"Expected ISIS-2 FI=156, got {fi}"


# ─────────────────────────────────────────────────
# Test 7: Computed FI values are positive integers
# Test across all 3 built-in examples
# ─────────────────────────────────────────────────
def test_07_fi_values_are_positive_integers(driver):
    examples = [
        (489, 4484, 574, 4378, 'CRASH-2'),
        (155, 4223, 210, 4193, 'SPRINT'),
        (386, 1987, 502, 1869, 'DAPA-HF'),
    ]
    for a, b, c, d, name in examples:
        r = js(driver, f"return FI._computeFI({a}, {b}, {c}, {d}, 0.05, 'fewer');")
        fi = r['fi']
        assert fi is not None, f"{name}: FI is null"
        assert isinstance(fi, int), f"{name}: FI should be int, got {type(fi)}"
        assert fi > 0, f"{name}: FI should be positive, got {fi}"


# ─────────────────────────────────────────────────
# Test 8: Fragility Quotient is FI/N expressed as percentage in [0, 100]
# ─────────────────────────────────────────────────
def test_08_fq_is_percentage(driver):
    # CRASH-2
    r = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'fewer');")
    fi = r['fi']
    total_n = r['totalN']
    fq = r['fq']
    assert total_n == 489 + 4484 + 574 + 4378, f"totalN mismatch: {total_n}"
    expected_fq = fi / total_n
    assert abs(fq - expected_fq) < 1e-10, f"FQ={fq} != FI/N={expected_fq}"
    fq_pct = fq * 100
    assert 0 < fq_pct < 100, f"FQ% should be in (0,100), got {fq_pct}"


# ─────────────────────────────────────────────────
# Test 9: Sensitivity analysis - FI at alpha=0.01 <= FI at alpha=0.05
# Stricter alpha means significance is harder to reach,
# so fewer changes needed to cross the (already tight) threshold.
# ─────────────────────────────────────────────────
def test_09_sensitivity_alpha(driver):
    # CRASH-2 data
    r01 = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.01, 'fewer');")
    r025 = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.025, 'fewer');")
    r05 = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'fewer');")
    r10 = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.10, 'fewer');")

    # For a significant trial: stricter alpha => smaller FI (easier to lose significance)
    assert r01['fi'] <= r025['fi'], f"FI@0.01={r01['fi']} should be <= FI@0.025={r025['fi']}"
    assert r025['fi'] <= r05['fi'], f"FI@0.025={r025['fi']} should be <= FI@0.05={r05['fi']}"
    assert r05['fi'] <= r10['fi'], f"FI@0.05={r05['fi']} should be <= FI@0.10={r10['fi']}"


# ─────────────────────────────────────────────────
# Test 10: Sensitivity analysis populates the table in the UI
# ─────────────────────────────────────────────────
def test_10_sensitivity_ui_table(driver):
    fresh_page(driver)
    js(driver, "FI.loadExample('crash2');")
    time.sleep(0.2)
    js(driver, "FI.compute();")
    time.sleep(0.5)

    # Switch to sensitivity tab
    js(driver, "document.getElementById('tab-sensitivity').click();")
    time.sleep(0.3)

    # Sensitivity alpha table should have content
    table_html = js(driver, "return document.getElementById('sensAlphaTable').innerHTML;")
    assert '<table' in table_html, "Alpha sensitivity table not rendered"
    assert '0.01' in table_html, "Alpha=0.01 row missing from sensitivity table"
    assert '0.05' in table_html, "Alpha=0.05 row missing from sensitivity table"


# ─────────────────────────────────────────────────
# Test 11: Theme toggle switches between light and dark
# ─────────────────────────────────────────────────
def test_11_theme_toggle(driver):
    fresh_page(driver)
    theme = js(driver, "return document.documentElement.getAttribute('data-theme');")
    assert theme == 'light', f"Expected initial theme=light, got {theme}"

    # Click toggle via JS (reliable in headless)
    js(driver, "document.getElementById('themeToggle').click();")
    time.sleep(0.3)
    theme = js(driver, "return document.documentElement.getAttribute('data-theme');")
    assert theme == 'dark', f"Expected dark after toggle, got {theme}"

    # Toggle back
    js(driver, "document.getElementById('themeToggle').click();")
    time.sleep(0.3)
    theme = js(driver, "return document.documentElement.getAttribute('data-theme');")
    assert theme == 'light', f"Expected light after second toggle, got {theme}"


# ─────────────────────────────────────────────────
# Test 12: Compute button triggers results tab
# ─────────────────────────────────────────────────
def test_12_compute_switches_to_results(driver):
    fresh_page(driver)
    js(driver, "FI.loadExample('crash2');")
    time.sleep(0.2)
    js(driver, "FI.compute();")
    time.sleep(0.5)

    # Results panel should be visible
    panel = driver.find_element(By.ID, 'panel-results')
    assert panel.get_attribute('aria-hidden') == 'false', "Results panel not visible after compute"

    # Results tab should be selected
    tab = driver.find_element(By.ID, 'tab-results')
    assert tab.get_attribute('aria-selected') == 'true', "Results tab not selected"

    # FI value display should show a number
    fi_text = driver.find_element(By.ID, 'fiValueDisplay').text
    assert fi_text != '--', f"FI display not updated, still shows: {fi_text}"
    fi_val = int(fi_text)
    assert fi_val > 0, f"Expected positive FI on display, got {fi_val}"


# ─────────────────────────────────────────────────
# Test 13: Reverse FI for non-significant trial
# ISCHEMIA primary endpoint was not significant (p > 0.05)
# ─────────────────────────────────────────────────
def test_13_reverse_fi_nonsignificant(driver):
    r = js(driver, "return FI._computeFI(318, 2270, 352, 2239, 0.05, 'fewer');")
    # ISCHEMIA primary was not significant
    # Check if the result has a valid reverse FI
    assert r is not None, "computeFI returned null"
    if not r['significant']:
        assert r['reverse'] is True, "Non-significant trial should compute reverse FI"
        assert r['fi'] is not None and r['fi'] > 0, f"Reverse FI should be positive, got {r['fi']}"
    else:
        # If this particular 2x2 happens to be significant, still verify FI is positive
        assert r['fi'] > 0, f"FI should be positive, got {r['fi']}"


# ─────────────────────────────────────────────────
# Test 14: p-value trajectory is monotonic
# For a significant trial losing significance (forward FI),
# each step should move p closer to alpha.
# ─────────────────────────────────────────────────
def test_14_pvalue_trajectory(driver):
    r = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'fewer');")
    steps = r['steps']
    assert len(steps) > 0, "Should have iteration steps"

    # p-values should be monotonically increasing (approaching alpha from below)
    p_values = [s['p'] for s in steps]
    for i in range(1, len(p_values)):
        assert p_values[i] >= p_values[i-1] - 1e-12, \
            f"p-value trajectory not monotonic at step {i}: {p_values[i-1]} -> {p_values[i]}"

    # Final p should be >= alpha
    assert p_values[-1] >= 0.05 - 1e-10, \
        f"Final p={p_values[-1]} should be >= alpha=0.05"


# ─────────────────────────────────────────────────
# Test 15: FQ displayed as percentage after compute
# ─────────────────────────────────────────────────
def test_15_fq_displayed_as_percentage(driver):
    fresh_page(driver)
    js(driver, "FI.loadExample('crash2');")
    time.sleep(0.2)
    js(driver, "FI.compute();")
    time.sleep(0.5)

    # The result grid should contain a FQ with a % sign
    grid_html = js(driver, "return document.getElementById('resultGrid').innerHTML;")
    assert '%' in grid_html, "FQ percentage symbol missing from results grid"
    assert 'Fragility Quotient' in grid_html, "FQ label missing from results grid"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
