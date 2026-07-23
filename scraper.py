"""
Tesla price scraper — pulls trim-level prices for every model in every market
and stores them in a SQLite database (one row per date/country/model/trim).

Run daily:  python scraper.py
Optional:   python scraper.py --countries "Germany,United States" --models model3,modely

How it works
------------
Tesla's /design configurator pages embed a large JSON blob (the "DSServices"
lexicon) in the page source containing every trim and its price. This script
fetches each page, extracts that blob with brace-matching, and recursively
searches it for trim option dicts (code + price + name).

NOTE: This depends on Tesla's page structure. If Tesla changes their site the
extraction section below (marked EXTRACTION) is the part to update. Failures
are logged per market/model and never abort the whole run.
"""

import argparse
import json
import logging
import random
import re
import sqlite3
import sys
import time
from datetime import date

import requests

from config import DB_PATH, MARKETS, MODELS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("scraper.log", encoding="utf-8")],
)
log = logging.getLogger("tesla-scraper")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 30
RETRIES = 3
DELAY_RANGE = (2.0, 5.0)  # polite random delay between requests, seconds


# ---------------------------------------------------------------- database --

def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            pull_date  TEXT NOT NULL,          -- YYYY-MM-DD
            country    TEXT NOT NULL,
            model      TEXT NOT NULL,          -- model3 / modely / ...
            trim_code  TEXT NOT NULL,          -- Tesla option code, e.g. $MTS13
            trim_name  TEXT,
            price      REAL NOT NULL,
            currency   TEXT NOT NULL,
            PRIMARY KEY (pull_date, country, model, trim_code)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS run_log (
            run_ts    TEXT NOT NULL,
            country   TEXT NOT NULL,
            model     TEXT NOT NULL,
            status    TEXT NOT NULL,           -- ok / http_404 / parse_fail / error
            rows      INTEGER NOT NULL DEFAULT 0,
            detail    TEXT
        )
    """)
    conn.commit()


def save_rows(conn, rows):
    conn.executemany(
        """INSERT OR REPLACE INTO prices
           (pull_date, country, model, trim_code, trim_name, price, currency)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()


# -------------------------------------------------------------- EXTRACTION --

def extract_json_blob(html: str, marker: str) -> dict | None:
    """Find `marker` in the HTML and parse the first balanced {...} after it."""
    idx = html.find(marker)
    if idx == -1:
        return None
    start = html.find("{", idx)
    if start == -1:
        return None
    depth, i, in_str, esc = 0, start, False, False
    while i < len(html):
        ch = html[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(html[start:i + 1])
                    except json.JSONDecodeError:
                        return None
        i += 1
    return None


TRIM_CODE_RE = re.compile(r"^\$?MT\w+$", re.IGNORECASE)


def find_trims(node, out: dict) -> None:
    """Recursively collect option dicts that look like trims with prices."""
    if isinstance(node, dict):
        code = node.get("code")
        price = node.get("price")
        if (isinstance(code, str) and TRIM_CODE_RE.match(code)
                and isinstance(price, (int, float)) and price > 1000):
            name = (node.get("long_name") or node.get("name")
                    or node.get("description") or "")
            if isinstance(name, str):
                name = re.sub(r"<[^>]+>", " ", name).strip()
            # Keep the first (base) price seen per code
            out.setdefault(code.lstrip("$"), (name, float(price)))
        for v in node.values():
            find_trims(v, out)
    elif isinstance(node, list):
        for v in node:
            find_trims(v, out)


def parse_prices(html: str) -> dict:
    """Return {trim_code: (trim_name, price)} from a /design page."""
    for marker in ('const dataJson', '"DSServices"', 'DSServices'):
        blob = extract_json_blob(html, marker)
        if blob:
            trims: dict = {}
            find_trims(blob, trims)
            if trims:
                return trims
    return {}


# ----------------------------------------------------------------- fetching --

def fetch(url: str, session: requests.Session):
    for attempt in range(1, RETRIES + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 404:
                return None, "http_404"
            resp.raise_for_status()
            return resp.text, "ok"
        except requests.RequestException as exc:
            log.warning("attempt %d/%d failed for %s: %s", attempt, RETRIES, url, exc)
            time.sleep(2 * attempt)
    return None, "error"


def run(countries=None, models=None):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    session = requests.Session()

    markets = {k: v for k, v in MARKETS.items() if not countries or k in countries}
    model_list = models or MODELS
    total_rows = 0

    for country, (base, locale, currency) in markets.items():
        for model in model_list:
            url = f"{base}/{locale}/{model}/design" if locale else f"{base}/{model}/design"
            html, status = fetch(url, session)
            rows = []
            if html:
                trims = parse_prices(html)
                if trims:
                    rows = [(today, country, model, code, name, price, currency)
                            for code, (name, price) in trims.items()]
                    save_rows(conn, rows)
                    total_rows += len(rows)
                    log.info("%s / %s: %d trims", country, model, len(rows))
                else:
                    status = "parse_fail"
                    log.error("%s / %s: page fetched but no prices parsed (%s)",
                              country, model, url)
            elif status == "http_404":
                log.info("%s / %s: not sold in this market (404)", country, model)
            conn.execute(
                "INSERT INTO run_log (run_ts, country, model, status, rows, detail) "
                "VALUES (datetime('now'), ?, ?, ?, ?, ?)",
                (country, model, status, len(rows), url),
            )
            conn.commit()
            time.sleep(random.uniform(*DELAY_RANGE))

    log.info("Done. %d price rows saved for %s.", total_rows, today)
    conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", help="Comma-separated subset, e.g. 'Germany,France'")
    ap.add_argument("--models", help="Comma-separated subset, e.g. 'model3,modely'")
    args = ap.parse_args()
    run(
        countries=[c.strip() for c in args.countries.split(",")] if args.countries else None,
        models=[m.strip() for m in args.models.split(",")] if args.models else None,
    )
