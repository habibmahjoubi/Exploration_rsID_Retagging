"""Rebuild the candidate panel with allele-exact matching (POS+REF+ALT) instead
of position-only matching, restricted to SNVs (both REF and ALT length 1) where
the SPDI<->VCF correspondence is unambiguous. Indels are counted separately and
excluded from the exact-match panel (documented simplification -- SPDI's anchor
convention for indels does not map 1:1 onto VCF's left-padded convention without
extra normalization work).
"""
import sys, json, csv

# ---- load real GIAB HG002 chr20 variants keyed by (pos, ref, alt) ----
giab_exact = {}
giab_positions_only = {}
n_giab_snv = 0
n_giab_indel = 0
with open("chr20_giab.vcf", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        chrom, pos, vid, ref, alt = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
        giab_positions_only.setdefault(pos, []).append((ref, alt))
        # multi-allelic ALT (comma-separated) -- register each allele separately
        for a in alt.split(","):
            if len(ref) == 1 and len(a) == 1:
                giab_exact[(pos, ref, a)] = True
                n_giab_snv += 1
            else:
                n_giab_indel += 1

sys.stderr.write(f"GIAB chr20: {n_giab_snv} SNV alleles, {n_giab_indel} indel alleles (excluded from exact panel)\n")
sys.stderr.write(f"GIAB distinct positions (any type): {len(giab_positions_only)}\n")

out = csv.writer(open("candidate_panel_allele_exact.csv", "w", newline="", encoding="utf-8"))
out.writerow(["current_rsid", "chr20_position", "ref", "alt", "n_merges", "merged_from_rsids", "merge_dates"])

total = 0
written_exact = 0
written_position_only_would_have_matched = 0
skipped_indel_or_ref_allele = 0

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
    exact_hit = None
    position_only_hit = False
    for p in psd.get("placements_with_allele", []):
        if p.get("seq_id") != "NC_000020.11":
            continue
        for a in p.get("alleles", []):
            spdi = a.get("allele", {}).get("spdi", {})
            pos0 = spdi.get("position")
            deleted = spdi.get("deleted_sequence", "")
            inserted = spdi.get("inserted_sequence", "")
            if pos0 is None:
                continue
            pos1 = pos0 + 1
            if deleted == inserted:
                continue  # reference-allele placeholder entry, not a variant
            if len(deleted) != 1 or len(inserted) != 1:
                skipped_indel_or_ref_allele += 1
                if pos1 in giab_positions_only:
                    position_only_hit = True
                continue
            key = (pos1, deleted, inserted)
            if key in giab_exact:
                exact_hit = (pos1, deleted, inserted)
            elif pos1 in giab_positions_only:
                position_only_hit = True

    if exact_hit:
        written_exact += 1
        pos1, ref, alt = exact_hit
        out.writerow([
            rec.get("refsnp_id"), pos1, ref, alt,
            len(merges),
            ";".join(m["merged_rsid"] for m in merges),
            ";".join(m["merge_date"] for m in merges),
        ])
    elif position_only_hit:
        written_position_only_would_have_matched += 1

sys.stderr.write(f"Total records scanned: {total}\n")
sys.stderr.write(f"Candidates written (ALLELE-EXACT match, SNV only): {written_exact}\n")
sys.stderr.write(f"Would-have-matched under POSITION-ONLY but NOT allele-exact "
                  f"(different allele or indel at same position): {written_position_only_would_have_matched}\n")
sys.stderr.write(f"Indel/ref-placeholder SPDI entries skipped from exact scoring: {skipped_indel_or_ref_allele}\n")
