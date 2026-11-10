## Table 1. Retired rsIDs written by four dbSNP files to three whole genomes

Benchmark variants (chr1-22): HG001 3,893,341, HG002 4,048,342, HG005 3,856,856.

| dbSNP file | Genome | Annotation rate (95% CI) | Variant rate (95% CI) | SNVs | Indels | Only retired rsIDs |
|---|---|---|---|---|---|---|
| dbSNP138 (WARP default) | HG001 | 5.00% (4.98-5.02) | 4.76% (4.74-4.79) | 1.41% | 27.47% | 2.00% |
| dbSNP138 (WARP default) | HG002 | 5.18% (5.16-5.20) | 4.95% (4.93-4.98) | 1.48% | 27.29% | 2.10% |
| dbSNP138 (WARP default) | HG005 | 4.72% (4.70-4.74) | 4.49% (4.46-4.51) | 1.50% | 27.44% | 2.04% |
| dbSNP144 (GDC) | HG001 | 10.17% (10.14-10.20) | 8.29% (8.26-8.31) | 0.73% | 57.30% | 1.17% |
| dbSNP144 (GDC) | HG002 | 10.52% (10.49-10.55) | 8.62% (8.59-8.65) | 0.75% | 56.79% | 1.28% |
| dbSNP144 (GDC) | HG005 | 8.78% (8.76-8.81) | 7.24% (7.21-7.27) | 0.76% | 55.54% | 1.00% |
| dbSNP146 (sarek default) | HG001 | 10.38% (10.35-10.41) | 8.42% (8.39-8.44) | 0.15% | 62.11% | 1.34% |
| dbSNP146 (sarek default) | HG002 | 10.71% (10.68-10.74) | 8.72% (8.70-8.75) | 0.16% | 61.27% | 1.45% |
| dbSNP146 (sarek default) | HG005 | 8.93% (8.90-8.96) | 7.30% (7.27-7.32) | 0.17% | 60.47% | 1.11% |
| dbSNP156 (NCBI release, Nov 2022) | HG001 | 0.469% (0.462-0.475) | 0.140% (0.136-0.144) | 0.142% | 0.127% | 0 variants |
| dbSNP156 (NCBI release, Nov 2022) | HG002 | 0.463% (0.456-0.469) | 0.141% (0.137-0.144) | 0.144% | 0.121% | 1 variant |
| dbSNP156 (NCBI release, Nov 2022) | HG005 | 0.490% (0.483-0.497) | 0.147% (0.143-0.150) | 0.149% | 0.131% | 1 variant |

## Table 2. What a plain rsID join changes downstream (values: HG001 / HG002 / HG005)

| Knowledge base and category | dbSNP138 (WARP default) | dbSNP146 (sarek default) | dbSNP156 (NCBI release, Nov 2022) |
|---|---|---|---|
| ClinVar P/LP (>=1 star) entries matching a variant by position and allele, n (a) | 3 / 1 / 1 | 3 / 1 / 3 | 3 / 1 / 3 |
|   of which missed because of a retired rsID, n | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| ClinVar P/LP (>=1 star) entries attached by the rsID join to a different allele, n | 31 / 30 / 31 | 31 / 30 / 31 | 34 / 33 / 33 |
| ClinVar B/LB (>=1 star) entries missed because of a retired rsID, % | 1.14% / 1.14% / 1.08% | 0.97% / 1.04% / 0.83% | 0.00% / 0.00% / 0.00% |
| ClinVar B/LB (>=1 star) entries missed because ClinVar gives no rsID, % | 1.86% / 1.89% / 1.61% | 1.88% / 1.94% / 1.64% | 1.88% / 1.94% / 1.65% |
| GWAS Catalog associations (p < 5x10^-8) missed, % | 1.02% / 1.03% / 0.93% | 0.53% / 0.49% / 0.43% | 1.13% / 1.16% / 0.97% |
|   of which retired rsID on the pipeline side, % | 0.47% / 0.45% / 0.49% | 0.09% / 0.10% / 0.07% | 0.00% / 0.00% / 0.00% |
| PharmGKB clinical annotations, levels 1A-2B, missed, n of N | 0 of 48 / 0 of 22 / 0 of 18 | 0 of 48 / 0 of 22 / 0 of 20 | 0 of 48 / 0 of 22 / 0 of 20 |

