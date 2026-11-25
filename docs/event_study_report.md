# Olay Analizi — S&P 100 bilanço açıklamaları (8-K Item 2.02)

_Üretildi: 2026-11-25 · Başlangıç: 2021-01-01 · Birincil PIT modu: `release_proxy` · Sınıflama getirisi: `ret_excess_sector` · BH-FDR α = 0.05_

> **Hayatta kalma yanlılığı uyarısı:** Evren bugünkü S&P 100 listesidir ve tüm geçmişe uygulanmıştır. Endeksten çıkmış şirketler yok, sonradan girenler (ör. PLTR, UBER, GEV, SNDK) var. Sonuçlar bu yanlılığı içerir.

> **Point-in-time:** Her olayın bilgi kümesi = 8-K kabul anından önce kabul edilmiş tüm XBRL değerleri. `release_proxy` modunda buna açıklanan dönemin rakamları eklenir; bu rakamlar 8-K ekinde XBRL'siz yayımlandığı için bağlı 10-Q/10-K XBRL değerleri vekil olarak kullanılır (yalnız o tek dosyalama; sonraki revizyonlar kullanılmaz). `strict` modunda açıklanan çeyrek görünmez, metrik bir önceki dönemi anlatır — sağlamlık kontrolü olarak raporlanır. Kullanılan her değer kabul zamanına göre yeniden doğrulanır; ihlalde `metrics` komutu çıkış kodu 1 ile durur.

## 1. Olay sayıları

- 8-K Item 2.02 olayı: **2355** · 10-Q/10-K'ya bağlanan: **2232** · eşleşmeyen: **123**

- Evren: 95 şirket (hariç: 5); olaylı şirket: 95

- 16:00 kuralı: before_close->same_day: 1299, after_close->next_day: 1055, non_trading_day->next_day: 1

- Metrik satırı (release_proxy): 17501 dolu / 22320


**Yıllara göre**

| yıl | bağlı olay | tüm 2.02 |
|---|---|---|
| 2021 | 372 | 391 |
| 2022 | 371 | 400 |
| 2023 | 372 | 394 |
| 2024 | 374 | 392 |
| 2025 | 378 | 390 |
| 2026 | 365 | 387 |


**GICS sektörlerine göre (bağlı olaylar)**

| GICS sektör | olay | şirket | ETF |
|---|---|---|---|
| Communication Services | 192 | 8 | XLC |
| Consumer Discretionary | 191 | 8 | XLY |
| Consumer Staples | 190 | 8 | XLP |
| Energy | 72 | 3 | XLE |
| Financials | 239 | 10 | XLF |
| Health Care | 359 | 15 | XLV |
| Industrials | 320 | 14 | XLI |
| Information Technology | 549 | 24 | XLK |
| Materials | 24 | 1 | XLB |
| Real Estate | 24 | 1 | XLRE |
| Utilities | 72 | 3 | XLU |


## 2. Metrik sınıflaması

Ardıl testi: metrik ↔ olay öncesi 60 işlem günü getirisi. Öncül testi: metrik ↔ olay sonrası 1/5/20/60 gün getirisi (`post_1` = açıklama tepki günü). Anlamlı = BH düzeltilmiş q < α **ve** firma-kümeli bootstrap %95 güven aralığı 0'ı içermiyor. ρ = Spearman sıra korelasyonu.


### 2.1 Birincil sonuç (`release_proxy`, `ret_excess_sector`, tüm evren)

