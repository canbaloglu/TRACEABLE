"""Point-in-time fundamental metrics per event, derived from EDGAR companyfacts.

Information set of an event (cutoff = 8-K acceptance time, UTC):
  strict        : facts whose filing was accepted <= cutoff
  release_proxy : strict set + facts of the linked 10-Q/10-K (proxy for the
                  figures published in the 8-K exhibit; 8-K financials carry no XBRL)
For every (tag, start, end) the linked-filing value wins in release_proxy,
otherwise the latest value accepted <= cutoff ("as known at the time").
Every value actually used is re-checked by `check_pit`; a violation raises
PITViolation and the CLI exits with code 1.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .common import PITViolation, load_yaml, log, path

QUARTER_DAYS = (80, 100)   # calendar length of a fiscal quarter (13 weeks +/- 52/53-week drift)
YEAR_DAYS = (350, 380)
END_MATCH_TOL = pd.Timedelta(days=20)  # matching quarter ends of 52/53-week calendars
N_QUARTERS = 14

METRICS = {
    "rev_growth_q": "Revenue growth, quarter vs same quarter a year earlier",
    "rev_growth_ttm": "Revenue growth, trailing 4 quarters vs prior 4",
    "gross_margin": "Gross profit / revenue (quarter); GP = GrossProfit or revenue - cost of revenue",
    "op_margin": "Operating income / revenue (quarter)",
    "fcf_margin": "(Operating cash flow - capex) / revenue (quarter)",
    "accrual_ratio": "(Net income TTM - OCF TTM) / average total assets (now, 1y ago)",
    "wc_change": "Change in non-cash working capital over 1y / revenue TTM",
    "net_debt_ebitda": "(Debt - cash) / (operating income + D&A, TTM); n/a if EBITDA <= 0",
    "eps_growth": "Diluted EPS growth, quarter vs same quarter a year earlier ((a-b)/|b|)",
    "rpo_growth": "Remaining performance obligation growth vs 1y earlier",
}


@dataclass
class Used:
    items: list = field(default_factory=list)  # (field, tag, start, end, accn, accepted)

    def add(self, *a):
        self.items.append(a)


def g(a, b):
    if a is None or b is None or b == 0 or np.isnan(a) or np.isnan(b):
        return None
    return (a - b) / abs(b)


def ratio(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b


def prepare_facts(facts: pd.DataFrame, filings: pd.DataFrame, fields_cfg: dict) -> pd.DataFrame:
    """Attach field name, tag priority and acceptance timestamp to raw facts."""
    tagmap = {}
    for fld, spec in fields_cfg["fields"].items():
        for i, t in enumerate(spec["tags"]):
            tagmap[(t, spec["unit"])] = (fld, i, spec["type"])
    keys = list(zip(facts["tag"], facts["unit"]))
    m = [tagmap.get(k) for k in keys]
    f = facts.assign(field=[x[0] if x else None for x in m], prio=[x[1] if x else None for x in m],
                     ftype=[x[2] if x else None for x in m])
    f = f[f["field"].notna()].copy()
    acc = pd.to_datetime(filings.drop_duplicates("accn").set_index("accn")["acceptance_utc"], utc=True)
    f["accepted"] = f["accn"].map(acc)
    # accession not in the filing index (other form types / older): be conservative
    # and treat it as accepted at the very end of its 'filed' day (NY), i.e. after
    # any 8-K accepted the same day.
    miss = f["accepted"].isna()
    if miss.any():
        late = (pd.to_datetime(f.loc[miss, "filed"]) + pd.Timedelta(hours=23, minutes=59, seconds=59))
        f.loc[miss, "accepted"] = late.dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    f["start"] = pd.to_datetime(f["start"])
    f["end"] = pd.to_datetime(f["end"])
    f["days"] = (f["end"] - f["start"]).dt.days
    f["prio"] = f["prio"].astype(int)
    return f.sort_values(["field", "prio", "end", "start", "accepted", "accn"]).reset_index(drop=True)


def info_set(f: pd.DataFrame, cutoff: pd.Timestamp, linked: str | None, mode: str) -> pd.DataFrame:
    allowed = f["accepted"] <= cutoff
    if mode == "release_proxy" and linked:
        allowed |= f["accn"] == linked
    a = f[allowed].copy()
    a["is_linked"] = (a["accn"] == linked) if (mode == "release_proxy" and linked) else False
    a = a.sort_values(["is_linked", "accepted", "accn"], ascending=[False, False, True], kind="mergesort")
    a = a.drop_duplicates(["field", "tag", "start", "end"], keep="first")
    return a


def check_pit(used: Used, cutoff: pd.Timestamp, linked: str | None, mode: str, event_id: str) -> None:
    for fld, tag, s, e, accn, accepted in used.items:
        ok = accepted <= cutoff or (mode == "release_proxy" and linked is not None and accn == linked)
        if not ok:
            raise PITViolation(f"{event_id}: {fld}/{tag} {s}->{e} from {accn} accepted {accepted} "
                               f"after event cutoff {cutoff} (mode={mode})")


class Book:
    """Lookups over one event's information set."""

    def __init__(self, a: pd.DataFrame):
        self.dur: dict = {}
        self.inst: dict = {}
        for r in a.itertuples(index=False):
            rec = (r.val, r.accn, r.accepted)
            if pd.isna(r.start):
                self.inst.setdefault(r.field, {}).setdefault(r.prio, {})[r.end] = (r.tag, rec)
            else:
                self.dur.setdefault(r.field, {}).setdefault(r.prio, {})[(r.start, r.end)] = (r.tag, rec)
        ends = set()
        for fd in self.dur.values():
            for d in fd.values():
                ends.update(e for (_, e) in d)
        self.ends = np.array(sorted(ends), dtype="datetime64[ns]")
        self.used = Used()

    def quarter_ends(self, e0: pd.Timestamp) -> list:
        out = [e0]
        for k in range(1, N_QUARTERS):
            target = e0 - pd.DateOffset(months=3 * k)
            if len(self.ends) == 0:
                out.append(None)
                continue
            i = np.argmin(np.abs(self.ends - pd.Timestamp(target).to_datetime64().astype("datetime64[ns]")))
            cand = pd.Timestamp(self.ends[i])
            out.append(cand if abs(cand - target) <= END_MATCH_TOL else None)
        return out

    def _use(self, fld, tag, s, e, rec):
        self.used.add(fld, tag, s, e, rec[1], rec[2])

    def q(self, fld, E, Eprev):
        """Quarterly flow value ending at E (direct 3-month fact, or YTD(E) - YTD(Eprev))."""
        if E is None or fld not in self.dur:
            return None
        for prio in sorted(self.dur[fld]):
            d = self.dur[fld][prio]
            direct = [(abs((e - s).days - 91), s, e) for (s, e) in d
                      if e == E and QUARTER_DAYS[0] <= (e - s).days <= QUARTER_DAYS[1]]
            if direct:
                _, s, e = min(direct)
                tag, rec = d[(s, e)]
                self._use(fld, tag, s, e, rec)
                return rec[0]
            if Eprev is None:
                continue
            for (s, e) in sorted(d):
                if e == E and (e - s).days > QUARTER_DAYS[1] and (s, Eprev) in d:
                    tag, rec = d[(s, e)]
                    tag2, rec2 = d[(s, Eprev)]
                    self._use(fld, tag, s, e, rec)
                    self._use(fld, tag2, s, Eprev, rec2)
                    return rec[0] - rec2[0]
        return None

    def i(self, fld, E):
        if E is None or fld not in self.inst:
            return None
        for prio in sorted(self.inst[fld]):
            d = self.inst[fld][prio]
            if E in d:
                tag, rec = d[E]
                self._use(fld, tag, None, E, rec)
                return rec[0]
        return None

    def ttm(self, fld, ends, k):
        if k + 4 >= len(ends):
            return None
        vals = [self.q(fld, ends[j], ends[j + 1]) for j in range(k, k + 4)]
        if all(v is not None for v in vals):
            return float(sum(vals))
        E = ends[k]
        if E is not None and fld in self.dur:  # fiscal-year fact ending at E
            for prio in sorted(self.dur[fld]):
                d = self.dur[fld][prio]
                for (s, e) in sorted(d):
                    if e == E and YEAR_DAYS[0] <= (e - s).days <= YEAR_DAYS[1]:
                        tag, rec = d[(s, e)]
                        self._use(fld, tag, s, e, rec)
                        return rec[0]
        return None


