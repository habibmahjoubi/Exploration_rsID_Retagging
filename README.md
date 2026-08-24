# Exploration — "False Novelty" via rsID Retagging (dbSNP)

Track explored for an original paper reusing existing infrastructure
(Article 1 = `llm-mr-discovery-genomics`, Paper A = taxid artifact, Paper B = KDCR).

## Idea

Paper A shows that a *current-day-only* taxid lookup manufactures false novelty
when the identifier has been renumbered between versions of NCBI taxonomy
(39/56 tested candidates = false novelty via renumbering).

dbSNP has a structurally identical phenomenon on a completely different
identifier system: an rsID can be merged into another rsID across
builds (`RsMergeArch` historically, replaced today by the
`dbsnp1_merges` field of each RefSNP JSON record). Hypothesis: a
"historical" re-annotation of old variant calls with a current dbSNP
build would make variants that already had an rsID at the time, simply
since merged, appear as "new" — exactly Paper A's mechanism, but in
clinical germline genomics (the domain of Article 1's nf-core/sarek
pipeline) rather than viral metagenomics.

## Data availability (verified 2026-08-23)

- **Legacy `RsMergeArch.bcp.gz` file** (builds <=151): legacy FTP path
  dead (404 confirmed), consistent with the system's deprecation in 2018.
- **Current mechanism (better)**: each RefSNP JSON record exposes
  a `dbsnp1_merges` field — a list of `{merged_rsid, revision (build), merge_date}`.
  Richer than `merged.dmp` (Paper A): each merge is individually dated and
  versioned. Verified live on rs268 and on the chr20 sample below.
- **Real historical build snapshots**: `ftp.ncbi.nlm.nih.gov/snp/archive/`
  contains complete builds b152-b157 (Oct 2021 -> Apr 2025); `pre_build152/`
  extends coverage back to ~2015-2020. Equivalent of the `taxdump_archive` used
  for Paper B's 13 Kraken2 databases.
- **Per-chromosome dbSNP files**: `refsnp-chr20.json.bz2` (~9.0GB compressed),
  accessible via HTTP range-fetch (HTTP 206 confirmed), the same technique as
  the partial byte-range already used for PRJNA1026487 in Paper B.

## What was done in this session

1. **Raw dbSNP chr20 sample** (`results/01_...txt`): first 30MB
   compressed chunk (~15,333 records) -> 73.75% have a merge
   history. **Biased**: the file is sorted by rsID number, so this
   sample only contains the oldest rsIDs (~2000-2001) —
   over-represents heavily-studied variants, not a representative rate.

2. **GIAB HG002 truth VCF (chr20)** downloaded in full from NIST
   (`HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz`, public source, the same
   HG002 sample used by Article 1) and filtered to chr20:
   **85,951 real variant positions** (`data/chr20_giab_HG002_v4.2.1_truth.vcf.gz`).
   Observation: the GIAB VCF's ID column is systematically "." (no rsID
   natively annotated — expected, it's a truth set, not a dbSNP
   annotation): the cross-reference must therefore be done by genomic POSITION
   (dbSNP SPDI, 0-based -> converted to 1-based to match the VCF), not by ID.

3. **Position-by-position cross-reference** (`scripts/cross_reference.py`): dbSNP
   chr20 chunk widened to 400MB compressed (~8GB decompressed streamed,
   without writing the intermediate file to disk), chr20 positions
   (NC_000020.11) extracted from each RefSNP record and cross-referenced
   with the 85,951 real GIAB positions.

   **Result (see `results/02_...txt` for full detail)**: this chunk
   (315,939 RefSNP records) already touches 65,347 / 85,951 (76.0%) of
   the real HG002 chr20 variant positions. Among these real touched variants,
   **48,217 (73.79%) sit on an rsID that has historically absorbed one or
   more merged former identifiers** (real merge dates ranging
   from 2001 to 2009 in the examples). This is the equivalent, at chr20 scale and
   with a different identifier system (rsID vs taxid), of Paper A's "39/56"
   ratio — first empirical confirmation, on real data, that the
   candidate pool for this track is large and not anecdotal.