| metrik | varyant | sınıf | öncesi-60 ρ [CI] | q | n | en güçlü sonrası | sonrası ρ [CI] | q  | n  | anlamlı sonrası ufuklar |
|---|---|---|---|---|---|---|---|---|---|---|
| accrual_ratio | değer | belirsiz (inconclusive) | 0.012 [-0.035, 0.059] | 0.858 | 2153 | post_1 | -0.019 [-0.061, 0.023] | 0.675 | 2153 |  |
| accrual_ratio | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.003 [-0.040, 0.046] | 0.956 | 2099 | post_1 | -0.030 [-0.080, 0.012] | 0.509 | 2099 |  |
| accrual_ratio | YoY değişim | belirsiz (inconclusive) | 0.026 [-0.018, 0.070] | 0.568 | 2141 | post_60 | -0.040 [-0.083, 0.000] | 0.278 | 2060 |  |
| eps_growth | değer | ardıl (lagging) | 0.096 [0.059, 0.132] | 0.000 | 2129 | post_5 | 0.040 [0.001, 0.082] | 0.276 | 2128 |  |
| eps_growth | sektör-göreli (PIT) | ardıl (lagging) | 0.093 [0.050, 0.131] | 0.000 | 2072 | post_1 | 0.043 [0.001, 0.087] | 0.276 | 2073 |  |
| eps_growth | YoY değişim | belirsiz (inconclusive) | 0.041 [0.001, 0.084] | 0.276 | 2107 | post_20 | 0.015 [-0.025, 0.057] | 0.770 | 2069 |  |
| fcf_margin | değer | belirsiz (inconclusive) | 0.040 [-0.007, 0.089] | 0.359 | 2030 | post_5 | 0.050 [0.015, 0.087] | 0.165 | 2030 |  |
| fcf_margin | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.039 [-0.011, 0.088] | 0.376 | 1974 | post_5 | 0.056 [0.015, 0.095] | 0.165 | 1974 |  |
| fcf_margin | YoY değişim | belirsiz (inconclusive) | 0.040 [0.001, 0.079] | 0.276 | 2029 | post_5 | 0.063 [0.022, 0.109] | 0.165 | 2029 |  |
| gross_margin | değer | belirsiz (inconclusive) | -0.006 [-0.068, 0.062] | 0.956 | 1388 | post_1 | 0.044 [-0.010, 0.089] | 0.309 | 1390 |  |
| gross_margin | sektör-göreli (PIT) | belirsiz (inconclusive) | -0.001 [-0.061, 0.054] | 0.975 | 1379 | post_1 | 0.061 [0.009, 0.105] | 0.171 | 1381 |  |
| gross_margin | YoY değişim | belirsiz (inconclusive) | 0.060 [0.005, 0.113] | 0.276 | 1386 | post_60 | 0.046 [-0.010, 0.099] | 0.335 | 1333 |  |
| net_debt_ebitda | değer | belirsiz (inconclusive) | -0.076 [-0.134, -0.011] | 0.182 | 1022 | post_60 | -0.037 [-0.092, 0.024] | 0.529 | 986 |  |
| net_debt_ebitda | sektör-göreli (PIT) | belirsiz (inconclusive) | -0.033 [-0.099, 0.033] | 0.632 | 966 | post_1 | 0.045 [-0.007, 0.088] | 0.290 | 966 |  |
| net_debt_ebitda | YoY değişim | belirsiz (inconclusive) | -0.045 [-0.114, 0.029] | 0.518 | 988 | post_1 | 0.020 [-0.043, 0.089] | 0.805 | 988 |  |
| op_margin | değer | belirsiz (inconclusive) | 0.030 [-0.026, 0.082] | 0.600 | 1771 | post_20 | -0.005 [-0.044, 0.037] | 0.946 | 1741 |  |
| op_margin | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.051 [-0.009, 0.107] | 0.290 | 1715 | post_60 | 0.007 [-0.043, 0.056] | 0.913 | 1651 |  |
| op_margin | YoY değişim | belirsiz (inconclusive) | 0.038 [-0.010, 0.084] | 0.376 | 1770 | post_5 | 0.026 [-0.019, 0.071] | 0.600 | 1770 |  |
| rev_growth_q | değer | belirsiz (inconclusive) | 0.046 [0.002, 0.088] | 0.276 | 2139 | post_1 | 0.041 [0.003, 0.084] | 0.276 | 2141 |  |
| rev_growth_q | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.057 [0.015, 0.100] | 0.165 | 2082 | post_1 | 0.049 [0.010, 0.088] | 0.171 | 2084 |  |
| rev_growth_q | YoY değişim | belirsiz (inconclusive) | 0.016 [-0.020, 0.051] | 0.675 | 2129 | post_1 | 0.018 [-0.019, 0.056] | 0.632 | 2129 |  |
| rev_growth_ttm | değer | belirsiz (inconclusive) | 0.012 [-0.031, 0.054] | 0.819 | 2125 | post_60 | 0.023 [-0.017, 0.065] | 0.600 | 2044 |  |
| rev_growth_ttm | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.015 [-0.029, 0.059] | 0.770 | 2068 | post_60 | 0.033 [-0.001, 0.067] | 0.276 | 1989 |  |
| rev_growth_ttm | YoY değişim | belirsiz (inconclusive) | -0.007 [-0.047, 0.036] | 0.902 | 2117 | post_20 | -0.020 [-0.061, 0.020] | 0.632 | 2077 |  |
| rpo_growth | değer | belirsiz (inconclusive) | 0.011 [-0.064, 0.082] | 0.913 | 771 | post_60 | 0.061 [-0.016, 0.135] | 0.359 | 740 |  |
| rpo_growth | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.052 [-0.019, 0.120] | 0.424 | 727 | post_60 | 0.084 [0.015, 0.150] | 0.171 | 698 |  |
| rpo_growth | YoY değişim | belirsiz (inconclusive) | -0.020 [-0.094, 0.055] | 0.845 | 722 | post_60 | 0.046 [-0.049, 0.137] | 0.632 | 691 |  |
| wc_change | değer | belirsiz (inconclusive) | 0.049 [0.003, 0.102] | 0.276 | 1964 | post_1 | -0.053 [-0.095, -0.012] | 0.171 | 1964 |  |
| wc_change | sektör-göreli (PIT) | belirsiz (inconclusive) | 0.039 [-0.009, 0.084] | 0.359 | 1905 | post_5 | -0.051 [-0.101, -0.001] | 0.276 | 1903 |  |
| wc_change | YoY değişim | belirsiz (inconclusive) | 0.025 [-0.026, 0.075] | 0.654 | 1945 | post_20 | -0.025 [-0.069, 0.025] | 0.632 | 1907 |  |


### 2.2 Sağlamlık: farklı getiri tanımları ve strict PIT

