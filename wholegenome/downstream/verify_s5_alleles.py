"""Allele-level check of the sample-independent analysis (Table S5).
For ClinVar entries (P/LP and B/LB, >=1 star) that a file holds only under a retired rsID
(ID-level, 'retired-only'), does the file list that retired rsID at the same normalized allele
as the ClinVar entry? Same allele -> the entry is genuinely reachable only through a retired rsID.
Usage (from G:/rsid_wg): python downstream/verify_s5_alleles.py > downstream/verify_s5_alleles.txt"""
import collections, gc, gzip, json, pickle, sys
sys.path.insert(0, ".")
from normalize import normalize
FILES = [("dbSNP138 (GATK/WARP)", "dbsnp138.vcf.gz", "downstream/d138.ids"),
         ("dbSNP144 (GDC)", "dbsnp144.vcf.gz", "downstream/d144.ids"),
         ("dbSNP146 (sarek default)", "dbsnp146.vcf.gz", "downstream/d146.ids")]
CATS = {("P/LP", ">=1*"), ("B/LB", ">=1*")}
D = pickle.load(open("downstream/prep.pkl", "rb"))
E, pos_keys, cur, preds = D["E"], D["pos_keys"], D["cur"], D["preds"]
keys_of = collections.defaultdict(list)
for k, idxs in pos_keys.items():
    for i in idxs: keys_of[i].append(k)
todo = {}
for name, vcf, ids in FILES:
    B = {int(x) for x in open(ids).read().split()}
    rows = []
    for idx, e in enumerate(E):
        if e[0] != "ClinVar" or (e[1], e[3]) not in CATS or e[2] is None: continue
        r = cur[e[2]]
        if e[2] in B or r in B: continue
        pr = [x for x in preds.get(r, ()) if x in B]
        if pr: rows.append((idx, e[1] + " " + e[3], pr, keys_of.get(idx, [])))
    todo[name] = rows
    del B
del D, E, pos_keys, cur, preds; gc.collect()
out = {}
for name, vcf, ids in FILES:
    rows = todo[name]
    want = {x for _, _, pr, _ in rows for x in pr}
    found = collections.defaultdict(set)   # rsID -> normalized keys in the file
    with gzip.open(vcf, "rt") as f:
        for ln in f:
            if ln[0] == "#": continue
            c, p, i, r, a = ln.split("\t", 5)[:5]
            ids_ = {int(x[2:]) for x in i.split(";") if x.startswith("rs") and x[2:].isdigit()}
            hit = ids_ & want
            if not hit: continue
            c = c if c.startswith("chr") else "chr" + c
            for x in a.split(","):
                k = (c,) + normalize(int(p), r, x)
                for h in hit: found[h].add(k)
    tally = collections.Counter()
    for idx, cat, pr, ck in rows:
        same = any(k in found.get(x, ()) for x in pr for k in ck)
        samepos = any((k[0], k[1]) in {(y[0], y[1]) for y in found.get(x, ())} for x in pr for k in ck)
        cls = "same allele" if same else ("same position, other allele" if samepos else
               ("ClinVar entry without usable allele" if not ck else "other locus or not found"))
        tally[(cat, cls)] += 1
    print(f"\n-- {name}: retired-only entries {len(rows):,}")
    for k in sorted(tally): print(f"   {k[0]:<10} {k[1]:<36} {tally[k]:>6,}")
    out[name] = {" | ".join(k): v for k, v in tally.items()}
json.dump(out, open("downstream/verify_s5_alleles.json", "w"), indent=1)
print("\ndone")