4. **Full candidate panel extracted** (`results/candidate_panel_full_48217.csv.gz`): the 48,217 candidates
   (current rsID, chr20 position, merged historical rsIDs + dates) are now saved
   in structured form (script: `scripts/build_candidate_panel.py`), not just counted.

5. **Empirical naive-vs-merge-aware verification, on a 30-candidate pilot panel**
   (`scripts/verify_naive_vs_mergeaware.py`, result: `results/03_naive_vs_mergeaware_verification.json`):
   protocol modeled on Paper A. For 30 candidates randomly drawn (seed=42) from the 48,217-candidate panel,
   live query against the RefSNP API for the OLD rsID (the one that was merged):

   - **"Naive" verdict**: 30/30 of the old rsIDs have **no `primary_snapshot_data` of their
     own** (no position, no allele) — a naive consumer (simple join by rsID, a static
     table of "valid rsIDs") would treat them as unknown/orphaned identifiers, even though the variant
     they designated does exist today.
   - **"Merge-aware" verdict**: 30/30 correctly resolve via `merged_snapshot_data.merged_into`
     to the expected current rsID (100% cross-validation between two independent fields of the
     same record — `dbsnp1_merges` on the current rsID's side and `merged_snapshot_data` on the old rsID's side).

   **This is the first direct demonstration of the "false absence/false novelty" mechanism**
   (not just "a merge history exists somewhere") — equivalent to Paper A's
   naive/merge-aware protocol in §3.2-3.3, but still at pilot scale (n=30, not 48,217).

6. **Downstream impact — two tests, one honest negative and one confirmed positive**:

   - **Test A (negative, `results/04_...1000G.txt`)**: searched for recently
     merged rsIDs (2014-2016) in 1000 Genomes Phase 3 (2013) — 0/8 found. Refines
     the hypothesis: by dbSNP convention ("high merged into low"), a resource
     established BEFORE the merged identifier was created could never have used it —
     the risk is not generic to "any old resource."

   - **Test B (POSITIVE, CONFIRMED, `results/05_...GATK_bundle_STALE_CONFIRMED.txt`)**:
     cross-referenced the 2,788 candidates with a 2014-2017 merge against the real GATK
     `Homo_sapiens_assembly38.dbsnp138.vcf.gz` bundle (standard "known-sites"
     reference, GRCh38, still massively deployed as-is in production today):

     **217 / 2,788 (7.78%) show the bundle still reports the OLD rsID**,
     even though dbSNP has since officially merged it into another. This is a
     concrete demonstration, on an artifact actually used in production, of the
     "false absence" mechanism (a naive join between a VCF annotated with this
     bundle and a modern resource like ClinVar would fail silently).

     **This is the missing link with Paper B/KDCR**: this frozen bundle is a
     concrete, already-deployed example of the "reference frozen for
     validation stability" phenomenon KDCR theorizes — with a measured (~8%)
     rather than assumed cost.

7. **Multi-version comparison (`results/06_multiversion_bundle_trend.txt`)**: same
   panel of 2,788 candidates tested against a second, independent real bundle, dbSNP144
   (used by the NCI Genomic Data Commons, June 2015) — stale-ID rate:
   **7.78% (138) -> 0.68% (144)**, a real two-point temporal trend,
   in the expected direction. Directly reinforces the link with Paper B/KDCR (gradual,
   measurable drift, not a binary frozen/up-to-date state).

8. **Full coverage, definitive figure (`results/08_full_coverage_FINAL.txt`)**:
   25,938,655 dbSNP chr20 records processed in a full streaming pass (~1h). **Real
   merge rate: 47.78%** (49,730/104,082 touched GIAB positions) — notably
   lower than the initial biased estimate (73.79%), precisely confirming
   the anticipated bias (sorting by rsID over-represents older variants). The
   qualitative conclusion holds (nearly 1 variant in 2), the precise figure is
   corrected. **The "downstream impact" panel (05-07) is still based on the
   partial sample, not this full coverage — next step if this continues.**