def metric_funcs(b: Book, ends: list):
    """name -> f(k) computing the metric with quarter index k as 'now'."""
    E = lambda j: ends[j] if j < len(ends) else None  # noqa: E731
    q = lambda f, j: b.q(f, E(j), E(j + 1))  # noqa: E731

    def rev_growth_q(k):
        return g(q("revenue", k), q("revenue", k + 4))

    def rev_growth_ttm(k):
        return g(b.ttm("revenue", ends, k), b.ttm("revenue", ends, k + 4))

    def gross_margin(k):
        rev, gp = q("revenue", k), q("gross_profit", k)
        if gp is None:
            cor = q("cost_of_revenue", k)
            gp = rev - cor if (rev is not None and cor is not None) else None
        return ratio(gp, rev)

    def op_margin(k):
        return ratio(q("operating_income", k), q("revenue", k))

    def fcf_margin(k):
        ocf, capex, rev = q("ocf", k), q("capex", k), q("revenue", k)
        return ratio(ocf - capex, rev) if (ocf is not None and capex is not None) else None

    def accrual_ratio(k):
        ni_t, ocf_t = b.ttm("net_income", ends, k), b.ttm("ocf", ends, k)
        a0, a4 = b.i("total_assets", E(k)), b.i("total_assets", E(k + 4))
        return ratio(ni_t - ocf_t, (a0 + a4) / 2) if None not in (ni_t, ocf_t, a0, a4) else None

    def wc(j):
        ca, cl, cash = b.i("current_assets", E(j)), b.i("current_liabilities", E(j)), b.i("cash", E(j))
        if None in (ca, cl, cash):
            return None
        dc = b.i("debt_current", E(j)) or 0.0
        return (ca - cash) - (cl - dc)

    def wc_change(k):
        w0, w4, rt = wc(k), wc(k + 4), b.ttm("revenue", ends, k)
        return ratio(w0 - w4, rt) if None not in (w0, w4, rt) else None

    def net_debt_ebitda(k):
        dn, cash = b.i("debt_noncurrent", E(k)), b.i("cash", E(k))
        oi_t, dna_t = b.ttm("operating_income", ends, k), b.ttm("dna", ends, k)
        if None in (dn, cash, oi_t, dna_t) or (oi_t + dna_t) <= 0:
            return None
        debt = dn + (b.i("debt_current", E(k)) or 0.0) + (b.i("short_term_borrowings", E(k)) or 0.0)
        return (debt - cash) / (oi_t + dna_t)

    def eps_growth(k):
        return g(q("eps_diluted", k), q("eps_diluted", k + 4))

    def rpo_growth(k):
        return g(b.i("rpo", E(k)), b.i("rpo", E(k + 4)))

    loc = locals()
    return {name: loc[name] for name in METRICS}


