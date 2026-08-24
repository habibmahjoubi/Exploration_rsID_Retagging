#!/bin/bash
BAM=/mnt/c/Users/PC/Desktop/Exploration_rsID_Retagging/sarek_validation/work/chr20_30x.bam
echo "--- @RG header lines ---"
samtools view -H "$BAM" | grep "^@RG"
echo "--- sample of read RG tags (first 5 reads) ---"
samtools view "$BAM" | head -5 | grep -o "RG:Z:[^	]*"
echo "--- count reads missing RG tag (first 100000 checked) ---"
samtools view "$BAM" | head -100000 | awk '{if ($0 !~ /RG:Z:/) c++} END {print c+0, "missing out of 100000"}'
