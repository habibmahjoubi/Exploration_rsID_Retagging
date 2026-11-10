# Whole-genome study: scripts and results

This folder is the working directory of the analysis. Scripts and their small result files sit
side by side, as they did when the analysis was run (10 November 2026). Large inputs (about 40 GB)
and large intermediate files are not included; `download_inputs.sh` fetches the inputs and checks
their md5 sums.

## Reproduce

```bash
bash download_inputs.sh      # GIAB benchmarks, dbSNP files, merge ledger, ClinVar, GWAS Catalog, PharmGKB
bash run_all.sh              # every analysis, in order; restartable (skips outputs that exist)
python tables/make_tables.py # rebuilds tables/tables_generated.md (all table numbers)
python tables/make_figures.py
```

Requirements: Python 3.11 or later (standard library), matplotlib for figures, statsmodels for
the audits. Note that `refsnp-merged.json.bz2` is served from NCBI's `latest_release` folder;
a newer build will differ from the build 157 file used here (md5 in `download_inputs.sh`).

## Files and where they appear in the article

| File | Content | Article |
|---|---|---|
| `filter_local.py` | keeps dbSNP records at benchmark positions (chr1-22) | Methods |
| `normalize.py` | allele trimming (SPDI-like), no left-alignment | Methods, M3 |
| `wg_analysis.py` -> `wg_results*.json/.txt` | annotation and variant rates, SNV/indel split, per-chromosome ranges | Table 1, Tables S11, S7 |
| `bundle_rate.py` -> `bundle_rate.txt` | retired rsIDs among all rsIDs of each file, by retiring build | Figure 1b, Table S11 |
| `merged_years.py` -> `merged_years.txt` | retirements per dbSNP build in the ledger | Figure 1a, Table S9 |
| `dup_keys.py` -> `dup_keys.txt` | sites holding two or more rsIDs, and a retired plus a current one | Supplementary Note |
| `dup_keys_chr20.py` -> `dup_keys_chr20.txt` | same, chromosome 20 only | Supplementary Note |
| `check_indel_examples.py` -> `indel_examples_d146.txt` | live check of 25 indels and 5 SNVs | M7, check 2 |
| `retired_variants_HG00x_d146.tsv.gz` | every benchmark variant carrying a retired rsID with dbSNP146 | derived table |
| `downstream/downstream_join.py` -> `downstream_results*.json/.txt` | rsID joins to ClinVar, GWAS Catalog, PharmGKB; whole-file check | Table 2, Table S5 |
| `downstream/post_locus_allele.py` -> `post_*.txt`, `post_locus_allele_*.json` | locus check of merges; allele-aware ClinVar reference | Tables 2, S3, S4 |
| `downstream/check_elsewhere.py` -> `elsewhere_live_HG002.txt` | live RefSNP check of 30 "elsewhere" cases | Table S3 |
| `downstream/check_other_allele.py` -> `other_allele_PLP_HG002_d146.tsv` | P/LP ClinVar entries attached to another allele | Table S6 |
| `downstream/verify_s5_alleles.py` -> `verify_s5_alleles.*` | allele check of the whole-file estimate | Table S5 |
| `downstream/SOURCES.txt`, `MD5SUMS.txt`, `MD5_samples.txt` | exact sources and checksums | Table S1 |
| `audit_*.py` | independent Wilson intervals (statsmodels), ledger records without target, unmatched indels | M1, M3 |
| `sarek_chr20/` | real nf-core/sarek 3.9.0 run, HG002 chr20 30x: output VCF, ledger check, live checks, pipeline defaults | Table S10, M2, M4, M7 |
| `tables/make_tables.py` -> `tables/tables_generated.md` | every table number, read from the files above | Tables 1-2, S2-S8, S11 |
| `tables/check_hgvs.py` -> `tables/hgvs_validation.tsv` | VariantValidator check of all 60 HGVS descriptions | Table S6, Related Manuscript File |
| `tables/fetch_transcripts.py` -> `tables/hgvs_transcripts.tsv` | MANE Select transcript and protein descriptions (VariantValidator) | Related Manuscript File |

`sarek_chr20/ledger_check.py` also needs the chromosome 20 extracts of the four dbSNP files
(`d138.tsv`, `d144.tsv`, `d146_chr20_idmap.tsv`, `b156_chr20_idmap.tsv`), made with
`fetch_chrom_filtered.py` / `fetch_chrom_from_tabix.py`; they are not included because of their
size (the dbSNP138 and dbSNP144 extracts are in `../data/`).
