"""EDGAR collectors.

* companyfacts -> data_fundamentals/edgar.sqlite table `facts` (APPEND-ONLY:
  INSERT OR IGNORE, UPDATE/DELETE blocked by triggers).
* submissions  -> data_fundamentals/event_study.sqlite table `filings`
  (acceptance datetimes are needed for point-in-time checks and event dating).
"""
from __future__ import annotations

import datetime as dt

import pandas as pd

from .common import connect, load_yaml, log, path, write_table
from .sec import SECClient

FACTS_DDL = """
CREATE TABLE IF NOT EXISTS facts (
    cik INTEGER NOT NULL, taxonomy TEXT NOT NULL, tag TEXT NOT NULL, unit TEXT NOT NULL,
    start TEXT, end TEXT NOT NULL, val REAL NOT NULL, accn TEXT NOT NULL,
    fy INTEGER, fp TEXT, form TEXT, filed TEXT NOT NULL, frame TEXT,
    fetched_at TEXT NOT NULL
);
-- expression index: instants have start NULL and NULLs are distinct in plain UNIQUE
CREATE UNIQUE INDEX IF NOT EXISTS ux_facts ON facts (cik, taxonomy, tag, unit, COALESCE(start, ''), end, val, accn);
CREATE INDEX IF NOT EXISTS ix_facts_cik_tag ON facts (cik, tag);
CREATE TRIGGER IF NOT EXISTS facts_no_update BEFORE UPDATE ON facts
BEGIN SELECT RAISE(ABORT, 'edgar.sqlite facts is append-only'); END;
CREATE TRIGGER IF NOT EXISTS facts_no_delete BEFORE DELETE ON facts
BEGIN SELECT RAISE(ABORT, 'edgar.sqlite facts is append-only'); END;
"""


def init_edgar_db(con) -> None:
    con.executescript(FACTS_DDL)


def sec_client(cfg) -> SECClient:
    return SECClient(cfg["sec"]["user_agent"], cfg["sec"]["max_requests_per_second"],
                     cache_dir=path(cfg, "raw_cache") / "sec")


def all_ciks(uni: dict) -> list[tuple[str, int]]:
    out = []
    for c in uni["companies"]:
        out.append((c["ticker"], int(c["cik"])))
        out += [(c["ticker"], int(p)) for p in c.get("predecessor_ciks") or []]
    return out