| metrik | varyant | release_proxy/excess_sector | release_proxy/excess_spy | release_proxy/raw | strict/excess_sector | strict/excess_spy | strict/raw |
|---|---|---|---|---|---|---|---|
| accrual_ratio | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| accrual_ratio | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| accrual_ratio | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | öncül (leading) | belirsiz (inconclusive) | belirsiz (inconclusive) | öncül (leading) |
| eps_growth | değer | ardıl (lagging) | ardıl (lagging) | ardıl (lagging) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| eps_growth | sektör-göreli (PIT) | ardıl (lagging) | belirsiz (inconclusive) | ardıl (lagging) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| eps_growth | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | ardıl (lagging) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| fcf_margin | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | ikisi (both) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| fcf_margin | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | öncül (leading) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| fcf_margin | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | ikisi (both) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| gross_margin | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| gross_margin | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | öncül (leading) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| gross_margin | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | ardıl (lagging) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| net_debt_ebitda | değer | belirsiz (inconclusive) | ardıl (lagging) | ardıl (lagging) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| net_debt_ebitda | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| net_debt_ebitda | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| op_margin | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| op_margin | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| op_margin | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rev_growth_q | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rev_growth_q | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rev_growth_q | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | ardıl (lagging) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rev_growth_ttm | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | ardıl (lagging) |
| rev_growth_ttm | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rev_growth_ttm | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | öncül (leading) | belirsiz (inconclusive) | belirsiz (inconclusive) | ikisi (both) |
| rpo_growth | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rpo_growth | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| rpo_growth | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| wc_change | değer | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| wc_change | sektör-göreli (PIT) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |
| wc_change | YoY değişim | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) | belirsiz (inconclusive) |


## 3. En güçlü 5 öncül ve 5 ardıl metrik

(`release_proxy`, `ret_excess_sector`; önce anlamlı olanlar, sonra |ρ| büyüklüğü; her metrik×varyant bir kez)


**Öncül (metrik ↔ sonrası getiri)**

| metric | variant | ufuk | Spearman ρ [95% CI] | BH q | olay | şirket | anlamlı |
|---|---|---|---|---|---|---|---|
| rpo_growth | sektör-göreli (PIT) | post_60 | 0.084 [0.015, 0.150] | 0.1712 | 698 | 41 | hayır |
| fcf_margin | YoY değişim | post_5 | 0.063 [0.022, 0.109] | 0.1652 | 2029 | 90 | hayır |
| gross_margin | sektör-göreli (PIT) | post_1 | 0.061 [0.009, 0.105] | 0.1712 | 1381 | 63 | hayır |
| rpo_growth | değer | post_60 | 0.061 [-0.016, 0.135] | 0.3587 | 740 | 43 | hayır |
| fcf_margin | sektör-göreli (PIT) | post_5 | 0.056 [0.015, 0.095] | 0.1652 | 1974 | 88 | hayır |


**Ardıl (metrik ↔ öncesi-60 getiri)**

| metric | variant | ufuk | Spearman ρ [95% CI] | BH q | olay | şirket | anlamlı |
|---|---|---|---|---|---|---|---|
| eps_growth | değer | pre_60 | 0.096 [0.059, 0.132] | 0.0001 | 2129 | 92 | evet |
| eps_growth | sektör-göreli (PIT) | pre_60 | 0.093 [0.050, 0.131] | 0.0003 | 2072 | 90 | evet |
| net_debt_ebitda | değer | pre_60 | -0.076 [-0.134, -0.011] | 0.1821 | 1022 | 56 | hayır |
| gross_margin | YoY değişim | pre_60 | 0.060 [0.005, 0.113] | 0.2758 | 1386 | 63 | hayır |
| rev_growth_q | sektör-göreli (PIT) | pre_60 | 0.057 [0.015, 0.100] | 0.1652 | 2082 | 90 | hayır |


## 4. Yıllara ve sektörlere göre IC (değer varyantı)


**Yıl · pre_60 · Spearman ρ** (BH ile anlamlılar `ic_results` tablosunda)


| Yıl | n(maks) | accrual_ratio | eps_growth | fcf_margin | gross_margin | net_debt_ebitda | op_margin | rev_growth_q | rev_growth_ttm | rpo_growth | wc_change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 357 | 0.01 | 0.1 | 0.01 | -0.03 | -0.03 | 0.0 | 0.02 | -0.03 | 0.03 | 0.1 |
| 2022 | 358 | -0.01 | 0.13 | 0.04 | 0.06 | 0.21 | 0.12 | -0.11 | -0.2 | -0.08 | 0.04 |
| 2023 | 365 | -0.07 | 0.0 | 0.1 | 0.04 | -0.29 | 0.06 | 0.11 | 0.1 | 0.03 | -0.1 |
| 2024 | 359 | -0.04 | 0.17 | 0.06 | 0.04 | -0.16 | -0.01 | 0.15 | 0.1 | -0.0 | 0.04 |
| 2025 | 364 | 0.15 | 0.1 | 0.03 | -0.1 | -0.08 | 0.02 | 0.15 | 0.13 | 0.17 | 0.09 |
| 2026 | 350 | -0.02 | 0.1 | -0.01 | -0.04 | -0.06 | -0.01 | -0.0 | -0.06 | -0.05 | 0.11 |


**Yıl · post_20 · Spearman ρ** (BH ile anlamlılar `ic_results` tablosunda)


| Yıl | n(maks) | accrual_ratio | eps_growth | fcf_margin | gross_margin | net_debt_ebitda | op_margin | rev_growth_q | rev_growth_ttm | rpo_growth | wc_change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 357 | 0.07 | 0.02 | 0.01 | 0.05 | 0.15 | -0.01 | 0.04 | 0.03 | 0.07 | -0.06 |
| 2022 | 358 | -0.02 | -0.03 | 0.06 | 0.05 | 0.01 | 0.03 | -0.04 | -0.06 | 0.08 | -0.06 |
| 2023 | 365 | -0.18 | 0.06 | 0.07 | 0.12 | -0.13 | -0.07 | 0.14 | 0.11 | -0.05 | -0.06 |
| 2024 | 360 | 0.01 | 0.05 | 0.05 | 0.01 | -0.12 | 0.04 | 0.04 | 0.05 | 0.11 | 0.01 |
| 2025 | 365 | 0.07 | 0.02 | 0.04 | -0.02 | 0.05 | 0.02 | -0.06 | -0.06 | -0.03 | -0.04 |
| 2026 | 312 | 0.01 | 0.01 | -0.08 | -0.07 | 0.06 | -0.05 | -0.1 | -0.13 | -0.04 | -0.04 |


