"""Pipeline steps behind the event_study.py CLI."""
from __future__ import annotations

import numpy as np
import pandas as pd
import requests

from . import analyze as an
from . import edgar, events as evmod, metrics as mt, prices as px, returns as rt, universe as un
from .common import PITViolation, connect, load_yaml, log, path, read_table, write_table


def _db(cfg):
    return connect(path(cfg, "event_db"))


def sector_maps(cfg, uni):
    sector_of = {c["ticker"]: c["gics_sector"] for c in uni["companies"]}
    return sector_of, cfg["prices"]["sector_etfs"]


# ------------------------------------------------------------------ universe
def step_universe(cfg):
    sec = edgar.sec_client(cfg)
    tick = sec.get_json("https://www.sec.gov/files/company_tickers.json", cache_name="company_tickers")
    sec_map = {v["ticker"]: int(v["cik_str"]) for v in tick.values()}
    uni = un.build_universe(cfg, sec_tickers=sec_map)
    un.write_universe(cfg, uni)
    return uni


# ------------------------------------------------------------------ edgar
def step_edgar(cfg):
    uni = un.load_universe(cfg)
    stats = edgar.collect_companyfacts(cfg, uni)
    filings = edgar.collect_submissions(cfg, uni)
    con = _db(cfg)
    write_table(con, "edgar_collect_log", stats)
    con.close()
    return stats, filings


# ------------------------------------------------------------------ prices
def price_tickers(cfg, uni):
    t = [c["ticker"] for c in uni["companies"]]
    return t + [cfg["prices"]["benchmark"]] + sorted(set(cfg["prices"]["sector_etfs"].values()))


def step_prices(cfg, full=False):
    uni = un.load_universe(cfg)
    st = px.update_prices(cfg, price_tickers(cfg, uni), full=full)
    con = _db(cfg)
    write_table(con, "price_status", st.astype(str))
    con.close()
    log.info("prices: %s", st["status"].value_counts().to_dict())
    return st


# ------------------------------------------------------------------ events
def step_events(cfg):
    con = _db(cfg)
    try:
        filings = read_table(con, "filings")
    except Exception:  # noqa: BLE001
        con.close()
        edgar.collect_submissions(cfg, un.load_universe(cfg))
        con = _db(cfg)
        filings = read_table(con, "filings")
    cal = px.trading_calendar(cfg)
    ev, lg = evmod.build_events(filings, cal, cfg["start_date"], cfg["events"]["after_close_time"],
                                cfg["events"]["timezone"])
    write_table(con, "events", ev)
    write_table(con, "event_log", lg)
    con.close()
    return ev, lg


# ------------------------------------------------------------------ metrics
def compute_all_metrics(facts_raw, filings, events, uni, fields_cfg, modes):
    rows = []
    for c in uni["companies"]:
        t = c["ticker"]
        ciks = [int(c["cik"])] + [int(x) for x in c.get("predecessor_ciks") or []]
        fl = filings[filings["ticker"] == t]
        f = mt.prepare_facts(facts_raw[facts_raw["cik"].isin(ciks)], fl, fields_cfg)
        periodic = fl[fl["form"].isin(evmod.PERIODIC)]
        # both PIT modes use the same event set: events linked to a 10-Q/10-K
        evs = events[(events["ticker"] == t) & (events["match_status"] == "matched")]
        for ev in evs.to_dict("records"):
            for mode in modes:
                rows += mt.compute_event_metrics(f, ev, mode, periodic)
    return pd.DataFrame(rows)


