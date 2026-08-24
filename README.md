# Reference Bundle Staleness — rsID/dbSNP Merge Retagging Artifact

Code and data for the study "Reference Bundle Staleness: Quantifying rsID
Obsolescence and Its Impact on Clinical Variant Annotation" (manuscript:
`Manuscript_Draft.docx` / `.pdf`).

## Idea

dbSNP periodically merges administratively duplicate reference-SNP
identifiers (rsIDs), retiring one into another via the `dbsnp1_merges`
field of each RefSNP record. A reference bundle frozen before a merge event
still reports the retired (pre-merge) identifier — the same
false-novelty/false-absence mechanism previously shown for NCBI taxonomy
identifiers in a companion study, applied here to a second, independent
identifier system (rsID/dbSNP) in a second domain (clinical germline variant
calling rather than viral metagenomics).

## Core results (see the manuscript for full methodology and figures)

- Among real chr20 variants from the GIAB HG002 truth set with an
  allele-exact dbSNP match, **66.44%** sit on a historically-merged rsID —
  a **~111x enrichment** over the 0.60% background merge rate across all
  chr20 records.
- Against the real, still-deployed GATK dbSNP138 known-sites bundle,
  **12.75%** of variants with a 2014-2017 merge event are reported under
  the retired identifier. A second real bundle (dbSNP144) shows this fall
  to **2.59%**, but also reveals a distinct, non-deterministic failure
  mode: **2.18%** of variants carry both the current and a not-yet-merged
  identifier simultaneously (combined exposure: 4.77%).
- A real nf-core/sarek pipeline run confirms the mechanism is not a
  truth-set artifact: it writes a stale rsID into its own output calls
  (11.58% among calls restricted to the same merge-dated population).
- gnomAD returns zero results for 369 of 369 (100%) dbSNP138-stale
  identifiers under the identifier each variant actually carries, while the
  current identifier resolves every time — a concrete downstream
  consequence for population-frequency lookup during variant
  interpretation.
- The merge-date distribution across the full candidate panel shows none of
  81,963 recorded merge events postdate 2017 — staleness here is a bounded
  historical debt from a merge wave that had largely run its course, not
  an open-ended accumulating rate.

## Repository contents

- `Manuscript_Draft.docx` / `.pdf` — the manuscript.
- `project_brief.md` — positioning and status summary.
- `scripts/` — the final scripts that produce the manuscript's numbers and
  figures:
  - `build_full_coverage_panel.py` — single full-coverage pass over
    `refsnp-chr20.json.bz2`, builds the allele-exact candidate panel.
  - `check_bundle_staleness_with_indels_SPLIT.py` — cross-references a
    bundle's chr20 idmap against the candidate panel, reporting SNV/indel
    stale and ambiguous rates separately.
  - `normalize.py` — shared SPDI/VCF variant normalization (used for
    indel matching).
  - `verify_naive_vs_mergeaware_n100.py` — naive-vs-merge-aware
    verification (n=100) against the live RefSNP API.
  - `check_clinvar.py` — ClinVar lookup for the 369 dbSNP138-stale pairs.
  - `demonstrate_nondeterminism.py` — forward/reverse VCF traversal test
    on the 63 ambiguous dbSNP144 sites.
  - `make_figures.py` — generates the 3 manuscript figures.
  - `build_manuscript_docx.py` — generates `Manuscript_Draft.docx`
    (re-run after editing; never hand-edit the .docx).
- `data/` — the data these scripts consume/produce: the GIAB HG002 chr20
  truth VCF, the GATK dbSNP138 and GDC dbSNP144 chr20 idmaps, the final
  full-coverage candidate panel (SNV-only, 48,746 candidates) and its
  2014-2017-merge, SNV+indel-extended subset (4,613 candidates), and the
  raw ClinVar check inputs/results (369 stale pairs).
- `figures/` — the 3 figures embedded in the manuscript.
- `sarek_validation/` — the real nf-core/sarek pipeline validation run:
  `README.md`/`RESULTS.md` document the run and its outcome,
  `run_full_pipeline.sh`/`rerun_native_dbsnp.sh` are the pipeline
  invocations, `add_readgroup.sh`/`reheader_bam.sh`/`rename_contig.sh`
  are the fixes required for the public GIAB BAM (documented in
  RESULTS.md), `cross_reference_sarek_output.py` cross-references the
  pipeline's own annotated output against the live dbSNP merge ledger,
  and `build_ambiguous_test_vcf.py`/`pysam_test.py` back the three-way
  bcftools/pysam/GATK annotation-tool comparison. `work/` (the raw
  Nextflow pipeline intermediates, several GB) is intentionally excluded
  via `.gitignore`.

## Reproducing the results

These scripts were run from a flat working directory with the relevant
`data/` files alongside them, so several reference their input by a bare
filename rather than a CLI argument. To re-run one, `gunzip` the file it
needs into the same directory, renamed as shown:

| Script | Expects (in its working directory) | Source in `data/` |
|---|---|---|
| `build_full_coverage_panel.py` | `chr20_giab.vcf` (uncompressed) + dbSNP records piped via stdin (`curl .../refsnp-chr20.json.bz2 \| bzip2 -dc \| python build_full_coverage_panel.py`) | `chr20_giab_HG002_v4.2.1_truth.vcf.gz` (gunzip) |
| `check_bundle_staleness_with_indels_SPLIT.py` | two CLI args: a bundle idmap and a candidates file | `gatk_dbsnp138_chr20_idmap.tsv.gz` / `gdc_dbsnp144_chr20_idmap.tsv.gz` and `candidate_panel_with_indels.csv` (gunzip the idmap first) |
| `verify_naive_vs_mergeaware_n100.py` | `candidate_panel_allele_exact.csv` | `candidate_panel_FULLCOV_allele_exact_48746.csv.gz` (gunzip, rename) |
| `check_clinvar.py` | `stale_pairs_138.tsv` | `stale_pairs_138.tsv` (already uncompressed) |
| `demonstrate_nondeterminism.py` | `gdc_dbsnp144_chr20_full.tsv` + `recent_candidates_2014_2017_FULLCOV.txt` | `gdc_dbsnp144_chr20_idmap.tsv.gz` (gunzip, rename) + `recent_candidates_2014_2017_FULLCOV.tsv.gz` (gunzip, rename) |
| `make_figures.py`, `build_manuscript_docx.py` | run directly from `scripts/`; figures are read/written as bare filenames, so run from (or copy the three `figures/*.png` into) the same directory | — |

`build_full_coverage_panel.py`, `check_clinvar.py`, and
`verify_naive_vs_mergeaware_n100.py` also make live calls to NCBI (the
dbSNP RefSNP API and/or ClinVar E-utilities) as part of their verification
methodology — they are not fully offline-reproducible by design.

## Data sources

All data sources are public: dbSNP (NCBI, `latest_release` JSON
distribution and RefSNP REST API), GIAB HG002 v4.2.1 (NIST), 1000 Genomes
Phase 3 (IGSR), and the GATK dbSNP138 / NCI GDC dbSNP144 known-sites
bundles (Broad Institute public reference buckets).
