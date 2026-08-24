#!/bin/bash
set -euo pipefail

REPO=/mnt/c/Users/PC/Desktop/llm-mr-discovery-genomics
WORKDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work
OUTDIR="$WORKDIR/data/reference"
cd "$WORKDIR"

echo "=== [3/6] Build the sarek samplesheet ==="
cat > "$WORKDIR/samplesheet.csv" <<EOF
patient,sample,lane,bam,bai
HG002,HG002,L1,${WORKDIR}/chr20_30x.rg.reheader.bam,${WORKDIR}/chr20_30x.rg.reheader.bam.bai
EOF
cat "$WORKDIR/samplesheet.csv"

echo "=== [4/6] Run nf-core/sarek (HaplotypeCaller, same invocation as Article 1) ==="
bash "$REPO/pipeline/run_sarek.sh" \
  --input "$WORKDIR/samplesheet.csv" \
  --outdir "$WORKDIR/sarek_out" \
  --fasta-prefix "${OUTDIR}/chr20" \
  --intervals "${OUTDIR}/chr20_intervals.bed" \
  --step markduplicates

echo "=== [5/6] Locate sarek's VCF and annotate against the real dbSNP138 production bundle ==="
SAREK_VCF=$(find "$WORKDIR/sarek_out" -iname "*.haplotypecaller*.vcf.gz" | head -1)
echo "Sarek output VCF: $SAREK_VCF"
DBSNP138="/mnt/c/Users/PC/AppData/Local/Temp/claude/C--Users-PC/c47bf09f-c65c-4bce-b62a-ffa15b1e2525/scratchpad/dbsnp_pull/gatk_dbsnp138_hg38.vcf.gz"
bcftools index -tf "$SAREK_VCF"
bcftools annotate -a "$DBSNP138" -c ID -O z -o "$WORKDIR/sarek_annotated_dbsnp138.vcf.gz" "$SAREK_VCF"
bcftools index -t "$WORKDIR/sarek_annotated_dbsnp138.vcf.gz"

echo "=== [6/6] Extract annotated rsIDs for cross-reference against the LIVE dbSNP merge ledger ==="
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%ID\n' "$WORKDIR/sarek_annotated_dbsnp138.vcf.gz" \
  | awk '$5 != "."' > "$WORKDIR/sarek_annotated_rsids.tsv"
wc -l "$WORKDIR/sarek_annotated_rsids.tsv"
echo "Done. Next step (run back on the Windows side, reuses existing scripts):"
echo "  cross-reference sarek_annotated_rsids.tsv against candidate_panel_FULLCOV_allele_exact.csv"
echo "  to see how many of THIS REAL PIPELINE RUN's own rsID annotations are already stale today."
