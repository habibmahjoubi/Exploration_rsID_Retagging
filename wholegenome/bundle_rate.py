"""Box 1 rate (a): distinct rsIDs on chr1-22 of each bundle, and how many are retired in the b157
ledger. Bitmaps over the rsID number space keep memory at ~1 GB.
Usage: python bundle_rate.py <bundle.vcf.gz> [<bundle.vcf.gz> ...]"""
import bz2, gzip, re, sys, collections
N = 4_000_000_000  # rsIDs are < 2.5e9 today; headroom
ret = bytearray(N // 8 + 1); build = {}
rx = re.compile(rb'^\{"refsnp_id":"(\d+)".*"proxy_build_id":"(\d+)"')
with bz2.open("refsnp-merged.json.bz2", "rb") as f:
    for ln in f:
        m = rx.match(ln)
        if m:
            i = int(m.group(1)); ret[i >> 3] |= 1 << (i & 7); build[i] = int(m.group(2))
print(f"ledger: {len(build):,} retired rsIDs", flush=True)
def ok(c):
    c = c.decode()
    if c.startswith("NC_0000"): return 1 <= int(c[7:9]) <= 22
    c = c[3:] if c.startswith("chr") else c
    return c.isdigit() and 1 <= int(c) <= 22
for src in sys.argv[1:]:
    seen = bytearray(N // 8 + 1); n = r = 0; byb = collections.Counter(); okc = {}
    with gzip.open(src, "rb") as g:
        for ln in g:
            if ln[:1] == b"#": continue
            c, _, idf, _ = ln.split(b"\t", 3)
            if okc.setdefault(c, ok(c)) is False: continue
            for x in idf.split(b";"):
                if x[:2] != b"rs": continue
                i = int(x[2:]); b, m = i >> 3, 1 << (i & 7)
                if seen[b] & m: continue
                seen[b] |= m; n += 1
                if ret[b] & m: r += 1; byb[build[i]] += 1
    print(f"{src}: distinct chr1-22 rsIDs {n:,}; retired {r:,} = {100*r/n:.3f}%; by retiring build {dict(sorted(byb.items()))}", flush=True)
