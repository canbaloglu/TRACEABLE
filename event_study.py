#!/usr/bin/env python
"""S&P 100 earnings event study.

Usage:
    python event_study.py universe   # S&P 100 + GICS (Wikipedia) -> config/event_universe.yaml
    python event_study.py edgar      # companyfacts -> edgar.sqlite (append-only), submissions -> filings
    python event_study.py prices     # incremental daily adjusted closes -> data_pit/prices/*.parquet
    python event_study.py events     # 8-K Item 2.02 events, 16:00 rule, link to 10-Q/10-K
    python event_study.py metrics    # point-in-time metrics (exit code 1 on PIT violation)
    python event_study.py returns    # pre/post window returns (raw, -SPY, -sector ETF)
    python event_study.py analyze    # Spearman IC, cluster bootstrap CI, BH-FDR, classification
    python event_study.py report     # docs/event_study_report.md
    python event_study.py all        # everything in order
"""
from __future__ import annotations

import argparse
import sys

from eventstudy.common import PITViolation, load_config, log, setup_logging

STEPS = ["universe", "edgar", "prices", "events", "metrics", "returns", "analyze", "report"]


def run(step: str, cfg: dict, args) -> None:
    from eventstudy import pipeline as pl
    from eventstudy import report

    if step == "universe":
        pl.step_universe(cfg)
    elif step == "edgar":
        pl.step_edgar(cfg)
    elif step == "prices":
        pl.step_prices(cfg, full=args.full)
    elif step == "events":
        pl.step_events(cfg)
    elif step == "metrics":
        pl.step_metrics(cfg)
    elif step == "returns":
        pl.step_returns(cfg)
    elif step == "analyze":
        pl.step_analyze(cfg)
    elif step == "report":
        report.write_report(cfg)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=STEPS + ["all"])
    ap.add_argument("--config", default=None)
    ap.add_argument("--full", action="store_true", help="prices: re-download full history")
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args(argv)
    setup_logging(args.log_level)
    cfg = load_config(args.config)
    try:
        for s in (STEPS if args.command == "all" else [args.command]):
            log.info("== %s ==", s)
            run(s, cfg, args)
    except PITViolation as e:
        log.error("POINT-IN-TIME VIOLATION: %s", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
