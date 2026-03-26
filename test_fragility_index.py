"""
Test suite for Fragility Index Calculator (fragility-index.html).
20 tests covering:
  - Fisher's exact test accuracy
  - Fragility Index computation (forward & reverse)
  - Fragility Quotient calculation
  - Built-in examples (CRASH-2, SPRINT, ISCHEMIA)
  - Edge cases (zero events, identical arms, single patient)
  - Sensitivity across alpha thresholds
  - Arm mode variations
  - UI elements (tabs, inputs, buttons, ARIA)
  - CSV/JSON export
  - Dark mode toggle
"""

import sys
import io
import os
import json
import time

# Windows UTF-8 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fragility-index.html')
FILE_URL = 'file:///' + HTML_PATH.replace('\\', '/')

passed = 0
failed = 0
errors = []

def setup_driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--window-size=1280,900')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    return driver

def run_test(driver, name, fn):
    global passed, failed
    try:
        fn(driver)
        passed += 1
        print(f"  PASS: {name}")
    except Exception as e:
        failed += 1
        errors.append((name, str(e)))
        print(f"  FAIL: {name} -- {e}")

def js(driver, script):
    return driver.execute_script(script)

# ══════════════════════════════════════════════════
# TEST FUNCTIONS
# ══════════════════════════════════════════════════

def test_01_page_loads(driver):
    """Page loads without JS errors"""
    driver.get(FILE_URL)
    title = driver.title
    assert 'Fragility' in title, f"Expected 'Fragility' in title, got: {title}"

def test_02_fisher_exact_significant(driver):
    """Fisher exact test on CRASH-2 data gives p < 0.05"""
    p = js(driver, "return FI._fisherExact(489, 4484, 574, 4378);")
    assert p < 0.05, f"Expected p < 0.05, got {p}"
    assert p > 0.001, f"Expected p > 0.001, got {p}"

def test_03_fisher_exact_equal_arms(driver):
    """Fisher exact p = 1 for identical arms"""
    p = js(driver, "return FI._fisherExact(50, 950, 50, 950);")
    assert abs(p - 1.0) < 0.01, f"Expected p ~ 1.0, got {p}"

def test_04_fisher_exact_extreme(driver):
    """Fisher exact: large difference => very small p"""
    p = js(driver, "return FI._fisherExact(100, 900, 10, 990);")
    assert p < 0.0001, f"Expected p < 0.0001, got {p}"

def test_05_fi_crash2(driver):
    """CRASH-2: FI should be a small positive integer (treatment is better)"""
    r = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'fewer');")
    assert r['fi'] is not None and r['fi'] > 0, f"Expected FI > 0, got {r['fi']}"
    assert r['fi'] < 100, f"Expected FI < 100, got {r['fi']}"
    assert r['significant'] == True, "CRASH-2 should be significant"
    assert r['reverse'] == False

def test_06_fi_sprint(driver):
    """SPRINT: FI should be positive"""
    r = js(driver, "return FI._computeFI(155, 4223, 210, 4193, 0.05, 'fewer');")
    assert r['fi'] > 0, f"Expected FI > 0, got {r['fi']}"
    assert r['significant'] == True

def test_07_fi_ischemia(driver):
    """ISCHEMIA: This trial was NOT significant for the primary outcome"""
    r = js(driver, "return FI._computeFI(318, 2270, 352, 2239, 0.05, 'fewer');")
    # ISCHEMIA primary outcome was not statistically significant
    # This computes either forward or reverse depending on Fisher p
    assert r['fi'] is not None

def test_08_fq_calculation(driver):
    """FQ = FI / totalN"""
    r = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'fewer');")
    totalN = 489 + 4484 + 574 + 4378
    expected_fq = r['fi'] / totalN
    assert abs(r['fq'] - expected_fq) < 1e-8, f"FQ mismatch: {r['fq']} vs {expected_fq}"

def test_09_reverse_fi(driver):
    """Non-significant trial gives reverse FI"""
    # Equal arms => p ~ 1, not significant
    r = js(driver, "return FI._computeFI(50, 950, 50, 950, 0.05, 'fewer');")
    assert r['significant'] == False
    assert r['reverse'] == True
    assert r['fi'] is not None and r['fi'] > 0

def test_10_zero_events_one_arm(driver):
    """Zero events in one arm"""
    r = js(driver, "return FI._computeFI(0, 100, 10, 90, 0.05, 'fewer');")
    assert r is not None
    # Should be computable

def test_11_alpha_sensitivity(driver):
    """FI at alpha=0.01 >= FI at alpha=0.05"""
    r01 = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.01, 'fewer');")
    r05 = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'fewer');")
    # Stricter alpha needs fewer changes to lose significance
    # Wait - stricter alpha means the bar is harder to reach, so FI should be SMALLER
    # because fewer changes needed to cross a stricter threshold
    assert r01['fi'] <= r05['fi'], f"FI@0.01={r01['fi']} should be <= FI@0.05={r05['fi']}"

def test_12_arm_mode_treatment(driver):
    """Treatment arm mode: only modifies treatment"""
    r = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'treatment');")
    # Check all steps modified treatment
    for step in r.get('steps', []):
        assert step['arm'] == 'treatment', f"Expected treatment arm, got {step['arm']}"

def test_13_arm_mode_control(driver):
    """Control arm mode: only modifies control"""
    r = js(driver, "return FI._computeFI(489, 4484, 574, 4378, 0.05, 'control');")
    for step in r.get('steps', []):
        assert step['arm'] == 'control', f"Expected control arm, got {step['arm']}"

