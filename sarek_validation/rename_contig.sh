#!/bin/bash
set -euo pipefail
OUTDIR=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work/data/reference
cd "$OUTDIR"
echo "Renaming FASTA contig 20 -> chr20 (to match GIAB BAM / intervals.bed naming)..."
sed -i '1s/^>20 />chr20 /' chr20.fa
rm -f chr20.fa.fai chr20.dict
samtools faidx chr20.fa
env PATH=/home/hm/bin:/home/hm/tools/gatk-4.5.0.0:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  gatk CreateSequenceDictionary -R chr20.fa -O chr20.dict
echo "--- new .fai ---"
cat chr20.fa.fai
echo "--- new .dict ---"
cat chr20.dict
