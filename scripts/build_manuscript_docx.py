# -*- coding: utf-8 -*-
"""Builds the first structured draft of the rsID-retagging manuscript.
Mirrors the structure of Paper A ("When Current Taxids Make Historical Taxa Look
New", JBCB, accepted) since this paper replicates the same mechanism on a second,
independent identifier system (rsID/dbSNP) in a second domain (clinical germline
genomics). All numbers below are taken directly from this session's real analysis
(see README.md / results/ in the same project folder) -- nothing is invented.
"""
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

BLACK = RGBColor(0, 0, 0)
BODY_FONT = "Times New Roman"

def _force_font(run, name=BODY_FONT, size=None, bold=None, italic=None, color=BLACK):
    run.font.name = name
    # east-asian font slot must also be set, otherwise Word can silently fall
    # back to a theme font for some code points and break font homogeneity
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = size
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color

# ---- base style: one font family, black text, homogeneous everywhere ----
normal = doc.styles["Normal"]
normal.font.name = BODY_FONT
normal.font.size = Pt(11)
normal.font.color.rgb = BLACK

for level, size in [(1, 13), (2, 12), (3, 11)]:
    hs = doc.styles[f"Heading {level}"]
    hs.font.name = BODY_FONT
    hs.font.size = Pt(size)
    hs.font.bold = True
    hs.font.italic = False
    hs.font.color.rgb = BLACK
    # clear any inherited paragraph border/shading some Word themes apply to headings
    hs.paragraph_format.space_before = Pt(14)
    hs.paragraph_format.space_after = Pt(6)

def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        _force_font(r, size=Pt({1: 13, 2: 12, 3: 11}[level]), bold=True)
    return p

def para(text, italic=False, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    _force_font(r, bold=bold, italic=italic)
    return p

def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    _force_font(r)
    return p

def add_figure(path, caption, width_in=6.0):
    doc.add_picture(path, width=Inches(width_in))
    last = doc.paragraphs[-1]
    last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    _force_font(r, size=Pt(9.5), italic=True)
    doc.add_paragraph()

_table_counter = [0]

def add_table(headers, rows, title=None):
    # Table title goes ABOVE the table (journal convention; figure captions
    # go below -- see add_figure). Auto-numbered "Table N." if a title is given.
    if title:
        _table_counter[0] += 1
        cap = doc.add_paragraph()
        r = cap.add_run(f"Table {_table_counter[0]}. {title}")
        _force_font(r, bold=True, size=Pt(10.5))
    # "Table Grid" = plain black hairlines, no header shading/banding --
    # a filled/colored table style reads as a slide deck, not a manuscript.
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for i, htext in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(htext)
        _force_font(r, bold=True)
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val))
            _force_font(r)
    doc.add_paragraph()
    return t

# ---- Title page ----
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run("The Half-Life of a Reference Bundle: "
                   "Quantifying rsID Obsolescence in Production Genomic Pipelines")
_force_font(r, size=Pt(15), bold=True)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
_force_font(sub.add_run("[DRAFT MANUSCRIPT]"), italic=True)

doc.add_paragraph()
auth = doc.add_paragraph()
auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
_force_font(auth.add_run("Habib Mahjoubi"), bold=True)

affil = doc.add_paragraph()
affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
_force_font(affil.add_run("Independent Researcher, Nantes, France"))

orcid = doc.add_paragraph()
orcid.alignment = WD_ALIGN_PARAGRAPH.CENTER
_force_font(orcid.add_run("ORCID: 0000-0003-2521-7938"))

email = doc.add_paragraph()
email.alignment = WD_ALIGN_PARAGRAPH.CENTER
_force_font(email.add_run("Email: habibmahjoubi62@gmail.com"))
doc.add_paragraph()

# ---- Abstract ----
h("Abstract", level=1)
para(
    "Reference-identifier renumbering is a known source of false novelty in "
    "historical reconstruction tasks: a companion technical note [1] showed "
    "that resolving a viral sequence's NCBI taxonomy identifier (taxid) via a "
    "current-day lookup manufactures false novelty whenever the identifier was "
    "later merged into another. Whether this failure mode generalizes beyond "
    "taxonomic classification -- to a different identifier system, in a different "
    "genomics domain -- has not been tested. We investigate dbSNP's reference-SNP "
    "identifier (rsID), which is merged under the same administrative logic "
    "(a newer, duplicate rsID is retired into an existing one) but is used in "
    "clinical and research germline variant calling rather than viral metagenomic "
    "classification."
)
para(
    "Using dbSNP's own merge ledger (the dbsnp1_merges field of each RefSNP "
    "record, which dates and versions every historically-absorbed predecessor "
    "identifier), we first confirm the mechanism exists at scale: among real "
    "chr20 variants from the Genome in a Bottle (GIAB) HG002 high-confidence "
    "truth set that have an allele-exact (POS+REF+ALT, SNV-only) match in the "
    "full dbSNP chr20 record set (25,938,655 records scanned; 73,370 such "
    "matches), 66.44% sit on a historically-merged rsID. A verification on "
    "100 randomly sampled retired identifiers confirms the naive-lookup "
    "failure mode directly: all 100 carry no primary variant data of their "
    "own and resolve only through the merge ledger. (Two earlier, "
    "methodologically superseded estimates of the headline rate -- 73.79% "
    "and 47.78%, from a sampling bias and a matching-precision issue "
    "respectively, both since corrected -- are reported and explained in "
    "full in Section 5.2 rather than here.)"
)
para(
    "We then test for downstream impact on artifacts actually used in "
    "production, on the same full-coverage, allele-exact candidate panel "
    "throughout. dbSNP's merge convention retires the numerically higher "
    "identifier into the lower one in 99.97% of 81,963 recorded merge events "
    "(22 documented exceptions); this near-deterministic rule predicts that a "
    "resource assembled before a given identifier existed cannot cite it, "
    "illustrated (not statistically tested, n=8) on 1000 Genomes Phase 3 "
    "(2013). Against a real, still-deployed production bundle (GATK's "
    "dbSNP138 known-sites VCF), 12.75% of 2,894 variants with a 2014-2017 "
    "merge event are reported under the retired identifier (95% CI "
    "11.6-14.0%). A second real bundle (dbSNP144, used by the NCI Genomic "
    "Data Commons) tested on the identical, paired panel shows the "
    "unambiguous rate fall to 2.59% (McNemar's exact test, p=1.9x10^-79) -- "
    "but also reveals a distinct, previously-unanticipated failure mode: "
    "2.18% of variants carry both the current and a not-yet-merged retired "
    "identifier simultaneously in the same bundle file, a non-deterministic "
    "rather than simply outdated outcome -- confirmed directly, not just "
    "inferred, by reparsing the identical bundle file in reverse line order: "
    "all 63 of 63 ambiguous sites return a different identifier depending on "
    "traversal order alone. Combined, dbSNP144's real exposure "
    "(stale or ambiguous) is 4.77%. This is a concrete, currently-live "
    "instance of the reference-artifact drift problem formalized "
    "theoretically in a separate companion work [2]: "
    "identifiers frozen for pipeline-validation stability go stale, or "
    "become ambiguous, at a measurable, age-dependent rate."
)