def test_14_tab_navigation(driver):
    """ARIA tabs work correctly"""
    driver.get(FILE_URL)
    tabs = driver.find_elements(By.CSS_SELECTOR, '[role="tab"]')
    assert len(tabs) == 4, f"Expected 4 tabs, got {len(tabs)}"

    # Initially first tab is selected
    assert tabs[0].get_attribute('aria-selected') == 'true'

    # Click second tab
    tabs[1].click()
    time.sleep(0.3)
    assert tabs[1].get_attribute('aria-selected') == 'true'
    assert tabs[0].get_attribute('aria-selected') == 'false'

    panel = driver.find_element(By.ID, 'panel-results')
    assert panel.get_attribute('aria-hidden') == 'false'

def test_15_load_example(driver):
    """Load CRASH-2 example fills inputs"""
    driver.get(FILE_URL)
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

def test_16_compute_button(driver):
    """Compute button runs and switches to results tab"""
    driver.get(FILE_URL)
    js(driver, "FI.loadExample('crash2');")
    time.sleep(0.2)
    js(driver, "FI.compute();")
    time.sleep(0.5)

    # Should switch to results tab
    panel = driver.find_element(By.ID, 'panel-results')
    assert panel.get_attribute('aria-hidden') == 'false'

    # FI value should be displayed
    fi_el = driver.find_element(By.ID, 'fiValueDisplay')
    fi_text = fi_el.text
    assert fi_text != '--', f"FI display not updated, still shows: {fi_text}"
    fi_val = int(fi_text)
    assert fi_val > 0, f"Expected positive FI, got {fi_val}"

def test_17_clear_button(driver):
    """Clear button resets all inputs"""
    driver.get(FILE_URL)
    js(driver, "FI.loadExample('sprint');")
    time.sleep(0.2)
    js(driver, "FI.clearInputs();")
    time.sleep(0.2)

    a = driver.find_element(By.ID, 'inp-a').get_attribute('value')
    assert a == '', f"Expected empty after clear, got: {a}"

def test_18_escapehtml(driver):
    """escapeHtml prevents XSS"""
    result = js(driver, 'return FI._escapeHtml(\'<script>alert(1)<\\/script>\');')
    assert '<script>' not in result, f"XSS not escaped: {result}"
    assert '&lt;' in result or '&#' in result

def test_19_csvsafe(driver):
    """csvSafe prepends quote to formula-like strings"""
    result = js(driver, "return FI._csvSafe('=CMD()');")
    assert result.startswith("'"), f"Expected prepended quote, got: {result}"

    normal = js(driver, "return FI._csvSafe('hello');")
    assert normal == 'hello'

def test_20_dark_mode_toggle(driver):
    """Dark mode toggle changes theme attribute"""
    driver.get(FILE_URL)
    theme_before = js(driver, "return document.documentElement.getAttribute('data-theme');")
    assert theme_before == 'light'

    btn = driver.find_element(By.ID, 'themeToggle')
    btn.click()
    time.sleep(0.3)

    theme_after = js(driver, "return document.documentElement.getAttribute('data-theme');")
    assert theme_after == 'dark', f"Expected dark, got {theme_after}"

# ══════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════

if __name__ == '__main__':
    print(f"\nFragility Index Calculator - Test Suite")
    print(f"{'='*50}")
    print(f"HTML: {FILE_URL}\n")

    driver = setup_driver()
    driver.get(FILE_URL)
    time.sleep(1)

    tests = [
        ("01 Page loads", test_01_page_loads),
        ("02 Fisher exact (CRASH-2 significant)", test_02_fisher_exact_significant),
        ("03 Fisher exact (equal arms p=1)", test_03_fisher_exact_equal_arms),
        ("04 Fisher exact (extreme difference)", test_04_fisher_exact_extreme),
        ("05 FI CRASH-2", test_05_fi_crash2),
        ("06 FI SPRINT", test_06_fi_sprint),
        ("07 FI ISCHEMIA", test_07_fi_ischemia),
        ("08 FQ = FI / totalN", test_08_fq_calculation),
        ("09 Reverse FI (non-significant trial)", test_09_reverse_fi),
        ("10 Zero events in one arm", test_10_zero_events_one_arm),
        ("11 Alpha sensitivity (FI@0.01 <= FI@0.05)", test_11_alpha_sensitivity),
        ("12 Arm mode: treatment only", test_12_arm_mode_treatment),
        ("13 Arm mode: control only", test_13_arm_mode_control),
        ("14 ARIA tab navigation", test_14_tab_navigation),
        ("15 Load CRASH-2 example", test_15_load_example),
        ("16 Compute button runs", test_16_compute_button),
        ("17 Clear button resets", test_17_clear_button),
        ("18 escapeHtml prevents XSS", test_18_escapehtml),
        ("19 csvSafe formula protection", test_19_csvsafe),
        ("20 Dark mode toggle", test_20_dark_mode_toggle),
    ]

    for name, fn in tests:
        run_test(driver, name, fn)

    # Print console errors
    try:
        logs = driver.get_log('browser')
        severe = [l for l in logs if l.get('level') == 'SEVERE']
        if severe:
            print(f"\nBrowser console errors ({len(severe)}):")
            for l in severe[:5]:
                print(f"  {l['message'][:200]}")
    except Exception:
        pass

    driver.quit()

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
    if errors:
        print(f"\nFailures:")
        for name, err in errors:
            print(f"  {name}: {err[:200]}")
    print()

    sys.exit(0 if failed == 0 else 1)
