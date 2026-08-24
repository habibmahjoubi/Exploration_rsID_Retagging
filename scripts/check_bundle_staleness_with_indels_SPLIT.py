"""Same as check_bundle_staleness_with_indels.py but reports SNV and indel
categories separately (full-coverage finalization, Section 5.7)."""
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

cats = {"snv": defaultdict(int), "indel": defaultdict(int)}

with open(candidates_file, encoding="utf-8") as f:
    for line in f:
        pos, ref, alt, current, old_ids, dates = line.rstrip("\n").split("\t")
        old_list = set(old_ids.split(";"))
        is_indel = not (len(ref) == 1 and len(alt) == 1)
        key = "indel" if is_indel else "snv"
        c = cats[key]
        c["total"] += 1
        ids_here = bundle.get((int(pos), ref, alt))
        if not ids_here:
            c["not_in_bundle"] += 1
            continue
        has_current = current in ids_here
        has_old = bool(ids_here & old_list)
        if has_current and has_old:
            c["both"] += 1
        elif has_current:
            c["current"] += 1
        elif has_old:
            c["stale"] += 1
        else:
            c["neither"] += 1

print(f"=== {bundle_file} vs {candidates_file} ===")
for key in ("snv", "indel"):
    c = cats[key]
    t = c["total"]
    print(f"-- {key.upper()} (n={t}) --")
    print(f"   ONLY old (STALE):   {c['stale']:4d} ({c['stale']/t*100:.2f}%)")
    print(f"   BOTH (ambiguous):   {c['both']:4d} ({c['both']/t*100:.2f}%)")
    print(f"   ONLY current:       {c['current']:4d} ({c['current']/t*100:.2f}%)")
    print(f"   Not in bundle:      {c['not_in_bundle']:4d} ({c['not_in_bundle']/t*100:.2f}%)")
    print(f"   Neither (mismatch): {c['neither']:4d} ({c['neither']/t*100:.2f}%)")
print()
