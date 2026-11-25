"""Tests: 16:00 rule, look-ahead (point-in-time), reproducibility (hash)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from eventstudy import analyze as an
from eventstudy import events as evmod
from eventstudy import metrics as mt
from eventstudy import pipeline as pl
from eventstudy.common import PITViolation, frame_hash, load_config, load_yaml, path

FIELDS = load_yaml(path(load_config(), "edgar_fields"))


def bdays(a, b):
    return np.array(pd.bdate_range(a, b).values, dtype="datetime64[D]")


# ----------------------------------------------------------------------------- 16:00 rule
@pytest.mark.parametrize("utc, expected, rule", [
    ("2024-08-01T20:30:26.000Z", "2024-08-02", "after_close->next_day"),   # 16:30 EDT Thu
    ("2024-02-01T21:30:30.000Z", "2024-02-02", "after_close->next_day"),   # 16:30 EST Thu
    ("2024-02-01T20:59:59.000Z", "2024-02-01", "before_close->same_day"),  # 15:59:59 EST
    ("2024-02-01T21:00:00.000Z", "2024-02-02", "after_close->next_day"),   # exactly 16:00 EST
    ("2024-08-01T19:59:00.000Z", "2024-08-01", "before_close->same_day"),  # 15:59 EDT
    ("2024-08-01T11:00:00.000Z", "2024-08-01", "before_close->same_day"),  # 07:00 pre-market
    ("2024-08-02T20:30:00.000Z", "2024-08-05", "after_close->next_day"),   # Fri 16:30 -> Mon
    ("2024-08-03T14:00:00.000Z", "2024-08-05", "non_trading_day->next_day"),  # Saturday
    ("2024-08-02T03:30:00.000Z", "2024-08-01", None),  # 23:30 Thu NY (UTC date is Fri!) -> Fri
])
def test_sixteen_rule(utc, expected, rule):
    cal = bdays("2024-01-01", "2024-12-31")
    acc = evmod.to_ny(utc)
    d, r = evmod.event_trading_day(acc, cal, "16:00")
    if rule is None:  # 23:30 NY on Thursday 2024-08-01 -> next trading day Friday
        assert acc.date().isoformat() == "2024-08-01"
        assert d.strftime("%Y-%m-%d") == "2024-08-02" and r == "after_close->next_day"
        return
    assert d.strftime("%Y-%m-%d") == expected
    assert r == rule


def test_sixteen_rule_holiday():
    cal = np.array([x for x in bdays("2024-06-01", "2024-07-31") if str(x) != "2024-07-04"], dtype="datetime64[D]")
    d, _ = evmod.event_trading_day(evmod.to_ny("2024-07-03T21:05:00Z"), cal)  # Wed 17:05 EDT
    assert d.strftime("%Y-%m-%d") == "2024-07-05"


# ----------------------------------------------------------------------------- synthetic company
Q_ENDS = pd.to_datetime(["2022-03-31", "2022-06-30", "2022-09-30", "2022-12-31",
                         "2023-03-31", "2023-06-30", "2023-09-30", "2023-12-31", "2024-03-31"])
REV = {e: 100.0 + 10 * i for i, e in enumerate(Q_ENDS)}  # 100, 110, ... 180


def _acc(d, hh):
    return pd.Timestamp(d, tz="America/New_York").replace(hour=hh, minute=30).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%S.000Z")


def synthetic():
    facts, filings = [], []
    n = 0
    for i, e in enumerate(Q_ENDS):
        n += 1
        fy_start = pd.Timestamp(year=e.year, month=1, day=1)
        q_start = (e - pd.offsets.QuarterBegin(startingMonth=1)).normalize()
        q_start = pd.Timestamp(year=e.year, month=e.month - 2, day=1)
        rel_8k = e + pd.Timedelta(days=25)
        per_day = e + pd.Timedelta(days=30)
        accn_8k, accn_p = f"0000000001-{n:02d}-000001", f"0000000001-{n:02d}-000002"
        form = "10-K" if e.month == 12 else "10-Q"
        filings += [
            dict(accn=accn_8k, form="8-K", filing_date=str(rel_8k.date()), report_date=str(rel_8k.date()),
                 acceptance_utc=_acc(rel_8k, 16), items="2.02,9.01", primary_doc="", cik=1, ticker="TST"),
            dict(accn=accn_p, form=form, filing_date=str(per_day.date()), report_date=str(e.date()),
                 acceptance_utc=_acc(per_day, 12), items="", primary_doc="", cik=1, ticker="TST"),
        ]
        rows = []
        if form == "10-Q":
            rows.append(("Revenues", q_start, e, REV[e]))
            prev = e - pd.DateOffset(years=1)
            prev = Q_ENDS[Q_ENDS.get_indexer([prev], method="nearest")[0]]
            if abs((prev - (e - pd.DateOffset(years=1))).days) < 5:
                rows.append(("Revenues", pd.Timestamp(year=prev.year, month=prev.month - 2, day=1), prev, REV[prev]))
            if e.month == 9:  # 9M YTD for Q4 derivation
                rows.append(("Revenues", fy_start, e, sum(REV[x] for x in Q_ENDS if x.year == e.year and x <= e)))
        else:
            rows.append(("Revenues", fy_start, e, sum(REV[x] for x in Q_ENDS if x.year == e.year)))
        rows.append(("Assets", None, e, 1000.0 + i))
        for tag, s, en, v in rows:
            unit = "USD"
            facts.append(dict(cik=1, tag=tag, unit=unit, start=None if s is None else str(s.date()), end=str(en.date()),
                              val=float(v), accn=accn_p, form=form, filed=str(per_day.date())))
    # LOOK-AHEAD TRAP: an amendment filed long after the 2024-Q1 release restates
    # 2023-Q1 revenue; it must never be used for the 2024-Q1 event.
    filings.append(dict(accn="0000000001-99-000009", form="10-Q/A", filing_date="2024-09-01", report_date="2023-03-31",
                        acceptance_utc=_acc(pd.Timestamp("2024-09-01"), 10), items="", primary_doc="", cik=1, ticker="TST"))
    facts.append(dict(cik=1, tag="Revenues", unit="USD", start="2023-01-01", end="2023-03-31", val=9999.0,
                      accn="0000000001-99-000009", form="10-Q/A", filed="2024-09-01"))
    return pd.DataFrame(facts), pd.DataFrame(filings)


def synthetic_events():
    facts, filings = synthetic()
    cal = bdays("2021-06-01", "2024-12-31")
    ev, lg = evmod.build_events(filings, cal, "2022-01-01")
    return facts, filings, ev, lg


def test_linking_all_matched():
    _, _, ev, lg = synthetic_events()
    assert (ev["match_status"] == "matched").all()
    assert list(ev["period_end"]) == [str(e.date()) for e in Q_ENDS]


def _event_metrics(mode):
    facts, filings, ev, _ = synthetic_events()
    f = mt.prepare_facts(facts, filings, FIELDS)
    per = filings[filings["form"].isin(evmod.PERIODIC)]
    e = ev[ev["period_end"] == "2024-03-31"].iloc[0].to_dict()
    rows = mt.compute_event_metrics(f, e, mode, per)
    return {r["metric"]: r for r in rows}, e, f


def test_lookahead_release_proxy():
    rows, e, _ = _event_metrics("release_proxy")
    r = rows["rev_growth_q"]
    # 2024Q1 = 180 (linked 10-Q proxy for the 8-K figures), 2023Q1 = 140 as originally filed
    assert r["basis_period_end"] == "2024-03-31"
    assert r["value"] == pytest.approx(180 / 140 - 1)
    assert "0000000001-99-000009" not in r["input_accns"]  # restatement filed after the event
    assert pd.Timestamp(r["max_nonlinked_input_accepted_utc"]) <= pd.Timestamp(e["acceptance_utc"])


def test_lookahead_strict_hides_announced_quarter():
    rows, e, _ = _event_metrics("strict")
    r = rows["rev_growth_q"]
    assert r["basis_period_end"] == "2023-12-31"            # announced 2024Q1 not visible yet
    assert e["linked_accn"] not in r["input_accns"]
    # 2023Q4 derived = FY2023 - 9M2023 = 170; 2022Q4 = 130
    assert r["value"] == pytest.approx(170 / 130 - 1)
    assert pd.Timestamp(r["max_input_accepted_utc"]) <= pd.Timestamp(e["acceptance_utc"])


def test_check_pit_raises_on_injected_future_value():
    used = mt.Used()
    cutoff = pd.Timestamp("2024-04-25T20:30:00Z")
    used.add("revenue", "Revenues", None, None, "X-LATER", pd.Timestamp("2024-09-01T14:00:00Z"))
    with pytest.raises(PITViolation):
        mt.check_pit(used, cutoff, linked=None, mode="strict", event_id="TST:x")
    # the linked filing is allowed only in release_proxy mode
    used2 = mt.Used()
    used2.add("revenue", "Revenues", None, None, "LINKED", pd.Timestamp("2024-04-30T16:30:00Z"))
    mt.check_pit(used2, cutoff, linked="LINKED", mode="release_proxy", event_id="TST:x")
    with pytest.raises(PITViolation):
        mt.check_pit(used2, cutoff, linked="LINKED", mode="strict", event_id="TST:x")


def test_validate_metrics_table_and_exit_code(monkeypatch):
    facts, filings, ev, _ = synthetic_events()
    f = mt.prepare_facts(facts, filings, FIELDS)
    per = filings[filings["form"].isin(evmod.PERIODIC)]
    rows = []
    for e in ev.to_dict("records"):
        for mode in ("release_proxy", "strict"):
            rows += mt.compute_event_metrics(f, e, mode, per)
    m = pd.DataFrame(rows)
    assert pl.validate_metrics_pit(m, ev, filings) > 0
    bad = m.copy()
    i = bad.index[(bad["pit_mode"] == "strict") & bad["input_accns"].fillna("").ne("")][0]
    bad.loc[i, "input_accns"] += ",0000000001-99-000009"   # tamper: use the later restatement
    with pytest.raises(PITViolation):
        pl.validate_metrics_pit(bad, ev, filings)

    import event_study
    def boom(cfg):
        raise PITViolation("injected")
    monkeypatch.setattr(pl, "step_metrics", boom)
    assert event_study.main(["metrics"]) == 1


# ----------------------------------------------------------------------------- statistics
def test_weighted_spearman_matches_replication():
    rng = np.random.default_rng(0)
    x = rng.integers(0, 6, 40).astype(float)       # ties on purpose
    y = x + rng.normal(size=40)
    W = np.ones((1, 40))
    assert an.weighted_spearman(x, y, W)[0] == pytest.approx(stats.spearmanr(x, y)[0])
    w = rng.integers(0, 4, 40)
    rep = np.repeat(np.arange(40), w)
    assert an.weighted_spearman(x, y, w[None, :].astype(float))[0] == pytest.approx(stats.spearmanr(x[rep], y[rep])[0])


def test_bh():
    p = np.array([0.01, 0.04, 0.03, np.nan, 0.5])
    q = an.bh(p)
    assert np.isnan(q[3])
    assert q[0] == pytest.approx(0.04) and q[4] == pytest.approx(0.5)


def _synthetic_analysis_inputs():
    rng = np.random.default_rng(42)
    tick = [f"T{i}" for i in range(12)]
    ev_rows, m_rows, r_rows = [], [], []
    for t in tick:
        for k in range(10):
            eid = f"{t}:{k}"
            date = pd.Timestamp("2021-02-01") + pd.Timedelta(days=91 * k)
            ev_rows.append(dict(event_id=eid, ticker=t, event_date=str(date.date())))
            for met in mt.METRICS:
                v = rng.normal()
                m_rows.append(dict(event_id=eid, ticker=t, pit_mode="release_proxy", metric=met,
                                   value=v, yoy_change=rng.normal(), value_rel_sector=v - 0.1))
            for w in ["pre_60", "post_1", "post_5", "post_20", "post_60"]:
                r_rows.append(dict(event_id=eid, window=w, ret_raw=rng.normal(), ret_excess_spy=rng.normal(),
                                   ret_excess_sector=rng.normal()))
    sector_of = {t: ("A" if i % 2 else "B") for i, t in enumerate(tick)}
    return pd.DataFrame(m_rows), pd.DataFrame(r_rows), pd.DataFrame(ev_rows), sector_of


def test_reproducible_hash():
    cfg_an = dict(bootstrap_reps=200, bootstrap_ci=0.95, seed=7)
    m, r, e, s = _synthetic_analysis_inputs()
    h1 = frame_hash(pl.run_analysis(m, r, e, s, cfg_an))
    # shuffled input order must not change the result
    h2 = frame_hash(pl.run_analysis(m.sample(frac=1, random_state=1), r.sample(frac=1, random_state=2),
                                    e.sample(frac=1, random_state=3), s, cfg_an))
    assert h1 == h2
    _, _, ev1, _ = synthetic_events()
    _, _, ev2, _ = synthetic_events()
    assert frame_hash(ev1) == frame_hash(ev2)


def test_reproducible_on_real_db_if_present():
    """If the pipeline has been run, re-running the analysis reproduces ic_results exactly."""
    from eventstudy.common import connect, read_table
    from eventstudy import universe as un
    cfg = load_config()
    p = path(cfg, "event_db")
    if not p.exists():
        pytest.skip("no event_study.sqlite")
    con = connect(p)
    try:
        ic = read_table(con, "ic_results")
        m, r, e = read_table(con, "metrics"), read_table(con, "returns"), read_table(con, "events")
    except Exception:
        pytest.skip("analysis not run")
    finally:
        con.close()
    uni = un.load_universe(cfg)
    s = {c["ticker"]: c["gics_sector"] for c in uni["companies"]}
    # restrict to one metric to keep the test fast; compare against the stored rows
    met = "eps_growth"
    new = pl.run_analysis(m[m["metric"] == met], r, e, s, cfg["analysis"])
    old = ic[ic["metric"] == met]
    assert frame_hash(new.drop(columns=["q_value_bh"])) == frame_hash(old.drop(columns=["q_value_bh"]))


def test_edgar_db_append_only(tmp_path):
    import sqlite3
    from eventstudy.edgar import init_edgar_db
    con = sqlite3.connect(tmp_path / "edgar.sqlite")
    init_edgar_db(con)
    row = (1, "us-gaap", "Assets", "USD", None, "2024-03-31", 1.0, "a", 2024, "Q1", "10-Q", "2024-04-30", None, "now")
    con.execute("INSERT OR IGNORE INTO facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)
    con.execute("INSERT OR IGNORE INTO facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row)  # duplicate ignored
    assert con.execute("SELECT COUNT(*) FROM facts").fetchone()[0] == 1
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("UPDATE facts SET val = 2")
    with pytest.raises(sqlite3.DatabaseError):
        con.execute("DELETE FROM facts")
