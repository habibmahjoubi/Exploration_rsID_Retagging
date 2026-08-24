"""Cross-reference candidates with a recent (2014-2017) dbSNP merge against the real
GATK dbSNP138 GRCh38 known-sites bundle, to check whether the bundle still reports
the pre-merge (stale) rsID at that genomic position -- a real, currently-deployed
downstream-impact demonstration of the taxid-retagging-style artifact (Paper A),
applied to rsID/dbSNP instead of taxid/NCBI Taxonomy.

Inputs (must exist in the working directory):
  - gatk_dbsnp138_chr20_idmap.tsv : "POS\\tID" for every chr20 line of
    Homo_sapiens_assembly38.dbsnp138.vcf.gz (gcp-public-data--broad-references bucket)
  - recent_candidates_2014_2017.txt : "POS\\tcurrent_rsid\\told_rsids;...\\tdates;..."
    extracted from candidate_panel_full.csv (build_candidate_panel.py)
"""

idmap = {}
with open("gatk_dbsnp138_chr20_idmap.tsv", encoding="utf-8") as f:
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

with open("recent_candidates_2014_2017.txt", encoding="utf-8") as f:
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

print("Total 2014-2017 candidates tested:", total)
print("Position not present at all in GATK dbSNP138 bundle:", not_in_bundle)
print("Bundle shows the CURRENT (post-merge) rsID:", matches_current)
print("Bundle shows an OLD (pre-merge / stale) rsID <-- downstream-impact case:", matches_old)
print("Bundle shows neither (different ID entirely):", matches_neither)
print()
print("Stale examples (bundle still shows an old, since-merged rsID):")
for ex in stale_examples:
    print(" ", ex)
