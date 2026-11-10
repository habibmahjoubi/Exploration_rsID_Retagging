"""Whole-genome (chr1-22) HG002 v4.2.1: annotate each benchmark variant with rsIDs from each
bundle (allele-exact after normalization, as GATK -D does) and count retired IDs against the
complete dbSNP b157 merged-rsID ledger. Reports per-annotation and per-variant rates, Wilson
95% CIs, per-chromosome spread, and retiring-build breakdown."""
import bz2, gzip, re, math, collections, json, sys
from normalize import normalize
# optional: wg_analysis.py <sample.vcf.gz> <bundle-tsv prefix> <output tag>; defaults = HG002 run
SAMPLE = sys.argv[1] if len(sys.argv) > 1 else "HG002_wg.vcf.gz"
PFX = sys.argv[2] if len(sys.argv) > 2 else "wg_"
TAG = sys.argv[3] if len(sys.argv) > 3 else ""
B = {"dbSNP138 (GATK/WARP)": PFX + "d138.tsv", "dbSNP144 (GDC)": PFX + "d144.tsv",
     "dbSNP146 (sarek default)": PFX + "d146.tsv", "dbSNP156 (NCBI, Nov 2022)": PFX + "b156.tsv"}
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*(c-h), 100*(c+h)
calls = []  # (chrom, set(keys), is_snv)
with gzip.open(SAMPLE, "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c, p, _, r, a = ln.split("\t", 5)[:5]
        alts = a.split(",")
        calls.append((c, {(c,) + normalize(int(p), r, x) for x in alts}, len(r) == 1 and all(len(x) == 1 for x in alts)))
print(f"{SAMPLE} chr1-22 benchmark variants: {len(calls):,} (SNV {sum(1 for x in calls if x[2]):,})")
ann = {}
allids = set()
for name, path in B.items():
    km = collections.defaultdict(set)
    with open(path) as f:
        for ln in f:
            c, p, r, a, i = ln.rstrip("\n").split("\t")
            ids = {int(x) for x in i.replace("rs", "").split(";") if x.isdigit()}
            for x in a.split(","):
                km[(c,) + normalize(int(p), r, x)] |= ids
    ann[name] = [set().union(*(km.get(k, set()) for k in keys)) for _, keys, _ in calls]
    for s in ann[name]: allids |= s
retired = {}
rx = re.compile(rb'^\{"refsnp_id":"(\d+)".*"proxy_build_id":"(\d+)"')
with bz2.open("refsnp-merged.json.bz2", "rb") as f:
    for ln in f:
        m = rx.match(ln)
        if m and int(m.group(1)) in allids: retired[int(m.group(1))] = int(m.group(2))
res = {}
for name, A in ann.items():
    tot = sum(len(s) for s in A); st = sum(1 for s in A for i in s if i in retired)
    nv = sum(1 for s in A if s); vr = sum(1 for s in A if any(i in retired for i in s))
    vr_only = sum(1 for s in A if s and all(i in retired for i in s))
    snv = [(s) for (c, k, sn), s in zip(calls, A) if sn and s]
    snv_r = sum(1 for s in snv if any(i in retired for i in s))
    per = collections.defaultdict(lambda: [0, 0])
    for (c, _, _), s in zip(calls, A):
        if s:
            per[c][1] += 1; per[c][0] += any(i in retired for i in s)
    rates = sorted(100*a/b for a, b in per.values())
    builds = collections.Counter(retired[i] for s in A for i in s if i in retired)
    lo, hi = wilson(vr, nv)
    print(f"\n== {name}")
    print(f"  annotations: {tot:,}; retired: {st:,} ({100*st/tot:.2f}%)")
    print(f"  annotated variants: {nv:,} ({100*nv/len(calls):.1f}% of calls); carrying >=1 retired ID: {vr:,} = {100*vr/nv:.2f}% [95% CI {lo:.2f}-{hi:.2f}]")
    print(f"  ONLY retired ID(s) (no current ID at all): {vr_only:,} ({100*vr_only/nv:.2f}%)")
    print(f"  SNVs: {snv_r:,}/{len(snv):,} = {100*snv_r/len(snv):.2f}%; indels: {vr-snv_r:,}/{nv-len(snv):,} = {100*(vr-snv_r)/max(1,nv-len(snv)):.2f}%")
    print(f"  per-chromosome rate range: {rates[0]:.2f}%-{rates[-1]:.2f}% (median {rates[len(rates)//2]:.2f}%)")
    print(f"  chr20: {per['chr20'][0]:,}/{per['chr20'][1]:,} = {100*per['chr20'][0]/per['chr20'][1]:.2f}%")
    print(f"  retiring build: {dict(sorted(builds.items()))}")
    res[name] = dict(variants_annotated=nv, variants_retired=vr, only_retired=vr_only, annotations=tot, retired_annotations=st,
                     per_chrom={c: v for c, v in per.items()}, builds=dict(builds))
json.dump(res, open(f"wg_results{TAG}.json", "w"), indent=1)
# list of retired->variant for downstream (gnomAD etc.) checks, dbSNP146
with open(f"wg{TAG}_d146_retired_variants.tsv", "w") as o:
    for (c, keys, sn), s in zip(calls, ann["dbSNP146 (sarek default)"]):
        r = [i for i in s if i in retired]
        if r: o.write(f"{c}\t{sorted(keys)[0][1]}\t{';'.join(map(str, r))}\t{';'.join(str(i) for i in s if i not in retired)}\n")
