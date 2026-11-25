"""Event dating (8-K Item 2.02) and linking to the 10-Q/10-K period."""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from .common import log

PERIODIC = {"10-Q", "10-K", "10-KT"}


def to_ny(acceptance_utc: str, tz: str = "America/New_York") -> pd.Timestamp:
    """EDGAR acceptanceDateTime is ISO-8601 UTC ('...Z')."""
    ts = pd.Timestamp(acceptance_utc)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert(ZoneInfo(tz))


def event_trading_day(acc_ny: pd.Timestamp, calendar: np.ndarray, after_close: str = "16:00") -> tuple[pd.Timestamp | None, str]:
    """16:00 rule.

    acceptance time >= 16:00 NY  -> next trading day after the acceptance date
    acceptance time <  16:00 NY  -> the acceptance date if it is a trading day,
                                    otherwise the next trading day.
    `calendar` is a sorted numpy array of datetime64[D] trading days.
    Returns (event_date or None if beyond calendar, rule label).
    """
    hh, mm = (int(x) for x in after_close.split(":"))
    d = np.datetime64(acc_ny.date(), "D")
    after = (acc_ny.hour, acc_ny.minute) >= (hh, mm)
    side = "right" if after else "left"   # right: strictly after d; left: d itself allowed
    i = np.searchsorted(calendar, d, side=side)
    rule = "after_close->next_day" if after else ("before_close->same_day" if i < len(calendar) and calendar[i] == d else "non_trading_day->next_day")
    if i >= len(calendar):
        return None, rule
    return pd.Timestamp(calendar[i]), rule


def is_202(items: str) -> bool:
    return "2.02" in [s.strip() for s in str(items or "").split(",")]


def build_events(filings: pd.DataFrame, calendar: np.ndarray, start_date: str,
                 after_close: str = "16:00", tz: str = "America/New_York") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (events, event_log).

    Linking rule (structural, no day-count thresholds). Candidates for event e_i are
    original 10-Q/10-K/10-KT filings, not yet linked, accepted strictly between the
    previous and the next 2.02 event of the company, whose period end (reportDate) is
    before e_i's acceptance date and later than the period linked to the previous
    event. Preferred: the first candidate accepted on/after e_i's acceptance date
    (the usual case: 10-Q follows the release); otherwise the latest candidate
    accepted before it (e.g. SO files its 10-Q the evening before the 8-K).
    Unlinked events (pre-announcements, delivery updates, 10-Q not yet filed) are logged.
    """
    f = filings.copy()
    f["acc_ny"] = [to_ny(a, tz) for a in f["acceptance_utc"]]
    events, logs = [], []
    for ticker, g in f.groupby("ticker", sort=True):
        g = g.sort_values(["acc_ny", "accn"])
        ev = g[(g["form"] == "8-K") & g["items"].map(is_202)]
        per = g[g["form"].isin(PERIODIC)]
        last_period = pd.Timestamp("1900-01-01")
        used = set()
        ev_list = list(ev.itertuples(index=False))
        for i, e in enumerate(ev_list):
            prv = ev_list[i - 1].acc_ny if i > 0 else pd.Timestamp("1900-01-01", tz=tz)
            nxt = ev_list[i + 1].acc_ny if i + 1 < len(ev_list) else pd.Timestamp("2200-01-01", tz=tz)
            day0 = e.acc_ny.normalize()
            cand = per[(per["acc_ny"] > prv) & (per["acc_ny"] < nxt) & (~per["accn"].isin(used))]
            rd = pd.to_datetime(cand["report_date"])
            cand = cand[rd.lt(pd.Timestamp(e.acc_ny.date())) & rd.gt(last_period)]
            after_ = cand[cand["acc_ny"] >= day0]
            cand = after_.iloc[:1] if not after_.empty else cand.iloc[-1:]
            ev_date, rule = event_trading_day(e.acc_ny, calendar, after_close)
            rec = {
                "event_id": f"{ticker}:{e.accn}", "ticker": ticker, "cik": int(e.cik), "accn": e.accn,
                "acceptance_utc": e.acceptance_utc, "acceptance_ny": e.acc_ny.isoformat(),
                "event_date": ev_date.strftime("%Y-%m-%d") if ev_date is not None else None,
                "day_rule": rule, "items": e.items, "source": "EDGAR submissions (8-K Item 2.02)",
            }
            if cand.empty:
                rec.update(linked_accn=None, linked_form=None, period_end=None, linked_acceptance_utc=None,
                           match_status="unmatched")
            else:
                c = cand.iloc[0]
                used.add(c["accn"])
                last_period = pd.Timestamp(c["report_date"])
                rec.update(linked_accn=c["accn"], linked_form=c["form"], period_end=c["report_date"],
                           linked_acceptance_utc=c["acceptance_utc"], match_status="matched")
            if str(e.acc_ny.date()) < start_date:
                continue
            events.append(rec)
            if rec["match_status"] != "matched":
                logs.append({"event_id": rec["event_id"], "ticker": ticker, "acceptance_ny": rec["acceptance_ny"],
                             "issue": "no 10-Q/10-K accepted between this 2.02 and the next 2.02"})
            if ev_date is None:
                logs.append({"event_id": rec["event_id"], "ticker": ticker, "acceptance_ny": rec["acceptance_ny"],
                             "issue": "event date beyond price calendar"})
    ev = pd.DataFrame(events)
    lg = pd.DataFrame(logs, columns=["event_id", "ticker", "acceptance_ny", "issue"])
    log.info("events: %d (matched %d, unmatched %d)", len(ev),
             int((ev["match_status"] == "matched").sum()) if len(ev) else 0,
             int((ev["match_status"] != "matched").sum()) if len(ev) else 0)
    return ev, lg
