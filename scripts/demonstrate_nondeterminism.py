"""B1 (critical review): concrete demonstration that the 63 dbSNP144 ambiguous
sites (Section 5.6) produce different answers under forward vs reverse VCF
traversal order alone, with file content unchanged. See results/15 for the
full write-up; this script is the reproducible source of that result.
"""
from collections import defaultdict

lines = open("gdc_dbsnp144_chr20_full.tsv", encoding="utf-8").readlines()

def naive_last_wins(line_iter):
    d = {}
    for line in line_iter:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 4:
            continue
        pos, ref, alt, rid = parts
        for a in alt.split(","):
            d[(pos, ref, a)] = rid
    return d

forward = naive_last_wins(lines)
backward = naive_last_wins(reversed(lines))

diffs = 0
examples = []
with open("recent_candidates_2014_2017_FULLCOV.txt", encoding="utf-8") as f:
    for line in f:
        pos, ref, alt, current, old_ids, dates = line.rstrip("\n").split("\t")
        key = (pos, ref, alt)
        fwd = forward.get(key)
        bwd = backward.get(key)
        if fwd and bwd and fwd != bwd:
            diffs += 1
            examples.append((pos, ref, alt, current, fwd, bwd))

print("Ambiguous sites where forward-order vs reverse-order naive parsing disagree:", diffs)
for e in examples:
    print(" ", e)
