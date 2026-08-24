#!/bin/bash
set -euo pipefail
WORKDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work
cd "$WORKDIR"

echo "Filtering header to chr20-only via text SAM round-trip (name-based tid resolution)..."
samtools view -h chr20_30x.rg.bam \
  | awk '/^@SQ/{if ($0 ~ /SN:chr20\t/) print; next} {print}' \
  | samtools view -b -o chr20_30x.rg.reheader.bam -

echo "Indexing..."
samtools index chr20_30x.rg.reheader.bam

echo "--- new header ---"
samtools view -H chr20_30x.rg.reheader.bam

echo "--- sanity: reads with RNEXT referencing a contig no longer in header? ---"
samtools view chr20_30x.rg.reheader.bam | awk '$7!="=" && $7!="chr20" && $7!="*"' | wc -l

echo "Done: $WORKDIR/chr20_30x.rg.reheader.bam"
