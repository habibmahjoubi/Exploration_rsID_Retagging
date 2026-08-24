#!/bin/bash
set -euo pipefail

REPO=/mnt/c/Users/PC/Desktop/llm-mr-discovery-genomics
WORKDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work
OUTDIR="$WORKDIR/data/reference"
DBSNP138="/mnt/c/Users/PC/AppData/Local/Temp/claude/C--Users-PC/c47bf09f-c65c-4bce-b62a-ffa15b1e2525/scratchpad/dbsnp_pull/gatk_dbsnp138_hg38.vcf.gz"
cd "$WORKDIR"

echo "=== Native sarek rerun with --dbsnp (real GATK -D flag, no bcftools substitute) ==="
nextflow run nf-core/sarek -r 3.9.0 -profile docker \
  -c "$REPO/pipeline/resource_limits.config" \
  -resume \
  --step markduplicates \
  --input "$WORKDIR/samplesheet.csv" \
  --outdir "$WORKDIR/sarek_out_native_dbsnp" \
  --fasta "${OUTDIR}/chr20.fa" \
  --fasta_fai "${OUTDIR}/chr20.fa.fai" \
  --dict "${OUTDIR}/chr20.dict" \
  --tools haplotypecaller \
  --skip_tools baserecalibrator,fastqc,multiqc,mosdepth,documentation,versions \
  --wes false \
  --intervals "${OUTDIR}/chr20_intervals.bed" \
  --dbsnp "$DBSNP138" \
  --igenomes_ignore true \
  --max_cpus 8 \
  --max_memory 12.GB

echo "=== Locate native VCF and cross-reference rsIDs against the live dbSNP merge ledger ==="
NATIVE_VCF=$(find "$WORKDIR/sarek_out_native_dbsnp" -iname "*.haplotypecaller*.vcf.gz" | head -1)
echo "Native sarek --dbsnp VCF: $NATIVE_VCF"
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%ID\n' "$NATIVE_VCF" \
  | awk '$5 != "."' > "$WORKDIR/sarek_native_dbsnp_rsids.tsv"
wc -l "$WORKDIR/sarek_native_dbsnp_rsids.tsv"
echo "Done."
