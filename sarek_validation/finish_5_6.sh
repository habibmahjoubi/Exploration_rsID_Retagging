#!/bin/bash
set -euo pipefail
WORKDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work
cd "$WORKDIR"

echo "=== [5/6] Locate sarek's VCF and annotate against the real dbSNP138 production bundle ==="
SAREK_VCF=$(find "$WORKDIR/sarek_out" -iname "*.haplotypecaller*.vcf.gz" | head -1)
echo "Sarek output VCF: $SAREK_VCF"
DBSNP138="/mnt/c/Users/PC/AppData/Local/Temp/claude/C--Users-PC/c47bf09f-c65c-4bce-b62a-ffa15b1e2525/scratchpad/dbsnp_pull/gatk_dbsnp138_hg38.vcf.gz"
bcftools index -tf "$SAREK_VCF"
bcftools annotate -a "$DBSNP138" -c ID -O z -o "$WORKDIR/sarek_annotated_dbsnp138.vcf.gz" "$SAREK_VCF"
bcftools index -tf "$WORKDIR/sarek_annotated_dbsnp138.vcf.gz"

echo "=== [6/6] Extract annotated rsIDs for cross-reference against the LIVE dbSNP merge ledger ==="
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%ID\n' "$WORKDIR/sarek_annotated_dbsnp138.vcf.gz" \
  | awk '$5 != "."' > "$WORKDIR/sarek_annotated_rsids.tsv"
wc -l "$WORKDIR/sarek_annotated_rsids.tsv"
echo "Done."
