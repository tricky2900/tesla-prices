# Tesla Global Price Tracker

Pulls trim-level prices for every Tesla model across ~43 markets daily, stores
them in SQLite, and exports an analysis workbook your Excel forecast model can
link to.

## Files

| File | Purpose |
|---|---|
| `config.py` | Market list (URLs, currencies) and models — edit here to add/remove countries |
| `scraper.py` | Daily pull → `tesla_prices.db` (SQLite) |
| `export_analysis.py` | Builds `tesla_price_analysis.xlsx` (latest prices, monthly averages, MoM % change, raw data) |
| `daily_scrape.yml` | Optional GitHub Actions workflow for fully automated daily runs |

## Setup

```bash
pip install requests pandas openpyxl
python scraper.py                 # first pull (takes ~10-15 min for all markets)
python export_analysis.py         # builds the Excel export
```

Test on a subset first:

```bash
python scraper.py --countries "United States,Germany" --models model3,modely
```

## Scheduling daily

**GitHub Actions (recommended — runs even when your machine is off):** put these
files in a private repo, add `daily_scrape.yml` at `.github/workflows/`, done.
The database and Excel file are committed back to the repo each day.

**Windows Task Scheduler:** create a Basic Task → Daily → Action "Start a
program" → `python.exe` with arguments `C:\path\to\scraper.py`, then a second
task 30 min later for `export_analysis.py`.

**Mac/Linux cron:** `crontab -e` →
`0 6 * * * cd /path/to/tesla_prices && python scraper.py && python export_analysis.py`

## Connecting your Excel model

In your quarterly model: **Data → Get Data → From Workbook** →
`tesla_price_analysis.xlsx` → choose the *Monthly Averages* (or *Raw Data*)
sheet → Load. From then on, **Data → Refresh All** pulls the latest numbers
into your model. The *MoM Change* sheet uses live formulas so it always
recalculates against the averages.

Prices are in **local currency** (currency column included). If your model
needs everything in USD, join an FX table in Power Query or ask me to add an
FX-conversion step.

## Important caveats

- **This scrapes tesla.com configurator pages — there is no official API.**
  If Tesla redesigns their pages, parsing can break. The scraper logs
  `parse_fail` per market/model in `scraper.log` and the `run_log` table
  instead of crashing, so you can spot breakage quickly. The extraction logic
  lives in the section of `scraper.py` marked `EXTRACTION`.
- Prices are **base trim prices before incentives/taxes as displayed in the
  configurator**; display conventions differ by country (some include VAT,
  some show post-incentive prices).
- The scraper uses polite 2–5 s delays between requests. Don't reduce them —
  aggressive scraping may get the IP blocked.
- Check Tesla's terms of service for your intended use, particularly if the
  data feeds commercial research distributed to clients.
