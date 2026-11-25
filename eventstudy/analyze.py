"""Rank-correlation (Spearman IC) tests, cluster bootstrap CIs, BH-FDR, classification.

Lagging test ("ardıl") : metric vs pre_60 return  (did the price move before the release?)
Leading test ("öncül") : metric vs post_{1,5,20,60} returns (does the metric anticipate?)

Uncertainty: events of one company are not independent, so the bootstrap
resamples companies (clusters) with replacement; this is implemented exactly as
a weighted Spearman correlation (weight = how often the event's company was drawn).
p-values for BH use the cluster-bootstrap standard error (z = rho / se_boot);
the i.i.d. Spearman p-value is stored alongside for reference.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

VARIANTS = ["value", "yoy_change", "value_rel_sector"]
RET_TYPES = ["ret_raw", "ret_excess_spy", "ret_excess_sector"]


def _group_ranks(v: np.ndarray, W: np.ndarray) -> np.ndarray:
    """Average ranks of v in the dataset where row-b item i is replicated W[b,i] times."""
    order = np.argsort(v, kind="mergesort")
    vs = v[order]
    starts = np.r_[0, np.flatnonzero(np.diff(vs)) + 1]
    gid = np.repeat(np.arange(len(starts)), np.diff(np.r_[starts, len(vs)]))
    Ws = W[:, order]
    gtot = np.add.reduceat(Ws, starts, axis=1)
    before = np.cumsum(gtot, axis=1) - gtot
    rank_g = before + (gtot + 1.0) / 2.0
    out = np.empty_like(Ws, dtype=float)
    out[:, order] = rank_g[:, gid]
    return out


def weighted_spearman(x: np.ndarray, y: np.ndarray, W: np.ndarray) -> np.ndarray:
    rx, ry = _group_ranks(x, W), _group_ranks(y, W)
    sw = W.sum(axis=1, keepdims=True)
    mx = (W * rx).sum(1, keepdims=True) / sw
    my = (W * ry).sum(1, keepdims=True) / sw
    cov = (W * (rx - mx) * (ry - my)).sum(1)
    vx = (W * (rx - mx) ** 2).sum(1)
    vy = (W * (ry - my) ** 2).sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return cov / np.sqrt(vx * vy)


def ic_test(x, y, clusters, reps: int, ci: float, rng: np.random.Generator) -> dict:
    m = ~(np.isnan(x) | np.isnan(y))
    x, y, cl = x[m], y[m], clusters[m]
    n = len(x)
    res = {"n_events": n, "n_companies": int(len(np.unique(cl))) if n else 0}
    if n < 3 or np.unique(x).size < 2 or np.unique(y).size < 2:
        return {**res, "rho": np.nan, "p_iid": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                "se_boot": np.nan, "p_value": np.nan}
    rho, p_iid = stats.spearmanr(x, y)
    uc, cidx = np.unique(cl, return_inverse=True)
    draws = rng.integers(0, len(uc), size=(reps, len(uc)))
    counts = np.zeros((reps, len(uc)))
    np.add.at(counts, (np.repeat(np.arange(reps), len(uc)), draws.ravel()), 1.0)
    W = counts[:, cidx]
    boots = weighted_spearman(x, y, W)
    boots = boots[np.isfinite(boots)]
    a = (1 - ci) / 2
    se = float(np.std(boots, ddof=1)) if len(boots) > 1 else np.nan
    p = float(2 * stats.norm.sf(abs(rho) / se)) if se and se > 0 else np.nan
    return {**res, "rho": float(rho), "p_iid": float(p_iid),
            "ci_low": float(np.quantile(boots, a)), "ci_high": float(np.quantile(boots, 1 - a)),
            "se_boot": se, "p_value": p}


def bh(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (NaN kept)."""
    p = np.asarray(p, dtype=float)
    out = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    pv = p[ok]
    if pv.size == 0:
        return out
    order = np.argsort(pv)
    ranked = pv[order] * pv.size / (np.arange(pv.size) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    res = np.empty_like(pv)
    res[order] = np.minimum(q, 1.0)
    out[ok] = res
    return out


def build_dataset(metrics: pd.DataFrame, returns: pd.DataFrame, events: pd.DataFrame, sector_of: dict) -> pd.DataFrame:
    long = metrics.melt(id_vars=["event_id", "ticker", "pit_mode", "metric"], value_vars=VARIANTS,
                        var_name="variant", value_name="x")
    r = returns.melt(id_vars=["event_id", "window"], value_vars=RET_TYPES, var_name="ret_type", value_name="y")
    d = long.merge(r, on="event_id", how="inner")
    ev = events.set_index("event_id")
    d["year"] = pd.to_datetime(d["event_id"].map(ev["event_date"])).dt.year
    d["sector"] = d["ticker"].map(sector_of)
    return d


def run_ic(d: pd.DataFrame, cfg_an: dict) -> pd.DataFrame:
    reps, ci = int(cfg_an["bootstrap_reps"]), float(cfg_an["bootstrap_ci"])
    rows = []
    groupings = [("all", None), ("year", "year"), ("sector", "sector")]
    d = d.sort_values(["pit_mode", "metric", "variant", "ret_type", "window", "event_id"], kind="mergesort")
    for (mode, metric, variant, rtype, window), g in d.groupby(["pit_mode", "metric", "variant", "ret_type", "window"], sort=True):
        for gtype, col in groupings:
            parts = [("ALL", g)] if col is None else list(g.groupby(col, sort=True))
            for gval, gg in parts:
                key = f"{mode}|{metric}|{variant}|{rtype}|{window}|{gtype}|{gval}"
                rng = np.random.default_rng([int(cfg_an["seed"]), abs(hash_key(key))])
                res = ic_test(gg["x"].to_numpy(float), gg["y"].to_numpy(float), gg["ticker"].to_numpy(),
                              reps, ci, rng)
                rows.append({"pit_mode": mode, "metric": metric, "variant": variant, "ret_type": rtype,
                             "window": window, "group_type": gtype, "group": str(gval), **res})
    ic = pd.DataFrame(rows)
    fam = ["pit_mode", "ret_type", "group_type", "group"]
    ic["q_value_bh"] = ic.groupby(fam, group_keys=False)["p_value"].transform(lambda s: pd.Series(bh(s.to_numpy()), index=s.index))
    ic["test"] = np.where(ic["window"] == "pre_60", "lagging(pre)", "leading(post)")
    return ic


def hash_key(key: str) -> int:
    """Deterministic (process-independent) 32-bit hash for per-test RNG streams."""
    import zlib
    return zlib.crc32(key.encode())


def significant(row, alpha) -> bool:
    return (row["q_value_bh"] < alpha) and (np.sign(row["ci_low"]) == np.sign(row["ci_high"])) and row["ci_low"] != 0


def classify(ic: pd.DataFrame, mode: str, rtype: str, alpha: float) -> pd.DataFrame:
    a = ic[(ic["group_type"] == "all") & (ic["pit_mode"] == mode) & (ic["ret_type"] == rtype)].copy()
    a["sig"] = a.apply(lambda r: bool(significant(r, alpha)) if pd.notna(r["q_value_bh"]) else False, axis=1)
    rows = []
    for (metric, variant), g in a.groupby(["metric", "variant"], sort=True):
        pre = g[g["window"] == "pre_60"]
        post = g[g["window"] != "pre_60"]
        lag = bool(pre["sig"].any())
        lead = bool(post["sig"].any())
        label = "ikisi (both)" if (lag and lead) else "ardıl (lagging)" if lag else "öncül (leading)" if lead else "belirsiz (inconclusive)"
        best_post = post.loc[post["rho"].abs().idxmax()] if post["rho"].notna().any() else None
        p0 = pre.iloc[0] if len(pre) else None
        rows.append({
            "metric": metric, "variant": variant, "classification": label,
            "pre60_rho": p0["rho"] if p0 is not None else np.nan,
            "pre60_ci_low": p0["ci_low"] if p0 is not None else np.nan,
            "pre60_ci_high": p0["ci_high"] if p0 is not None else np.nan,
            "pre60_q": p0["q_value_bh"] if p0 is not None else np.nan,
            "pre60_n": p0["n_events"] if p0 is not None else 0,
            "best_post_window": best_post["window"] if best_post is not None else None,
            "best_post_rho": best_post["rho"] if best_post is not None else np.nan,
            "best_post_ci_low": best_post["ci_low"] if best_post is not None else np.nan,
            "best_post_ci_high": best_post["ci_high"] if best_post is not None else np.nan,
            "best_post_q": best_post["q_value_bh"] if best_post is not None else np.nan,
            "best_post_n": best_post["n_events"] if best_post is not None else 0,
            "sig_post_windows": ",".join(post.loc[post["sig"], "window"]),
        })
    return pd.DataFrame(rows)