para("Keywords: dbSNP; rsID merge; reference-identifier drift; false novelty; "
     "GATK known-sites bundle; genomic annotation; reproducibility")

doc.add_page_break()

# ---- 1. Introduction ----
h("1. Introduction", level=1)
para(
    "Biological databases assign identifiers to entities -- taxonomic units, "
    "genetic variants, genes -- that are expected to be stable enough to support "
    "cross-reference over time. In practice, identifiers are periodically "
    "consolidated: two independently-registered entries are later recognized as "
    "the same underlying entity and merged, with one identifier retired in favor "
    "of the other. A companion technical note [1] documented this "
    "phenomenon for NCBI Taxonomy identifiers (taxids) in the context of viral "
    "metagenomic classification, and showed that a naive, current-day-only "
    "lookup manufactures false novelty: an entity that already existed under a "
    "retired identifier appears, incorrectly, to be newly created."
)
para(
    "This raises a natural generalization question: is this an idiosyncrasy of "
    "NCBI Taxonomy's specific curation practice, or a structural property of any "
    "identifier system that undergoes administrative merging? We test this on "
    "dbSNP's reference-SNP identifier (rsID), chosen because it (a) is "
    "administratively merged under a documented, comparable mechanism (a "
    "duplicate submission's identifier is retired into an established one), (b) "
    "belongs to an entirely different genomics domain -- clinical/research "
    "germline variant calling rather than viral metagenomic classification -- "
    "and (c) is embedded in reference resources (known-sites bundles) that are "
    "explicitly, deliberately frozen for long periods in regulated and "
    "production pipelines, for reasons of validation stability."
)
para(
    "A known-sites bundle such as Homo_sapiens_assembly38.dbsnp138.vcf.gz is not "
    "used in only one way, and the two uses differ sharply in whether a stale "
    "identifier matters at all. Fed to GATK's [7] BaseRecalibrator, only the "
    "bundle's genomic positions are consulted -- the ID column is not read, so "
    "a retired rsID there has no effect whatsoever on base-quality "
    "recalibration. Fed to HaplotypeCaller's -D flag (or to VariantAnnotator "
    "--dbsnp), the bundle's ID column is copied directly into the ID field of "
    "every output call at a matching position -- a retired rsID there is "
    "written, verbatim, into the pipeline's own variant-calling output. This "
    "paper's claim concerns the second usage only; nothing here implies BQSR "
    "is affected, and the two must not be conflated. That the annotation "
    "pathway exists and copies the ID column verbatim is documented GATK "
    "behavior, not an assumption of this study; whether a real "
    "HaplotypeCaller -D run against this exact bundle actually emits a stale "
    "identifier in practice, on real chr20 reads, is addressed directly as a "
    "limitation (Section 6.2) and is the subject of ongoing follow-up work."
)
para(
    "That last point connects this study to a second, independent line of work: "
    "a companion theoretical paper [2] argues that regulated "
    "bioinformatics pipelines routinely freeze reference artifacts for "
    "validation-stability reasons, and that the resulting drift between the "
    "frozen artifact and the live reference is a governance problem that current "
    "practice does not measure. This paper supplies exactly that missing "
    "measurement for one concrete, real, currently-deployed artifact: how often "
    "does a frozen dbSNP-based reference bundle actually go stale relative to "
    "the live dbSNP merge ledger?"
)
para(
    "Contribution. We (1) confirm the rsID merge mechanism exists at scale on "
    "real clinical-relevant variants, (2) demonstrate the naive-vs-merge-aware "
    "failure mode directly and reproducibly, (3) show a concrete negative result "
    "refining the hypothesis (an old but actively-used community resource is not "
    "affected), and (4) show a concrete positive result: a specific, widely-used, "
    "still-deployed production reference bundle already carries a measurable "
    "rate of stale identifiers today."
)

# ---- 2. Illustrative Examples ----
h("2. Illustrative Examples", level=1)
para(
    "Before detailing the full protocol, three real cases illustrate the "
    "mechanism concretely (all drawn from this study's own chr20 data; see "
    "Section 5 for the full-scale results)."
)
add_table(
    ["Case", "Position (GRCh38, chr20)", "Current rsID", "Retired rsID found", "Merge date", "Where the retired ID was found"],
    [
        ["A -- naive-lookup failure (internal to dbSNP)", "3,250,488", "rs1207", "rs732922", "2001-01-18",
         "Live dbSNP API record for rs732922 carries no primary variant data of its own (Section 5.3)"],
        ["B -- downstream artifact unaffected (negative control)", "22,279,230*", "rs199784", "rs74969895", "2016-07-19",
         "1000 Genomes Phase 3 (2013) already used the current ID (Section 5.4)"],
        ["C -- downstream artifact stale (positive finding)", "21,320,295", "rs202831", "rs74621691", "2016-02-17",
         "GATK dbSNP138 known-sites bundle still reports rs74621691 today (Section 5.5)"],
    ],
    title="Three illustrative cases of the naive-vs-merge-aware mechanism, drawn from this study's own chr20 data.",
)
para("* Position given in GRCh37/b37 coordinates as used by the 1000 Genomes Phase 3 VCF; "
     "the GRCh38 coordinate for the same variant differs (see Section 4.4).", italic=True)
para(
    "Case A and Case C are the same class of failure (a naive, ID-only lookup "
    "cannot find data for the retired identifier) observed at two different "
    "levels: A is internal to dbSNP itself (proving the mechanism exists), C is "
    "in a real, independently-produced, currently-deployed artifact (proving it "
    "has downstream consequences). Case B shows the same mechanism does not "
    "automatically propagate everywhere -- it depends on whether the specific "
    "downstream artifact was assembled before or after the retired identifier "
    "was ever in active use (Section 6.1)."
)

