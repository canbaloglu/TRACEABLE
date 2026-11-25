"""Minimal SEC EDGAR HTTP client: User-Agent required, rate-limited (< 10 req/s)."""
from __future__ import annotations

import gzip
import json
import threading
import time
from pathlib import Path

import requests

from .common import log


class SECClient:
    def __init__(self, user_agent: str, max_rps: float = 8, cache_dir: Path | None = None):
        if not user_agent or "@" not in user_agent:
            raise ValueError("SEC requires a User-Agent with contact e-mail (set SEC_USER_AGENT)")
        if max_rps > 10:
            raise ValueError("SEC fair-access limit is 10 requests/second")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": user_agent, "Accept-Encoding": "gzip, deflate"})
        self.min_interval = 1.0 / max_rps
        self._last = 0.0
        self._lock = threading.Lock()
        self.cache_dir = cache_dir

    def _wait(self):
        with self._lock:
            dt = time.monotonic() - self._last
            if dt < self.min_interval:
                time.sleep(self.min_interval - dt)
            self._last = time.monotonic()

    def get_json(self, url: str, cache_name: str | None = None, refresh: bool = True) -> dict:
        cpath = self.cache_dir / f"{cache_name}.json.gz" if (self.cache_dir and cache_name) else None
        if cpath and cpath.exists() and not refresh:
            with gzip.open(cpath, "rt", encoding="utf-8") as f:
                return json.load(f)
        for attempt in range(5):
            self._wait()
            r = self.s.get(url, timeout=60)
            if r.status_code == 200:
                data = r.json()
                if cpath:
                    cpath.parent.mkdir(parents=True, exist_ok=True)
                    with gzip.open(cpath, "wt", encoding="utf-8") as f:
                        json.dump(data, f)
                return data
            if r.status_code == 404:
                raise FileNotFoundError(url)
            wait = 2 ** attempt
            log.warning("SEC %s -> HTTP %s, retry in %ss", url, r.status_code, wait)
            time.sleep(wait)
        raise RuntimeError(f"SEC request failed: {url}")
