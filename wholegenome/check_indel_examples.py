"""Spot-check HG002 variants that the dbSNP146 bundle labels with a retired rsID (whole genome),
against the live dbSNP RefSNP API. Random sample of indels (and a few SNVs as controls).

For each sampled variant:
  - the dbSNP146 bundle records at that locus (allele-exact rsIDs, from wg_d146.tsv)
  - live API on each retired rsID: merged? merged_into target?
  - live API on the target: is it placed at the same normalized allele as the HG002 variant?
Usage (from G:/rsid_wg): python check_indel_examples.py [n_indels] [n_snvs] [seed]
"""
import gzip, json, random, sys, time, urllib.request, collections
sys.path.insert(0, ".")
from normalize import normalize

N_IND = int(sys.argv[1]) if len(sys.argv) > 1 else 25
N_SNV = int(sys.argv[2]) if len(sys.argv) > 2 else 5
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7

# HG002 calls keyed by normalized allele
calls = {}
with gzip.open("HG002_wg.vcf.gz", "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c, p, _, r, a = ln.split("\t", 5)[:5]
        for x in a.split(","):
            calls[(c,) + normalize(int(p), r, x)] = (int(p), r, x)
# bundle: normalized key -> set of rsIDs (as GATK -D would assign them)
km = collections.defaultdict(set); raw = collections.defaultdict(list)
with open("wg_d146.tsv") as f:
    for ln in f:
        c, p, r, a, i = ln.rstrip("\n").split("\t")
        for x in a.split(","):
            k = (c,) + normalize(int(p), r, x)
            if k in calls:
                km[k] |= {int(z) for z in i.replace("rs", "").split(";") if z.isdigit()}
                raw[k].append(f"{c}:{p} {r}>{a} {i}")
# retired variants written by wg_analysis.py: chrom, pos0, retired ids, current ids
rows = [ln.rstrip("\n").split("\t") for ln in open("wg_d146_retired_variants.tsv")]
# index keys by (chrom,pos0) for lookup
by_pos = collections.defaultdict(list)
for k in km: by_pos[(k[0], k[1])].append(k)
cases = []
for c, p0, ret, cur in rows:
    ret_ids = {int(x) for x in ret.split(";") if x}
    for k in by_pos.get((c, int(p0)), []):
        if km[k] & ret_ids:
            is_snv = len(k[2]) == 1 and len(k[3]) == 1
            cases.append((is_snv, k, sorted(ret_ids & km[k]), sorted(km[k] - ret_ids)))
            break
random.seed(SEED)
ind = [x for x in cases if not x[0]]; snv = [x for x in cases if x[0]]
print(f"retired-labelled variants: {len(cases):,} (indels {len(ind):,}, SNVs {len(snv):,}); "
      f"sampling {N_IND} indels + {N_SNV} SNVs, seed {SEED}\n")
sample = random.sample(ind, min(N_IND, len(ind))) + random.sample(snv, min(N_SNV, len(snv)))


def api(i):
    for k in range(6):
        try:
            req = urllib.request.Request(f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{i}",
                                         headers={"User-Agent": "rsid-check/1.0"})
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception as e:
            err = e; time.sleep(3 * (k + 1))
    return {"_error": str(err)}


def placements(rec, chrom):
    """normalized (pos0, del, ins) alleles of a current record on the GRCh38 chromosome."""
    n = int(chrom[3:]); out = set()
    for pl in rec.get("primary_snapshot_data", {}).get("placements_with_allele", []):
        sid = pl.get("seq_id", "")
        if sid.startswith("NC_0000") and int(sid[7:9]) == n and pl.get("is_ptlp"):
            for al in pl["alleles"]:
                s = al["allele"].get("spdi")
                if s and s["deleted_sequence"] != s["inserted_sequence"]:
                    out.add(normalize(s["position"] + 1, s["deleted_sequence"], s["inserted_sequence"]))
    return out


tally = collections.Counter()
for is_snv, k, ret, cur in sample:
    c, pos0, d, ins = k
    p, r, a = calls[k]
    print(f"{'SNV  ' if is_snv else 'INDEL'} {c}:{p} {r}>{a}  (normalized {pos0},{d or '-'},{ins or '-'})")
    print(f"   bundle dbSNP146 at this allele: retired {['rs%d' % x for x in ret]}  current {['rs%d' % x for x in cur]}")
    for line in raw[k][:4]: print(f"      bundle record: {line}")
    for rid in ret:
        rec = api(rid); time.sleep(0.35)
        into = rec.get("merged_snapshot_data", {}).get("merged_into", [])
        live = "primary_snapshot_data" in rec
        tgt = int(into[0]) if into else None
        same = None
        if tgt:
            t = api(tgt); time.sleep(0.35)
            same = (pos0, d, ins) in placements(t, c)
        in_cur = tgt in cur if tgt else None
        verdict = ("MERGED into an rsID also in the bundle annotation" if in_cur else
                   "MERGED into an rsID NOT in the bundle annotation" if tgt else
                   "NOT MERGED per API" if live else "no record / error")
        tally[(("SNV" if is_snv else "INDEL"), verdict, same)] += 1
        print(f"   rs{rid}: retired={not live}, merged_into={['rs' + x for x in into]}, "
              f"target placed at the same normalized allele={same}  -> {verdict}")
    print()
print("SUMMARY (type, verdict, target at same allele): count")
for k, v in sorted(tally.items(), key=str): print(f"  {k}: {v}")