**GICS sektör · pre_60 · Spearman ρ** (BH ile anlamlılar `ic_results` tablosunda)


| GICS sektör | n(maks) | accrual_ratio | eps_growth | fcf_margin | gross_margin | net_debt_ebitda | op_margin | rev_growth_q | rev_growth_ttm | rpo_growth | wc_change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Communication Services | 192 | -0.03 | 0.05 | 0.08 | 0.0 | -0.1 | 0.1 | 0.13 | 0.07 | 0.12 | 0.02 |
| Consumer Discretionary | 191 | -0.15 | 0.0 | -0.02 | -0.06 | -0.05 | -0.1 | -0.01 | -0.03 | -0.02 | 0.03 |
| Consumer Staples | 183 | -0.07 | 0.19 | 0.13 | 0.08 | -0.14 | 0.09 | 0.03 | -0.04 |  | 0.01 |
| Energy | 72 | -0.06 | 0.17 | 0.36 | 0.04 |  |  | 0.08 | 0.13 |  | -0.1 |
| Financials | 239 | 0.04 | 0.17 | -0.02 |  | 0.13 | -0.0 | 0.03 | -0.08 | 0.44 | -0.01 |
| Health Care | 359 | 0.01 | 0.11 | 0.07 | 0.11 | -0.0 | 0.14 | 0.08 | 0.04 | -0.02 | -0.0 |
| Industrials | 319 | 0.06 | 0.12 | 0.07 | 0.01 | 0.08 | 0.06 | 0.01 | -0.04 | -0.14 | 0.06 |
| Information Technology | 546 | 0.04 | 0.1 | 0.03 | -0.07 | -0.02 | 0.04 | 0.06 | 0.04 | 0.04 | 0.1 |
| Materials | 24 | 0.18 | -0.11 | -0.31 |  | 0.08 | 0.19 | -0.05 | 0.0 | -0.1 | 0.15 |
| Real Estate | 24 | 0.02 | -0.15 | -0.04 |  | 0.17 | 0.06 | 0.1 | -0.03 |  | -0.33 |
| Utilities | 66 | -0.08 | 0.16 | -0.2 |  | 0.09 | 0.0 | 0.04 | 0.01 |  | -0.03 |


**GICS sektör · post_20 · Spearman ρ** (BH ile anlamlılar `ic_results` tablosunda)


| GICS sektör | n(maks) | accrual_ratio | eps_growth | fcf_margin | gross_margin | net_debt_ebitda | op_margin | rev_growth_q | rev_growth_ttm | rpo_growth | wc_change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Communication Services | 189 | -0.04 | -0.04 | 0.07 | -0.06 | 0.03 | -0.03 | -0.05 | -0.05 | 0.02 | -0.01 |
| Consumer Discretionary | 186 | 0.1 | 0.0 | 0.02 | 0.14 | 0.01 | 0.06 | -0.07 | -0.06 | 0.2 | 0.07 |
| Consumer Staples | 181 | -0.09 | 0.16 | 0.01 | 0.02 | -0.09 | 0.02 | 0.06 | 0.03 |  | 0.01 |
| Energy | 69 | -0.09 | 0.04 | -0.03 | 0.07 |  |  | 0.11 | 0.07 |  | -0.13 |
| Financials | 237 | 0.06 | 0.12 | 0.1 |  | 0.02 | 0.05 | -0.06 | -0.01 | 0.16 | -0.21 |
| Health Care | 351 | -0.06 | 0.01 | -0.0 | 0.11 | -0.0 | 0.07 | 0.1 | 0.08 | 0.09 | -0.04 |
| Industrials | 315 | -0.06 | 0.12 | 0.12 | 0.07 | 0.03 | 0.07 | 0.09 | 0.02 | -0.03 | -0.0 |
| Information Technology | 535 | -0.01 | -0.01 | 0.0 | -0.03 | 0.03 | -0.05 | 0.02 | 0.04 | -0.02 | -0.08 |
| Materials | 23 | -0.02 | 0.11 | 0.11 |  | -0.38 | -0.12 | -0.1 | 0.05 | -0.31 | -0.12 |
| Real Estate | 24 | 0.31 | 0.28 | -0.42 |  | 0.21 | -0.33 | 0.13 | 0.01 |  | 0.37 |
| Utilities | 66 | -0.07 | -0.25 | -0.08 |  | 0.03 | -0.19 | 0.01 | 0.03 |  | -0.08 |


## 5. Sektör özetleri (metrik medyanları, tüm yıllar)

