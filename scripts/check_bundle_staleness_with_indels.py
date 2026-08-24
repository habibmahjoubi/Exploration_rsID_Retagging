"""Bundle staleness check including indels: normalizes the bundle's VCF-style
(pos,ref,alt) via normalize.normalize() before matching, so indels compare
correctly against the SPDI-normalized candidate panel. Retains ALL identifiers
seen at a normalized key (the duplicate-key fix from the critical review).
"""
import sys
from collections import defaultdict
from normalize import normalize

bundle_file = sys.argv[1]
candidates_file = sys.argv[2]

bundle = defaultdict(set)
with open(bundle_file, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 4:
            continue
        pos, ref, alt, rid = parts
        for a in alt.split(","):
            npos, ndel, nins = normalize(int(pos), ref, a)
            bundle[(npos, ndel, nins)].add(rid.replace("rs", ""))

total = 0
matches_current = 0
matches_old = 0
matches_both = 0
matches_neither = 0
not_in_bundle = 0
n_indel_total = 0
n_indel_stale = 0

with open(candidates_file, encoding="utf-8") as f:
    for line in f:
        pos, ref, alt, current, old_ids, dates = line.rstrip("\n").split("\t")
        old_list = set(old_ids.split(";"))
        is_indel = not (len(ref) == 1 and len(alt) == 1)
        total += 1
        if is_indel:
            n_indel_total += 1
        ids_here = bundle.get((int(pos), ref, alt))
        if not ids_here:
            not_in_bundle += 1
            continue
        has_current = current in ids_here
        has_old = bool(ids_here & old_list)
        if has_current and has_old:
            matches_both += 1
        elif has_current:
            matches_current += 1
        elif has_old:
            matches_old += 1
            if is_indel:
                n_indel_stale += 1
        else:
            matches_neither += 1

print(f"=== {bundle_file} vs {candidates_file} (WITH INDELS, normalized) ===")
print("Total candidates tested:", total, f"(indels: {n_indel_total})")
print("Not present in bundle:", not_in_bundle)
print("ONLY current:", matches_current)
print("ONLY old (STALE):", matches_old, f"({matches_old/total*100:.2f}%)",
      f"-- of which indels: {n_indel_stale}")
print("BOTH (ambiguous):", matches_both, f"({matches_both/total*100:.2f}%)")
print("Neither:", matches_neither)