# ---- 3. Background ----
h("3. Background: The dbSNP Merge Mechanism", level=1)
para(
    "dbSNP assigns a reference-SNP identifier (rsID) to each distinct variant "
    "cluster [4]. When two independently-submitted clusters are later found to "
    "represent the same underlying variant, dbSNP merges them: by convention, "
    "the numerically higher rsID is retired into the numerically lower one. "
    "Historically this was tracked in a standalone relational table "
    "(RsMergeArch.bcp.gz), decommissioned along with the rest of the legacy "
    "build system in 2018 [8]. The current system exposes the same information "
    "directly on each RefSNP JSON record: a dbsnp1_merges array lists every "
    "predecessor identifier ever merged into the current one, each entry dated "
    "and tagged with the dbSNP build revision at which the merge occurred. The "
    "retired identifier's own record correspondingly carries a "
    "merged_snapshot_data.merged_into pointer and no primary_snapshot_data of "
    "its own -- i.e., no position, no alleles, nothing that a naive, "
    "ID-keyed data consumer could use."
)
para(
    "Historical dbSNP build snapshots are archived (NCBI's public archive covers "
    "builds b152 through the current release, 2021-2025, extending back further "
    "for select legacy files to approximately 2015), which -- as with the "
    "NCBI Taxonomy taxdump_archive used in [1] and [2] -- makes multi-version "
    "replay studies possible in principle. This paper instead focuses on a "
    "specific, real, already-deployed static resource (Section 4.4) rather than "
    "a controlled multi-version replay, as a first, concrete demonstration of "
    "downstream impact."
)

# ---- 4. Analysis Protocol ----
h("4. Analysis Protocol", level=1)

h("4.1 Data sources", level=2)
para(
    "(a) dbSNP RefSNP records for chromosome 20 (refsnp-chr20.json.bz2, NCBI "
    "dbSNP latest_release JSON distribution), accessed via HTTP range-fetch and "
    "streamed decompression (the same byte-range partial-fetch technique used "
    "for SRA/ENA data in a companion study [9]). (b) The GIAB HG002 "
    "high-confidence small-variant truth set (NIST v4.2.1, GRCh38) [5], used as a "
    "real, public, clinically-relevant variant panel -- standing in for an "
    "actual pipeline output (see Section 6.2). (c) 1000 Genomes "
    "Project Phase 3 chromosome 20 genotypes (2013 release, GRCh37) [6] as a "
    "historical, still-cited community resource. (d) The GATK best-practices "
    "known-sites bundle Homo_sapiens_assembly38.dbsnp138.vcf.gz (Broad "
    "Institute public reference bucket, GRCh38, dbSNP build 138 content), as a "
    "real, currently-deployed production reference artifact."
)

h("4.2 Candidate panel construction", level=2)
para(
    "For each RefSNP record with a non-empty dbsnp1_merges field, we extracted "
    "its chr20 genomic placement(s) from the record's SPDI representation "
    "(sequence NC_000020.11, 0-based position, deleted_sequence, "
    "inserted_sequence), converted to 1-based VCF-style coordinates, and kept "
    "only true variant alleles (deleted_sequence != inserted_sequence) where "
    "both are a single base (SNVs). Each (position, reference allele, "
    "alternate allele) triple was intersected against the identical triples "
    "observed in the real GIAB HG002 chr20 truth set, i.e., matching is "
    "allele-exact, not position-only. Indel alleles (both in dbSNP's SPDI "
    "representation and in the GIAB truth set) were excluded from this exact "
    "match, since SPDI's anchor convention does not map one-to-one onto VCF's "
    "left-padded indel convention without additional normalization; indels "
    "are handled separately, via an explicit normalization step, in Section "
    "5.7. A position-only variant of this same panel was also built, "
    "to quantify how much allele-exactness matters (Section 5.2)."
)

h("4.3 Naive-vs-merge-aware verification protocol", level=2)
para(
    "Mirroring the naive-vs-merge-aware audit design of [1]: for a random sample "
    "of predecessor (retired) identifiers, we queried the live dbSNP RefSNP API "
    "directly on the OLD identifier. The 'naive' verdict is what a simple, "
    "ID-keyed data consumer would see (does the record carry its own variant "
    "data -- position, alleles -- at all?); the 'merge-aware' verdict follows "
    "the record's merged_snapshot_data.merged_into pointer to the current "
    "identifier and cross-checks it against the current record's own "
    "dbsnp1_merges entry (two independent fields on two different records, "
    "which should agree if the merge ledger is internally consistent)."
)

h("4.4 Downstream-impact test design", level=2)
para(
    "We define a downstream artifact as 'stale' with respect to a given merge "
    "event if it reports the retired (pre-merge) identifier at the variant's "
    "position, rather than the current one. Three artifacts were tested: (i) "
    "1000 Genomes Phase 3 (2013), searched by direct identifier-string match "
    "(chosen specifically because it is coordinate-system-independent, since "
    "this resource uses GRCh37 while the rest of this study uses GRCh38); (ii) "
    "the GATK dbSNP138 bundle (dbSNP build 138, officially released 2013-10-23; exact GRCh38 bundle assembly date not independently verified, GRCh38-native); (iii) the "
    "dbSNP144 bundle used by the NCI Genomic Data Commons (June-2015-vintage "
    "content, GRCh38-native). (ii) and (iii) were both searched by exact "
    "genomic position AND exact allele (REF/ALT extracted directly from each "
    "bundle's own VCF records, matched against the allele-exact candidate "
    "panel of Section 4.2), on the identical subset of candidates whose most "
    "recent recorded merge falls in 2014-2017 -- the window in which each bundle's own "
    "snapshot date makes staleness plausible either way -- so the two bundles' "
    "results are directly, apples-to-apples comparable. A given (position, "
    "reference, alternate) key can appear on more than one line of a bundle's "
    "VCF -- concretely, when a duplicate submission had not yet been merged "
    "into its target at the bundle's snapshot date, both the current and the "
    "eventually-retired identifier are present as separate records at the "
    "same coordinate. All identifiers observed at a given key are retained "
    "(not silently reduced to one), and a key carrying both the current and a "
    "retired identifier simultaneously is scored as a distinct 'ambiguous' "
    "outcome rather than folded into either 'current' or 'stale' (Section 5.6)."
)

# ---- 5. Results ----
h("5. Results", level=1)

