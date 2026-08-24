import sys, json

# Load real GIAB HG002 chr20 truth-variant positions (1-based VCF POS)
giab_positions = {}
with open("chr20_giab.vcf", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        chrom, pos, vid, ref, alt = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
        giab_positions.setdefault(pos, []).append((ref, alt))

sys.stderr.write(f"Loaded {len(giab_positions)} distinct GIAB chr20 positions\n")

total_records = 0
parse_errors = 0
chr20_records = 0
matched_records = 0
matched_with_merges = 0
matched_no_merges = 0
sample_matches_with_merges = []
sample_matches_no_merges = []

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        parse_errors += 1
        continue
    total_records += 1

    psd = rec.get("primary_snapshot_data", {})
    placements = psd.get("placements_with_allele", [])
    positions_1based = set()
    for p in placements:
        if p.get("seq_id") != "NC_000020.11":
            continue
        for a in p.get("alleles", []):
            spdi = a.get("allele", {}).get("spdi", {})
            pos0 = spdi.get("position")
            if pos0 is not None:
                positions_1based.add(pos0 + 1)  # SPDI is 0-based -> VCF 1-based
    if not positions_1based:
        continue
    chr20_records += 1

    hit_positions = positions_1based & giab_positions.keys()
    if not hit_positions:
        continue
    matched_records += 1
    merges = rec.get("dbsnp1_merges", [])
    if merges:
        matched_with_merges += 1
        if len(sample_matches_with_merges) < 8:
            sample_matches_with_merges.append((rec.get("refsnp_id"), sorted(hit_positions), merges))
    else:
        matched_no_merges += 1
        if len(sample_matches_no_merges) < 5:
            sample_matches_no_merges.append((rec.get("refsnp_id"), sorted(hit_positions)))

print(f"Total JSON records parsed: {total_records}")
print(f"Parse errors (trailing truncated line etc.): {parse_errors}")
print(f"Records with a chr20 (NC_000020.11) placement: {chr20_records}")
print(f"Records matching a real GIAB HG002 chr20 variant position: {matched_records}")
print(f"  -> of which WITH merge history (dbsnp1_merges non-empty): {matched_with_merges}")
print(f"  -> of which with NO merge history: {matched_no_merges}")
if matched_records:
    print(f"Merge rate among GIAB-matched real variants: {matched_with_merges/matched_records*100:.2f}%")
print()
print("Sample GIAB-matched variants WITH merge history:")
for rid, pos, m in sample_matches_with_merges:
    print(f"  rs{rid} @ chr20:{pos} -> merged from {[x['merged_rsid'] for x in m]} (dates: {[x['merge_date'] for x in m]})")
print()
print("Sample GIAB-matched variants with NO merge history:")
for rid, pos in sample_matches_no_merges:
    print(f"  rs{rid} @ chr20:{pos}")
