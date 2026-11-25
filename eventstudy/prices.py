"""Daily adjusted closes -> data_pit/prices/<TICKER>.parquet (incremental).

Columns: date, adj_close, source, retrieved_at.
Adjusted series get re-based by the vendor after every dividend/split; on an
incremental update the overlap is compared with what is stored and, if the
vendor re-based the history, the full history is re-downloaded (otherwise the
spliced series would contain an artificial jump).
"""
from __future__ import annotations

import datetime as dt
import io
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from .common import log, path

OVERLAP_DAYS = 10  # calendar days re-fetched to verify consistency of stored history


def vendor_symbol(ticker: str, source: str) -> str:
    if source == "yfinance":
        return ticker.replace(".", "-")
    if source == "stooq":
        return ticker.replace(".", "-").lower() + ".us"
    raise ValueError(source)


def fetch_yfinance(tickers: list[str], start: str) -> dict[str, pd.DataFrame]:
    import yfinance as yf
    syms = {vendor_symbol(t, "yfinance"): t for t in tickers}
    raw = yf.download(list(syms), start=start, auto_adjust=True, progress=False,
                      group_by="ticker", threads=True)
    out = {}
    for sym, t in syms.items():
        try:
            s = raw[sym]["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw["Close"]
        except KeyError:
            continue
        s = s.dropna()
        if s.empty:
            continue
        out[t] = pd.DataFrame({"date": pd.to_datetime(s.index).tz_localize(None).normalize(),
                               "adj_close": s.values.astype(float)})
    return out


def fetch_stooq(ticker: str, start: str) -> pd.DataFrame | None:
    url = f"https://stooq.com/q/d/l/?s={vendor_symbol(ticker, 'stooq')}&d1={start.replace('-', '')}&i=d"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        if "Close" not in df:
            return None
        return pd.DataFrame({"date": pd.to_datetime(df["Date"]), "adj_close": df["Close"].astype(float)})
    except Exception as e:  # noqa: BLE001 - fallback source, failures are logged
        log.warning("stooq failed for %s: %s", ticker, e)
        return None


def price_file(cfg: dict, ticker: str) -> Path:
    return path(cfg, "prices_dir") / f"{ticker.replace('.', '-')}.parquet"


def read_prices(cfg: dict, ticker: str) -> pd.DataFrame | None:
    p = price_file(cfg, ticker)
    return pd.read_parquet(p) if p.exists() else None


def update_prices(cfg: dict, tickers: list[str], full: bool = False) -> pd.DataFrame:
    start_all = (pd.Timestamp(cfg["start_date"]) - pd.Timedelta(days=cfg["price_history_buffer_days"])).strftime("%Y-%m-%d")
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    path(cfg, "prices_dir").mkdir(parents=True, exist_ok=True)
    existing = {t: (None if full else read_prices(cfg, t)) for t in tickers}
    # group by fetch start so yfinance can batch
    starts = {}
    for t, df in existing.items():
        if df is None or df.empty or df["date"].min() > pd.Timestamp(start_all):
            starts[t] = start_all
        else:
            starts[t] = (df["date"].max() - pd.Timedelta(days=OVERLAP_DAYS)).strftime("%Y-%m-%d")
    status = []
    by_start: dict[str, list[str]] = {}
    for t, s in starts.items():
        by_start.setdefault(s, []).append(t)
    fetched: dict[str, tuple[pd.DataFrame, str]] = {}
    for s, ts in by_start.items():
        for i in range(0, len(ts), 50):
            chunk = ts[i:i + 50]
            got = fetch_yfinance(chunk, s)
            for t in chunk:
                if t in got:
                    fetched[t] = (got[t], "yfinance(auto_adjust=True)")
                else:
                    st = fetch_stooq(t, s)
                    if st is not None and not st.empty:
                        fetched[t] = (st, "stooq")
    rebase = []
    for t in tickers:
        if t not in fetched:
            status.append({"ticker": t, "status": "no data from any source", "rows": 0})
            continue
        new, src = fetched[t]
        new = new.assign(source=src, retrieved_at=now)
        old = existing.get(t)
        if old is not None and not old.empty and starts[t] != start_all:
            ov = old.merge(new, on="date", suffixes=("_o", "_n"))
            same_src = (ov["source_o"] == ov["source_n"]).all()
            consistent = same_src and len(ov) > 0 and np.allclose(ov["adj_close_o"], ov["adj_close_n"], rtol=1e-6)
            if not consistent:
                rebase.append(t)
                continue
            new = pd.concat([old[old["date"] < new["date"].min()], new], ignore_index=True)
        new = new.drop_duplicates("date", keep="last").sort_values("date").reset_index(drop=True)
        new.to_parquet(price_file(cfg, t), index=False)
        status.append({"ticker": t, "status": f"ok ({src})", "rows": len(new),
                       "first": new["date"].min().date(), "last": new["date"].max().date()})
    if rebase:
        log.info("vendor re-based adjusted history for %d tickers -> full refresh", len(rebase))
        for t in rebase:
            if price_file(cfg, t).exists():
                price_file(cfg, t).unlink()
        status = [s for s in status if s["ticker"] not in rebase] + update_prices(cfg, rebase, full=True).to_dict("records")
    return pd.DataFrame(status)


def load_panel(cfg: dict, tickers: list[str]) -> tuple[pd.DataFrame, dict[str, str]]:
    """Wide adj_close panel (index = date) and per-ticker source label."""
    cols, srcs = {}, {}
    for t in tickers:
        df = read_prices(cfg, t)
        if df is None:
            continue
        cols[t] = df.set_index("date")["adj_close"]
        srcs[t] = ",".join(sorted(df["source"].unique()))
    return pd.DataFrame(cols).sort_index(), srcs


def trading_calendar(cfg: dict) -> np.ndarray:
    spy = read_prices(cfg, cfg["prices"]["benchmark"])
    if spy is None:
        raise RuntimeError("benchmark prices missing: run `event_study.py prices` first")
    return np.array(sorted(spy["date"].dt.normalize().unique()), dtype="datetime64[D]")
