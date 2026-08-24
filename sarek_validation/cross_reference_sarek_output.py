"""Step 7 (run on Windows side once sarek_annotated_rsids.tsv exists): checks
how many of the REAL sarek pipeline's own dbSNP138-annotated rsID calls are
identifiers that the CURRENT, live dbSNP merge ledger has since retired --
i.e., does a real pipeline run, today, actually emit stale identifiers, not
just a hypothetical cross-reference against the GIAB truth set.

Usage: python cross_reference_sarek_output.py sarek_annotated_rsids.tsv

Requires candidate_panel_FULLCOV_allele_exact.csv (built earlier this
session) as the source of "which rsIDs are known retired predecessors, and
what is each one's current successor" -- built from ALL 25.9M chr20 dbSNP
records, not just the GIAB-matched subset, so this works for ANY rsID sarek
happens to emit, not only ones already in our GIAB-derived candidate panel.
"""
import sys, csv, json, urllib.request, time

sarek_tsv = sys.argv[1] if len(sys.argv) > 1 else "sarek_annotated_rsids.tsv"

# Build a retired-id -> current-id lookup from the full merge panel already built.
retired_to_current = {}
panel_path = "C:/Users/PC/AppData/Local/Temp/claude/C--Users-PC/c47bf09f-c65c-4bce-b62a-ffa15b1e2525/scratchpad/dbsnp_pull/candidate_panel_FULLCOV_allele_exact.csv"
try:
    with open(panel_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            current = row["current_rsid"]
            for old in row["merged_from_rsids"].split(";"):
                retired_to_current[old] = current
except FileNotFoundError:
    print(f"NOTE: {panel_path} not found locally -- falling back to live API "
          f"lookups per rsID (slower, rate-limited).", file=sys.stderr)
    retired_to_current = None


def is_retired_live(rsid):
    """Fallback: ask the live dbSNP API directly whether this ID has been merged."""
    url = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{rsid}"
    req = urllib.request.Request(url, headers={"User-Agent": "sarek-validation/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        rec = json.loads(resp.read().decode("utf-8"))
    merged_into = rec.get("merged_snapshot_data", {}).get("merged_into", [])
    return (merged_into[0] if merged_into else None)


total = 0
stale = 0
current_ok = 0
examples = []

with open(sarek_tsv, encoding="utf-8") as f:
    for line in f:
        chrom, pos, ref, alt, rsid_field = line.rstrip("\n").split("\t")
        for rid in rsid_field.replace("rs", "").split(";"):
            total += 1
            if retired_to_current is not None:
                current = retired_to_current.get(rid)
            else:
                current = is_retired_live(rid)
                time.sleep(0.4)
            if current:
                stale += 1
                if len(examples) < 15:
                    examples.append((chrom, pos, ref, alt, rid, current))
            else:
                current_ok += 1

print(f"Total rsID annotations emitted by this real sarek run: {total}")
print(f"  -> STALE (dbSNP has since retired this exact ID sarek just assigned): {stale} "
      f"({stale/total*100:.2f}%)" if total else "  -> no annotations found")
print(f"  -> Still current: {current_ok}")
print()
print("Examples of REAL sarek-called, dbSNP138-annotated variants that are "
      "already stale today:")
for ex in examples:
    print(" ", ex)
