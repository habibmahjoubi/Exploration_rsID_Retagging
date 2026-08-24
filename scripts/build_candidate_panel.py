import sys, json, csv

giab_positions = {}
with open("chr20_giab.vcf", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        chrom, pos, vid, ref, alt = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
        giab_positions.setdefault(pos, []).append((ref, alt))

sys.stderr.write(f"Loaded {len(giab_positions)} distinct GIAB chr20 positions\n")

out = csv.writer(open("candidate_panel_full.csv", "w", newline="", encoding="utf-8"))
out.writerow(["current_rsid", "chr20_position", "n_merges", "merged_from_rsids", "merge_dates"])

total = 0
written = 0
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        continue
    total += 1
    merges = rec.get("dbsnp1_merges", [])
    if not merges:
        continue
    psd = rec.get("primary_snapshot_data", {})
    positions_1based = set()
    for p in psd.get("placements_with_allele", []):
        if p.get("seq_id") != "NC_000020.11":
            continue
        for a in p.get("alleles", []):
            spdi = a.get("allele", {}).get("spdi", {})
            pos0 = spdi.get("position")
            if pos0 is not None:
                positions_1based.add(pos0 + 1)
    hit = positions_1based & giab_positions.keys()
    if not hit:
        continue
    written += 1
    out.writerow([
        rec.get("refsnp_id"),
        ";".join(str(p) for p in sorted(hit)),
        len(merges),
        ";".join(m["merged_rsid"] for m in merges),
        ";".join(m["merge_date"] for m in merges),
    ])

sys.stderr.write(f"Total records scanned: {total}\n")
sys.stderr.write(f"Candidates written (real GIAB variant + merge history): {written}\n")
