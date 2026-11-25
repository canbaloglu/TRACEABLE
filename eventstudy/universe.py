"""Universe: S&P 100 from config/options_universe.yaml + GICS data from Wikipedia."""
from __future__ import annotations

import datetime as dt
import io

import pandas as pd
import requests
import yaml

from .common import load_yaml, log, path

# GICS sub-industry -> industry (GICS structure as of 2023 revision).
# source: AI-derived (Claude) from the public GICS hierarchy; Wikipedia only lists sub-industries.
GICS_SUB_TO_INDUSTRY = {
    "Aerospace & Defense": "Aerospace & Defense",
    "Agricultural & Farm Machinery": "Machinery",
    "Construction Machinery & Heavy Transportation Equipment": "Machinery",
    "Industrial Machinery & Supplies & Components": "Machinery",
    "Air Freight & Logistics": "Air Freight & Logistics",
    "Application Software": "Software",
    "Systems Software": "Software",
    "Asset Management & Custody Banks": "Capital Markets",
    "Investment Banking & Brokerage": "Capital Markets",
    "Financial Exchanges & Data": "Capital Markets",
    "Diversified Capital Markets": "Capital Markets",
    "Automobile Manufacturers": "Automobiles",
    "Biotechnology": "Biotechnology",
    "Broadline Retail": "Broadline Retail",
    "Cable & Satellite": "Media",
    "Movies & Entertainment": "Entertainment",
    "Communications Equipment": "Communications Equipment",
    "Consumer Finance": "Consumer Finance",
    "Consumer Staples Merchandise Retail": "Consumer Staples Distribution & Retail",
    "Diversified Banks": "Banks",
    "Regional Banks": "Banks",
    "Electric Utilities": "Electric Utilities",
    "Multi-Utilities": "Multi-Utilities",
    "Electrical Components & Equipment": "Electrical Equipment",
    "Heavy Electrical Equipment": "Electrical Equipment",
    "Health Care Equipment": "Health Care Equipment & Supplies",
    "Health Care Supplies": "Health Care Equipment & Supplies",
    "Health Care Services": "Health Care Providers & Services",
    "Managed Health Care": "Health Care Providers & Services",
    "Home Improvement Retail": "Specialty Retail",
    "Hotels, Resorts & Cruise Lines": "Hotels, Restaurants & Leisure",
    "Restaurants": "Hotels, Restaurants & Leisure",
    "IT Consulting & Other Services": "IT Services",
    "Industrial Conglomerates": "Industrial Conglomerates",
    "Industrial Gases": "Chemicals",
    "Integrated Oil & Gas": "Oil, Gas & Consumable Fuels",
    "Oil & Gas Exploration & Production": "Oil, Gas & Consumable Fuels",
    "Integrated Telecommunication Services": "Diversified Telecommunication Services",
    "Interactive Media & Services": "Interactive Media & Services",
    "Life Sciences Tools & Services": "Life Sciences Tools & Services",
    "Multi-Sector Holdings": "Financial Services",
    "Transaction & Payment Processing Services": "Financial Services",
    "Packaged Foods & Meats": "Food Products",
    "Passenger Ground Transportation": "Ground Transportation",
    "Rail Transportation": "Ground Transportation",
    "Personal Care Products": "Personal Care Products",
    "Pharmaceuticals": "Pharmaceuticals",
    "Semiconductor Materials & Equipment": "Semiconductors & Semiconductor Equipment",
    "Semiconductors": "Semiconductors & Semiconductor Equipment",
    "Soft Drinks & Non-alcoholic Beverages": "Beverages",
    "Technology Hardware, Storage & Peripherals": "Technology Hardware, Storage & Peripherals",
    "Telecom Tower REITs": "Specialized REITs",
    "Tobacco": "Tobacco",
    "Wireless Telecommunication Services": "Wireless Telecommunication Services",
    "Property & Casualty Insurance": "Insurance",
    "Life & Health Insurance": "Insurance",
    "Multi-line Insurance": "Insurance",
}

