# Event study (S&P 100, 8-K Item 2.02) — usage

```
pip install -r requirements.txt
set SEC_USER_AGENT=Your Name your@email      # Windows (bash: export SEC_USER_AGENT=...)
python event_study.py universe   # config/event_universe.yaml (GICS from Wikipedia, Banks excluded)
python event_study.py edgar      # companyfacts -> data_fundamentals/edgar.sqlite (append-only)
                                 # submissions  -> event_study.sqlite:filings
python event_study.py prices     # data_pit/prices/*.parquet (incremental; --full to rebuild)
python event_study.py events     # events, event_log
python event_study.py metrics    # metrics, sector_stats, missing_fields  (exit 1 on PIT violation)
python event_study.py returns    # returns
python event_study.py analyze    # ic_results, classification
python event_study.py report     # docs/event_study_report.md
python -m pytest -q tests        # 16:00 rule, look-ahead, append-only, hash reproducibility
```

Configuration: `config/event_study.yaml` (`start_date`, PIT modes, bootstrap, FDR α).
Field/tag definitions: `config/edgar_fields.yaml`.

## Integration notes for `ai_market_agent`

This branch was built in a fresh repository: the original `ai_market_agent`
collector, `edgar_fields.yaml`, `options_universe.yaml` and `edgar.sqlite`
were not available. Equivalents were created at the same relative paths:

* `config/options_universe.yaml` — S&P 100 from Wikipedia (key `sp100`); replace with the project file.
* `config/edgar_fields.yaml` — AI-derived us-gaap tag lists; replace/merge with the project file
  (format: `fields.<name>.{type, unit, tags[]}`).
* `eventstudy/edgar.py::collect_companyfacts` — collector writing table `facts`
  (append-only via `INSERT OR IGNORE` + UPDATE/DELETE triggers). If the project's
  `edgar.sqlite` has a different schema, only `edgar.load_facts` needs adapting
  (it must return `cik, tag, unit, start, end, val, accn, form, filed`).
* All new tables go to `data_fundamentals/event_study.sqlite`.
