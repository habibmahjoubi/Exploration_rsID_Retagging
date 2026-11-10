"""Live RefSNP API check of a random sample of merge targets classified "elsewhere or absent in
dbSNP156" by post_locus_allele.py (dbSNP146 annotations). For each: where does dbSNP place the
target now (same chromosome near/far, other chromosome, or unplaced)?
Usage: python check_elsewhere.py <elsewhere_examples_TAG.tsv> [n] [seed]"""
import json, random, sys, time, urllib.request, collections
src = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 30; seed = int(sys.argv[3]) if len(sys.argv) > 3 else 11
rows = [l.rstrip("\n").split("\t") for l in open(src)]
random.seed(seed); sample = random.sample(rows, min(n, len(rows)))


def api(i):
    for k in range(6):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(
                f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{i}", headers={"User-Agent": "rsid-check/1.0"}), timeout=30).read())
        except Exception:
            time.sleep(3 * (k + 1))
    return {}


tally = collections.Counter()
print(f"{len(rows)} 'elsewhere' examples in {src}; checking {len(sample)} (seed {seed})")
for c, p, d, ins, old, tgt in sample:
    r = api(tgt[2:]); time.sleep(0.4)
    pls = [pl for pl in r.get("primary_snapshot_data", {}).get("placements_with_allele", [])
           if pl.get("is_ptlp") and pl.get("seq_id", "").startswith("NC_0000")]
    if not pls:
        cls = "target not placed on GRCh38 chromosomes" if r else "API error"
        where = "-"
    else:
        sid = pls[0]["seq_id"]; pos = pls[0]["alleles"][0]["allele"]["spdi"]["position"] + 1
        chrom = f"chr{int(sid[7:9])}"
        if chrom != c: cls = "other chromosome"
        elif abs(pos - int(p)) <= 50: cls = "same chromosome, within 50 bp"
        else: cls = "same chromosome, > 50 bp away"
        where = f"{chrom}:{pos}"
    tally[cls] += 1
    print(f"  {c}:{p} {d}>{ins}  {old} -> {tgt}  now at {where}  [{cls}]")
print("\nSUMMARY:", dict(tally))