def collect_companyfacts(cfg: dict, uni: dict, client: SECClient | None = None) -> pd.DataFrame:
    """Run the companyfacts collector for every universe CIK with edgar_fields.yaml."""
    fields = load_yaml(path(cfg, "edgar_fields"))
    tax = fields.get("taxonomy", "us-gaap")
    wanted = {}
    for f, spec in fields["fields"].items():
        for t in spec["tags"]:
            wanted.setdefault(t, set()).add(spec["unit"])
    client = client or sec_client(cfg)
    con = connect(path(cfg, "edgar_db"))
    init_edgar_db(con)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    stats = []
    for ticker, cik in all_ciks(uni):
        try:
            d = client.get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json",
                                cache_name=f"companyfacts_{cik}")
        except FileNotFoundError:
            log.warning("companyfacts missing for %s CIK %s", ticker, cik)
            stats.append({"ticker": ticker, "cik": cik, "inserted": 0, "status": "no companyfacts"})
            continue
        facts = d.get("facts", {}).get(tax, {})
        rows = []
        for tag, units in wanted.items():
            if tag not in facts:
                continue
            for unit, items in facts[tag]["units"].items():
                if unit not in units:
                    continue
                for it in items:
                    rows.append((cik, tax, tag, unit, it.get("start"), it["end"], float(it["val"]),
                                 it["accn"], it.get("fy"), it.get("fp"), it.get("form"), it["filed"],
                                 it.get("frame"), now))
        before = con.total_changes
        con.executemany("INSERT OR IGNORE INTO facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        con.commit()
        stats.append({"ticker": ticker, "cik": cik, "inserted": con.total_changes - before, "status": "ok"})
        log.info("companyfacts %s (%s): %d rows, %d new", ticker, cik, len(rows), stats[-1]["inserted"])
    con.close()
    return pd.DataFrame(stats)


def _rows_from_block(block: dict, cik: int, ticker: str) -> pd.DataFrame:
    df = pd.DataFrame({
        "accn": block["accessionNumber"], "form": block["form"], "filing_date": block["filingDate"],
        "report_date": block["reportDate"], "acceptance_utc": block["acceptanceDateTime"],
        "items": block.get("items", [""] * len(block["form"])),
        "primary_doc": block.get("primaryDocument", [""] * len(block["form"])),
    })
    df["cik"] = cik
    df["ticker"] = ticker
    return df


def collect_submissions(cfg: dict, uni: dict, client: SECClient | None = None) -> pd.DataFrame:
    """Filing index (forms 8-K / 10-Q / 10-K and amendments) since start_date - 2y."""
    client = client or sec_client(cfg)
    since = (pd.Timestamp(cfg["start_date"]) - pd.DateOffset(years=2)).strftime("%Y-%m-%d")
    frames = []
    for ticker, cik in all_ciks(uni):
        d = client.get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json",
                            cache_name=f"submissions_{cik}")
        parts = [_rows_from_block(d["filings"]["recent"], cik, ticker)]
        for f in d["filings"].get("files", []):
            if f["filingTo"] < since:
                continue
            extra = client.get_json(f"https://data.sec.gov/submissions/{f['name']}",
                                    cache_name=f["name"].replace(".json", ""))
            parts.append(_rows_from_block(extra, cik, ticker))
        df = pd.concat(parts, ignore_index=True)
        df = df[df["form"].isin(["8-K", "8-K/A", "10-Q", "10-K", "10-Q/A", "10-K/A", "10-KT"])]
        df = df[df["filing_date"] >= since]
        frames.append(df)
        log.info("submissions %s (%s): %d relevant filings", ticker, cik, len(df))
    out = pd.concat(frames, ignore_index=True).drop_duplicates("accn")
    out["source"] = "EDGAR submissions API"
    out = out.sort_values(["ticker", "acceptance_utc", "accn"]).reset_index(drop=True)
    con = connect(path(cfg, "event_db"))
    write_table(con, "filings", out)
    con.close()
    return out


def load_facts(cfg: dict, ciks: list[int] | None = None):
    con = connect(path(cfg, "edgar_db"))
    q = "SELECT cik, tag, unit, start, end, val, accn, form, filed FROM facts"
    df = pd.read_sql_query(q, con)
    con.close()
    if ciks is not None:
        df = df[df["cik"].isin(ciks)]
    return df


def missing_fields_report(cfg: dict, uni: dict, facts: pd.DataFrame, since: str) -> pd.DataFrame:
    """company x field: which fields have no value (under any listed tag) since `since`."""
    fields = load_yaml(path(cfg, "edgar_fields"))["fields"]
    tag_field = {(t, s["unit"]): f for f, s in fields.items() for t in s["tags"]}
    f = facts[facts["end"] >= since].copy()
    f["field"] = [tag_field.get((t, u)) for t, u in zip(f["tag"], f["unit"])]
    rows = []
    for c in uni["companies"]:
        ciks = [int(c["cik"])] + [int(x) for x in c.get("predecessor_ciks") or []]
        have = f[f["cik"].isin(ciks)]
        for fld, spec in fields.items():
            sub = have[have["field"] == fld]
            rows.append({
                "ticker": c["ticker"], "field": fld, "has_data": not sub.empty,
                "tags_found": ",".join(sorted(sub["tag"].unique())),
                "n_periods": int(sub["end"].nunique()),
                "tags_searched": ",".join(spec["tags"]),
            })
    return pd.DataFrame(rows)