## Table S2. Per-chromosome range of the annotation rate, and bundle rate

| dbSNP file | Bundle rate (retired / distinct rsIDs, chr1-22) | Per-chromosome annotation rate, range: HG001 / HG002 / HG005 |
|---|---|---|
| dbSNP138 | 1,021,831 / 58,373,860 = 1.750% | 4.03-5.09% / 4.18-5.33% / 3.53-4.84% |
| dbSNP144 | 2,145,350 / 138,551,914 = 1.548% | 7.17-9.22% / 7.69-9.65% / 6.20-8.11% |
| dbSNP146 | 2,294,215 / 143,491,344 = 1.599% | 7.64-9.44% / 8.11-9.74% / 6.53-8.45% |
| dbSNP156 | 508,061 / 1,051,650,413 = 0.048% | 0.04-0.29% / 0.03-0.29% / 0.03-0.34% |

## Table S3. Where the current rsID of each retired rsID sits in dbSNP156

| dbSNP file | Genome | Retired rsIDs written | Same allele (95% CI) | Same position, other allele | Elsewhere or absent |
|---|---|---|---|---|---|
| dbSNP138 | HG001 | 199,651 | 99.69% (99.66-99.71) | 91 (0.05%) | 535 (0.27%) |
| dbSNP138 | HG002 | 212,757 | 99.65% (99.62-99.67) | 102 (0.05%) | 644 (0.30%) |
| dbSNP138 | HG005 | 183,974 | 99.70% (99.68-99.73) | 95 (0.05%) | 449 (0.24%) |
| dbSNP144 | HG001 | 428,647 | 99.79% (99.77-99.80) | 163 (0.04%) | 753 (0.18%) |
| dbSNP144 | HG002 | 458,933 | 99.77% (99.75-99.78) | 182 (0.04%) | 892 (0.19%) |
| dbSNP144 | HG005 | 358,302 | 99.83% (99.81-99.84) | 151 (0.04%) | 463 (0.13%) |
| dbSNP146 | HG001 | 447,812 | 99.59% (99.57-99.61) | 189 (0.04%) | 1,657 (0.37%) |
| dbSNP146 | HG002 | 478,756 | 99.59% (99.57-99.60) | 253 (0.05%) | 1,731 (0.36%) |
| dbSNP146 | HG005 | 372,616 | 99.56% (99.54-99.58) | 199 (0.05%) | 1,452 (0.39%) |
| dbSNP156 | HG001 | 18,325 | 99.99% (99.97-100.00) | 0 (0.00%) | 1 (0.01%) |
| dbSNP156 | HG002 | 18,812 | 99.98% (99.95-99.99) | 1 (0.01%) | 3 (0.02%) |
| dbSNP156 | HG005 | 18,966 | 99.98% (99.95-99.99) | 0 (0.00%) | 4 (0.02%) |

## Table S4. ClinVar entries brought in by blind reconciliation (no locus check), by category

Counts per genome, HG001 / HG002 / HG005: entries reached only after converting every retired rsID through the ledger without checking the locus, that do not match the variant's position and allele. Counts are net of the entries that the plain rsID join already attaches (Table 2).

| dbSNP file | P/LP >=1 star: same position, other allele | P/LP >=1 star: other locus | B/LB >=1 star: other locus |
|---|---|---|---|
| dbSNP138 | 0 / 1 / 0 | 1 / 2 / 1 | 1 / 1 / 1 |
| dbSNP144 | 0 / 1 / 0 | 1 / 2 / 1 | 2 / 2 / 1 |
| dbSNP146 | 0 / 1 / 0 | 1 / 2 / 1 | 6 / 8 / 5 |
| dbSNP156 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

