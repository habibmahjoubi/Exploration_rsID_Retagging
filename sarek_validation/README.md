# Real sarek pipeline validation — plan, ready to execute

Goal: replace the "GIAB truth VCF used as a stand-in for a real pipeline
output" limitation (manuscript Section 6.2) with an actual nf-core/sarek run
(same tool/version/invocation as Article 1's own study), to check whether a
**real pipeline's own dbSNP-annotated output** already carries stale rsIDs
today — not just a hypothetical cross-reference against a public benchmark.

## Status (2026-08-24, this session)

Blocked mid-setup by a genuine WSL/Hyper-V hang: even basic `wsl.exe -l`
stopped responding, `wsl --shutdown` itself hung, and killing the stuck
`wsl.exe`/service processes did not fully clear it (a fresh `wsl -l` still
hangs after cleanup). This is a deeper OS-level issue than the "WSL sometimes
needs `wsl --shutdown`" gotcha noted in earlier sessions' work on this
machine — it needs a full Windows restart to clear cleanly. **User has been
asked to restart when convenient; nothing else in this project (all the
dbSNP/manuscript work) depends on WSL and was unaffected.**

## What's already prepared, ready to run once WSL/Docker are back

- `run_full_pipeline.sh` — end-to-end driver: measures real chr20 depth,
  calls Article 1's own `prepare_reference.sh`/`run_sarek.sh` unmodified,
  runs sarek (HaplotypeCaller only, same flags as Article 1), annotates the
  output against the real GATK dbSNP138 bundle (already downloaded this
  session), extracts the rsIDs sarek actually assigned.
- `cross_reference_sarek_output.py` — takes sarek's own annotated rsIDs and
  checks them against the full-coverage merge panel already built
  (`candidate_panel_FULLCOV_allele_exact.csv`, 25.9M dbSNP records scanned)
  to report how many of THIS REAL RUN's own identifiers are stale today.

## To resume after the restart

1. Confirm WSL is healthy: `wsl -l` should return near-instantly.
2. Confirm Docker Desktop is running AND its WSL integration is enabled for
   the Ubuntu distro (Settings > Resources > WSL Integration) — this was
   never verified this session since WSL never came back up.
3. Inside WSL: install Nextflow if not already present
   (`curl -s https://get.nextflow.io | bash` — this only works inside WSL,
   confirmed it fails on native Windows/Git Bash this session) and confirm
   `samtools`/`bcftools` are available (the `kdcr` conda env from the KDCR/
   Papier B work already has samtools; bcftools may need
   `conda install -c bioconda bcftools`).
4. Run `run_full_pipeline.sh` from inside WSL (see its header for the exact
   invocation). Expect real runtime cost: sarek will pull several GB of
   Docker images on first run, plus alignment + variant calling time for a
   30x chr20 BAM (order of tens of minutes, not hours, for one chromosome/
   one sample with BQSR skipped).
5. Once `sarek_annotated_rsids.tsv` exists, run
   `python cross_reference_sarek_output.py sarek_annotated_rsids.tsv`
   (from Windows, in this same directory) for the final numbers.
6. Fold the result into the manuscript as a new subsection (replacing the
   "GIAB truth VCF as a stand-in" limitation with an actual measured number),
   and update Section 6.2 Limitations accordingly.

## Known risks / things that may still need adjusting

- The exact sarek output filename pattern (`*.haplotypecaller*.vcf.gz`) is a
  reasonable guess based on sarek's known output layout but has not been
  verified against a real run in this environment; check
  `find sarek_out -iname "*.vcf.gz"` if the script's `find` comes up empty.
- `bcftools annotate -c ID` requires both VCFs to use the same chromosome
  naming (`chr20`) and be coordinate-sorted + tabix-indexed; the GATK
  dbSNP138 bundle already uses `chr20` (confirmed earlier this session).
- Docker Desktop's WSL integration toggle is per-distro and off by default
  for a manually-added distro like this session's `Ubuntu` — this is the
  most likely NEW blocker to hit once WSL itself is healthy again.