def compute_event_metrics(f: pd.DataFrame, ev: dict, mode: str, periodic: pd.DataFrame) -> list[dict]:
    cutoff = pd.Timestamp(ev["acceptance_utc"])
    if cutoff.tzinfo is None:
        cutoff = cutoff.tz_localize("UTC")
    linked = ev.get("linked_accn") if mode == "release_proxy" else None
    if linked is not None and (not isinstance(linked, str) or not linked):
        linked = None  # NULL from SQLite comes back as NaN
    if mode == "release_proxy":
        if not linked:
            return []
        e0 = pd.Timestamp(ev["period_end"])
    else:
        known = periodic[pd.to_datetime(periodic["acceptance_utc"], utc=True) <= cutoff]
        known = known[known["form"].isin(["10-Q", "10-K", "10-KT"])]
        if known.empty:
            return []
        e0 = pd.Timestamp(known["report_date"].max())
    b = Book(info_set(f, cutoff, linked, mode))
    ends = b.quarter_ends(e0)
    rows = []
    for name, fn in metric_funcs(b, ends).items():
        n0 = len(b.used.items)
        v0, v4 = fn(0), fn(4)
        used = b.used.items[n0:]
        tags = sorted({f"EDGAR:us-gaap:{t}" for (_, t, *_r) in used})
        rows.append({
            "event_id": ev["event_id"], "ticker": ev["ticker"], "pit_mode": mode, "metric": name,
            "basis_period_end": e0.strftime("%Y-%m-%d"),
            "value": v0, "value_1y_ago": v4,
            "yoy_change": (v0 - v4) if (v0 is not None and v4 is not None) else None,
            "source": ("derived from " + ";".join(tags)) if tags else None,
            "input_accns": ",".join(sorted({x[4] for x in used})),
            "max_input_accepted_utc": str(max((x[5] for x in used), default="")) or None,
            "max_nonlinked_input_accepted_utc": str(max((x[5] for x in used if x[4] != linked), default="")) or None,
        })
    check_pit(b.used, cutoff, linked, mode, ev["event_id"])
    return rows