## Table S5. Sample-independent check: ClinVar and GWAS entries that a file holds only under a retired rsID

Denominator: entries whose rsID the file holds in current or retired form (identifier level). Retired only: the file holds a retired rsID that merges into the entry's rsID, but not the entry's own rsID or its current rsID. Same allele: that retired rsID is listed by the file at the allele of the ClinVar entry, so a genome carrying this variant would miss the entry in a plain rsID join. Allele verification was run for dbSNP138, 144 and 146 (verify_s5_alleles.py).

| dbSNP file | ClinVar P/LP >=1 star: retired only | of which same allele | ClinVar B/LB >=1 star: retired only | of which same allele | GWAS p < 5x10^-8: retired only | GWAS p < 5x10^-8 filed under a retired rsID by the Catalog |
|---|---|---|---|---|---|---|
| dbSNP138 | 41 of 24,032 (0.17%) | 33 (0.14%) | 844 of 377,644 (0.22%) | 671 (0.18%) | 3,287 of 828,710 (0.40%) | 5,021 (0.61%) |
| dbSNP144 | 189 of 56,334 (0.34%) | 159 (0.28%) | 468 of 616,941 (0.08%) | 376 (0.06%) | 336 of 809,757 (0.04%) | 757 (0.09%) |
| dbSNP146 | 92 of 61,329 (0.15%) | 70 (0.11%) | 588 of 645,970 (0.09%) | 440 (0.07%) | 321 of 850,722 (0.04%) | 1,313 (0.15%) |
| dbSNP156 | 0 of 175,257 (0.00%) | 0 | 0 of 957,042 (0.00%) | 0 | 0 of 854,345 (0.00%) | 9,912 (1.16%) |

## Table S6. ClinVar P/LP (>=1 star) entries attached by a plain rsID join to a different allele (HG002, dbSNP146)

n = 30; all at the same position as the HG002 variant (source: other_allele_PLP_HG002_d146.tsv).

