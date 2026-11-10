"""Check every rsID in each chr20 bundle, and every rsID assigned to the real sarek
calls (re-annotated by allele-exact match against each bundle), against the
complete genome-wide dbSNP b157 merged-rsID ledger (refsnp-merged.json.bz2)."""
import bz2, gzip, re, sys, collections
from normalize import normalize

bundles = {"dbSNP138 (GATK)": "d138.tsv", "dbSNP144 (GDC)": "d144.tsv",
           "dbSNP146 (sarek default)": "d146_chr20_idmap.tsv", "dbSNP156 (NCBI 2022)": "b156_chr20_idmap.tsv"}
# native nf-core/sarek output (HaplotypeCaller with GATK -D dbSNP138), included in this folder
SAREK = "HG002.chr20.sarek_haplotypecaller.dbsnp138.vcf.gz"

# sarek calls: normalized allele keys + native ID field
calls, native_ids = [], []
with gzip.open(SAREK, "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c = ln.split("\t", 6)
        keys = [normalize(int(c[1]), c[3], a) for a in c[4].split(",") if a != "<NON_REF>" and a != "*"]
        calls.append(keys)
        native_ids.append([] if c[2] == "." else c[2].replace("rs", "").split(";"))
print(f"sarek calls: {len(calls):,}; with native (dbSNP138 -D) ID: {sum(1 for x in native_ids if x):,}", flush=True)
need = set()
for ids in native_ids: need.update(int(i) for i in ids)

per_bundle_ids, sarek_ann = {}, {}
for name, path in bundles.items():
    ids, keymap = set(), collections.defaultdict(set)
    with open(path) as f:
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) != 4: continue
            for rid in p[3].replace("rs", "").split(";"):
                if rid.isdigit(): ids.add(int(rid))
            for a in p[2].split(","):
                keymap[normalize(int(p[0]), p[1], a)].update(int(r) for r in p[3].replace("rs", "").split(";") if r.isdigit())
    ann = []
    for keys in calls:
        s = set()
        for k in keys: s |= keymap.get(k, set())
        ann.append(s)
    per_bundle_ids[name], sarek_ann[name] = ids, ann
    need |= ids
    print(f"{name}: {len(ids):,} distinct chr20 rsIDs; sarek calls annotated: {sum(1 for a in ann if a):,}", flush=True)

retired = set()
pid = re.compile(rb'^\{"refsnp_id":"(\d+)"')
with bz2.open("refsnp-merged.json.bz2", "rb") as f:
    for ln in f:
        m = pid.match(ln)
        if m:
            r = int(m.group(1))
            if r in need: retired.add(r)
print(f"\nretired IDs among all IDs of interest: {len(retired):,}\n")

print("A. Bundle-intrinsic: share of a bundle's chr20 rsIDs that are retired in b157")
for name, ids in per_bundle_ids.items():
    k = len(ids & retired); print(f"  {name}: {k:,} / {len(ids):,} = {k/len(ids)*100:.3f}%")

print("\nB. Real sarek calls (HG002 chr20 30x), rsIDs assigned per bundle")
tot = sum(len(x) for x in native_ids); st = sum(1 for x in native_ids for i in x if int(i) in retired)
print(f"  native GATK -D (dbSNP138): {st:,} / {tot:,} annotations retired = {st/tot*100:.3f}%")
for name, ann in sarek_ann.items():
    tot = sum(len(a) for a in ann); st = sum(len(a & retired) for a in ann)
    recs = sum(1 for a in ann if a & retired)
    print(f"  re-annotated {name}: {st:,} / {tot:,} annotations retired = {st/tot*100:.3f}% ({recs:,} call records)")
