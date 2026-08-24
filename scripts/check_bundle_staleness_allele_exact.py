"""Allele-exact version of check_bundle_staleness_generic.py: matches on
(POS, REF, ALT) instead of POS alone, using a bundle's full chr20 TSV
(POS\tREF\tALT\tID) and the allele-exact candidates file (POS\tREF\tALT\t
current_rsid\told_rsids;...\tdates;...).
"""
import sys

bundle_file = sys.argv[1]
candidates_file = sys.argv[2]

# bundle: (pos, ref, alt) -> id  (handle multi-allelic ALT by registering each)
bundle = {}
with open(bundle_file, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 4:
            continue
        pos, ref, alt, rid = parts
        for a in alt.split(","):
            bundle[(pos, ref, a)] = rid

total = 0
matches_current = 0
matches_old = 0
matches_neither = 0
not_in_bundle = 0
stale_examples = []

with open(candidates_file, encoding="utf-8") as f:
    for line in f:
        pos, ref, alt, current, old_ids, dates = line.rstrip("\n").split("\t")
        old_list = old_ids.split(";")
        total += 1
        rid = bundle.get((pos, ref, alt))
        if rid is None:
            not_in_bundle += 1
            continue
        rid_clean = rid.replace("rs", "")
        if rid_clean == current:
            matches_current += 1
        elif rid_clean in old_list:
            matches_old += 1
            stale_examples.append((pos, ref, alt, current, rid, dates))
        else:
            matches_neither += 1

print(f"=== {bundle_file} vs {candidates_file} (ALLELE-EXACT) ===")
print("Total candidates tested:", total)
print("Position+allele not present in bundle:", not_in_bundle)
print("Bundle shows CURRENT (post-merge) rsID:", matches_current)
print("Bundle shows OLD (pre-merge/stale) rsID:", matches_old,
      f"({matches_old/total*100:.2f}%)" if total else "")
print("Bundle shows a different identifier (SAME allele, still unexplained):", matches_neither)
print()
for ex in stale_examples[:10]:
    print(" STALE:", ex)