h("5.1 Merge rate among sampled chr20 RefSNP records", level=2)
para(
    "An initial byte-range sample of the first ~15,300 chr20 RefSNP records "
    "(necessarily biased toward the lowest, oldest rsID numbers, since the "
    "source file is sorted by identifier rather than genomic position) showed "
    "73.75% carrying at least one merge event (22,755 individual merge events "
    "across 11,308 records; dates 2000-2016). Section 5.2 supersedes this with "
    "the full-coverage figure; it is reported here as a methodological record "
    "of the sampling-bias correction, not as a final estimate."
)

h("5.2 Cross-reference against real GIAB HG002 chr20 variants", level=2)
add_table(
    ["Metric", "Value"],
    [
        ["Distinct real GIAB HG002 chr20 variant positions", "85,951"],
        ["dbSNP chr20 records scanned -- FULL COVERAGE", "25,938,655"],
        ["Allele-exact (SNV) GIAB matches, any merge status -- full coverage", "73,370"],
        ["...of which with merge history -- FINAL FIGURE", "48,746 (66.44%)"],
        ["...of which with no merge history", "24,624"],
        ["[superseded] full-coverage, position-only match", "49,730/104,082 (47.78%)"],
        ["[superseded] partial-sample estimate, position-only", "48,217/65,347 (73.79%)"],
        ["Position-only matches NOT allele-exact, partial sample (false positives)", "376 (0.78%)"],
    ],
    title="Merge rate among real GIAB HG002 chr20 variants: full-coverage, allele-exact final figure versus superseded estimates.",
)
para(
    "This progression is reported in full because each step is a genuine "
    "methodological correction, not a rounding difference. The initial partial "
    "sample (73.79%) over-represented old, heavily-studied variants because "
    "the source file is sorted by identifier, not genomic position. Correcting "
    "for that with full coverage but still matching by position alone gave "
    "47.78% -- but position-only matching also picks up unrelated dbSNP "
    "records that merely share a coordinate with a real GIAB variant (a "
    "multi-allelic site, for instance), which dilutes the rate downward. "
    "Matching allele-exact (POS+REF+ALT, SNV-only) at full coverage removes "
    "both distortions and gives the final, methodologically correct figure: "
    "66.44% -- stated precisely, among the 73,370 real GIAB HG002 chr20 SNV "
    "alleles that have an allele-exact dbSNP record at all (85.4% of the "
    "85,951 distinct GIAB positions; the remainder are indels, excluded here "
    "and addressed separately in Section 5.7, or simply have no dbSNP record "
    "under this exact matching), 48,746 (66.44%) sit on an identifier that "
    "has, at some point, absorbed one or more retired predecessors. Relative "
    "to all 85,951 GIAB positions regardless of match status, the "
    "corresponding figure is 56.71% (48,746/85,951); the two denominators "
    "answer different questions and neither should be read as the other."
)

h("5.3 Naive-vs-merge-aware verification (n=100)", level=2)
para(
    "An initial pilot (n=30, seed=42) was extended to n=100 (seed=42, drawn "
    "from the allele-exact candidate panel of Section 4.2). For all 100 "
    "randomly sampled retired identifiers, querying the live dbSNP RefSNP API "
    "directly on the retired identifier returned no primary_snapshot_data of "
    "its own (100/100), and all 100 (100%) resolved via "
    "merged_snapshot_data.merged_into to the expected current identifier "
    "-- perfect agreement between two independent fields of dbSNP's own record "
    "structure, at more than 3x the original pilot's scale. Full results: see "
    "results/09_naive_vs_mergeaware_verification_n100.json (supersedes the "
    "earlier n=30 pilot, results/03_...json, kept for the record)."
)

h("5.4 A structural argument, illustrated on 1000 Genomes Phase 3", level=2)
para(
    "The real load-bearing argument in this section is deductive, not "
    "empirical: dbSNP's merge convention retires the numerically higher "
    "identifier into the lower one, so a resource assembled before the "
    "retired identifier was ever registered could not possibly have cited "
    "it. We verified this convention directly rather than assuming it: "
    "across all 81,963 merge events recorded for our full-coverage "
    "candidate panel, the retired identifier is numerically higher than the "
    "current one in 81,941 cases (99.97%), with 22 documented exceptions "
    "(e.g., current rsID 73623650 absorbed the numerically lower rs58444546). "
    "The structural argument therefore holds with near-certainty, not "
    "absolute certainty, and is stated that way."
)
para(
    "An empirical illustration, not a statistically powered test in its own "
    "right, confirms the argument on one real resource: of 8 tested retired "
    "identifiers (the most-recently-merged 2014-2016 candidates available at "
    "the time this check was run), zero were found in the 1000 Genomes Phase "
    "3 chr20 VCF (2013); the corresponding current identifiers were found "
    "instead, already present in that 2013 release. With n=8 and 0 events, "
    "the exact (Clopper-Pearson) 95% upper bound on the true rate is 36.9% -- "
    "this illustration alone could not detect a real but modest effect, "
    "which is precisely why the structural argument above, not this count, "
    "is what the claim rests on."
)

h("5.5 Downstream impact -- GATK dbSNP138 known-sites bundle (positive)", level=2)
para(
    "Candidates and bundle contents are both matched allele-exact "
    "(POS+REF+ALT, SNV-only; see Section 4.2), on the full-coverage candidate "
    "panel of Section 5.2 (48,746 merged variants) restricted to those whose "
    "most recent merge falls in 2014-2017 -- 2,894 candidates. Two earlier, "
    "smaller-scale passes on a partial sample (position-only: 217/2,788, "
    "7.78%, with 99 unexplained 'different identifier' cases; allele-exact on "
    "that same partial sample: 219/2,657, 8.24%, with 0 unexplained cases) are "
    "both superseded by the full-coverage figure below; the 'different "
    "identifier' category stays at zero throughout once matching is "
    "allele-exact."
)
add_table(
    ["Metric", "Value"],
    [
        ["Candidates tested (merge date 2014-2017, full-coverage allele-exact panel)", "2,894"],
        ["Position+allele absent from the bundle", "19"],
        ["Bundle reports the current (post-merge) rsID", "2,506 (86.6%)"],
        ["Bundle reports a retired (pre-merge) rsID -- STALE", "369 (12.75%, 95% Wilson CI 11.58-14.02%)"],
        ["Bundle reports a different identifier (same allele)", "0"],
    ],
    title="Stale-identifier rate for the GATK dbSNP138 known-sites bundle (full-coverage, allele-exact matching).",
)
para(
    "369 real, clinically-relevant chr20 variants are reported today, by a "
    "still-actively-deployed production reference bundle, under an identifier "
    "that dbSNP has since formally retired. A variant-calling pipeline "
    "annotating against this bundle right now would emit exactly these stale "
    "identifiers; any downstream, identifier-keyed cross-reference against a "
    "current resource would silently fail to recognize the match."
)

