import bz2, json, re, math, collections
from statsmodels.stats.proportion import proportion_confint
# 1. ledger records without a merged_into target
nt = []
with bz2.open("refsnp-merged.json.bz2", "rb") as f:
    for ln in f:
        if b'"merged_into":[' not in ln or re.search(rb'"merged_into":\[\]', ln):
            nt.append(ln[:400])
print("ledger records without merged_into target:", len(nt))
for x in nt[:3]: print("  ", x.decode()[:300])
# 2. independent CI check (statsmodels Wilson and Clopper-Pearson) for Table 1
S = {"HG001": "wg_results_HG001.json", "HG002": "wg_results.json", "HG005": "wg_results_HG005.json"}
for s, p in S.items():
    w = json.load(open(p))
    for b, r in w.items():
        k, n = r["variants_retired"], r["variants_annotated"]
        lo, hi = proportion_confint(k, n, method="wilson")
        print(f"{s} {b[:9]} variant {100*k/n:.2f}% wilson {100*lo:.2f}-{100*hi:.2f}")
