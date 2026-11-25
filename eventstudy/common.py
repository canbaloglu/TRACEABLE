"""Config, paths, logging and database helpers."""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
log = logging.getLogger("event_study")


class PITViolation(RuntimeError):
    """Raised when a value filed after the event moment would be used."""


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=getattr(logging, level), format="%(asctime)s %(levelname)s %(message)s")


def load_config(path: str | os.PathLike | None = None) -> dict:
    p = Path(path) if path else ROOT / "config" / "event_study.yaml"
    cfg = yaml.safe_load(p.read_text(encoding="utf-8"))
    cfg["_root"] = str(p.resolve().parent.parent)
    ua = os.environ.get("SEC_USER_AGENT")
    if ua:
        cfg["sec"]["user_agent"] = ua
    return cfg


def path(cfg: dict, key: str) -> Path:
    p = Path(cfg["paths"][key])
    return p if p.is_absolute() else Path(cfg["_root"]) / p


def load_yaml(p: Path) -> dict:
    return yaml.safe_load(Path(p).read_text(encoding="utf-8"))


def connect(p: Path) -> sqlite3.Connection:
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(p)
    con.execute("PRAGMA journal_mode=WAL")
    return con


def write_table(con: sqlite3.Connection, name: str, df: pd.DataFrame) -> None:
    """Derived tables in event_study.sqlite are rebuilt deterministically."""
    df.to_sql(name, con, if_exists="replace", index=False)
    con.commit()


def read_table(con: sqlite3.Connection, name: str) -> pd.DataFrame:
    return pd.read_sql_query(f"SELECT * FROM {name}", con)


def frame_hash(df: pd.DataFrame) -> str:
    """Order-independent content hash of a table (used by reproducibility tests)."""
    d = df.copy()
    d = d.reindex(sorted(d.columns), axis=1)
    d = d.sort_values(list(d.columns), kind="mergesort").reset_index(drop=True)
    payload = d.to_csv(index=False, float_format="%.12g", na_rep="NA")
    return hashlib.sha256(payload.encode()).hexdigest()


def dumps(o) -> str:
    return json.dumps(o, sort_keys=True, default=str)