| HG002 variant (HGVS, GRCh38) | Genotype | rsID | ClinVar P/LP variant (HGVS) | Gene | ClinVar classification |
|---|---|---|---|---|---|
| NC_000001.11:g.42930743G>A | 0/1 | rs11537641 | NC_000001.11:g.42930743G>T | *SLC2A1* | Pathogenic |
| NC_000002.12:g.26232259G>A | 0/1 | rs11552518 | NC_000002.12:g.26232259G>T | *HADHA* | Likely pathogenic |
| NC_000002.12:g.55656182G>T | 0/1 | rs2627765 | NC_000002.12:g.55656182G>A | *PNPT1* | Pathogenic |
| NC_000002.12:g.61839792A>G | 1/1 | rs4672457 | NC_000002.12:g.61839792A>T | *FAM161A* | Pathogenic/Likely pathogenic |
| NC_000002.12:g.151619514C>G | 0/1 | rs10172023 | NC_000002.12:g.151619514C>T | *NEB* | Pathogenic |
| NC_000002.12:g.173263785C>T | 1/1 | rs3769148 | NC_000002.12:g.173263785C>A | *MAP3K20* | Pathogenic |
| NC_000002.12:g.208124313A>G | 1/1 | rs2242074 | NC_000002.12:g.208124313A>C | *CRYGD* | Likely pathogenic |
| NC_000003.12:g.49510575C>G | 1/1 | rs2131107 | NC_000003.12:g.49510575C>A | *DAG1* | Pathogenic |
| NC_000003.12:g.128895342A>C | 0/1 | rs1680778 | NC_000003.12:g.128895342A>T | *ACAD9* | Likely pathogenic |
| NC_000004.12:g.3493171C>T | 0/1 | rs6850908 | NC_000004.12:g.3493171C>G | *DOK7* | Likely pathogenic |
| NC_000005.10:g.112827157T>C | 0/1 | rs2229992 | NC_000005.10:g.112827157T>G | *APC* | Pathogenic |
| NC_000006.12:g.32039081C>A | 1/0 | rs6467 | NC_000006.12:g.32039081C>G | *CYP21A2* | Pathogenic/Likely pathogenic |
| NC_000006.12:g.42698426G>C | 0/1 | rs390659 | NC_000006.12:g.42698426G>A | *PRPH2* | Likely pathogenic |
| NC_000007.14:g.150951110A>G | 0/1 | rs1137617 | NC_000007.14:g.150951110A>C | *KCNH2* | Pathogenic |
| NC_000007.14:g.150951110A>G | 0/1 | rs1137617 | NC_000007.14:g.150951110A>T | *KCNH2* | Pathogenic |
| NC_000008.11:g.117835543G>A | 0/1 | rs11546829 | NC_000008.11:g.117835543G>T | *EXT1* | Pathogenic |
| NC_000008.11:g.133131869C>T | 0/1 | rs2294024 | NC_000008.11:g.133131869C>A | *TG* | Pathogenic |
| NC_000008.11:g.142913286G>T | 0/1 | rs4538 | NC_000008.11:g.142913286G>C | *CYP11B2* | Likely pathogenic |
| NC_000010.11:g.49470323T>C | 0/1 | rs2228527 | NC_000010.11:g.49470323T>A | *ERCC6* | Likely pathogenic |
| NC_000011.10:g.71441415A>G | 1/1 | rs949177 | NC_000011.10:g.71441415A>C | *DHCR7* | Pathogenic/Likely pathogenic |
| NC_000012.12:g.6058030A>G | 0/1 | rs1800379 | NC_000012.12:g.6058030A>T | *VWF* | Pathogenic |
| NC_000013.11:g.102875499G>C | 1/1 | rs9514066 | NC_000013.11:g.102875499G>T | *ERCC5* | Likely pathogenic |
| NC_000014.9:g.87941544A>G | 1/1 | rs398607 | NC_000014.9:g.87941544A>T | *GALC* | Likely pathogenic |
| NC_000015.10:g.92978374A>G | 1/1 | rs11074121 | NC_000015.10:g.92978374A>C | *CHD2* | Likely pathogenic |
| NC_000016.10:g.23630140C>G | 0/1 | rs45532440 | NC_000016.10:g.23630140C>A | *PALB2* | Pathogenic |
| NC_000017.11:g.3494408C>T | 0/1 | rs12948217 | NC_000017.11:g.3494408C>A | *ASPA* | Pathogenic |
| NC_000018.10:g.57695300T>G | 1/1 | rs319443 | NC_000018.10:g.57695300T>A | *ATP8B1* | Pathogenic |
| NC_000019.10:g.11100236C>T | 0/1 | rs2228671 | NC_000019.10:g.11100236C>A | *LDLR* | Pathogenic/Likely pathogenic |
| NC_000019.10:g.11100236C>T | 0/1 | rs2228671 | NC_000019.10:g.11100236C>G | *LDLR* | Pathogenic |
| NC_000020.11:g.10652589G>A | 1/1 | rs1131695 | NC_000020.11:g.10652589G>C | *JAG1* | Pathogenic |

## Table S9. Live RefSNP check of 30 retired rsIDs whose current rsID is not at the same position in dbSNP156 (HG002, dbSNP146)

30 cases drawn at random (seed 11) from the first 400 'elsewhere' cases in genome order (chromosomes 1-3; Supplementary Methods M7), listed in genome order. Classes: same chromosome, within 50 bp: 23; same chromosome, > 50 bp away: 4; API error: 2; target not placed on GRCh38 chromosomes: 1. Variants are given as position, then reference and alternate allele after normalization; an empty allele is shown as nothing (before '>') or '-' (after '>'). API error: the live query failed.

