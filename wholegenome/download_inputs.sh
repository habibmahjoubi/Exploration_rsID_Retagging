#!/bin/bash
# Downloads every input of the whole-genome study into this directory (about 40 GB), then checks
# the md5 sums recorded at the time of the analysis (Supplementary Table S1).
# Note: the ClinVar, GWAS Catalog and PharmGKB URLs below point to the releases used
# (8 Nov 2026, 2 Nov 2026, 5 Jul / 5 Nov 2026); "latest" URLs would give newer files.
cd "$(dirname "$0")" || exit 1
B=https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0
GIAB=https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release
./dl.sh $GIAB/NA12878_HG001/NISTv4.2.1/GRCh38/HG001_GRCh38_1_22_v4.2.1_benchmark.vcf.gz HG001_wg.vcf.gz
./dl.sh $GIAB/AshkenazimTrio/HG002_NA24385_son/NISTv4.2.1/GRCh38/HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz HG002_wg.vcf.gz
./dl.sh $GIAB/ChineseTrio/HG005_NA24631_son/NISTv4.2.1/GRCh38/HG005_GRCh38_1_22_v4.2.1_benchmark.vcf.gz HG005_wg.vcf.gz
md5sum -c MD5_samples.txt
./dl.sh https://ftp.ncbi.nlm.nih.gov/snp/latest_release/JSON/refsnp-merged.json.bz2 refsnp-merged.json.bz2
echo "5d9c56c9b8c3412eb0195a63f12e1ebf *refsnp-merged.json.bz2" | md5sum -c   # build 157; a later release will differ
./dl.sh $B/Homo_sapiens_assembly38.dbsnp138.vcf.gz dbsnp138.vcf.gz
./dl.sh $B/gdc/dbsnp_144.hg38.vcf.gz dbsnp144.vcf.gz
./dl.sh https://ngi-igenomes.s3.amazonaws.com/igenomes/Homo_sapiens/GATK/GRCh38/Annotation/GATKBundle/dbsnp_146.hg38.vcf.gz dbsnp146.vcf.gz
./dl.sh https://ftp.ncbi.nlm.nih.gov/snp/archive/b156/VCF/GCF_000001405.40.gz b156.vcf.gz
echo "a1082ca70e15eb63301dfc33b19d0ae7 *b156.vcf.gz" | md5sum -c
cd downstream || exit 1
# ClinVar moves weekly files to vcf_GRCh38/archive_2.0/<year>/ after a few weeks
../dl.sh https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar_20261108.vcf.gz clinvar_GRCh38.vcf.gz
../dl.sh https://ftp.ebi.ac.uk/pub/databases/gwas/releases/2026/11/02/gwas-catalog-associations-full.zip gwas-catalog-associations-full.zip
../dl.sh https://api.clinpgx.org/v1/download/file/data/clinicalAnnotations.zip clinicalAnnotations.zip
../dl.sh https://api.clinpgx.org/v1/download/file/data/variantAnnotations.zip variantAnnotations.zip
md5sum -c MD5SUMS.txt --ignore-missing
unzip -o -q gwas-catalog-associations-full.zip -d gwas-catalog-associations-full
unzip -o -q clinicalAnnotations.zip -d clinicalAnnotations
unzip -o -q variantAnnotations.zip -d variantAnnotations
echo "inputs ready"
