# Real nf-core/sarek pipeline validation — results (2026-08-24)

## Update: native GATK --dbsnp rerun (supersedes the bcftools-substitute run below)

The initial run below used `bcftools annotate -c ID` as a post-hoc substitute
for HaplotypeCaller's native `-D`/`--dbsnp` annotation (WSL/Docker issues at
the time prevented passing `--dbsnp` directly to sarek). This was re-run
natively (`sarek_validation/rerun_native_dbsnp.sh`, reusing the nextflow
`-resume` cache — 31m52s, 20% cached) with `--dbsnp` pointing at the real
GATK dbSNP138 bundle, so HaplotypeCaller's own `-D` mechanism performs the
annotation directly, no substitute.

**Final, native numbers**: of **94,467** rsID annotations (89,676 VCF
records; the annotation count is higher because GATK's native `-D` writes
semicolon-joined multi-identifier ID fields at colliding positions — the
same behavior independently confirmed by the three-way bcftools/pysam/GATK
comparison), **325 (0.34%)** are already-retired identifiers. Restricted to
the same 2,894-candidate (2014-2017 merge) panel as the 12.75% headline
figure: 2,799 sarek calls fall in that panel, 324 (11.58%) stale — identical
to the bcftools-substitute run's matched-subset figure (dbSNP138 has zero
ambiguous/duplicate-position cases within that specific panel, so semicolon
-joining never triggers there).

These numbers (94,467 / 325 / 0.34% / 11.58%) are now the ones used in the
manuscript. The section below is kept for the record of how the validation
was originally executed.


## Summary

A real nf-core/sarek 3.9.0 run (HaplotypeCaller, GATK4, Docker, same invocation
pattern as Article 1) was executed end-to-end on the 30x-downsampled HG002 chr20
BAM (GIAB, novoalign, GRCh38), starting from `--step markduplicates`. Runtime:
25m27s, 7/7 processes succeeded.

The resulting VCF (`sarek_out/variant_calling/haplotypecaller/HG002/HG002.haplotypecaller.vcf.gz`)
was annotated against the real GATK dbSNP138 production bundle, then cross-referenced
against the live dbSNP merge ledger (the same `candidate_panel_FULLCOV_allele_exact.csv`
built from full-coverage chr20 scanning used throughout the rest of the paper).

**Result: of 89,568 rsID annotations emitted by this real pipeline run, 325 (0.36%)
are identifiers that dbSNP has already retired as of today** — i.e. a real,
current sarek run assigns a stale rsID that no longer matches its current
canonical form, empirically confirming the paper's central claim on actual
pipeline output rather than only on the GIAB-truth-VCF stand-in.

Note this 0.36% is not directly comparable to the paper's headline 12.75%
GATK-dbSNP138 stale rate: that figure is computed over the full GIAB-truth-set
allele-exact-match candidate panel, while this figure is restricted to
whatever HaplotypeCaller actually called and matched on this one real,
downsampled (30x) BAM. The two numbers measure different things (theoretical
exposure of a bundle vs. what a single real run actually emits); both point
the same direction and this real-run result is the direct empirical validation
that was missing before this run.

## Reproducibility notes / deviations from the original plan

`run_full_pipeline.sh` (the Paper-C-authored orchestration wrapper, NOT
Article 1's `prepare_reference.sh`/`run_sarek.sh`, which were used unmodified)
had two glue-code bugs, both fixed in place:
- `DOWNSAMPLE_FRACTION` was formatted with a leading `0.` and directly
  concatenated after `${DOWNSAMPLE_SEED}.`, producing an invalid
  `samtools view -s` argument (`42.0.4264...`). Fixed to emit only the
  fractional digits.
- The samplesheet generator assumed `prepare_reference.sh` writes the
  downsampled BAM into `$OUTDIR`; it actually writes it relative to the
  script's cwd (`$WORKDIR`). Fixed the samplesheet path.

Additional, non-scripted fixes required once real execution started (documented
here for the Methods/Limitations section, not applied by modifying Article 1's
own scripts):
- The public GIAB HG002 novoalign BAM carries no `@RG` (read-group) tags at
  all (header or per-read) — GATK4 MarkDuplicates requires one. A synthetic
  read group (`ID:HG002, SM:HG002, LB:lib1, PL:ILLUMINA`) was added via
  `samtools addreplacerg`, then the BAM was re-sorted by coordinate (the
  add step had cleared the `SO:coordinate` header tag).
- The Ensembl GRCh38 chr20 FASTA uses bare contig naming (`20`), while the
  GIAB BAM and the derived intervals BED use UCSC-style naming (`chr20`).
  Renamed the FASTA header to `chr20` and regenerated `.fai`/`.dict` to match.
- The extracted BAM's header still carried the full original alignment
  reference's ~1000+ contigs (chr1-22/X/Y/M + hs38d1 decoys), which GATK
  HaplotypeCaller rejects as incompatible with a single-contig reference
  dictionary. Rebuilt the BAM with a chr20-only header via a SAM text
  round-trip (`samtools view -h | awk '...' | samtools view -b`, which
  resolves RNAME by name rather than by the original integer contig index,
  avoiding the corruption a plain `samtools reheader` would cause).

None of these are scientific/methodological changes to Article 1's pipeline
invocation itself — they are data-preparation fixes needed because the public
GIAB BAM's header/read-group metadata doesn't match a fresh Ensembl-downloaded,
single-chromosome reference out of the box. Worth one sentence in the
manuscript's reproducibility/limitations notes if reviewers ask how the real
run was executed.

## Artifacts

- `work/sarek_out/variant_calling/haplotypecaller/HG002/HG002.haplotypecaller.vcf.gz` — real sarek output VCF
- `work/sarek_annotated_dbsnp138.vcf.gz` — annotated against GATK dbSNP138
- `work/sarek_annotated_rsids.tsv` — 89,568 CHROM/POS/REF/ALT/ID rows
- `cross_reference_sarek_output.py` output above — final stale-rate figure