h("5.6 Downstream impact -- multi-version bundle comparison", level=2)
para(
    "To test whether staleness is a graded, age-dependent property rather than a "
    "single data point, we repeated the Section 5.5 protocol on a second real, "
    "independently-deployed GRCh38 bundle: dbsnp_144.hg38.vcf.gz (Broad Institute "
    "public reference bucket, path used by the NCI Genomic Data Commons for TCGA "
    "and other cancer genomics cohorts; file date 2015-06-03, dbSNP build 144), "
    "against the identical 2,894-candidate full-coverage allele-exact panel."
)
add_table(
    ["Metric", "dbSNP138 (build 2013-10-23)", "dbSNP144 (June 2015)"],
    [
        ["Position+allele absent from bundle", "19", "31"],
        ["Bundle reports ONLY the current (post-merge) rsID", "2,506 (86.6%)", "2,725 (94.16%)"],
        ["Bundle reports ONLY a retired (pre-merge) rsID -- STALE", "369 (12.75%, CI 11.58-14.02%)", "75 (2.59%, CI 2.07-3.24%)"],
        ["Bundle reports BOTH current and retired rsID at the same site -- AMBIGUOUS", "0", "63 (2.18%)"],
    ],
    title="Stale-identifier rate compared across two real, independently-deployed GRCh38 bundle vintages (full coverage).",
)
para(
    "The unambiguous stale-identifier rate drops from 12.75% to 2.59% between "
    "the two bundles, in the expected direction: the newer bundle has already "
    "absorbed most of the 2014-2015 merges present in this panel, while a "
    "number of later (2015-2017) merges remain stale in both (e.g., "
    "chr20:47,829,240, current rs440633, reported as rs80132470 -- merged "
    "2016-07-19 -- by both the dbSNP138 and the June-2015 bundle). This is a "
    "real, measured two-point temporal trend, not an artifact of a single "
    "snapshot, and is directly analogous in spirit to the multi-version "
    "drift analysis in the companion case study [2], applied here "
    "to a different identifier system and a real production artifact rather "
    "than a controlled replay. The two bundles are tested on the identical "
    "2,894 candidates, so this is a paired design: the correct test is "
    "McNemar's, not a Fisher/chi-square test on independent samples (an "
    "earlier draft of this analysis used Fisher's exact test, which is "
    "statistically mis-specified for paired data and has been replaced). On "
    "the strict stale-vs-not-stale paired table (68 stale in both bundles, "
    "301 stale only in dbSNP138, 7 stale only in dbSNP144, 2,518 stale in "
    "neither), McNemar's exact test gives p = 1.9x10^-79. The 369 stale "
    "positions in dbSNP138 are also not concentrated in one or two "
    "problematic loci: they span nearly the full length of chromosome 20 "
    "(position 130,329 to 63,061,840) across 54 of ~64 one-megabase bins, "
    "with the densest bin holding only 31 (8.4%) -- the effect is broadly "
    "distributed, not an artifact of a single repetitive or poorly-curated "
    "region."
)
para(
    "A cross-check for internal consistency -- the stale set at a later "
    "bundle snapshot should be nearly a subset of the stale set at an earlier "
    "one, since a merge event visible before a bundle's snapshot should still be unresolved in "
    "2015 unless the bundle specifically fixed it -- initially failed: 18 of "
    "105 dbSNP144 stale candidates were not stale in dbSNP138. Investigating "
    "this directly against the raw VCF (chr20:49,283,799 G>C, "
    "dbSNP144.hg38.vcf.gz) revealed a genuine, previously-unaccounted-for "
    "third outcome: the bundle can carry two separate VCF records at the "
    "exact same position and allele -- the current identifier (rs238202) and "
    "an as-yet-unmerged duplicate submission (rs386421256, merged into "
    "rs238202 on 2015-07-01, three weeks after this bundle's 2015-06-03 "
    "snapshot) -- rather than reporting a single, unambiguous identifier. "
    "Re-scoring with all identifiers retained per (position, reference, "
    "alternate) key, rather than collapsing to one, produces 63 AMBIGUOUS "
    "candidates in dbSNP144 (Table above). These 63 do not all come from the "
    "naive 'stale' bucket, and the reconciliation is exact: under the "
    "original single-identifier-per-key scoring, dbSNP144 showed 2,758 "
    "current and 105 stale; under the fixed, multi-identifier scoring it "
    "shows 2,725 current, 75 stale, and 63 ambiguous. Of the 63, 33 were "
    "originally (mis)classified as current and 30 as stale "
    "(33+30=63; 2,758-33=2,725; 105-30=75, both exact). dbSNP138 is "
    "unaffected by this correction (zero ambiguous cases in this panel). "
    "Ambiguity is arguably a more concerning failure mode than plain "
    "staleness for a naive, identifier-keyed consumer: which of the two "
    "co-located records it reads back depends on row order or tool "
    "implementation, not on anything the data itself resolves -- the query "
    "is non-deterministic rather than merely outdated. Combining the two "
    "concrete risk categories in a second, equally valid paired comparison "
    "(stale-or-ambiguous vs. current-only: 113 in both bundles, 256 only in "
    "dbSNP138, 25 only in dbSNP144, 2,500 in neither) puts dbSNP144's real "
    "exposure at 4.77% (138/2,894, 95% Wilson CI 4.05-5.61%) rather than the "
    "2.59% strict-stale figure alone -- McNemar's exact test on this combined "
    "table remains highly significant (p = 2.0x10^-49)."
)
para(
    "A confound in the '138 vs. 144' framing must be disclosed directly: "
    "these are not two snapshots of one export pipeline aging in place, but "
    "two independently-curated exports (GATK's own bundle; the NCI Genomic "
    "Data Commons' bundle), and they do not simply agree wherever a merge is "
    "not involved. 31 of the panel's positions are absent from dbSNP144 "
    "versus 19 from dbSNP138 -- the newer bundle is missing MORE positions, "
    "not fewer, which a pure aging story would not predict. Checked directly "
    "against the raw file, this is a real content difference, not a "
    "matching artifact: chr20:17,772,881 T>G (rs241136) has no VCF record at "
    "all in dbSNP144, while dbSNP138 reports it cleanly. Some portion of the "
    "observed 138-to-144 improvement therefore reflects a difference in "
    "curation/filtering criteria between GATK's and GDC's export pipelines, "
    "not purely the passage of time; this is stated as a limitation "
    "(Section 6.2), not resolved here."
)
para(
    "A simple predictive model of the drift itself -- for a bundle frozen at "
    "date T, the predicted stale rate is the fraction of variants whose most "
    "recent merge postdates T -- can be built directly from the merge-date "
    "distribution of the full 48,746-candidate panel and checked against the "
    "two observed points. Using dbSNP138's official build-release date "
    "(2013-10-23) and dbSNP144's file date (2015-06-03), the naive model "
    "predicts 5.94% stale for dbSNP138 and 0.77% for dbSNP144, evaluated over "
    "the full panel -- roughly 7-8x higher than the actually observed rates "
    "on that same full panel (0.76% and 0.15% respectively; these full-panel "
    "figures differ from the 12.75%/2.59% above because they are computed "
    "over all 48,746 candidates rather than the 2,894 restricted to a "
    "2014-2017 merge). This is an informative negative result, not a "
    "failure to hide: it indicates either that this bundle's true content "
    "date is materially later than dbSNP138's nominal build-release date "
    "(consistent with the unresolved uncertainty about the GRCh38 bundle's "
    "exact assembly date -- Section 4.1), or that a single hard cutoff date "
    "is too coarse a model for how a bundle's content is actually assembled. "
    "Either reading reinforces this paper's governance point: even the "
    "'when was this reference actually frozen' question, prerequisite to "
    "any calibrated drift model, is not reliably answerable from the "
    "artifact itself."
)

