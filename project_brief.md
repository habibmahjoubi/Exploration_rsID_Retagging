# Project Brief — "Paper C" (working title): rsID/dbSNP retagging artifact

## Positioning

Replication and extension of the "false novelty/false absence via identifier
renumbering" mechanism from **Paper A** (taxid/NCBI Taxonomy), applied to a
**second, independent identifier system** (rsID/dbSNP) in a **second domain**
(clinical germline genomics, not viral metagenomics). Also serves as a concrete
empirical demonstration for **Paper B/KDCR**'s thesis (reference frozen for
validation stability drifting over time) — with a measured rather than
theoretical cost.

## Core contribution (what has been empirically verified, not assumed)

1. The merge mechanism exists and is substantial at chr20 scale (initial sample:
   73.75% of the oldest rsIDs have a merge history).
2. On real variants (GIAB HG002 chr20 truth VCF, 85,951 positions), 73.79%
   of the positions touched by the dbSNP sample sit on a merged rsID.
3. The "naive vs. merge-aware" mechanism is demonstrated internally within dbSNP (n=30 pilot,
   30/30: the old ID has no data of its own without following the merge history).
4. **Downstream impact tested on two real resources**:
   - 1000 Genomes Phase 3 (2013): negative (0/8) — refines the hypothesis (dbSNP's
     "high merged into low" convention protects resources predating the merged ID).
   - **GATK `dbsnp138` bundle (GRCh38, still massively deployed in production)**:
     **positive — 217/2,788 candidates (7.78%) show a stale rsID**, a
     concrete demonstration of a real, measurable risk on a currently-in-production artifact.

## What's missing before submission (checklist, updated as work progresses)

- [x] **Full coverage** — done: 25,938,655 records, final rate
      **47.78%** (corrects the initial biased 73.79%). See results/08.
- [x] **Allele-exact matching** (REF/ALT) — done and validated (99.22% agreement
      with position-only matching on the partial sample).
- [x] **"Downstream impact" panel re-derived on FULL COVERAGE** (25.9M
      records, 48,746 candidates, 2,894 with a 2014-2017 merge) — DEFINITIVE
      figures: **12.75% (dbSNP138) -> 3.63% (dbSNP144)**, higher
      than the partial sample (8.24%/1.73%) — the biased sample was
      slightly under-estimating the real risk. See results/10 (final
      reference file, supersedes 05/06/07 for these figures).
- [x] **Global merge rate recomputed exact-allele, full coverage**:
      **66.44% (definitive figure)**, supersedes the 47.78% (position-only) and
      the initial 73.79% (biased sample). See results/08 and 10.
- [x] **Generalize the "frozen bundle" test to 2 versions** (dbSNP138, dbSNP144) —
      real temporal trend confirmed on full data (12.75% -> 3.63%).
      A 3rd point (151/152/current) would still be useful but is blocked by the
      proprietary Illumina Nirvana (.nsa) format of the only file found for that vintage.
- [x] **2 figures created** (rate by vintage, full breakdown by bundle),
      integrated into the manuscript, dataviz-skill palette validated.
- [x] **Indels handled** (results/12, manuscript Section 5.7) — normalization
      function (prefix/suffix trim) created and validated, 85% of indels
      match successfully (99.7% for SNVs). Honest, rich result:
      indels are LESS often stale (1.0-1.1% vs 8.3%/0.7% for SNVs) but
      MUCH more often ambiguous (4-12% vs 0-2.3% for SNVs). Done on
      the partial sample only — redoing at full coverage (~2h)
      remains possible future work, not done for lack of clear necessity.
- [ ] Replace the GIAB truth VCF (used as a stand-in) with a real output
      from Article 1's nf-core/sarek pipeline, to ground the demonstration in a
      real production pipeline rather than a public database.
- [x] **Naive-vs-merge-aware pilot extended n=30 -> n=100** (results/09) — same
      perfect result (100/100), drawn from the exact-allele panel.
- [x] **References [3]-[6] verified** against primary sources (full authors,
      volumes/pages confirmed) — "[verify...]" flags removed from the manuscript.
- [ ] Choose the target journal (candidates to discuss: JBCB — like Paper A, same
      "Critical Comments" style; or a journal more oriented toward clinical genomics
      given the GATK/production angle; or Bioinformatics/NAR Genomics if the
      APC budget allows — otherwise stick to no-fee journals like JBCB).
- [ ] Decide author(s) — Article 1 is co-authored with A. Rebai; to be settled
      whether this paper stays solo (like Paper A/B) or includes a co-author, depending
      on whether the "real sarek pipeline" angle (Article 1's infrastructure) is actually used.

## Folder contents

- `README.md` — full exploration log (idea, data availability,
  all intermediate results with dates)
- `Manuscript_Draft.docx` — first structured manuscript draft (this brief)
- `data/`, `results/`, `scripts/` — real data and scripts used for each
  result cited above (full traceability, nothing is invented)
