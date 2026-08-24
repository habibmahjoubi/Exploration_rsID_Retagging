"""Single full-coverage pass over refsnp-chr20.json.bz2 (streamed via stdin from
curl|bzip2 -dc, no intermediate disk file) that does BOTH the merge-rate audit
AND allele-exact (SNV, POS+REF+ALT) candidate-panel construction in one go, so
we don't need a second ~1h full-file pass. Writes the full candidate panel
(every allele-exact match with a non-empty merge history, any date) to CSV.
"""
import sys, json, csv

giab_exact = {}
n_giab_snv = 0
n_giab_indel = 0
with open("chr20_giab.vcf", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        chrom, pos, vid, ref, alt = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
        for a in alt.split(","):
            if len(ref) == 1 and len(a) == 1:
                giab_exact[(pos, ref, a)] = True
                n_giab_snv += 1
            else:
                n_giab_indel += 1

sys.stderr.write(f"GIAB chr20: {n_giab_snv} SNV alleles, {n_giab_indel} indel alleles (excluded)\n")

out = csv.writer(open("candidate_panel_FULLCOV_allele_exact.csv", "w", newline="", encoding="utf-8"))
out.writerow(["current_rsid", "chr20_position", "ref", "alt", "n_merges", "merged_from_rsids", "merge_dates"])

total_records = 0
chr20_records = 0
matched_exact_any_merge_status = 0
matched_exact_with_merges = 0
matched_exact_no_merges = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except json.JSONDecodeError:
        continue
    total_records += 1

    psd = rec.get("primary_snapshot_data", {})
    placements = psd.get("placements_with_allele", [])
    is_chr20 = False
    exact_hit = None
    for p in placements:
        if p.get("seq_id") != "NC_000020.11":
            continue
        is_chr20 = True
        for a in p.get("alleles", []):
            spdi = a.get("allele", {}).get("spdi", {})
            pos0 = spdi.get("position")
            deleted = spdi.get("deleted_sequence", "")
            inserted = spdi.get("inserted_sequence", "")
            if pos0 is None or deleted == inserted:
                continue
            if len(deleted) != 1 or len(inserted) != 1:
                continue
            pos1 = pos0 + 1
            key = (pos1, deleted, inserted)
            if key in giab_exact:
                exact_hit = key
    if is_chr20:
        chr20_records += 1
    if not exact_hit:
        continue

    matched_exact_any_merge_status += 1
    merges = rec.get("dbsnp1_merges", [])
    if merges:
        matched_exact_with_merges += 1
        pos1, ref, alt = exact_hit
        out.writerow([
            rec.get("refsnp_id"), pos1, ref, alt,
            len(merges),
            ";".join(m["merged_rsid"] for m in merges),
            ";".join(m["merge_date"] for m in merges),
        ])
    else:
        matched_exact_no_merges += 1

print(f"Total JSON records parsed: {total_records}")
print(f"Records with a chr20 placement: {chr20_records}")
print(f"Allele-exact GIAB matches (any merge status): {matched_exact_any_merge_status}")
print(f"  -> WITH merge history: {matched_exact_with_merges}")
print(f"  -> WITHOUT merge history: {matched_exact_no_merges}")
if matched_exact_any_merge_status:
    print(f"Allele-exact merge rate: {matched_exact_with_merges/matched_exact_any_merge_status*100:.2f}%")