add_figure(
    "figure1_stale_rate_by_vintage.png",
    "Figure 1. Unambiguous stale-identifier rate for the identical 2,894-variant, "
    "full-coverage allele-exact panel, tested against two real, independently-deployed "
    "GRCh38 dbSNP bundles of different vintage (excludes the ambiguous "
    "both-identifiers-present outcome; see Figure 2 and Section 5.6).",
)
add_figure(
    "figure2_composition_breakdown.png",
    "Figure 2. Full outcome breakdown per bundle: most variants are reported "
    "under their current identifier in both bundles, but dbSNP138 shows "
    "a larger unambiguous-stale share (red) while dbSNP144 (2015) instead "
    "shows a substantial ambiguous share (gray) -- both current and retired "
    "identifiers present for the same site (Section 5.6).",
)

h("5.7 Extending to indels (full coverage)", level=2)
para(
    "All results above are restricted to SNVs, since dbSNP's SPDI "
    "representation and VCF's anchor-base convention for indels do not "
    "align directly. We built a normalization function (shared prefix/suffix "
    "trimming, applied identically to both representations; verified "
    "idempotent on already-minimal SPDI input) and re-ran the full-coverage "
    "candidate-panel construction (all 25,938,655 chr20 dbSNP records scanned) "
    "including indel alleles, yielding 4,613 candidates with a 2014-2017 merge "
    "history (2,894 SNVs, unchanged from Section 5.5-5.6, plus 1,719 indels), "
    "specifically to test whether indels change the picture rather than "
    "simply padding it."
)
para(
    "Indel matching is real but imperfect. Against dbSNP138, the 1,719 indel "
    "candidates split into 1,421 resolved to a definite outcome (82.7%), 181 "
    "landing in neither the 'current' nor the 'stale' category, and 117 "
    "entirely absent from the bundle (181+117=298=1,719-1,421, exact); "
    "against dbSNP144, 1,416 resolved (82.4%), 212 in neither, and 91 absent "
    "(212+91=303=1,719-1,416, exact). SNVs, by contrast, resolve at 99.3% "
    "(dbSNP138) and 98.9% (dbSNP144). This confirms directly, at full "
    "coverage, that simple prefix/suffix trimming does not resolve every "
    "equivalent indel representation in low-complexity genomic contexts (a "
    "limitation now quantified rather than assumed); the 'absent' category "
    "is a separate, unremarkable outcome (the bundle simply does not carry "
    "that site) and is not evidence of a matching problem."
)
add_table(
    ["Outcome (of matched variants)", "SNV, dbSNP138", "Indel, dbSNP138", "SNV, dbSNP144", "Indel, dbSNP144"],
    [
        ["Stale", "369/2,875 (12.83%)", "19/1,421 (1.34%)", "75/2,863 (2.62%)", "17/1,416 (1.20%)"],
        ["Ambiguous (both IDs)", "0/2,875 (0.00%)", "62/1,421 (4.36%)", "63/2,863 (2.20%)", "172/1,416 (12.15%)"],
    ],
    title="Indels versus SNVs: stale and ambiguous rates among successfully matched variants (full coverage).",
)
para(
    "At full coverage, the direction is consistent, not reversed: indels are "
    "less often unambiguously stale than SNVs in both bundles (1.34% vs. "
    "12.83% in dbSNP138; 1.20% vs. 2.62% in dbSNP144). This corrects an "
    "earlier partial-sample reading from this study's development, which "
    "had reported a reversal for dbSNP144 (indels more often stale than "
    "SNVs) -- that reversal does not survive full-coverage re-analysis and is "
    "retracted here rather than carried forward, for the same reason "
    "Section 5.2's initial estimate was corrected. What does hold up at full "
    "coverage is the ambiguous rate: substantially higher for indels than "
    "SNVs in both bundles (4.36% vs. 0.00% in dbSNP138; 12.15% vs. 2.20% in "
    "dbSNP144, roughly 5.5x). One plausible reading is that indels in "
    "repetitive or low-complexity contexts are administratively harder for "
    "dbSNP itself to deduplicate promptly, leaving more of them in the "
    "ambiguous, not-yet-resolved state captured in Section 5.6; this is not "
    "established here and is noted as a direction for further work, not a "
    "conclusion."
)

