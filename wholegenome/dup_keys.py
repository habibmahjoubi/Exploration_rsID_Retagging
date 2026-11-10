"""Supplementary Note 1: keys (chr1-22, POS, REF, ALT as written in the file) that carry two or more
distinct rsIDs, and how many of them mix a retired and a current rsID (b157 ledger).
Usage: python dup_keys.py <bundle.vcf.gz> [...]"""
import bz2, gzip, re, sys
N = 4_000_000_000
ret = bytearray(N // 8 + 1)
rx = re.compile(rb'^\{"refsnp_id":"(\d+)"')
with bz2.open("refsnp-merged.json.bz2", "rb") as f:
    for ln in f:
        m = rx.match(ln)
        if m: i = int(m.group(1)); ret[i >> 3] |= 1 << (i & 7)
isret = lambda i: ret[i >> 3] >> (i & 7) & 1
def ok(c):
    c = c.decode()
    c = c[3:] if c.startswith("chr") else c
    return c.isdigit() and 1 <= int(c) <= 22
for src in sys.argv[1:]:
    multi = mixed = keys = 0; okc = {}; cur = None; grp = {}
    def flush():
        global multi, mixed, keys
        for ids in grp.values():
            keys += 1
            if len(ids) > 1:
                multi += 1
                r = sum(isret(i) for i in ids)
                if 0 < r < len(ids): mixed += 1
    with gzip.open(src, "rb") as g:
        for ln in g:
            if ln[:1] == b"#": continue
            c, pos, idf, ref, alt = ln.split(b"\t", 5)[:5]
            if okc.setdefault(c, ok(c)) is False: continue
            if (c, pos) != cur:
                flush(); grp = {}; cur = (c, pos)
            ids = [int(x[2:]) for x in idf.split(b";") if x[:2] == b"rs"]
            for a in alt.split(b","):
                grp.setdefault((ref, a), set()).update(ids)
        flush()
    print(f"{src}: keys {keys:,}; keys with >=2 rsIDs {multi:,}; of which retired + current {mixed:,}", flush=True)
