"""docs/event_study_report.md"""
from __future__ import annotations

import datetime as dt

import numpy as np
import pandas as pd

from . import analyze as an
from .common import connect, frame_hash, load_yaml, path, read_table
from .metrics import METRICS
from .universe import load_universe

VARIANT_TR = {"value": "değer", "yoy_change": "YoY değişim", "value_rel_sector": "sektör-göreli (PIT)"}


def _f(x, nd=3):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def _ci(r, lo, hi):
    return f"{_f(r)} [{_f(lo)}, {_f(hi)}]"


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_(yok)_\n"
    cols = list(df.columns)
    out = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in df.itertuples(index=False):
        out.append("| " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else str(v) for v in r) + " |")
    return "\n".join(out) + "\n"


def top_list(ic, mode, rtype, alpha, lead: bool, k=5):
    a = ic[(ic["group_type"] == "all") & (ic["pit_mode"] == mode) & (ic["ret_type"] == rtype)].copy()
    a = a[(a["window"] != "pre_60") if lead else (a["window"] == "pre_60")]
    a = a[a["rho"].notna()]
    a["sig"] = a.apply(lambda r: bool(an.significant(r, alpha)), axis=1)
    a["abs"] = a["rho"].abs()
    a = a.sort_values(["sig", "abs"], ascending=[False, False])
    a = a.drop_duplicates(["metric", "variant"]).head(k)
    return pd.DataFrame({
        "metric": a["metric"], "variant": a["variant"].map(VARIANT_TR), "ufuk": a["window"],
        "Spearman ρ [95% CI]": [_ci(r, l, h) for r, l, h in zip(a["rho"], a["ci_low"], a["ci_high"])],
        "BH q": a["q_value_bh"].map(lambda x: _f(x, 4)), "olay": a["n_events"], "şirket": a["n_companies"],
        "anlamlı": np.where(a["sig"], "evet", "hayır"),
    })