h("5.8 Demonstrating non-determinism directly", level=2)
para(
    "Section 5.6 argues that the ambiguous outcome is worse than plain "
    "staleness because the answer a consumer gets depends on implementation "
    "detail rather than on the data itself. This is tested directly, not "
    "just asserted, on all 63 dbSNP144 ambiguous sites: the identical bundle "
    "file was parsed twice with a single-identifier-per-key lookup (the same "
    "kind of plain, unordered key-value collection a short annotation script "
    "would naturally write) -- once reading the file forward, once reading "
    "it in reverse line order. Nothing about the file's content changes "
    "between the two runs, only the traversal order."
)
para(
    "Result: all 63 of 63 ambiguous sites (100%) return a DIFFERENT "
    "identifier under forward versus reverse traversal. For example, at "
    "chr20:49,283,799 (G>C), forward order returns rs386421256 (the retired "
    "identifier) while reverse order returns rs238202 (the current one) -- "
    "for the exact same file, the exact same site, the exact same query. "
    "This confirms the mechanism concretely: it is not merely plausible that "
    "different consumers could disagree, every single ambiguous site "
    "produces a different answer under two entirely legitimate, "
    "deterministic-in-isolation processing strategies. A literal three-way "
    "comparison across bcftools, pysam, and GATK's own VCF readers was "
    "planned but could not be completed in this draft (blocked by the same "
    "WSL/Docker environment outage noted in Section 6.2 for the sarek "
    "validation); the forward/reverse test above demonstrates the same "
    "underlying order-dependence without requiring those specific tools, "
    "and is offered as the concrete result pending that fuller comparison."
)

# ---- 6. Discussion ----
h("6. Discussion", level=1)

h("6.1 Generalizing the Taxid-Retagging Mechanism", level=2)
para(
    "These results generalize the core finding of [1] beyond taxonomic "
    "classification: reference-identifier retagging causing false novelty (or, "
    "in this case, false absence/orphaning under naive lookup) is not specific "
    "to NCBI Taxonomy's curation practice -- it recurs under dbSNP's rsID "
    "system, in an unrelated genomics domain (germline variant calling rather "
    "than viral classification). dbSNP and NCBI Taxonomy are both maintained "
    "by NCBI, so this is not a test of two organizationally unrelated "
    "institutions; what is independent is the curation logic itself -- "
    "distinct data models, distinct submission and deduplication pipelines, "
    "and distinct triggers for when a merge happens (taxonomic reclassification "
    "versus duplicate-variant-submission consolidation). The generalization "
    "claim is that the same naive-lookup failure mode recurs whenever an "
    "identifier system merges entities administratively, not that it recurs "
    "across unrelated organizations."
)
para(
    "The negative result (Section 5.4) sharpens rather than weakens this claim: "
    "it shows the risk is not diffuse ('any old resource is dangerous') but "
    "structurally concentrated in a specific, identifiable class of artifact -- "
    "one frozen after the retired identifier came into existence. The positive "
    "result (Section 5.5) shows that this class is not hypothetical: a real, "
    "specifically-named, still-widely-used production artifact already belongs "
    "to it, today, at a measurable rate (12.75% in this sample)."
)
para(
    "This directly instantiates the drift-governance problem formalized "
    "theoretically in the companion paper [2]: pipelines "
    "deliberately freeze reference artifacts such as known-sites bundles for "
    "validation stability, and current regulatory practice (blanket "
    "revalidation on any reference change, per AMP/CAP guidance) offers no "
    "calibrated way to weigh that frozen artifact's accumulating staleness "
    "against the cost of re-validating against a refreshed one. This paper "
    "supplies a first, concrete, measured instance of that cost for one real "
    "artifact, rather than a theoretical or simulated one."
)

h("6.2 Limitations", level=2)
for item in [
    "Both the GIAB-wide merge rate (Section 5.2) and the downstream-impact "
    "panel (Sections 5.5-5.6) are now full-coverage (25,938,655 records "
    "scanned; 2,894 candidates), superseding all earlier partial-sample "
    "estimates reported during this study's development.",
    "Section 5.7 extends matching to indels via prefix/suffix normalization, "
    "now also at full coverage (25,938,655 records scanned; 1,719 indel "
    "candidates), and finds a genuinely different pattern from SNVs (lower "
    "unambiguous-stale rate, substantially higher ambiguous rate) rather than "
    "a simple confirmation -- but only ~82.5% of indel candidates resolve to "
    "a definite outcome (versus ~99% of SNVs) due to unresolved "
    "equivalent-representation cases in low-complexity contexts. An earlier "
    "partial-sample reading of this same comparison had reported a reversal "
    "(indels more often stale than SNVs in dbSNP144) that did not survive "
    "full-coverage re-analysis and has been retracted in Section 5.7.",
    "The GIAB HG002 truth VCF is used as a stand-in for a real pipeline output; "
    "no actual nf-core/sarek run (the pipeline used in [3]) has yet been "
    "annotated against these resources.",
    "Two frozen bundles have been tested (dbSNP138, dbSNP144), giving a real "
    "but short two-point trend (12.75% to 2.59% unambiguous stale, "
    "full-coverage allele-exact); a third, later point (dbSNP151/152 or the "
    "current release) would better bound the curve. The only dbSNP151/156-"
    "vintage GRCh38 resource found in the same public bucket is in Illumina's "
    "proprietary Nirvana annotation format (.nsa), not a standard VCF, and "
    "was not processed for this draft.",
    "The ambiguous-outcome category (Sections 5.6, 5.8; 2.18% of dbSNP144 "
    "candidates) was discovered via a single internal-consistency check "
    "(stale-set monotonicity across bundle vintage) and has only been "
    "characterized on this one bundle; whether it recurs at other snapshot "
    "dates, in dbSNP138, or in other reference-database export pipelines "
    "entirely is not yet known. Section 5.8's forward/reverse test "
    "demonstrates order-dependence concretely but is not a substitute for "
    "testing literal disagreement across bcftools, pysam, and GATK's own "
    "readers, which remains blocked by this session's WSL/Docker "
    "environment outage (see the sarek-validation limitation below).",
    "dbSNP138 and dbSNP144 are two independently-curated exports (GATK's own "
    "bundle; the NCI Genomic Data Commons' bundle), not two snapshots of one "
    "pipeline -- Section 5.6 documents a real, unexplained content "
    "difference (31 candidate positions entirely absent from dbSNP144 versus "
    "19 from dbSNP138) consistent with differing curation/filtering criteria "
    "between the two exports. Some fraction of the observed 138-to-144 "
    "improvement may reflect this rather than pure temporal drift; this "
    "study does not separate the two effects.",
    "The exact assembly date of the GATK GRCh38 dbSNP138 bundle (as opposed "
    "to dbSNP build 138's official 2013-10-23 release date, used throughout "
    "as this study's best available anchor) could not be independently "
    "verified from the file itself. A simple drift-prediction model built "
    "from this date overestimates the observed full-panel stale rate by "
    "roughly 7-8x (Section 5.6), which is itself evidence that either this "
    "date is materially wrong or a single hard cutoff is too coarse a model "
    "-- both readings leave the exact predictive calibration of the "
    "'half-life' promised in this paper's title as future work, not a "
    "delivered result.",
    "The background merge rate across ALL 25,938,655 scanned chr20 records "
    "(not just the 73,370 with a GIAB match) has not been computed; without "
    "it, whether 66.44% represents enrichment in real, clinically-observed "
    "variants or is unremarkable relative to dbSNP's general population of "
    "registered identifiers cannot be determined from this draft.",
    "ClinVar was queried directly for all 369 dbSNP138-stale identifiers "
    "(both the current and the retired id, via NCBI E-utilities; method "
    "validated against two known-pathogenic controls, rs334 and rs6025, "
    "which correctly returned 10 and 3 ClinVar records respectively). The "
    "honest result is a clean negative: none of the 369 pairs -- neither the "
    "current nor the retired identifier -- has any ClinVar record at all. "
    "This panel therefore does not support a clinical-safety framing of the "
    "finding; the population here (old, low-numbered, commonly-resubmitted "
    "polymorphisms selected only for having a 2014-2017 merge date) is "
    "plausibly enriched for benign, well-established variants rather than "
    "rare disease-associated ones. Whether the stale-identifier problem has "
    "real clinical consequence remains an open question, to be tested on a "
    "panel constructed the other way around -- starting from known ClinVar "
    "pathogenic variants and checking their merge history -- not answered "
    "by this study. gnomAD was not queried, since the ClinVar result already "
    "closes the specific question asked without needing a second negative "
    "check.",
    "The GIAB HG002 high-confidence call set is itself enriched for "
    "well-characterized, easy-to-call genomic regions, which tend to be "
    "older and more heavily resubmitted to dbSNP than a typical clinical "
    "call set's variants; the 66.44% figure is likely an overestimate "
    "relative to a real, unselected clinical variant-calling workload.",
]:
    bullet(item)

