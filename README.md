# Planit UI Automation Assessment

![UI](https://github.com/devinig97/planit-automation-assessment/actions/workflows/ui.yml/badge.svg)

Selenium + pytest solution for the Planit.  
Uses Page Objects (OOP) and is ready for CI (GitHub Actions).

## What’s covered (per assessment)

**Test Case 1 – Contact validation**
- Submit empty → three field errors present
- Fill valid data → errors disappear
- 
**Test Case 2 – Contact submit 5×**
- Parameterized 5 runs
- Assert success banner contains the submitted name

**Test Case 3 – Shop / cart totals**
- Verify product prices (Frog/Bunny/Bear)
- Buy 2 / 5 / 3
- Check unit price, qty, subtotal per row
- Verify **Total = sum(subtotals)**
- 
## Tech stack

- Python **3.11**
- Selenium WebDriver + **webdriver-manager**
- **pytest**
- Headless Chrome in CI (toggle via `HEADLESS=1`)

## Project layout

automation_assessment_planit/
├─ tests/
│  └─ test_planit_min.py        # Page Objects + 3 tests
├─ requirements.txt
├─ pytest.ini                   # minimal pytest config
└─ .github/workflows/ui.yml     # GitHub Actions workflow (CI)
```

---

## Run locally

### 1) Create & activate a virtual environment

**Windows (PowerShell)**
```powershell
py -3.11 -m venv .venv
. .\\.venv\\Scripts\\Activate.ps1
```

**macOS / Linux**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
python -m pip install -U pip
python -m pip install -r requirements.txt
```

### 3) Run tests

**Headful (see the browser)**
```bash
pytest
```

**Headless (CI-style)**  
Windows (PowerShell):
```powershell
$env:HEADLESS="1"; pytest
```
macOS/Linux:
```bash
HEADLESS=1 pytest
```

**Run a single test**
```bash
pytest -k test_case_3_shop_cart_totals -q

## Continuous Integration

### GitHub Actions (already set up)
Workflow: `.github/workflows/ui.yml`  
Runs on every push/PR:
1. Setup Python 3.11 & Chrome
2. Install deps
3. `HEADLESS=1 pytest -q --junitxml=pytest-results.xml`

Results are visible on the **Actions** tab; the JUnit XML is uploaded as an artifact.

### Jenkins (optional alternative)
If using Jenkins, a declarative pipeline can:
- Use a `python:3.11-slim` Docker agent
- Install Google Chrome in the container
- Install Python deps
- Run `pytest -q --junitxml=pytest-results.xml`

## Notes

- **WebDriver**: `webdriver-manager` auto-downloads the matching ChromeDriver at runtime—no manual driver management.
- **Headless toggle**: Controlled by the `HEADLESS` environment variable.

## Troubleshooting
- **`ModuleNotFoundError` / pytest not found**  
  Ensure the venv is active:  
  `python --version` shows 3.11.x and `pytest` resolves inside `.venv`.

- **Timeouts on CI**  
  The Contact success assertion uses longer waits and scrolls to top. If your network is slow, re-run; the test is resilient.