| GICS sektör | olay | accrual_ratio | eps_growth | fcf_margin | gross_margin | net_debt_ebitda | op_margin | rev_growth_q | rev_growth_ttm | rpo_growth | wc_change |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Communication Services | 192 | -0.052 | 0.181 | 0.16 | 0.579 | 2.441 | 0.209 | 0.052 | 0.044 | 0.072 | -0.003 |
| Consumer Discretionary | 191 | -0.049 | 0.085 | 0.094 | 0.337 | 1.754 | 0.127 | 0.082 | 0.084 | 0.083 | 0.0 |
| Consumer Staples | 190 | -0.032 | 0.095 | 0.116 | 0.524 | 2.067 | 0.201 | 0.057 | 0.054 |  | -0.004 |
| Energy | 72 | -0.07 | 0.037 | 0.112 | 0.503 |  |  | 0.026 | 0.018 |  | 0.004 |
| Financials | 239 | -0.003 | 0.187 | 0.395 |  | 0.439 | 0.553 | 0.116 | 0.113 | 0.242 | -0.038 |
| Health Care | 359 | -0.033 | 0.086 | 0.208 | 0.689 | 2.692 | 0.194 | 0.068 | 0.068 | 0.0 | 0.005 |
| Industrials | 320 | -0.029 | 0.148 | 0.103 | 0.3 | 1.583 | 0.106 | 0.072 | 0.062 | 0.091 | -0.004 |
| Information Technology | 549 | -0.054 | 0.25 | 0.231 | 0.603 | 0.264 | 0.269 | 0.153 | 0.142 | 0.172 | 0.009 |
| Materials | 24 | -0.04 | 0.212 | 0.165 |  | 1.372 | 0.24 | 0.041 | 0.024 | 0.064 | 0.006 |
| Real Estate | 24 | -0.043 | 0.161 | 0.318 |  | 5.716 | 0.377 | 0.062 | 0.062 |  | -0.017 |
| Utilities | 72 | -0.032 | 0.068 | -0.081 | 0.928 | 6.001 | 0.255 | 0.075 | 0.059 |  | -0.008 |


Yıl × sektör ortalama/medyanları `sector_stats` tablosunda; her hissenin bu medyana göre farkı `metrics.value_minus_sector_year_median` (betimsel, aynı yılın sonraki olaylarını da içerir) ve testlerde kullanılan PIT versiyonu `metrics.value_rel_sector` (yalnız olaydan önceki 365 günde açıklanmış sektör eşlerinin son değerlerinin medyanı) sütunlarındadır.


**2026 yıl × sektör medyanları**

| GICS sektör | accrual_ratio | eps_growth | fcf_margin | gross_margin | net_debt_ebitda | op_margin | rev_growth_q | rev_growth_ttm | rpo_growth | wc_change |
|---|---|---|---|---|---|---|---|---|---|---|
| Communication Services | -0.051 | 0.0 | 0.164 | 0.607 | 2.378 | 0.222 | 0.076 | 0.084 | 0.1 | 0.014 |
| Consumer Discretionary | -0.067 | 0.048 | 0.094 | 0.33 | 2.116 | 0.117 | 0.057 | 0.058 | 0.01 | -0.003 |
| Consumer Staples | -0.029 | 0.081 | 0.143 | 0.542 | 2.035 | 0.208 | 0.064 | 0.057 |  | -0.005 |
| Energy | -0.075 | 0.483 | 0.132 | 0.539 |  |  | 0.159 | 0.084 |  | 0.01 |
| Financials | -0.0 | 0.249 | 0.337 |  | 0.42 | 0.588 | 0.152 | 0.16 | 0.143 | -0.052 |
| Health Care | -0.033 | 0.113 | 0.213 | 0.698 | 2.721 | 0.19 | 0.073 | 0.072 | 0.134 | 0.015 |
| Industrials | -0.028 | 0.159 | 0.137 | 0.275 | 1.649 | 0.114 | 0.104 | 0.09 | 0.225 | -0.008 |
| Information Technology | -0.058 | 0.371 | 0.245 | 0.633 | 0.073 | 0.323 | 0.217 | 0.178 | 0.253 | 0.022 |
| Materials | -0.04 | 0.01 | 0.141 |  | 1.74 | 0.253 | 0.087 | 0.058 | 0.067 | -0.007 |
| Real Estate | -0.039 | 0.335 | 0.352 |  | 5.137 | 0.454 | 0.057 | 0.058 |  | -0.018 |
| Utilities | -0.034 | 0.056 | -0.223 |  | 5.468 | 0.266 | 0.087 | 0.083 |  | -0.048 |


## 6. Veri boşlukları


### 6.1 Eksik EDGAR alanları (şirket × alan, 216 boşluk)

Listelenen us-gaap etiketlerinin hiçbirinde değer yok. Standart dışı/şirkete özel etiketler için fallback yazılmadı (kural gereği yalnız listelendi).


| alan | şirket sayısı | şirketler |
|---|---|---|
| capex | 2 | MS, NEE |
| cost_of_revenue | 20 | AXP, BKNG, BLK, BNY, BRK.B, CMCSA, COF, DIS, GS, LIN, MA, MS, NEE, ORCL, SCHW, UBER, UNP, UPS, V, XOM |
| current_assets | 9 | AXP, BLK, BNY, BRK.B, COF, DE, GS, MS, SCHW |
| current_liabilities | 9 | AXP, BLK, BNY, BRK.B, COF, DE, GS, MS, SCHW |
| debt_current | 14 | ANET, AXP, BLK, BNY, BRK.B, CAT, COF, GM, GS, ISRG, NFLX, PANW, PLTR, SCHW |
| debt_noncurrent | 10 | ANET, AXP, BLK, BNY, BRK.B, GM, ISRG, MS, ORCL, PANW |
| dna | 12 | ABBV, ABT, GEV, GILD, GOOG, IBM, INTU, ISRG, MSFT, ORCL, TXN, UNP |
| eps_diluted | 2 | BRK.B, V |
| gross_profit | 46 | ACN, AMT, AMZN, AXP, BKNG, BLK, BNY, BRK.B, CMCSA, COF, COP, CVX, DIS, DUK, FDX, GD, GE, GM, GOOG, GS, INTU, LIN, LLY, MA, MCD, META, MMM, MRK, MS, NEE, PFE, PG, QCOM, SBUX, SCHW, SO, T, TMUS, UBER, UNH, UNP, UPS, V, VZ, WMT, XOM |
| operating_income | 18 | AXP, BMY, BNY, BRK.B, COF, COP, CVX, EMR, GE, GS, IBM, JNJ, LLY, MRK, MS, PFE, SCHW, XOM |
| revenue | 1 | GS |
| rpo | 44 | AAPL, ABBV, ABT, AMAT, AMGN, AMT, AXP, BKNG, BLK, BNY, BRK.B, CMCSA, COF, COST, CVS, CVX, DUK, FDX, GILD, GS, INTU, JNJ, KO, LLY, LOW, MCD, MDLZ, META, MMM, MO, MRK, MS, NEE, NFLX, PEP, PG, PM, SBUX, SCHW, TXN, UPS, VZ, WMT, XOM |
| short_term_borrowings | 29 | ADBE, AMT, ANET, BKNG, BLK, BRK.B, CMCSA, COP, COST, CRM, CSCO, DE, DELL, DHR, DIS, GILD, GM, INTU, ISRG, LRCX, MA, META, MRK, MU, ORCL, PANW, PLTR, SNDK, TSLA |


