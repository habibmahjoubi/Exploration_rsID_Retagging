"""Genome-wide retirement-date distribution of merged rsIDs (refsnp-merged.json.bz2, b157)."""
import bz2, re, sys, collections
pt = re.compile(rb'"merged_snapshot_data":\{"proxy_time":"(\d{4})[^"]*","proxy_build_id":"(\d+)"')
cit = re.compile(rb'"citations":\[(\d)')
year = collections.Counter(); build = collections.Counter(); cited_year = collections.Counter()
n = bad = 0
with bz2.open(sys.argv[1], "rb") as f:
    for ln in f:
        n += 1
        m = pt.search(ln)
        if not m:
            bad += 1; continue
        y, b = m.group(1).decode(), int(m.group(2))
        year[y] += 1; build[b] += 1
        if cit.search(ln): cited_year[y] += 1
        if n % 2_000_000 == 0: print(f"  {n:,}", file=sys.stderr, flush=True)
print(f"records={n} unparsed={bad}")
print("year\tretired_rsids\twith_citations")
for y in sorted(year): print(f"{y}\t{year[y]}\t{cited_year[y]}")
print("build\tretired_rsids")
for b in sorted(build): print(f"{b}\t{build[b]}")
