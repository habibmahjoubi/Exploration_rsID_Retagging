import json, re
from statsmodels.stats.proportion import proportion_confint
S = {"HG001": ("wg_results_HG001", "_HG001", "downstream/downstream_results_HG001.json"),
     "HG002": ("wg_results", "_HG002", "downstream/downstream_results.json"),
     "HG005": ("wg_results_HG005", "_HG005", "downstream/downstream_results_HG005.json")}
B = ["dbSNP138 (GATK/WARP)", "dbSNP144 (GDC)", "dbSNP146 (sarek default)", "dbSNP156 (NCBI, Nov 2022)"]
txt = {}; tot = {}
for s, (w, t, d) in S.items():
    T = open(w + ".txt").read()
    tot[s] = (int(re.search(r"variants: ([\d,]+) \(SNV ([\d,]+)", T).group(1).replace(",", "")),
              int(re.search(r"variants: ([\d,]+) \(SNV ([\d,]+)", T).group(2).replace(",", "")))
    txt[s] = {}
    for blk in T.split("\n== ")[1:]:
        nm = blk.split("\n")[0].strip()
        m = re.search(r"SNVs: ([\d,]+)/([\d,]+) = .*?; indels: ([\d,]+)/([\d,]+)", blk)
        txt[s][nm] = [int(x.replace(",", "")) for x in m.groups()]
print("== (c) composition: expected HG005 variant rate from HG002 per-type rates")
for b in B:
    sr2, sn2, ir2, in2 = txt["HG002"][b]; sr5, sn5, ir5, in5 = txt["HG005"][b]
    exp = (sn5 * sr2 / sn2 + in5 * ir2 / in2) / (sn5 + in5)
    print(f"  {b[:9]}: indel share HG002 {in2/(sn2+in2):.3f} HG005 {in5/(sn5+in5):.3f}; HG005 observed {(sr5+ir5)/(sn5+in5):.4f} expected {exp:.4f}")
print("== (d) indels with no rsID from the file: bounds on the variant rate")
for s in S:
    nvar, nsnv = tot[s]; nind = nvar - nsnv
    for b in B:
        sr, sn, ir, inn = txt[s][b]
        un_ind = nind - inn; un_snv = nsnv - sn
        k, n = sr + ir, sn + inn
        print(f"  {s} {b[:9]}: unannotated indels {un_ind:,} ({un_ind/nind:.1%}), SNVs {un_snv:,} ({un_snv/nsnv:.1%}); "
              f"rate {k/n:.2%}; bounds if unannotated indels were all clean {k/(n+un_ind):.2%} / all retired {(k+un_ind)/(n+un_ind):.2%}")
print("== (e) PharmGKB levels 1A-2B per genome (validated join)")
for s, (w, t, d) in S.items():
    po = json.load(open(f"downstream/post_locus_allele{t}.json"))["dbSNP146 (sarek default)"]["other"]
    print("  ", s, {k: v["validated"] for k, v in po.items() if "PharmGKB-clinical" in k})
print("== (f) ClinVar P/LP >=1*, pooled over genomes")
for b in B:
    m = x = 0
    for s, (w, t, d) in S.items():
        c = json.load(open(f"downstream/post_locus_allele{t}.json"))[b]["clinvar"]["P/LP >=1*"]
        m += c.get("position-matched", 0); x += c.get("missed, recovered by validated join (retired rsID)", 0)
    lo, hi = proportion_confint(x, m, method="beta")
    print(f"  {b[:9]}: missed because of retired rsID {x}/{m}; exact 95% CI {100*lo:.1f}-{100*hi:.1f}%")
print("== (g) GWAS p<5e-8 missed entries vs distinct variants; validated vs reconciled totals")
for s, (w, t, d) in S.items():
    D = json.load(open(d)); P = json.load(open(f"downstream/post_locus_allele{t}.json"))
    for b in B:
        r = D[b]["sample"]["GWAS | p<5e-8"]; v = P[b]["other"]["GWAS | p<5e-8"]
        print(f"  {s} {b[:9]}: missed entries reconciled {r['missed']:,} (variants {r['hg002_variants_losing']:,}) | validated {v['missed by plain, recovered by validated']:,}")
print("== (h) retired annotations: wg (full ledger) vs post (ledger with target)")
for s, (w, t, d) in S.items():
    W = json.load(open(w + ".json")); P = json.load(open(f"downstream/post_locus_allele{t}.json"))
    print("  ", s, [W[b]["retired_annotations"] - sum(P[b]["locus"].values()) for b in B])
print("== (i) chr20: benchmark HG002 vs real sarek calls (variant rate)")
W = json.load(open("wg_results.json"))
for b in B:
    pc = W[b]["per_chrom"]; print("  ", b[:9], pc.get("chr20"))