| HG002 variant (normalized) | Retired rsID | Current rsID | Current placement (GRCh38) | Class |
|---|---|---|---|---|
| chr1:37226208 AC>- | rs796605960 | rs56354176 | chr1:37226231 | same chromosome, within 50 bp |
| chr1:85135901 TT>- | rs796668822 | rs201107815 | chr1:85135904 | same chromosome, within 50 bp |
| chr1:89685824 AG>- | rs368863397 | rs60383275 | chr1:89685827 | same chromosome, within 50 bp |
| chr1:120140189 A>G | rs782746578 | rs9428331 | chr1:120140185 | same chromosome, within 50 bp |
| chr1:120384100 G>A | rs61802526 | rs4146760 | chr1:149133823 | same chromosome, > 50 bp away |
| chr1:120432023 C>T | rs147916038 | rs71257634 | chr1:149086644 | same chromosome, > 50 bp away |
| chr1:120473467 T>C | rs201145622 | rs79590380 | chr1:149048396 | same chromosome, > 50 bp away |
| chr1:120850864 G>A | rs61812821 | rs2743793 | chr1:148522720 | same chromosome, > 50 bp away |
| chr1:189316388 ->A | rs386369081 | rs35968536 | - | target not placed on GRCh38 chromosomes |
| chr1:235945800 CC>- | rs796557382 | rs752861014 | chr1:235945801 | same chromosome, within 50 bp |
| chr2:28396790 ->AC | rs56073413 | rs3221243 | chr2:28396838 | same chromosome, within 50 bp |
| chr2:32339598 ->TG | rs796293028 | rs10562584 | chr2:32339599 | same chromosome, within 50 bp |
| chr2:40054976 T>- | rs376282147 | rs66663754 | - | API error |
| chr2:53678141 GT>- | rs796760388 | rs397799029 | chr2:53678159 | same chromosome, within 50 bp |
| chr2:87103986 ->A | rs199650306 | rs111461968 | chr2:87103977 | same chromosome, within 50 bp |
| chr2:104152546 AT>- | rs796258064 | rs565761052 | chr2:104152560 | same chromosome, within 50 bp |
| chr2:140278037 ->AC | rs796723933 | rs58190447 | chr2:140278057 | same chromosome, within 50 bp |
| chr2:156072675 ->GT | rs796151063 | rs67022528 | chr2:156072719 | same chromosome, within 50 bp |
| chr2:192310412 TT>- | rs796068516 | rs79417268 | chr2:192310413 | same chromosome, within 50 bp |
| chr2:201033160 TG>- | rs796126753 | rs57506756 | chr2:201033197 | same chromosome, within 50 bp |
| chr2:216772479 CG>- | rs796745026 | rs71054493 | chr2:216772480 | same chromosome, within 50 bp |
| chr2:220601670 ->TGTGTG | rs796802531 | rs58887053 | chr2:220601702 | same chromosome, within 50 bp |
| chr2:225597513 ->ATATATATATATAT | rs33994851 | rs11267904 | - | API error |
| chr2:229168729 TG>- | rs796878625 | rs35083173 | chr2:229168738 | same chromosome, within 50 bp |
| chr2:233915761 TC>- | rs796315555 | rs767811082 | chr2:233915801 | same chromosome, within 50 bp |
| chr3:4681625 ->GT | rs796443526 | rs143638502 | chr3:4681626 | same chromosome, within 50 bp |
| chr3:7853186 CA>- | rs796497857 | rs34780047 | chr3:7853184 | same chromosome, within 50 bp |
| chr3:48425806 ->AC | rs529553401 | rs35420820 | chr3:48425837 | same chromosome, within 50 bp |
| chr3:101116569 AC>- | rs796992790 | rs764183857 | chr3:101116578 | same chromosome, within 50 bp |
| chr3:126079239 CC>- | rs796693172 | rs34429413 | chr3:126079240 | same chromosome, within 50 bp |

## Table S10. Indels that received no rsID, and bounds on the variant rate

Indels were not left-aligned, so an indel written at a shifted position by the file receives no rsID and leaves both the numerator and the denominator of the variant rate. Lower bound: all such indels would have received only current rsIDs. Upper bound: all would have received a retired rsID. Indels absent from the file because they were submitted to dbSNP later also fall in this group, so the bounds are conservative.

