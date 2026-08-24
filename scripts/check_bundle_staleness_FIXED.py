"""Fixed version of check_bundle_staleness_allele_exact.py: keeps ALL rsIDs
seen at a given (pos, ref, alt) key (some bundle files have multiple dbSNP
records colliding on the same coordinate+allele, e.g. an unresolved duplicate
submission alongside its eventual merge target) instead of silently
overwriting with whichever line appears last in the file.
"""
import sys
from collections import defaultdict

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
            bundle[(pos, ref, a)].add(rid.replace("rs", ""))

total = 0
matches_current = 0
matches_old = 0
matches_both = 0  # both the current AND an old id present at this key (the real anomaly class)
matches_neither = 0
not_in_bundle = 0
both_examples = []

with open(candidates_file, encoding="utf-8") as f:
    for line in f:
        pos, ref, alt, current, old_ids, dates = line.rstrip("\n").split("\t")
        old_list = set(old_ids.split(";"))
        total += 1
        ids_here = bundle.get((pos, ref, alt))
        if not ids_here:
            not_in_bundle += 1
            continue
        has_current = current in ids_here
        has_old = bool(ids_here & old_list)
        if has_current and has_old:
            matches_both += 1
            if len(both_examples) < 10:
                both_examples.append((pos, ref, alt, current, sorted(ids_here & old_list), dates))
        elif has_current:
            matches_current += 1
        elif has_old:
            matches_old += 1
        else:
            matches_neither += 1

print(f"=== {bundle_file} vs {candidates_file} (FIXED: multi-ID per key) ===")
print("Total candidates tested:", total)
print("Position+allele not present in bundle:", not_in_bundle)
print("Bundle shows ONLY current (post-merge) rsID:", matches_current)
print("Bundle shows ONLY old (pre-merge/stale) rsID:", matches_old,
      f"({matches_old/total*100:.2f}%)")
print("Bundle shows BOTH current AND old at the same key (duplicate-submission artifact):", matches_both,
      f"({matches_both/total*100:.2f}%)")
print("Bundle shows neither:", matches_neither)
print()
for ex in both_examples:
    print(" BOTH:", ex)