### 6.2 Metrik kapsama oranı (bağlı olaylar)

| metric | dolu |
|---|---|
| accrual_ratio | 96% |
| eps_growth | 95% |
| fcf_margin | 91% |
| gross_margin | 62% |
| net_debt_ebitda | 46% |
| op_margin | 79% |
| rev_growth_q | 96% |
| rev_growth_ttm | 95% |
| rpo_growth | 35% |
| wc_change | 88% |


**Metriklerinin yarısından azı hesaplanabilen şirketler:** MS (20%), GS (20%), BNY (22%), BRK.B (40%)


### 6.3 Eşleşmeyen olaylar

Önceki ve sonraki 2.02 arasında bu olaya bağlanabilecek 10-Q/10-K yok: çoğunlukla ön-duyurular (ör. ABBV IPR&D, TSLA teslimat), yıllık rehberlik güncellemeleri ve 10-Q'su henüz dosyalanmamış son olaylar. Bu olaylar metrik ve testlere girmez.


| issue | adet |
|---|---|
| event date beyond price calendar | 1 |
| no 10-Q/10-K accepted between this 2.02 and the next 2.02 | 123 |


Şirket bazında: TSLA (24), ABBV (20), DHR (7), EMR (6), ISRG (6), CVS (4), MMM (4), LLY (4), INTU (4), FDX (4), PFE (3), CVX (3), JNJ (2), NVDA (2), GILD (2), IBM (2), T (2), CAT (1), CRM (1), BA (1), BMY (1), AMD (1), AMAT (1), GE (1), GM (1), LMT (1), INTC (1), GS (1), GOOG (1), DELL (1), MDT (1), MRK (1), LOW (1), ORCL (1), NEE (1), SO (1), SBUX (1), TMO (1), UBER (1), UNP (1), WMT (1)


<details><summary>Tüm eşleşmeyen olaylar</summary>

