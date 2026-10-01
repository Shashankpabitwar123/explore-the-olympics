# Run the checks

Viewing the dashboard only requires a browser, or Tableau to open the packaged workbook. Python is needed only to run the data checks and regenerate the summaries.

From the repository folder, with Python 3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-checks.txt
python scripts/check_and_export.py
```

On Windows, activate the environment with `.venv\Scripts\activate`.

The script reads the local CSVs and extracts the workbook's connected Hyper file into a temporary directory. It uses SQL through the Hyper API to inspect the published records. No network requests or Tableau Desktop session are required.

It checks unique IDs, table relationships, medal codes, team flags, event dimensions, display-label changes, recorded roster names and the opening podium. It then writes:

- `validation/check-results.json` — 23 passed checks, workbook hash and row counts.
- `data/summary/editions.csv` — per-edition event, sport and medal-award counts.
- `data/summary/paris-2024-womens-100m.csv` — the opening podium.

A failed check stops the script with an error. Successful execution prints the number of checks and reconciled records.

## What this reproduces

This reproduces validation and summary exports from the saved data and published workbook. The editable `.twbx` is the starting point for dashboard changes. This repository does not rebuild the dashboard layout from raw CSVs or scrape fresh Olympic results.

The workbook includes presentation rows for selectors, geometry and result text in addition to factual award records. Rebuilding that presentation model is separate from the summary exports above.