def write_report(cfg: dict) -> str:
    uni = load_universe(cfg)
    con = connect(path(cfg, "event_db"))
    T = {n: read_table(con, n) for n in ["events", "event_log", "metrics", "returns", "ic_results",
                                         "classification", "sector_stats", "missing_fields", "price_status"]}
    con.close()
    ev, ic, cls, m = T["events"], T["ic_results"], T["classification"], T["metrics"]
    mode = cfg["pit"]["primary_mode"]
    rtype = "ret_" + cfg["analysis"]["classification_return"].removeprefix("ret_")
    alpha = float(cfg["analysis"]["fdr_alpha"])
    sector_of = {c["ticker"]: c["gics_sector"] for c in uni["companies"]}
    ev["year"] = pd.to_datetime(ev["event_date"]).dt.year.astype("Int64")
    ev["sector"] = ev["ticker"].map(sector_of)
    L = []
    w = L.append
    w("# Olay Analizi — S&P 100 bilanço açıklamaları (8-K Item 2.02)\n")
    w(f"_Üretildi: {dt.date.today().isoformat()} · Başlangıç: {cfg['start_date']} · "
      f"Birincil PIT modu: `{mode}` · Sınıflama getirisi: `{rtype}` · BH-FDR α = {alpha}_\n")
    w("> **Hayatta kalma yanlılığı uyarısı:** Evren bugünkü S&P 100 listesidir ve tüm geçmişe "
      "uygulanmıştır. Endeksten çıkmış şirketler yok, sonradan girenler (ör. PLTR, UBER, GEV, SNDK) var. "
      "Sonuçlar bu yanlılığı içerir.\n")
    w("> **Point-in-time:** Her olayın bilgi kümesi = 8-K kabul anından önce kabul edilmiş tüm XBRL "
      "değerleri. `release_proxy` modunda buna açıklanan dönemin rakamları eklenir; bu rakamlar 8-K ekinde "
      "XBRL'siz yayımlandığı için bağlı 10-Q/10-K XBRL değerleri vekil olarak kullanılır (yalnız o tek "
      "dosyalama; sonraki revizyonlar kullanılmaz). `strict` modunda açıklanan çeyrek görünmez, metrik "
      "bir önceki dönemi anlatır — sağlamlık kontrolü olarak raporlanır. Kullanılan her değer kabul "
      "zamanına göre yeniden doğrulanır; ihlalde `metrics` komutu çıkış kodu 1 ile durur.\n")

    # ---------------------------------------------------------------- counts
    w("## 1. Olay sayıları\n")
    matched = ev[ev["match_status"] == "matched"]
    w(f"- 8-K Item 2.02 olayı: **{len(ev)}** · 10-Q/10-K'ya bağlanan: **{len(matched)}** · "
      f"eşleşmeyen: **{len(ev) - len(matched)}**\n")
    w(f"- Evren: {len(uni['companies'])} şirket (hariç: {len(uni['excluded'])}); olaylı şirket: "
      f"{ev['ticker'].nunique()}\n")
    w(f"- 16:00 kuralı: " + ", ".join(f"{k}: {v}" for k, v in ev["day_rule"].value_counts().items()) + "\n")
    nm = m[m["pit_mode"] == mode]
    w(f"- Metrik satırı ({mode}): {nm['value'].notna().sum()} dolu / {len(nm)}\n")
    by_year = matched.groupby("year").size().rename("bağlı olay").to_frame()
    by_year["tüm 2.02"] = ev.groupby("year").size()
    w("\n**Yıllara göre**\n\n" + md_table(by_year.reset_index().rename(columns={"year": "yıl"})))
    by_sec = matched.groupby("sector").agg(olay=("event_id", "count"), şirket=("ticker", "nunique")).reset_index()
    by_sec["ETF"] = by_sec["sector"].map(cfg["prices"]["sector_etfs"])
    w("\n**GICS sektörlerine göre (bağlı olaylar)**\n\n" + md_table(by_sec.rename(columns={"sector": "GICS sektör"})))

    # ---------------------------------------------------------------- classification
    w("\n## 2. Metrik sınıflaması\n")
    w("Ardıl testi: metrik ↔ olay öncesi 60 işlem günü getirisi. Öncül testi: metrik ↔ olay sonrası "
      "1/5/20/60 gün getirisi (`post_1` = açıklama tepki günü). Anlamlı = BH düzeltilmiş q < α **ve** "
      "firma-kümeli bootstrap %95 güven aralığı 0'ı içermiyor. ρ = Spearman sıra korelasyonu.\n")
    w(f"\n### 2.1 Birincil sonuç (`{mode}`, `{rtype}`, tüm evren)\n")
    p = cls[(cls["pit_mode"] == mode) & (cls["ret_type"] == rtype)].copy()
    rob = {}
    for (md, rt), g in cls.groupby(["pit_mode", "ret_type"]):
        rob[(md, rt)] = g.set_index(["metric", "variant"])["classification"]
    tab = pd.DataFrame({
        "metrik": p["metric"], "varyant": p["variant"].map(VARIANT_TR), "sınıf": p["classification"],
        "öncesi-60 ρ [CI]": [_ci(r, l, h) for r, l, h in zip(p["pre60_rho"], p["pre60_ci_low"], p["pre60_ci_high"])],
        "q": p["pre60_q"].map(lambda x: _f(x, 3)), "n": p["pre60_n"],
        "en güçlü sonrası": p["best_post_window"],
        "sonrası ρ [CI]": [_ci(r, l, h) for r, l, h in zip(p["best_post_rho"], p["best_post_ci_low"], p["best_post_ci_high"])],
        "q ": p["best_post_q"].map(lambda x: _f(x, 3)), "n ": p["best_post_n"],
        "anlamlı sonrası ufuklar": p["sig_post_windows"],
    })
    w(md_table(tab))
    w("\n### 2.2 Sağlamlık: farklı getiri tanımları ve strict PIT\n")
    keys = list(zip(p["metric"], p["variant"]))
    rt_rows = []
    for k in keys:
        row = {"metrik": k[0], "varyant": VARIANT_TR[k[1]]}
        for (md, rt), s in sorted(rob.items()):
            row[f"{md}/{rt.replace('ret_', '')}"] = s.get(k, "")
        rt_rows.append(row)
    w(md_table(pd.DataFrame(rt_rows)))

    w("\n## 3. En güçlü 5 öncül ve 5 ardıl metrik\n")
    w(f"(`{mode}`, `{rtype}`; önce anlamlı olanlar, sonra |ρ| büyüklüğü; her metrik×varyant bir kez)\n")
    w("\n**Öncül (metrik ↔ sonrası getiri)**\n\n" + md_table(top_list(ic, mode, rtype, alpha, True)))
    w("\n**Ardıl (metrik ↔ öncesi-60 getiri)**\n\n" + md_table(top_list(ic, mode, rtype, alpha, False)))

    # ---------------------------------------------------------------- by year / sector ICs
    w("\n## 4. Yıllara ve sektörlere göre IC (değer varyantı)\n")
    sub = ic[(ic["pit_mode"] == mode) & (ic["ret_type"] == rtype) & (ic["variant"] == "value")]
    for gtype, title in [("year", "Yıl"), ("sector", "GICS sektör")]:
        for window in ["pre_60", "post_20"]:
            s = sub[(sub["group_type"] == gtype) & (sub["window"] == window)]
            pv = s.pivot_table(index="group", columns="metric", values="rho", aggfunc="first").round(2)
            nn = s.groupby("group")["n_events"].max()
            pv.insert(0, "n(maks)", nn)
            w(f"\n**{title} · {window} · Spearman ρ** (BH ile anlamlılar `ic_results` tablosunda)\n\n")
            w(md_table(pv.reset_index().rename(columns={"group": title})))

    # ---------------------------------------------------------------- sector stats
    w("\n## 5. Sektör özetleri (metrik medyanları, tüm yıllar)\n")
    ss = m[(m["pit_mode"] == mode)].groupby(["gics_sector", "metric"])["value"].median().unstack().round(3)
    ss.insert(0, "olay", m[(m["pit_mode"] == mode)].groupby("gics_sector")["event_id"].nunique())
    w(md_table(ss.reset_index().rename(columns={"gics_sector": "GICS sektör"})))
    w("\nYıl × sektör ortalama/medyanları `sector_stats` tablosunda; her hissenin bu medyana göre farkı "
      "`metrics.value_minus_sector_year_median` (betimsel, aynı yılın sonraki olaylarını da içerir) ve "
      "testlerde kullanılan PIT versiyonu `metrics.value_rel_sector` (yalnız olaydan önceki 365 günde "
      "açıklanmış sektör eşlerinin son değerlerinin medyanı) sütunlarındadır.\n")
    last_year = int(m["year"].max())
    ly = T["sector_stats"][(T["sector_stats"]["pit_mode"] == mode) & (T["sector_stats"]["year"] == last_year)]
    pv = ly.pivot_table(index="gics_sector", columns="metric", values="median").round(3)
    w(f"\n**{last_year} yıl × sektör medyanları**\n\n" + md_table(pv.reset_index().rename(columns={"gics_sector": "GICS sektör"})))

    # ---------------------------------------------------------------- gaps
    w("\n## 6. Veri boşlukları\n")
    mf = T["missing_fields"]
    miss = mf[~mf["has_data"].astype(bool)]
    w(f"\n### 6.1 Eksik EDGAR alanları (şirket × alan, {len(miss)} boşluk)\n")
    w("Listelenen us-gaap etiketlerinin hiçbirinde değer yok. Standart dışı/şirkete özel etiketler için "
      "fallback yazılmadı (kural gereği yalnız listelendi).\n\n")
    agg = miss.groupby("field")["ticker"].apply(lambda s: ", ".join(sorted(s))).reset_index()
    agg.insert(1, "şirket sayısı", miss.groupby("field").size().values)
    w(md_table(agg.rename(columns={"field": "alan", "ticker": "şirketler"})))
    cov = nm.groupby("metric")["value"].apply(lambda s: f"{s.notna().mean():.0%}").reset_index()
    w("\n### 6.2 Metrik kapsama oranı (bağlı olaylar)\n\n" + md_table(cov.rename(columns={"value": "dolu"})))
    nomet = nm.groupby("ticker")["value"].apply(lambda s: s.notna().mean())
    low = nomet[nomet < 0.5].sort_values()
    w("\n**Metriklerinin yarısından azı hesaplanabilen şirketler:** " +
      (", ".join(f"{t} ({v:.0%})" for t, v in low.items()) or "yok") + "\n")
    w("\n### 6.3 Eşleşmeyen olaylar\n")
    lg = T["event_log"]
    w("Önceki ve sonraki 2.02 arasında bu olaya bağlanabilecek 10-Q/10-K yok: çoğunlukla ön-duyurular "
      "(ör. ABBV IPR&D, TSLA teslimat), yıllık rehberlik güncellemeleri ve 10-Q'su henüz dosyalanmamış son "
      "olaylar. Bu olaylar metrik ve testlere girmez.\n\n")
    cnt = lg.groupby("issue").size().reset_index(name="adet")
    w(md_table(cnt))
    per_t = lg[lg["issue"].str.startswith("no 10-Q")].groupby("ticker").size().sort_values(ascending=False)
    w("\nŞirket bazında: " + ", ".join(f"{t} ({n})" for t, n in per_t.items()) + "\n")
    w("\n<details><summary>Tüm eşleşmeyen olaylar</summary>\n\n" + md_table(lg) + "\n</details>\n")
    ps = T["price_status"]
    badp = ps[~ps["status"].str.startswith("ok")]
    w("\n### 6.4 Fiyat verisi\n")
    w(f"Kaynaklar: {', '.join(sorted(ps['status'].unique()))}. Eksik: " +
      (", ".join(badp["ticker"]) if len(badp) else "yok") + ". Stooq bu ortamdan erişilemedi; tüm seriler "
      "yfinance (auto_adjust=True) — kaynak her satırda `source`/`price_source` sütununda.\n")
    w("\n## 7. Hariç tutulan şirketler\n\n")
    exc = pd.DataFrame([{"ticker": c["ticker"], "şirket": c["name"], "GICS alt-endüstri": c["gics_sub_industry"],
                         "GICS endüstri": c["gics_industry"], "neden": c["exclusion_reason"]} for c in uni["excluded"]])
    w(md_table(exc))
    pr = pd.DataFrame(uni.get("problems", []))
    if len(pr):
        w("\nDiğer evren notları:\n\n" + md_table(pr))
    w("\n## 8. Yöntem notları\n")
    w("\n".join([
        "- Olay günü: kabul saati (New York) ≥ 16:00 → sonraki işlem günü; < 16:00 → aynı gün (işlem günü değilse sonraki). Takvim = SPY işlem günleri. Yarım gün kapanışları (13:00) için ayrı kural yok.",
        "- Getiriler: taban = olay gününden önceki kapanış. öncesi-60 = P[d0-1]/P[d0-61]-1; sonrası-h = P[d0-1+h]/P[d0-1]-1. Fazla getiri = hisse − SPY veya − sektör SPDR ETF'i (aynı pencere).",
        "- Çeyreklik akım değerleri: doğrudan 3 aylık XBRL değeri; yoksa YTD(t) − YTD(t−1 çeyrek) (aynı başlangıç tarihi). Q4 sulandırılmış EPS = FY − 9A farkıyla türetilir (yaklaşık).",
        "- YoY değişim = metrik(şimdi) − aynı metriğin 4 çeyrek önceki değeri (aynı bilgi kümesiyle).",
        "- Güven aralıkları: şirket düzeyinde küme bootstrap (aynı şirketin olayları bağımlı), "
        f"{cfg['analysis']['bootstrap_reps']} tekrar, sabit tohum. p = 2·(1−Φ(|ρ|/se_boot)); BH ailesi = (PIT modu, getiri türü, grup) içindeki tüm metrik×varyant×ufuk testleri.",
        "- Etiket kaynakları: metrik satırlarında `source` (kullanılan EDGAR us-gaap etiketleri) ve `input_accns`; getirilerde `price_source`; GICS sektör/alt-endüstri Wikipedia; GICS endüstri eşlemesi, öncül CIK eşlemesi (XOM, BLK) ve edgar_fields.yaml etiket listeleri **AI-derived** olarak işaretli.",
        "- Eşik: eşik değer kullanılmadı. Kullanılan sabitler takvimsel tanımlardır (çeyrek = 80–100 gün, yıl = 350–380 gün, 52/53 haftalık çeyrek sonu eşleştirme toleransı ±20 gün) ve BH-FDR α (konvansiyonel 0.05, config'de).",
    ]) + "\n")
    w(f"\n_Tekrar üretilebilirlik: ic_results sha256 = `{frame_hash(ic)[:16]}…`_\n")
    out = path(cfg, "report")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    return str(out)
