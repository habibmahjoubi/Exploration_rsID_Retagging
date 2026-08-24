import pysam

expected = {}
with open("/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work/ambiguous_63_expected.tsv") as f:
    next(f)
    for line in f:
        pos, ref, alt, current, old = line.rstrip("\n").split("\t")
        expected[int(pos)] = (current, old)

bcftools_result = {}
with open("/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work/ambiguous_63_bcftools_out.vcf") as f:
    for line in f:
        if line.startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        bcftools_result[int(parts[1])] = parts[2].replace("rs", "")

vcf = pysam.VariantFile("/mnt/c/Users/PC/AppData/Local/Temp/claude/C--Users-PC/c47bf09f-c65c-4bce-b62a-ffa15b1e2525/scratchpad/dbsnp_pull/gdc_dbsnp144_hg38.vcf.gz")

n_current = n_old = n_other = n_multi_records = 0
pysam_result = {}
for pos, (current, old) in sorted(expected.items()):
    recs = list(vcf.fetch("chr20", pos - 1, pos))
    if len(recs) > 1:
        n_multi_records += 1
    first = recs[0] if recs else None
    rid = (first.id or ".").replace("rs", "") if first else "."
    pysam_result[pos] = rid
    if rid == current:
        n_current += 1
    elif rid == old:
        n_old += 1
    else:
        n_other += 1
        print("OTHER case:", pos, current, old, "got:", rid, [r.id for r in recs])

print(f"pysam .fetch() returns >1 record at position: {n_multi_records}/{len(expected)}")
print(f"naive first()-record pattern picked CURRENT: {n_current}, OLD (stale): {n_old}, other: {n_other}")

agree = sum(1 for pos in expected if bcftools_result.get(pos) == pysam_result.get(pos))
print(f"bcftools vs pysam-naive-first agree on: {agree}/{len(expected)}")
