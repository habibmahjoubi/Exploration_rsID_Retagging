"""Generic version of check_gatk_bundle_staleness.py -- takes the bundle's
chr20 idmap file as argv[1] so the same logic can be run against dbSNP138,
dbSNP144, or any other GRCh38 chr20 position->ID map, for a multi-version
staleness comparison.
"""
import sys

idmap_file = sys.argv[1]
candidates_file = sys.argv[2] if len(sys.argv) > 2 else "recent_candidates_2014_2017.txt"

idmap = {}
with open(idmap_file, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 2:
            continue
        pos, rid = parts
        idmap.setdefault(pos, []).append(rid)

total = 0
matches_current = 0
matches_old = 0
matches_neither = 0
not_in_bundle = 0
stale_examples = []

with open(candidates_file, encoding="utf-8") as f:
    for line in f:
        pos, current, old_ids, dates = line.rstrip("\n").split("\t")
        old_list = old_ids.split(";")
        total += 1
        ids_here = idmap.get(pos)
        if not ids_here:
            not_in_bundle += 1
            continue
        ids_here_clean = [i.replace("rs", "") for i in ids_here]
        if current in ids_here_clean:
            matches_current += 1
        elif any(o in ids_here_clean for o in old_list):
            matches_old += 1
            stale_examples.append((pos, current, old_list, ids_here, dates))
        else:
            matches_neither += 1

print(f"=== {idmap_file} vs {candidates_file} ===")
print("Total candidates tested:", total)
print("Position not present in bundle:", not_in_bundle)
print("Bundle shows CURRENT (post-merge) rsID:", matches_current)
print("Bundle shows OLD (pre-merge/stale) rsID:", matches_old, f"({matches_old/total*100:.2f}%)")
print("Bundle shows a different identifier:", matches_neither)
print()
for ex in stale_examples[:10]:
    print(" STALE:", ex)
