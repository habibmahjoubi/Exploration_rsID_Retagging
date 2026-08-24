#!/bin/bash
set -euo pipefail
WORKDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work
cd "$WORKDIR"
echo "Adding read group to chr20_30x.bam and re-sorting by coordinate..."
samtools addreplacerg -r '@RG\tID:HG002\tSM:HG002\tLB:lib1\tPL:ILLUMINA' \
  -o chr20_30x.rg.unsorted.bam chr20_30x.bam
samtools sort -@ 4 -o chr20_30x.rg.bam chr20_30x.rg.unsorted.bam
rm -f chr20_30x.rg.unsorted.bam
samtools index chr20_30x.rg.bam
echo "Done. New BAM: $WORKDIR/chr20_30x.rg.bam"
samtools view -H chr20_30x.rg.bam | grep -E "^@HD|^@RG"
