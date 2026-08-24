"""Candidate panel construction including indels: uses normalize.normalize()
to convert both GIAB's VCF-style (POS,REF,ALT) and dbSNP's SPDI
(position0,deleted,inserted) to the same minimal comparable form, so SNVs
AND indels can be matched exactly (extends build_candidate_panel_allele_exact.py,
which excluded indels entirely).
"""
import sys, json, csv
from normalize import normalize

# ---- load real GIAB HG002 chr20 variants, SNV + indel, normalized ----
giab_exact = {}
n_snv = 0
n_indel = 0
with open("chr20_giab.vcf", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 5:
            continue
        chrom, pos, vid, ref, alt = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
        for a in alt.split(","):
            npos, ndel, nins = normalize(pos, ref, a)
            giab_exact[(npos, ndel, nins)] = True
            if len(ndel) == 1 and len(nins) == 1:
                n_snv += 1
            else:
                n_indel += 1

sys.stderr.write(f"GIAB chr20 (normalized): {n_snv} SNV-like alleles, {n_indel} indel alleles -- ALL included\n")

out = csv.writer(open("candidate_panel_with_indels.csv", "w", newline="", encoding="utf-8"))
out.writerow(["current_rsid", "norm_pos0", "norm_del", "norm_ins", "is_indel", "n_merges", "merged_from_rsids", "merge_dates"])

total = 0
written_exact = 0
written_indel = 0

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
    for p in psd.get("placements_with_allele", []):
        if p.get("seq_id") != "NC_000020.11":
            continue
        for a in p.get("alleles", []):
            spdi = a.get("allele", {}).get("spdi", {})
            pos0 = spdi.get("position")
            deleted = spdi.get("deleted_sequence", "")
            inserted = spdi.get("inserted_sequence", "")
            if pos0 is None or deleted == inserted:
                continue
            # reinterpret SPDI (0-based) as 1-based VCF-style input to normalize(),
            # which is a documented no-op/passthrough for already-minimal SPDI
            npos, ndel, nins = normalize(pos0 + 1, deleted, inserted)
            key = (npos, ndel, nins)
            if key in giab_exact:
                exact_hit = key

    if exact_hit:
        written_exact += 1
        npos, ndel, nins = exact_hit
        is_indel = not (len(ndel) == 1 and len(nins) == 1)
        if is_indel:
            written_indel += 1
        out.writerow([
            rec.get("refsnp_id"), npos, ndel, nins, int(is_indel),
            len(merges),
            ";".join(m["merged_rsid"] for m in merges),
            ";".join(m["merge_date"] for m in merges),
        ])

sys.stderr.write(f"Total records scanned: {total}\n")
sys.stderr.write(f"Candidates written (exact match, SNV+indel, with merge history): {written_exact}\n")
sys.stderr.write(f"  -> of which are indels: {written_indel}\n")