| event_id | ticker | acceptance_ny | issue |
|---|---|---|---|
| ABBV:0001104659-22-048450 | ABBV | 2022-04-21T17:12:34-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-22-000010 | ABBV | 2022-04-29T07:45:08-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-22-000023 | ABBV | 2022-07-06T16:17:34-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-22-000034 | ABBV | 2022-10-05T16:14:22-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-23-000004 | ABBV | 2023-01-06T16:15:27-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-23-000015 | ABBV | 2023-04-05T16:33:31-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-23-000026 | ABBV | 2023-07-06T16:18:09-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-23-000036 | ABBV | 2023-10-04T16:11:14-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-24-000002 | ABBV | 2024-01-05T16:03:27-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-24-000013 | ABBV | 2024-04-03T16:06:09-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-24-000024 | ABBV | 2024-07-03T14:07:48-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-24-000033 | ABBV | 2024-10-03T16:07:32-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-25-000002 | ABBV | 2025-01-06T16:02:39-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-25-000023 | ABBV | 2025-04-03T16:13:07-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-25-000034 | ABBV | 2025-07-03T13:07:55-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-25-000043 | ABBV | 2025-10-03T16:09:03-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-26-000002 | ABBV | 2026-01-07T16:08:59-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-26-000011 | ABBV | 2026-04-03T16:05:55-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-26-000021 | ABBV | 2026-07-06T16:12:09-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ABBV:0001551152-26-000030 | ABBV | 2026-10-05T16:07:45-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| AMAT:0001628280-26-073360 | AMAT | 2026-11-12T16:02:46-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| AMD:0000002488-22-000163 | AMD | 2022-10-06T16:20:03-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| BA:0000012927-24-000067 | BA | 2024-10-11T16:39:18-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| BMY:0001140361-22-014868 | BMY | 2022-04-18T16:30:40-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CAT:0000018230-24-000047 | CAT | 2024-10-11T08:34:44-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CRM:0001108524-21-000007 | CRM | 2021-02-25T16:17:25-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVS:0000064803-22-000002 | CVS | 2022-01-11T06:31:38-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVS:0000064803-23-000003 | CVS | 2023-01-09T06:27:52-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVS:0000947871-24-000009 | CVS | 2024-01-05T06:41:14-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVS:0001193125-24-239193 | CVS | 2024-10-18T06:46:01-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVX:0000950142-23-002083 | CVX | 2023-07-24T06:01:10-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVX:0000093410-24-000002 | CVX | 2024-01-02T08:00:35-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| CVX:0000093410-26-000108 | CVX | 2026-04-09T07:00:12-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DELL:0001571996-26-000050 | DELL | 2026-11-24T16:09:13-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DELL:0001571996-26-000050 | DELL | 2026-11-24T16:09:13-05:00 | event date beyond price calendar |
| DHR:0000313616-21-000004 | DHR | 2021-01-13T07:23:48-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DHR:0000313616-22-000003 | DHR | 2022-01-11T07:28:23-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DHR:0000313616-23-000002 | DHR | 2023-01-09T16:17:53-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DHR:0000313616-23-000175 | DHR | 2023-05-11T16:41:29-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DHR:0000313616-24-000004 | DHR | 2024-01-08T16:22:03-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DHR:0000313616-25-000002 | DHR | 2025-01-13T16:22:11-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| DHR:0000313616-26-000002 | DHR | 2026-01-12T09:07:26-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| EMR:0000950103-21-015731 | EMR | 2021-10-12T09:46:21-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| EMR:0000032604-22-000045 | EMR | 2022-11-29T06:55:25-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| EMR:0000032604-23-000027 | EMR | 2023-04-06T06:55:28-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| EMR:0000950103-23-005624 | EMR | 2023-04-12T08:11:30-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| EMR:0000032604-25-000094 | EMR | 2025-11-20T06:55:36-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| EMR:0000032604-26-000047 | EMR | 2026-10-13T06:57:44-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| FDX:0000950170-22-018545 | FDX | 2022-09-15T16:46:05-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| FDX:0000950170-24-102826 | FDX | 2024-09-03T16:15:17-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| FDX:0001048911-26-000108 | FDX | 2026-07-21T16:09:35-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| FDX:0001048911-26-000126 | FDX | 2026-10-28T16:05:46-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| GE:0000040545-23-000017 | GE | 2023-01-10T06:45:30-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| GILD:0000882095-21-000002 | GILD | 2021-01-11T06:04:39-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| GILD:0001104659-22-010300 | GILD | 2022-02-01T16:03:17-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| GM:0001467858-22-000088 | GM | 2022-07-01T08:52:14-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| GOOG:0001652044-23-000034 | GOOG | 2023-04-20T16:24:04-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| GS:0000886982-26-000004 | GS | 2026-01-08T16:15:56-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| IBM:0001558370-21-017039 | IBM | 2021-12-27T16:50:21-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| IBM:0000051143-26-000070 | IBM | 2026-07-14T07:01:52-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| INTC:0001193125-21-009142 | INTC | 2021-01-14T17:10:00-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| INTU:0000896878-21-000049 | INTU | 2021-02-09T08:09:10-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| INTU:0000896878-21-000108 | INTU | 2021-05-11T16:03:29-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| INTU:0000896878-22-000005 | INTU | 2022-02-14T16:08:52-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| INTU:0000896878-22-000030 | INTU | 2022-11-01T16:09:35-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ISRG:0001035267-21-000008 | ISRG | 2021-01-13T09:00:24-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ISRG:0001035267-22-000003 | ISRG | 2022-01-12T09:00:48-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ISRG:0001035267-23-000003 | ISRG | 2023-01-11T09:01:25-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ISRG:0001035267-24-000006 | ISRG | 2024-01-09T16:03:40-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ISRG:0001035267-25-000005 | ISRG | 2025-01-15T09:00:19-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ISRG:0001035267-26-000003 | ISRG | 2026-01-14T08:58:49-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| JNJ:0000200406-23-000091 | JNJ | 2023-08-30T07:46:49-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| JNJ:0000200406-24-000031 | JNJ | 2024-04-16T07:06:41-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| LLY:0001193125-21-357380 | LLY | 2021-12-15T07:05:57-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| LLY:0000059478-22-000117 | LLY | 2022-04-14T16:57:23-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| LLY:0000059478-22-000277 | LLY | 2022-12-13T07:03:51-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| LLY:0000059478-25-000005 | LLY | 2025-01-14T09:05:19-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| LMT:0000936468-22-000084 | LMT | 2022-06-27T16:20:44-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| LOW:0000060667-26-000126 | LOW | 2026-11-18T08:45:11-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| MDT:0001628280-26-075604 | MDT | 2026-11-24T06:32:02-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| MMM:0001558370-21-003283 | MMM | 2021-03-22T06:30:50-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| MMM:0000066740-22-000017 | MMM | 2022-02-11T16:11:49-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| MMM:0000066740-22-000030 | MMM | 2022-04-26T06:01:28-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| MMM:0000066740-23-000018 | MMM | 2023-02-21T16:16:12-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| MRK:0001104659-22-047977 | MRK | 2022-04-20T18:45:29-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| NEE:0000753308-26-000004 | NEE | 2026-01-02T16:31:56-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| NVDA:0001045810-22-000133 | NVDA | 2022-08-08T09:16:50-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| NVDA:0001045810-26-000088 | NVDA | 2026-11-17T16:20:51-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| ORCL:0001193125-22-191296 | ORCL | 2022-07-11T16:36:09-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| PFE:0000078003-22-000062 | PFE | 2022-04-20T16:41:43-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| PFE:0000078003-23-000099 | PFE | 2023-10-13T17:30:20-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| PFE:0001193125-23-294930 | PFE | 2023-12-14T07:51:03-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| SBUX:0000829224-24-000047 | SBUX | 2024-10-22T16:06:28-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| SO:0000092122-23-000103 | SO | 2023-11-02T08:17:32-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| T:0000732717-21-000054 | T | 2021-07-21T17:01:04-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| T:0000732717-22-000004 | T | 2022-01-05T06:46:04-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TMO:0000097745-21-000002 | TMO | 2021-01-11T07:00:17-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-21-000008 | TSLA | 2021-01-04T06:05:26-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-21-017443 | TSLA | 2021-04-02T08:38:07-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0000950170-21-000423 | TSLA | 2021-07-02T08:32:50-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-21-049874 | TSLA | 2021-10-04T06:09:14-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-22-000009 | TSLA | 2022-01-03T06:06:42-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-22-013264 | TSLA | 2022-04-04T06:07:24-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-22-025153 | TSLA | 2022-07-05T06:16:41-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-22-033053 | TSLA | 2022-10-03T06:05:40-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-23-000002 | TSLA | 2023-01-03T06:08:47-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001564590-23-005126 | TSLA | 2023-04-03T07:02:44-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0000950170-23-031241 | TSLA | 2023-07-03T06:05:58-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0000950170-23-050938 | TSLA | 2023-10-02T09:05:38-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0000950170-24-000282 | TSLA | 2024-01-02T16:29:17-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0000950170-24-040274 | TSLA | 2024-04-02T16:47:22-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-24-030714 | TSLA | 2024-07-02T09:24:01-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-24-041816 | TSLA | 2024-10-02T09:06:34-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-25-000007 | TSLA | 2025-01-02T09:06:39-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-25-016070 | TSLA | 2025-04-02T09:05:22-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-25-033842 | TSLA | 2025-07-02T09:05:13-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-25-043530 | TSLA | 2025-10-02T09:04:54-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-26-000016 | TSLA | 2026-01-02T09:20:13-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-26-022956 | TSLA | 2026-04-02T09:07:13-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-26-046717 | TSLA | 2026-07-02T09:01:26-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| TSLA:0001628280-26-064366 | TSLA | 2026-10-02T09:04:26-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| UBER:0001552781-21-000198 | UBER | 2021-04-12T06:45:27-04:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| UNP:0000100885-21-000027 | UNP | 2021-01-08T09:00:17-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |
| WMT:0000104169-26-000168 | WMT | 2026-11-19T06:58:52-05:00 | no 10-Q/10-K accepted between this 2.02 and the next 2.02 |