# Ticker -> earlier SEC registrants whose filings belong to the same economic entity
# (holding-company reorganisations). source: AI-derived (Claude), verified against
# EDGAR submissions:
#   XOM: CIK 34088 'EXXON MOBIL CORP' filed 10-Qs through 2026-08; holdco CIK 2115436
#        filed 8-K12B on 2026-07-01.
#   BLK: CIK 1364742 (now 'BlackRock Finance, Inc.') filed BlackRock's 10-Q/10-K until
#        2024-08; new holdco CIK 2012383 from 2024-10.
# Review before extending (e.g. DIS pre-2019 = CIK 1001039 when start_date moves to 2010).
PREDECESSOR_CIKS = {"XOM": [34088], "BLK": [1364742]}


def fetch_sp500_table(url: str) -> pd.DataFrame:
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (research script)"}, timeout=60)
    r.raise_for_status()
    t = pd.read_html(io.StringIO(r.text))[0]
    return t


def build_universe(cfg: dict, sp500: pd.DataFrame | None = None, sec_tickers: dict | None = None) -> dict:
    tickers = load_yaml(path(cfg, "options_universe"))["sp100"]
    if sp500 is None:
        sp500 = fetch_sp500_table(cfg["wikipedia"]["sp500_url"])
    sp500 = sp500.rename(columns={"GICS Sector": "sector", "GICS Sub-Industry": "sub_industry"})
    retrieved = dt.date.today().isoformat()
    excl_ind = set(cfg["universe"]["excluded_gics_industries"])
    rows, excluded, problems, seen_cik = [], [], [], {}
    for t in tickers:
        m = sp500[sp500["Symbol"] == t]
        if m.empty:
            problems.append({"ticker": t, "issue": "not in Wikipedia S&P 500 table"})
            continue
        m = m.iloc[0]
        cik = int(m["CIK"])
        sec_cik = (sec_tickers or {}).get(t.replace(".", "-"))
        if sec_cik is not None and int(sec_cik) != cik:
            problems.append({"ticker": t, "issue": f"Wikipedia CIK {cik} != SEC CIK {sec_cik}; using SEC"})
            cik = int(sec_cik)
        sub = m["sub_industry"]
        ind = GICS_SUB_TO_INDUSTRY.get(sub)
        if ind is None:
            problems.append({"ticker": t, "issue": f"sub-industry '{sub}' not in GICS map"})
        rec = {
            "ticker": t,
            "name": str(m["Security"]),
            "cik": cik,
            "predecessor_ciks": PREDECESSOR_CIKS.get(t, []),
            "gics_sector": m["sector"],
            "gics_sub_industry": sub,
            "gics_industry": ind,
            "sources": {
                "gics_sector": f"Wikipedia S&P 500 list ({retrieved})",
                "gics_sub_industry": f"Wikipedia S&P 500 list ({retrieved})",
                "gics_industry": "AI-derived from GICS sub-industry",
                "cik": "SEC company_tickers.json" if sec_cik is not None else "Wikipedia",
                "predecessor_ciks": "AI-derived, verified on EDGAR" if t in PREDECESSOR_CIKS else None,
            },
        }
        if cik in seen_cik:
            problems.append({"ticker": t, "issue": f"duplicate share class of {seen_cik[cik]} (same CIK) - dropped"})
            continue
        seen_cik[cik] = t
        if ind in excl_ind:
            rec["exclusion_reason"] = f"GICS industry = {ind}"
            excluded.append(rec)
        else:
            rows.append(rec)
    out = {
        "generated": retrieved,
        "source": "config/options_universe.yaml (S&P 100) + " + cfg["wikipedia"]["sp500_url"],
        "survivorship_bias_note": (
            "Current index membership is applied to the whole history: firms that left the "
            "S&P 100 are missing and later entrants are included -> survivorship bias."
        ),
        "companies": rows,
        "excluded": excluded,
        "problems": problems,
    }
    return out


def write_universe(cfg: dict, uni: dict) -> None:
    p = path(cfg, "event_universe")
    p.write_text(yaml.safe_dump(uni, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")
    log.info("universe: %d companies, %d excluded, %d problems -> %s",
             len(uni["companies"]), len(uni["excluded"]), len(uni["problems"]), p)


def load_universe(cfg: dict) -> dict:
    return load_yaml(path(cfg, "event_universe"))