def add_sector_relative(m: pd.DataFrame, events: pd.DataFrame, sector_of: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    ev = events.set_index("event_id")
    m = m.copy()
    m["acceptance_utc"] = pd.to_datetime(m["event_id"].map(ev["acceptance_utc"]), utc=True)
    m["year"] = pd.to_datetime(m["event_id"].map(ev["event_date"])).dt.year
    m["gics_sector"] = m["ticker"].map(sector_of)
    # descriptive year x sector stats (uses the whole year; NOT used in tests)
    grp = m.groupby(["pit_mode", "metric", "year", "gics_sector"])
    stats_ = grp.agg(n=("value", "count"), mean=("value", "mean"), median=("value", "median"),
                     yoy_n=("yoy_change", "count"), yoy_mean=("yoy_change", "mean"),
                     yoy_median=("yoy_change", "median")).reset_index()
    m = m.merge(stats_[["pit_mode", "metric", "year", "gics_sector", "mean", "median"]]
                .rename(columns={"mean": "sector_year_mean", "median": "sector_year_median"}),
                on=["pit_mode", "metric", "year", "gics_sector"], how="left")
    m["value_minus_sector_year_median"] = m["value"] - m["sector_year_median"]
    # point-in-time peer median: latest value of each other company in the same
    # sector from its events accepted in the 365 days before this event.
    rel = np.full(len(m), np.nan)
    npeers = np.zeros(len(m), dtype=int)
    for _, g in m.groupby(["pit_mode", "metric", "gics_sector"], sort=False):
        g = g.sort_values("acceptance_utc")
        acc = g["acceptance_utc"].to_numpy()
        tick = g["ticker"].to_numpy()
        val = g["value"].to_numpy(dtype=float)
        idx = g.index.to_numpy()
        for j in range(len(g)):
            lo = acc[j] - np.timedelta64(365, "D")
            mask = (acc < acc[j]) & (acc >= lo) & (tick != tick[j]) & ~np.isnan(val)
            if not mask.any():
                continue
            sub = pd.DataFrame({"t": tick[mask], "v": val[mask]})
            latest = sub.groupby("t", sort=False)["v"].last()
            npeers[idx[j]] = len(latest)
            if not np.isnan(val[j]):
                rel[idx[j]] = val[j] - float(np.median(latest.to_numpy()))
    m["value_rel_sector"] = rel
    m["n_sector_peers_pit"] = npeers
    m["acceptance_utc"] = m["acceptance_utc"].astype(str)
    stats_["source"] = "derived: metrics table (EDGAR-derived values)"
    return m, stats_


def validate_metrics_pit(m: pd.DataFrame, events: pd.DataFrame, filings: pd.DataFrame) -> int:
    """Independent post-hoc lookahead check on the stored metrics table.

    Every input accession of every metric row must have been accepted at or before
    the event's 8-K acceptance, except the event's own linked 10-Q/10-K in
    release_proxy mode. Accessions missing from the filing index are a violation
    too (their timing cannot be proven). Raises PITViolation; returns rows checked.
    """
    acc = pd.to_datetime(filings.drop_duplicates("accn").set_index("accn")["acceptance_utc"], utc=True)
    ev = events.set_index("event_id")
    cut = pd.to_datetime(ev["acceptance_utc"], utc=True)
    n = 0
    cols = ["event_id", "pit_mode", "metric", "input_accns", "max_nonlinked_input_accepted_utc"]
    for r in m[cols].itertuples(index=False):
        if not isinstance(r.input_accns, str) or not r.input_accns:
            continue
        c, linked = cut[r.event_id], ev.at[r.event_id, "linked_accn"]
        mx = r.max_nonlinked_input_accepted_utc
        if isinstance(mx, str) and mx and pd.Timestamp(mx) > c:
            raise PITViolation(f"{r.event_id} [{r.pit_mode}] {r.metric}: input accepted {mx} > event {c}")
        for a in r.input_accns.split(","):
            if r.pit_mode == "release_proxy" and a == linked:
                continue
            t = acc.get(a)
            if t is None or pd.isna(t):
                continue  # outside the filing index: covered by max_nonlinked_input_accepted_utc
            if t > c:
                raise PITViolation(f"{r.event_id} [{r.pit_mode}] {r.metric}: input {a} accepted {t} > event {c}")
        n += 1
    return n


def step_metrics(cfg):
    uni = un.load_universe(cfg)
    fields_cfg = load_yaml(path(cfg, "edgar_fields"))
    con = _db(cfg)
    filings, events = read_table(con, "filings"), read_table(con, "events")
    facts = edgar.load_facts(cfg)
    m = compute_all_metrics(facts, filings, events, uni, fields_cfg, cfg["pit"]["modes"])
    for c in ["value", "value_1y_ago", "yoy_change"]:
        m[c] = pd.to_numeric(m[c], errors="coerce")
    checked = validate_metrics_pit(m, events, filings)
    log.info("PIT validation passed for %d metric rows", checked)
    sector_of, _ = sector_maps(cfg, uni)
    m, sstats = add_sector_relative(m, events, sector_of)
    since = (pd.Timestamp(cfg["start_date"]) - pd.DateOffset(years=3)).strftime("%Y-%m-%d")
    miss = edgar.missing_fields_report(cfg, uni, facts, since)
    write_table(con, "metrics", m)
    write_table(con, "sector_stats", sstats)
    write_table(con, "missing_fields", miss)
    con.close()
    log.info("metrics: %d rows (%d events x modes)", len(m), m[["event_id", "pit_mode"]].drop_duplicates().shape[0])
    return m


# ------------------------------------------------------------------ returns
def step_returns(cfg):
    uni = un.load_universe(cfg)
    con = _db(cfg)
    events = read_table(con, "events")
    panel, srcs = px.load_panel(cfg, price_tickers(cfg, uni))
    sector_of, etfs = sector_maps(cfg, uni)
    r = rt.compute_returns(events, panel, srcs, sector_of, etfs, cfg["prices"]["benchmark"],
                           int(cfg["returns"]["pre_window"]), [int(x) for x in cfg["returns"]["post_windows"]])
    write_table(con, "returns", r)
    con.close()
    log.info("returns: %d rows", len(r))
    return r


# ------------------------------------------------------------------ analyze
def run_analysis(metrics, returns, events, sector_of, cfg_an):
    d = an.build_dataset(metrics, returns, events, sector_of)
    return an.run_ic(d, cfg_an)


def step_analyze(cfg):
    uni = un.load_universe(cfg)
    con = _db(cfg)
    metrics, returns, events = read_table(con, "metrics"), read_table(con, "returns"), read_table(con, "events")
    sector_of, _ = sector_maps(cfg, uni)
    ic = run_analysis(metrics, returns, events, sector_of, cfg["analysis"])
    write_table(con, "ic_results", ic)
    cls = []
    for mode in cfg["pit"]["modes"]:
        for rtype in an.RET_TYPES:
            c = an.classify(ic, mode, rtype, float(cfg["analysis"]["fdr_alpha"]))
            c.insert(0, "ret_type", rtype)
            c.insert(0, "pit_mode", mode)
            cls.append(c)
    cls = pd.concat(cls, ignore_index=True)
    write_table(con, "classification", cls)
    con.close()
    log.info("analyze: %d tests", len(ic))
    return ic, cls
