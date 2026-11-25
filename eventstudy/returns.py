"""Event-window returns: raw, minus SPY, minus sector SPDR ETF.

d0 = event trading day (16:00 rule). Base close = close of d0-1 (last close before
the market could react).
  pre_60   : P[d0-1] / P[d0-61] - 1
  post_h   : P[d0-1+h] / P[d0-1] - 1   (post_1 = reaction day d0)
Excess return = stock window return - benchmark window return (same dates).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def window_return(arr: np.ndarray, i_from: int, i_to: int) -> float:
    if i_from < 0 or i_to >= len(arr) or i_to < 0:
        return np.nan
    a, b = arr[i_from], arr[i_to]
    if np.isnan(a) or np.isnan(b) or a == 0:
        return np.nan
    return b / a - 1.0


def compute_returns(events: pd.DataFrame, panel: pd.DataFrame, srcs: dict, sector_of: dict,
                    etf_of_sector: dict, benchmark: str, pre: int, posts: list[int]) -> pd.DataFrame:
    dates = panel.index.values.astype("datetime64[D]")
    cols = {c: panel[c].to_numpy(dtype=float) for c in panel.columns}
    rows = []
    for ev in events.itertuples(index=False):
        if ev.event_date is None or (isinstance(ev.event_date, float) and np.isnan(ev.event_date)):
            continue
        d0 = np.datetime64(ev.event_date, "D")
        i0 = int(np.searchsorted(dates, d0))
        if i0 >= len(dates) or dates[i0] != d0:
            continue
        sector = sector_of.get(ev.ticker)
        etf = etf_of_sector.get(sector)
        windows = [("pre_60", i0 - 1 - pre, i0 - 1)] + [(f"post_{h}", i0 - 1, i0 - 1 + h) for h in posts]
        for name, a, b in windows:
            r = window_return(cols[ev.ticker], a, b) if ev.ticker in cols else np.nan
            rm = window_return(cols[benchmark], a, b) if benchmark in cols else np.nan
            rs = window_return(cols[etf], a, b) if etf in cols else np.nan
            rows.append({
                "event_id": ev.event_id, "ticker": ev.ticker, "event_date": ev.event_date,
                "window": name,
                "start_date": str(dates[a]) if 0 <= a < len(dates) else None,
                "end_date": str(dates[b]) if 0 <= b < len(dates) else None,
                "ret_raw": r, "ret_excess_spy": r - rm, "ret_excess_sector": r - rs,
                "sector_etf": etf,
                "price_source": f"{ev.ticker}:{srcs.get(ev.ticker)}|{benchmark}:{srcs.get(benchmark)}|{etf}:{srcs.get(etf)}",
            })
    return pd.DataFrame(rows)
