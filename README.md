# Retired dbSNP identifiers and rsID-based lookups in germline variant-calling pipelines

Code, derived tables and result files for the study of the same name (Mahjoubi H., Brief
Communication, submitted 2026). This repository covers the reproducibility of the results; it
does not include the manuscript.

## The study in short

Variant-calling pipelines copy dbSNP identifiers (rsIDs) from a frozen dbSNP file, while dbSNP
keeps retiring rsIDs by merging duplicates. We measured how often default GRCh38 pipelines write
retired rsIDs, and what this changes for ClinVar, GWAS Catalog and PharmGKB lookups.

- Broad WARP loads dbSNP build 138 (file of November 2013); nf-core/sarek 3.9.0-3.11.0 loads
  build 146 (November 2015).
- In three Genome in a Bottle v4.2.1 whole genomes (HG001, HG002, HG005; chromosomes 1-22),
  4.49-4.95% (build 138) and 7.30-8.72% (build 146) of variants with an rsID carry a retired one,
  mostly indels. The NCBI dbSNP156 release (November 2022) writes 0.46-0.49% retired rsIDs.
- Over 99.5% of retired rsIDs point to a current rsID at the same allele.
- Downstream losses are small: 0.83-1.14% of benign ClinVar entries, 0.11-0.14% of pathogenic
  entries across the whole default files, 0.43-1.03% of significant GWAS associations, no
  PharmGKB annotation of levels 1A-2B.
- A plain rsID join attaches 30-34 pathogenic ClinVar entries per genome to a variant carrying a
  different allele.

Retirement is judged against the complete dbSNP build 157 merge ledger
(`refsnp-merged.json.bz2`, 21,585,672 records).

## Repository layout

| Path | Content |
|---|---|
| `wholegenome/` | **Current study.** Scripts and result files; see `wholegenome/README.md` |
| `wholegenome/downstream/` | ClinVar, GWAS Catalog and PharmGKB test, locus check, live checks |
| `wholegenome/sarek_chr20/` | Real nf-core/sarek run (HG002 chromosome 20), its output VCF and ledger check |
| `wholegenome/tables/` | `make_tables.py` (every number of the tables), `make_figures.py`, HGVS validation |
| `sarek_validation/` | Scripts of the real nf-core/sarek run, re-analysed in `wholegenome/sarek_chr20/` |
| `scripts/`, `data/` | Exploratory chromosome 20 analyses, not used in the article |

## Licence and citation

MIT licence. Please cite the article, or this repository through `CITATION.cff`.
