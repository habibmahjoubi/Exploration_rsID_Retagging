# Project Brief — "Paper C": rsID/dbSNP retagging artifact

## Positioning

Replication and extension of the "false novelty/false absence via identifier
renumbering" mechanism from **Paper A** (taxid/NCBI Taxonomy), applied to a
**second, independent identifier system** (rsID/dbSNP) in a **second domain**
(clinical germline genomics, not viral metagenomics). Also serves as a concrete
empirical demonstration for **Paper B/KDCR**'s thesis (reference frozen for
validation stability drifting over time) — with a measured rather than
theoretical cost.

## Core contribution (all empirically verified, full coverage)

1. The merge mechanism exists and is substantial at chr20 scale: 66.44% of
   real GIAB HG002 chr20 SNVs with an allele-exact dbSNP match sit on a
   historically-merged rsID — a ~111x enrichment over the 0.60% background
   merge rate.
2. The naive-vs-merge-aware failure mode is demonstrated directly against
   the live dbSNP RefSNP API (n=100, 100/100: the old ID carries no primary
   variant data of its own).
3. A structural (deductive) argument, illustrated on 1000 Genomes Phase 3,
   shows the risk is concentrated in a specific, identifiable class of
   artifact rather than diffuse.
4. **Downstream impact on two real, independently-deployed production
   bundles**: GATK dbSNP138 — 12.75% unambiguous stale; dbSNP144 — 2.59%
   stale plus a distinct, non-deterministic 2.18% ambiguous state (combined
   exposure 4.77%).
5. Confirmed on a real nf-core/sarek pipeline run, not just a truth-set
   stand-in: the pipeline's own output writes a stale rsID into 11.58% of
   calls restricted to the same merge-dated population.
6. Concrete downstream consequence: gnomAD returns zero results for 369 of
   369 (100%) dbSNP138-stale identifiers under the identifier each variant
   actually carries.

## Status

Manuscript complete, targeting the **Journal of Molecular Diagnostics
(JMD)**. Two full external-review passes addressed (methodology, then
structure/scope). Repository cleaned up to the scripts and data that
actually produce the manuscript's final numbers and figures — see
`README.md`.

Remaining before submission:
- [ ] Zenodo DOI for this repository (repo is live at
      github.com/habibmahjoubi/Exploration_rsID_Retagging).
- [ ] Resolve the Reference [1] DOI (this manuscript vs. the accepted
      Paper A record) before finalizing the reference list.

## Folder contents

- `README.md` — study summary, final results, repository structure.
- `Manuscript_Draft.docx` / `.pdf` — the manuscript.
- `data/`, `figures/`, `scripts/` — the final data and scripts backing
  every number cited in the manuscript.
- `sarek_validation/` — the real pipeline validation run and its outputs.