9. **Allele-exact matching (`results/07_allele_exact_validation.txt`)**: the
   candidate panel and the GATK138/dbSNP144 bundle tests were redone with
   POS+REF+ALT matching (not just position). Result: robust (8.24%/1.73%
   instead of 7.78%/0.68%) AND resolves the mystery of the ~100 "different
   identifier" cases (drop to 0 — they were multi-allelic false positives from
   position-only matching). Manuscript and figures updated accordingly.

## Known limitations at this stage (to address honestly if the idea is pursued)

- The dbSNP file is sorted by rsID, not by position: even the
  400MB chunk only covers a fraction (the oldest/lowest rsIDs) of the
  full spectrum -> the overlap rate measured here is a **bound / first
  estimate**, not an exhaustive rate over the 85,951 GIAB variants.
- Position-only matching (not exact-allele): sufficient for
  most SNVs, more approximate for indels (SPDI vs VCF representation
  can differ in base anchoring).
- The naive-vs-merge-aware test (point 5) verifies the mechanism *internally within* dbSNP
  (absence of a proper `primary_snapshot_data` on the old ID) — this is solid proof of the
  mechanism, but not yet a demonstration of a *downstream* failure, in a real pipeline or
  a real cross-reference with another resource (ClinVar, gnomAD, an archived clinical report).
  A real paper would want to show the concrete impact on a real use case, not just dbSNP's
  internal structure.
- Pilot panel n=30 only (out of 48,217 already-extracted candidates) — to be extended before
  claiming a definitive "rate," but the 30/30 is already a clear signal.
- No VCF actually produced by Article 1's sarek pipeline yet
  (Nextflow/Docker unavailable in this environment): the VCF used
  here is the NIST/GIAB truth set, not a dbSNP-annotated sarek output —
  a reasonable substitute for a feasibility test, to be replaced by a
  real sarek run + dbSNP annotation if the paper is actually launched.

## Paper plan and manuscript

- `project_brief.md` — positioning, core contribution, pre-submission checklist
  (in the same style as the other projects' briefs).
- `Manuscript_Draft.docx` — first structured draft (working title: "When Frozen
  dbSNP Bundles Outlive Their Merges: A Reference-Identifier Retagging Artifact in
  Genomic Variant Annotation"), modeled on Paper A's structure (accepted, JBCB):
  Abstract, 1. Introduction, 2. Illustrative Examples (3-real-case table),
  3. Background (dbSNP merge mechanism), 4. Analysis Protocol (4.1-4.4),
  5. Results (5.1-5.5, with the real figure tables), 6. Impact and Implications
  (explicit link to Paper A and Paper B/KDCR), 7. Limitations, 8. Recommendations,
  Data/Code Availability, Acknowledgments, Conflict of Interest, References.
  Generated via `scripts/build_manuscript_docx.py` (re-run after editing the
  script, never hand-edit the .docx while still at this draft stage).
  **Author/affiliation, final title, target journal, and references [3]-[6] still
  to be verified/completed** — placeholders explicitly marked in the document.

## Formatting and restructuring (latest pass)

- **Consistent formatting**: Times New Roman everywhere (body text,
  headings, tables, captions, references), black text (no more Word's default
  theme blue on headings), bold headings, tables in "Table Grid" style
  (plain black grid, no fill color or alternating bands).
- **Restructuring**: the former separate sections "6. Impact and
  Implications" / "7. Limitations" / "8. Recommendations" were merged into
  a single **"6. Discussion"** with 3 subsections (6.1 Generalizing Paper A's
  mechanism, 6.2 Limitations, 6.3 Implications for practice) — a more
  standard convention for this type of paper than separate top-level sections. All
  internal cross-references ("Section 7," "see Limitations," etc.) were corrected
  accordingly. Verified visually (PDF conversion + rendered page images).

## Folder contents

- `README.md` — this file
- `data/chr20_giab_HG002_v4.2.1_truth.vcf.gz` — GIAB HG002 truth VCF,
  chr20-only filtered (85,951 variants), compressed
- `scripts/cross_reference.py` — dbSNP <-> GIAB position cross-reference script
- `results/01_dbsnp_chr20_sample_merge_rate.txt` — stats on the raw sample
- `results/02_cross_reference_giab_dbsnp_chr20.txt` — real cross-reference result
