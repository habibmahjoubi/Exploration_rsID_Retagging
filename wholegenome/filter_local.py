"""Local-file version of stream_bundle_filter.py: keep only dbSNP records at HG002 v4.2.1
chr1-22 benchmark positions. Usage: python filter_local.py <bundle.vcf.gz> <out.tsv>
Output: chrom pos ref alt id  (chrom as chrN)."""
import gzip, sys, time
src, out = sys.argv[1], sys.argv[2]
samples = sys.argv[3:] or ["HG002_wg.vcf.gz"]  # positions = union over these benchmark VCFs
def cnum(c):
    if c.startswith("NC_0000"):
        n = int(c[7:9]); return n if 1 <= n <= 22 else 0
    c = c[3:] if c.startswith("chr") else c
    return int(c) if c.isdigit() and 1 <= int(c) <= 22 else 0
want = set()
for smp in samples:
    with gzip.open(smp, "rt") as f:
        for ln in f:
            if ln[0] == "#": continue
            c, p = ln.split("\t", 2)[:2]
            want.add(cnum(c) * 1_000_000_000 + int(p))
print(f"{len(want):,} positions from {samples}", flush=True)
t0 = time.time(); n = k = 0; cache = {}
with gzip.open(src, "rb") as g, open(out + ".part", "w") as o:
    for ln in g:
        n += 1
        if ln[:1] == b"#": continue
        c, p, rest = ln.split(b"\t", 2)
        cn = cache.get(c)
        if cn is None: cn = cache[c] = cnum(c.decode())
        if not cn or cn * 1_000_000_000 + int(p) not in want: continue
        f = rest.split(b"\t", 3)
        o.write(f"chr{cn}\t{int(p)}\t{f[1].decode()}\t{f[2].decode()}\t{f[0].decode()}\n"); k += 1
        if n % 50_000_000 == 0: print(f"  {n:,} lines, {k:,} kept, {time.time()-t0:.0f}s, at {c.decode()}", flush=True)
import os; os.replace(out + ".part", out)
print(f"done: {n:,} lines, {k:,} kept, {time.time()-t0:.0f}s", flush=True)
