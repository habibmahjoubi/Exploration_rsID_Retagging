#!/bin/bash
# Real nf-core/sarek pipeline validation for the rsID-retagging paper.
#
# Goal: replace the GIAB-truth-VCF stand-in (documented limitation, Section 6.2
# of the manuscript) with an ACTUAL pipeline output -- call variants for chr20
# HG002 with nf-core/sarek (same tool/version as Article 1's own study),
# annotate them against a real production dbSNP bundle, and check whether the
# pipeline's own output would carry a stale rsID.
#
# Prerequisites (to verify once WSL/Docker are back up -- this session hit a
# WSL/Hyper-V hang that required a Windows restart to clear):
#   - WSL2 Ubuntu distro responsive (wsl -l should return instantly)
#   - Docker Desktop running, with WSL integration enabled for this distro
#     (Docker Desktop > Settings > Resources > WSL Integration)
#   - Nextflow installed in WSL (curl -s https://get.nextflow.io | bash --
#     this FAILS on native Windows/Git Bash, must run inside WSL)
#   - bcftools available (conda install -c bioconda bcftools, or apt)
#   - ~15-20GB free disk for sarek's Docker images + intermediate files
#
# Run this INSIDE WSL (not Git Bash / PowerShell), e.g.:
#   wsl -d Ubuntu -- bash /mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/run_full_pipeline.sh

set -euo pipefail

REPO=/mnt/c/Users/PC/Desktop/llm-mr-discovery-genomics
WORKDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "=== [0/6] Sanity checks ==="
command -v nextflow >/dev/null || { echo "Nextflow not found -- install first (see header)."; exit 1; }
command -v docker >/dev/null || { echo "docker CLI not found in WSL -- enable Docker Desktop WSL integration."; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker engine not reachable from WSL -- start Docker Desktop first."; exit 1; }
command -v samtools >/dev/null || { echo "samtools not found -- conda install -c bioconda samtools"; exit 1; }
command -v bcftools >/dev/null || { echo "bcftools not found -- conda install -c bioconda bcftools"; exit 1; }

echo "=== [1/6] Measure raw chr20 depth to compute the 30x downsample fraction ==="
GIAB_BAM_URL="https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/HG002_NA24385_son/NIST_Illumina_2x250bps/novoalign_bams/HG002.GRCh38.2x250.bam"
# samtools depth on a subsample of chr20 positions (every 1000th base) to estimate mean depth cheaply
RAW_DEPTH=$(samtools depth -r chr20:1000000-2000000 "$GIAB_BAM_URL" 2>/dev/null | awk '{sum+=$3; n++} END {if (n>0) print sum/n; else print "NA"}')
echo "Measured raw depth (chr20:1-2Mb sample): $RAW_DEPTH"
if [ "$RAW_DEPTH" = "NA" ] || [ -z "$RAW_DEPTH" ]; then
  echo "Could not measure depth remotely -- inspect manually and set DOWNSAMPLE_FRACTION by hand below."
  exit 1
fi
DOWNSAMPLE_FRACTION=$(python3 -c "print(f'{min(1.0, 30.0/$RAW_DEPTH):.8f}'.split('.', 1)[1])")
echo "Computed DOWNSAMPLE_FRACTION=$DOWNSAMPLE_FRACTION (samtools -s arg will be \${DOWNSAMPLE_SEED}.${DOWNSAMPLE_FRACTION})"

echo "=== [2/6] Prepare reference + reads (Article 1's own script, unmodified) ==="
export CHROM=20
export OUTDIR="$WORKDIR/data/reference"
export DOWNSAMPLE_FRACTION
bash "$REPO/pipeline/prepare_reference.sh"

echo "=== [3/6] Build the sarek samplesheet ==="
cat > "$WORKDIR/samplesheet.csv" <<EOF
patient,sample,lane,bam,bai
HG002,HG002,L1,${WORKDIR}/chr20_30x.bam,${WORKDIR}/chr20_30x.bam.bai
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