</details>


### 6.4 Fiyat verisi

Kaynaklar: ok (yfinance(auto_adjust=True)). Eksik: yok. Stooq bu ortamdan erişilemedi; tüm seriler yfinance (auto_adjust=True) — kaynak her satırda `source`/`price_source` sütununda.


## 7. Hariç tutulan şirketler


| ticker | şirket | GICS alt-endüstri | GICS endüstri | neden |
|---|---|---|---|---|
| BAC | Bank of America | Diversified Banks | Banks | GICS industry = Banks |
| C | Citigroup | Diversified Banks | Banks | GICS industry = Banks |
| JPM | JPMorgan Chase | Diversified Banks | Banks | GICS industry = Banks |
| USB | U.S. Bancorp | Diversified Banks | Banks | GICS industry = Banks |
| WFC | Wells Fargo | Diversified Banks | Banks | GICS industry = Banks |


Diğer evren notları:

| ticker | issue |
|---|---|
| GOOGL | duplicate share class of GOOG (same CIK) - dropped |


## 8. Yöntem notları

- Olay günü: kabul saati (New York) ≥ 16:00 → sonraki işlem günü; < 16:00 → aynı gün (işlem günü değilse sonraki). Takvim = SPY işlem günleri. Yarım gün kapanışları (13:00) için ayrı kural yok.
- Getiriler: taban = olay gününden önceki kapanış. öncesi-60 = P[d0-1]/P[d0-61]-1; sonrası-h = P[d0-1+h]/P[d0-1]-1. Fazla getiri = hisse − SPY veya − sektör SPDR ETF'i (aynı pencere).
- Çeyreklik akım değerleri: doğrudan 3 aylık XBRL değeri; yoksa YTD(t) − YTD(t−1 çeyrek) (aynı başlangıç tarihi). Q4 sulandırılmış EPS = FY − 9A farkıyla türetilir (yaklaşık).
- YoY değişim = metrik(şimdi) − aynı metriğin 4 çeyrek önceki değeri (aynı bilgi kümesiyle).
- Güven aralıkları: şirket düzeyinde küme bootstrap (aynı şirketin olayları bağımlı), 1000 tekrar, sabit tohum. p = 2·(1−Φ(|ρ|/se_boot)); BH ailesi = (PIT modu, getiri türü, grup) içindeki tüm metrik×varyant×ufuk testleri.
- Etiket kaynakları: metrik satırlarında `source` (kullanılan EDGAR us-gaap etiketleri) ve `input_accns`; getirilerde `price_source`; GICS sektör/alt-endüstri Wikipedia; GICS endüstri eşlemesi, öncül CIK eşlemesi (XOM, BLK) ve edgar_fields.yaml etiket listeleri **AI-derived** olarak işaretli.
- Eşik: eşik değer kullanılmadı. Kullanılan sabitler takvimsel tanımlardır (çeyrek = 80–100 gün, yıl = 350–380 gün, 52/53 haftalık çeyrek sonu eşleştirme toleransı ±20 gün) ve BH-FDR α (konvansiyonel 0.05, config'de).


_Tekrar üretilebilirlik: ic_results sha256 = `f5d62777dbd0b9a8…`_
