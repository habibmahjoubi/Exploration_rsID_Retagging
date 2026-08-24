"""Point 2.2: build a synthetic 63-record VCF (one per ambiguous dbSNP144
site) with no ID, to feed through bcftools annotate, GATK VariantAnnotator,
and pysam-based naive annotation, and compare what each tool writes into the
ID field when the resource VCF has two colliding records at that position.
"""
rows = []
with open("C:/Users/PC/AppData/Local/Temp/claude/C--Users-PC/c47bf09f-c65c-4bce-b62a-ffa15b1e2525/scratchpad/dbsnp_pull/ambiguous_63_dbsnp144.tsv", encoding="utf-8") as f:
    next(f)
    for line in f:
        pos, ref, alt, current, old = line.rstrip("\n").split("\t")
        rows.append((int(pos), ref, alt, current, old))

rows.sort(key=lambda r: r[0])

header = """##fileformat=VCFv4.2
##FILTER=<ID=PASS,Description="All filters passed">
##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">
##contig=<ID=chr20,length=64444167>
#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tSAMPLE1
"""

with open("C:/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work/ambiguous_63_test.vcf", "w", encoding="utf-8") as f:
    f.write(header)
    for pos, ref, alt, current, old in rows:
        f.write(f"chr20\t{pos}\t.\t{ref}\t{alt}\t.\tPASS\t.\tGT\t0/1\n")

with open("C:/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work/ambiguous_63_expected.tsv", "w", encoding="utf-8") as f:
    f.write("pos\tref\talt\tcurrent_id\told_id\n")
    for pos, ref, alt, current, old in rows:
        f.write(f"{pos}\t{ref}\t{alt}\t{current}\t{old}\n")

print(f"Wrote {len(rows)} records")