| dbSNP file | Genome | Indels without an rsID | Variant rate | Lower bound | Upper bound |
|---|---|---|---|---|---|
| dbSNP138 | HG001 | 47,404 of 536,579 (8.8%) | 4.76% | 4.71% | 5.94% |
| dbSNP138 | HG002 | 62,035 of 588,091 (10.5%) | 4.95% | 4.88% | 6.44% |
| dbSNP138 | HG005 | 39,374 of 469,951 (8.4%) | 4.49% | 4.44% | 5.48% |
| dbSNP144 | HG001 | 32,819 of 536,579 (6.1%) | 8.29% | 8.21% | 9.08% |
| dbSNP144 | HG002 | 42,140 of 588,091 (7.2%) | 8.62% | 8.53% | 9.60% |
| dbSNP144 | HG005 | 31,462 of 469,951 (6.7%) | 7.24% | 7.18% | 8.02% |
| dbSNP146 | HG001 | 21,940 of 536,579 (4.1%) | 8.42% | 8.37% | 8.93% |
| dbSNP146 | HG002 | 29,865 of 588,091 (5.1%) | 8.72% | 8.66% | 9.40% |
| dbSNP146 | HG005 | 21,444 of 469,951 (4.6%) | 7.30% | 7.25% | 7.82% |
| dbSNP156 | HG001 | 835 of 536,579 (0.2%) | 0.14% | 0.14% | 0.16% |
| dbSNP156 | HG002 | 535 of 588,091 (0.1%) | 0.14% | 0.14% | 0.15% |
| dbSNP156 | HG005 | 1,312 of 469,951 (0.3%) | 0.15% | 0.15% | 0.18% |

## Table S11. Counts behind the percentages of Table 2

Each cell: entries missed of reference entries (percentage). Reference entries as defined in the legend of Table 2.

| Knowledge base and category | Genome | dbSNP138 | dbSNP146 | dbSNP156 |
|---|---|---|---|---|
| ClinVar B/LB (>=1 star), missed because of a retired rsID | HG001 | 437 of 38,492 (1.14%) | 377 of 38,734 (0.97%) | 0 of 38,808 (0.00%) |
|  | HG002 | 446 of 39,061 (1.14%) | 410 of 39,387 (1.04%) | 0 of 39,511 (0.00%) |
|  | HG005 | 403 of 37,151 (1.08%) | 311 of 37,352 (0.83%) | 0 of 37,439 (0.00%) |
| ClinVar B/LB (>=1 star), missed because ClinVar gives no rsID | HG001 | 716 of 38,492 (1.86%) | 729 of 38,734 (1.88%) | 731 of 38,808 (1.88%) |
|  | HG002 | 739 of 39,061 (1.89%) | 763 of 39,387 (1.94%) | 768 of 39,511 (1.94%) |
|  | HG005 | 598 of 37,151 (1.61%) | 612 of 37,352 (1.64%) | 619 of 37,439 (1.65%) |
| GWAS Catalog associations (p < 5x10^-8), missed | HG001 | 3,889 of 380,969 (1.02%) | 2,049 of 384,762 (0.53%) | 4,359 of 385,607 (1.13%) |
|  | HG002 | 3,890 of 377,818 (1.03%) | 1,873 of 381,736 (0.49%) | 4,442 of 382,640 (1.16%) |
|  | HG005 | 3,241 of 349,065 (0.93%) | 1,505 of 352,230 (0.43%) | 3,419 of 353,165 (0.97%) |
| of which retired rsID on the pipeline side | HG001 | 1,793 of 380,992 (0.47%) | 351 of 384,765 (0.09%) | 0 of 385,607 (0.00%) |
|  | HG002 | 1,709 of 377,834 (0.45%) | 370 of 381,741 (0.10%) | 0 of 382,640 (0.00%) |
|  | HG005 | 1,706 of 349,083 (0.49%) | 252 of 352,237 (0.07%) | 0 of 353,165 (0.00%) |

