#!/bin/bash
# Whole-genome study: complete order of the analyses, from downloaded inputs to every result file.
# Run from this directory after download_inputs.sh. Each step is skipped if its output exists, so
# the script can be restarted. About 40 GB of inputs; the longest steps (b156 filter and scan,
# bundle_rate.py, dup_keys.py) take several hours each on one core.
# The original run used the same commands, split over several restartable scripts.
cd "$(dirname "$0")" || exit 1
step() { echo "[$(date +%H:%M:%S)] $*"; }
run() { local out=$1; shift; if [ -s "$out" ]; then step "skip $out"; return 0; fi; step "start $out"; "$@" || { step "FAILED $out"; exit 1; }; }
B="d138:dbsnp138.vcf.gz d144:dbsnp144.vcf.gz d146:dbsnp146.vcf.gz b156:b156.vcf.gz"

# 1. keep only the dbSNP records at benchmark positions (wg_ = HG002, wg2_ = HG001 + HG005)
for pair in $B; do
  k=${pair%%:*}; f=${pair#*:}
  run wg_$k.tsv  sh -c "python filter_local.py $f wg_$k.tsv > flog_$k.txt 2>&1"
  run wg2_$k.tsv sh -c "python filter_local.py $f wg2_$k.tsv HG001_wg.vcf.gz HG005_wg.vcf.gz > flog2_$k.txt 2>&1"
done

# 2. annotation and variant rates (Table 1)
run wg_results.json sh -c 'python wg_analysis.py > wg_results.txt 2>&1'
for s in HG001 HG005; do
  run wg_results_$s.json sh -c "python wg_analysis.py ${s}_wg.vcf.gz wg2_ _$s > wg_results_$s.txt 2>&1"
done

# 3. downstream test (Table 2, Table S5): knowledge-base targets, bundle scans, per-genome reports
run downstream/prep.pkl python downstream/downstream_join.py prep
for pair in $B; do
  k=${pair%%:*}; f=${pair#*:}
  run downstream/$k.ids python downstream/downstream_join.py scan $f downstream/$k.ids
done
run downstream/downstream_results.json sh -c 'python downstream/downstream_join.py report > downstream/downstream_results.txt 2>&1'
for s in HG001 HG005; do
  run downstream/downstream_results_$s.json sh -c "python downstream/downstream_join.py report ${s}_wg.vcf.gz wg2_ _$s > downstream/downstream_results_$s.txt 2>&1"
done

# 4. locus check and allele-aware ClinVar test (Table S3, S4, Table 2), live check (Table S9)
run downstream/post_locus_allele_HG002.json sh -c 'python downstream/post_locus_allele.py HG002_wg.vcf.gz wg_ _HG002 > downstream/post_HG002.txt 2>&1'
for s in HG001 HG005; do
  run downstream/post_locus_allele_$s.json sh -c "python downstream/post_locus_allele.py ${s}_wg.vcf.gz wg2_ _$s > downstream/post_$s.txt 2>&1"
done
run downstream/elsewhere_live_HG002.txt sh -c 'PYTHONIOENCODING=utf-8 python downstream/check_elsewhere.py downstream/elsewhere_examples_HG002.tsv 30 11 > downstream/elsewhere_live_HG002.txt 2>&1'

# 5. ClinVar P/LP entries attached to another allele (Table S6) and allele check of Table S5
run downstream/other_allele_PLP_HG002_d146.tsv python downstream/check_other_allele.py HG002_wg.vcf.gz wg_d146.tsv downstream/other_allele_PLP_HG002_d146.tsv
run downstream/verify_s5_alleles.json sh -c 'python downstream/verify_s5_alleles.py > downstream/verify_s5_alleles.txt 2>&1'

# 6. file-level rates (Table S2, Figure 1b), retirements per build (Figure 1a, Table S8),
#    sites holding a retired and a current rsID (Supplementary Note 1)
run bundle_rate.txt sh -c 'python bundle_rate.py dbsnp138.vcf.gz dbsnp144.vcf.gz dbsnp146.vcf.gz b156.vcf.gz > bundle_rate.tmp 2>&1 && md5sum b156.vcf.gz >> bundle_rate.tmp && mv bundle_rate.tmp bundle_rate.txt'
run merged_years.txt sh -c 'python merged_years.py refsnp-merged.json.bz2 > merged_years.txt 2>&1'
run dup_keys.txt sh -c 'python dup_keys.py dbsnp138.vcf.gz dbsnp144.vcf.gz dbsnp146.vcf.gz > dup_keys.txt 2>&1'

# 7. indels carrying a retired rsID, live check (Supplementary Methods M7, check 3)
run indel_examples_d146.txt sh -c 'python check_indel_examples.py > indel_examples_d146.txt 2>&1'

# 8. audits (independent Wilson intervals, ledger records without target, unmatched indels); need statsmodels
python audit_ledger_and_ci.py > audit_ledger_and_ci.txt 2>&1
python audit_consistency.py > audit_consistency.txt 2>&1
python audit_unmatched_indels.py > audit_unmatched_indels.txt 2>&1

step "done; tables: RSID_WG=$(pwd) python tables/make_tables.py"