h("6.3 Implications for practice", level=2)
for item in [
    "Reference bundles used for variant annotation should carry an explicit, "
    "machine-readable snapshot date/build identifier, and pipelines should log "
    "which build was used for every annotated call (many already do; this "
    "should be treated as a governance requirement, not an optional detail).",
    "Identifier-keyed cross-referencing between an annotated call set and any "
    "external resource (ClinVar, gnomAD, a prior study) should resolve merges "
    "via the current dbSNP merge ledger rather than assuming identifier "
    "stability -- exactly analogous to the recommendation in [1] for taxid-keyed "
    "historical reconstruction.",
    "A calibrated, risk-proportionate bundle-refresh policy (rather than either "
    "never refreshing, or blanket revalidation on every dbSNP release) is "
    "exactly the kind of decision the governance model of [2] is meant "
    "to support; this study's measured 12.75% stale-identifier rate for one "
    "bundle at one point in its lifetime is a candidate input to that model.",
]:
    bullet(item)

# ---- Backmatter ----
h("Data and Code Availability", level=1)
para(
    "All data sources used are public: dbSNP (NCBI, latest_release JSON "
    "distribution and RefSNP REST API), GIAB HG002 v4.2.1 (NIST), 1000 Genomes "
    "Phase 3 (IGSR), and the GATK dbSNP138 known-sites bundle (Broad Institute "
    "public reference bucket). All scripts and intermediate results referenced "
    "in this manuscript are archived alongside it "
    "[repository/DOI -- to be created before submission, following the same "
    "GitHub+Zenodo pattern used for [1]]."
)

h("Acknowledgments", level=1)
para(
    "This research received no external funding. The author used Claude Code "
    "(Anthropic) to assist with data analysis scripts and manuscript "
    "preparation, reviewed and edited all content, and takes full "
    "responsibility for the publication."
)

h("Conflict of Interest", level=1)
para("The author declares no conflict of interest.")

h("References", level=1)
refs = [
    "[1] Mahjoubi H. When Current Taxids Make Historical Taxa Look New. "
    "J Bioinform Comput Biol. 2026 [accepted]. Preprint: Zenodo, "
    "https://doi.org/10.5281/zenodo.21861803.",
    "[2] Mahjoubi H. Structural Change Is Not Impact: Why Reference-Artifact "
    "Diffs Fail to Scope Regression Testing, with a Bioinformatics Case Study. "
    "Software Quality Journal [submitted].",
    "[3] Mahjoubi H, Rebai A. Automated discovery of metamorphic relations by "
    "LLMs for oracle-free validation of regulated genomics pipelines. "
    "[manuscript in preparation]. Code: "
    "https://github.com/[repository pending -- to confirm before submission].",
    "[4] Sherry ST, Ward MH, Kholodov M, Baker J, Phan L, Smigielski EM, "
    "Sirotkin K. dbSNP: the NCBI database of genetic variation. Nucleic Acids "
    "Res. 2001;29(1):308-311.",
    "[5] Zook JM, McDaniel J, Olson ND, Wagner J, Parikh H, Heaton H, Irvine SA, "
    "Trigg L, Truty R, McLean CY, De La Vega FM, Xiao C, Sherry S, Salit M. An "
    "open resource for accurately benchmarking small variant and reference "
    "calls. Nat Biotechnol. 2019;37:561-566.",
    "[6] The 1000 Genomes Project Consortium. A global reference for human "
    "genetic variation. Nature. 2015;526(7571):68-74.",
    "[7] McKenna A, Hanna M, Banks E, Sivachenko A, Cibulskis K, Kernytsky A, "
    "Garimella K, Altshuler D, Gabriel S, Daly M, DePristo MA. The Genome "
    "Analysis Toolkit: a MapReduce framework for analyzing next-generation DNA "
    "sequencing data. Genome Res. 2010;20(9):1297-1303.",
    "[8] NCBI Insights. Important dbSNP updates: New JSON data files, RefSNP "
    "report, API. 2018. https://ncbiinsights.ncbi.nlm.nih.gov/2018/06/15/"
    "dbsnp-updates-json-refsnp-report-api/",
    "[9] Mahjoubi H. A probabilistic detection-confidence score for validating "
    "NGS-based adventitious virus detection in biopharmaceutical matrices: a "
    "risk-stratified benchmark. Biotechnology and Bioengineering [submitted].",
]
for ref_text in refs:
    para(ref_text)

doc.save("Manuscript_Draft.docx")
print("Saved Manuscript_Draft.docx")
