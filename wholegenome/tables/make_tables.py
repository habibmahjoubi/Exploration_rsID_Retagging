"""Builds every number table of the Brief Communication from the result files on G:/rsid_wg.
Nothing is typed by hand. Output: tables_generated.md (main Tables 1-2, Supplementary Tables S2-S5).
Usage: python make_tables.py
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WG = os.environ.get("RSID_WG", os.path.join(HERE, ".."))   # directory holding the result files
S = ["HG001", "HG002", "HG005"]
B = [("dbSNP138 (GATK/WARP)", "dbSNP138"), ("dbSNP144 (GDC)", "dbSNP144"),
     ("dbSNP146 (sarek default)", "dbSNP146"), ("dbSNP156 (NCBI, Nov 2022)", "dbSNP156")]
DEFAULT = {"dbSNP138": "WARP default", "dbSNP144": "GDC", "dbSNP146": "sarek default",
           "dbSNP156": "NCBI release, Nov 2022"}


def wil(k, n, z=1.96):
    if not n: return 0.0, 0.0
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*max(0.0, c-h), 100*min(1.0, c+h)


def pc(k, n, ci=False, dp=2):
    if not n: return "n/a"
    s = f"{100*k/n:.{dp}f}%"
    if ci:
        lo, hi = wil(k, n); s += f" ({lo:.{dp}f}-{hi:.{dp}f})"
    return s


ACC = {"chr1": "NC_000001.11", "chr2": "NC_000002.12", "chr3": "NC_000003.12", "chr4": "NC_000004.12",
       "chr5": "NC_000005.10", "chr6": "NC_000006.12", "chr7": "NC_000007.14", "chr8": "NC_000008.11",
       "chr9": "NC_000009.12", "chr10": "NC_000010.11", "chr11": "NC_000011.10", "chr12": "NC_000012.12",
       "chr13": "NC_000013.11", "chr14": "NC_000014.9", "chr15": "NC_000015.10", "chr16": "NC_000016.10",
       "chr17": "NC_000017.11", "chr18": "NC_000018.10", "chr19": "NC_000019.10", "chr20": "NC_000020.11",
       "chr21": "NC_000021.9", "chr22": "NC_000022.11"}


def j(p): return json.load(open(os.path.join(WG, p)))


wg = {s: j("wg_results.json" if s == "HG002" else f"wg_results_{s}.json") for s in S}
ds = {s: j("downstream/downstream_results.json" if s == "HG002" else f"downstream/downstream_results_{s}.json") for s in S}
po = {s: j(f"downstream/post_locus_allele_{s}.json") for s in S}

# SNV / indel split and per-chromosome range are only in the text reports
txt = {}
for s in S:
    t = open(os.path.join(WG, "wg_results.txt" if s == "HG002" else f"wg_results_{s}.txt")).read()
    txt[s] = {}
    for block in t.split("\n== ")[1:]:
        name = block.split("\n")[0].strip()
        m = re.search(r"SNVs: ([\d,]+)/([\d,]+) = .*?; indels: ([\d,]+)/([\d,]+)", block)
        r = re.search(r"per-chromosome rate range: ([\d.]+)%-([\d.]+)%", block)
        num = lambda x: int(x.replace(",", ""))
        txt[s][name] = dict(snv=(num(m.group(1)), num(m.group(2))), ind=(num(m.group(3)), num(m.group(4))),
                            chrom=(float(r.group(1)), float(r.group(2))))
    txt[s]["n"] = int(re.search(r"benchmark variants: ([\d,]+)", t).group(1).replace(",", ""))
    txt[s]["snv_total"] = int(re.search(r"\(SNV ([\d,]+)\)", t).group(1).replace(",", ""))

out = []
P = out.append


def trio(f):
    """one cell with the three genomes: HG001 / HG002 / HG005"""
    return " / ".join(f(s) for s in S)


# ---------------------------------------------------------------- Table 1
T1, T2 = [], []
P("## Table 1. Retired rsIDs written by four dbSNP files to three whole genomes\n")
P("Benchmark variants (chr1-22): " + ", ".join(f"{s} {txt[s]['n']:,}" for s in S) + ".\n")
P("| dbSNP file | Genome | Annotation rate (95% CI) | Variant rate (95% CI) | SNVs | Indels | Only retired rsIDs |")
P("|---|---|---|---|---|---|---|")
for key, lab in B:
    for s in S:
        r = wg[s][key]; t = txt[s][key]
        dp = 3 if lab == "dbSNP156" else 2   # two decimals would collapse the intervals of the small rates
        only = r['only_retired']
        only_s = pc(only, r['variants_annotated'], dp=dp) if only >= 10 else f"{only} variant" + ("s" if only != 1 else "")
        T1.append((lab, s, pc(r['retired_annotations'], r['annotations'], True, dp),
                   pc(r['variants_retired'], r['variants_annotated'], True, dp), pc(*t['snv'], dp=dp),
                   pc(*t['ind'], dp=dp), only_s))
        P(f"| {lab} ({DEFAULT[lab]}) | {s} | {pc(r['retired_annotations'], r['annotations'], True, dp)} | "
          f"{pc(r['variants_retired'], r['variants_annotated'], True, dp)} | {pc(*t['snv'], dp=dp)} | {pc(*t['ind'], dp=dp)} | "
          f"{only_s} |")
P("")

# ---------------------------------------------------------------- Table 2
P("## Table 2. What a plain rsID join changes downstream (values: HG001 / HG002 / HG005)\n")
cols = [b for b in B if b[1] in ("dbSNP138", "dbSNP146", "dbSNP156")]
P("| Knowledge base and category | " + " | ".join(f"{lab} ({DEFAULT[lab]})" for _, lab in cols) + " |")
P("|---|" + "---|" * len(cols))


def cv(s, key, cat): return po[s][key]["clinvar"].get(cat, {})


def row(label, f):
    cells = [trio(lambda s: f(s, key)) for key, _ in cols]
    T2.append(cells)
    P(f"| {label} | " + " | ".join(cells) + " |")


row("ClinVar P/LP (>=1 star) entries matching a variant by position and allele, n (a)",
    lambda s, k: f"{cv(s, k, 'P/LP >=1*').get('position-matched', 0)}")
row("  of which missed because of a retired rsID, n",
    lambda s, k: f"{cv(s, k, 'P/LP >=1*').get('missed, recovered by validated join (retired rsID)', 0)}")
row("ClinVar P/LP (>=1 star) entries attached by the rsID join to a different allele, n",
    lambda s, k: f"{cv(s, k, 'P/LP >=1*').get('plain-join entry not matching allele: same position, other allele', 0)}")
row("ClinVar B/LB (>=1 star) entries missed because of a retired rsID, %",
    lambda s, k: pc(cv(s, k, 'B/LB >=1*').get('missed, recovered by validated join (retired rsID)', 0),
                    cv(s, k, 'B/LB >=1*')['position-matched']))
row("ClinVar B/LB (>=1 star) entries missed because ClinVar gives no rsID, %",
    lambda s, k: pc(cv(s, k, 'B/LB >=1*').get('missed, ClinVar entry has no rsID', 0),
                    cv(s, k, 'B/LB >=1*')['position-matched']))
row("GWAS Catalog associations (p < 5x10^-8) missed, %",
    lambda s, k: pc(po[s][k]["other"]["GWAS | p<5e-8"]["missed by plain, recovered by validated"],
                    po[s][k]["other"]["GWAS | p<5e-8"]["validated"]))
row("  of which retired rsID on the pipeline side, %",
    lambda s, k: pc(ds[s][k]["sample"]["GWAS | p<5e-8"]["missed_pipeline_side"],
                    ds[s][k]["sample"]["GWAS | p<5e-8"]["reconciled"]))


def pgx(s, k, f):
    lv = [f"PharmGKB-clinical | level {x}" for x in ("1A", "1B", "2A", "2B")]
    o = po[s][k]["other"]
    return f(sum(o.get(x, {}).get("missed by plain, recovered by validated", 0) for x in lv),
             sum(o.get(x, {}).get("validated", 0) for x in lv))


row("PharmGKB clinical annotations, levels 1A-2B, missed, n of N", lambda s, k: pgx(s, k, lambda a, b: f"{a} of {b}"))
P("")

# ---------------------------------------------------------------- Table S2: per-chromosome + bundle-level
P("## Table S2. Per-chromosome range of the annotation rate, and bundle rate\n")
bundle_rate = {}
for ln in open(os.path.join(WG, "bundle_rate.txt")):
    m = re.match(r"(\S+)\.vcf\.gz: distinct chr1-22 rsIDs ([\d,]+); retired ([\d,]+)", ln)
    if m: bundle_rate[m.group(1)] = (int(m.group(3).replace(",", "")), int(m.group(2).replace(",", "")))
bmap = {"dbSNP138": "dbsnp138", "dbSNP144": "dbsnp144", "dbSNP146": "dbsnp146", "dbSNP156": "b156"}
P("| dbSNP file | Bundle rate (retired / distinct rsIDs, chr1-22) | Per-chromosome annotation rate, range: HG001 / HG002 / HG005 |")
P("|---|---|---|")
for key, lab in B:
    k, n = bundle_rate[bmap[lab]]
    P(f"| {lab} | {k:,} / {n:,} = {100*k/n:.3f}% | " +
      " / ".join(f"{txt[s][key]['chrom'][0]:.2f}-{txt[s][key]['chrom'][1]:.2f}%" for s in S) + " |")
P("")

# ---------------------------------------------------------------- Table S3: locus check
P("## Table S3. Where the current rsID of each retired rsID sits in dbSNP156\n")
P("| dbSNP file | Genome | Retired rsIDs written | Same allele (95% CI) | Same position, other allele | Elsewhere or absent |")
P("|---|---|---|---|---|---|")
for key, lab in B:
    for s in S:
        L = po[s][key]["locus"]; n = sum(L.values())
        P(f"| {lab} | {s} | {n:,} | {pc(L.get('same allele', 0), n, True)} | "
          f"{L.get('same position, other allele', 0):,} ({pc(L.get('same position, other allele', 0), n)}) | "
          f"{L.get('elsewhere or absent in dbSNP156', 0):,} ({pc(L.get('elsewhere or absent in dbSNP156', 0), n)}) |")
P("")

# ---------------------------------------------------------------- Table S4: blind reconciliation false entries
P("## Table S4. ClinVar entries brought in by blind reconciliation (no locus check), by category\n")
P("Counts per genome, HG001 / HG002 / HG005: entries reached only after converting every retired rsID "
  "through the ledger without checking the locus, that do not match the variant's position and allele. Counts are net of the entries that the plain rsID join already attaches (Table 2).\n")
P("| dbSNP file | P/LP >=1 star: same position, other allele | P/LP >=1 star: other locus | B/LB >=1 star: other locus |")
P("|---|---|---|---|")
for key, lab in B:
    def blind(cat, kind):
        return trio(lambda s: str(cv(s, key, cat).get(f"false via blind join: {kind}", 0)
                                  - cv(s, key, cat).get(f"plain-join entry not matching allele: {kind}", 0)))
    P(f"| {lab} | {blind('P/LP >=1*', 'same position, other allele')} | {blind('P/LP >=1*', 'other locus')} | "
      f"{blind('B/LB >=1*', 'other locus')} |")
P("")

# ---------------------------------------------------------------- Table S5: whole-file check, with allele verification
P("## Table S5. Sample-independent check: ClinVar and GWAS entries that a file holds only under a retired rsID\n")
P("Denominator: entries whose rsID the file holds in current or retired form (identifier level). "
  "Retired only: the file holds a retired rsID that merges into the entry's rsID, but not the entry's own "
  "rsID or its current rsID. Same allele: that retired rsID is listed by the file at the allele of the "
  "ClinVar entry, so a genome carrying this variant would miss the entry in a plain rsID join. "
  "Allele verification was run for dbSNP138, 144 and 146 (verify_s5_alleles.py).\n")
P("| dbSNP file | ClinVar P/LP >=1 star: retired only | of which same allele | ClinVar B/LB >=1 star: retired only | of which same allele | GWAS p < 5x10^-8: retired only | GWAS p < 5x10^-8 filed under a retired rsID by the Catalog |")
P("|---|---|---|---|---|---|---|")
ver = json.load(open(os.path.join(WG, "downstream", "verify_s5_alleles.json")))
for key, lab in B:
    rc = ds["HG002"][key]["resource_centric"]
    f = lambda c: f"{rc[c]['retired_only']:,} of {rc[c]['in_bundle']:,} ({pc(rc[c]['retired_only'], rc[c]['in_bundle'])})"
    def same(cat, c):
        if key not in ver: return "0" if rc[c]["retired_only"] == 0 else "n/a"
        n = ver[key].get(f"{cat} | same allele", 0)
        return f"{n:,} ({pc(n, rc[c]['in_bundle'])})"
    g = rc["GWAS | p<5e-8"]
    P(f"| {lab} | {f('ClinVar | P/LP >=1*')} | {same('P/LP >=1*', 'ClinVar | P/LP >=1*')} | "
      f"{f('ClinVar | B/LB >=1*')} | {same('B/LB >=1*', 'ClinVar | B/LB >=1*')} | {f('GWAS | p<5e-8')} | "
      f"{g['resource_stale']:,} ({pc(g['resource_stale'], g['in_bundle'])}) |")
P("")

# ---------------------------------------------------------------- Table S6: other-allele P/LP (HG002, dbSNP146)
P("## Table S6. ClinVar P/LP (>=1 star) entries attached by a plain rsID join to a different allele (HG002, dbSNP146)\n")
rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(WG, "downstream", "other_allele_PLP_HG002_d146.tsv"))][1:]
P(f"n = {len(rows)}; all at the same position as the HG002 variant (source: other_allele_PLP_HG002_d146.tsv).\n")
P("| HG002 variant (HGVS, GRCh38) | Genotype | rsID | ClinVar P/LP variant (HGVS) | Gene | ClinVar classification |")
P("|---|---|---|---|---|---|")
for r in rows:
    c, rest = r[0].split(":"); pos, ra = rest.split(" "); ref, alt = ra.split(">")
    P(f"| {ACC[c]}:g.{pos}{ref}>{alt} | {r[1]} | {r[3]} | {r[8]} | *{r[7]}* | {r[9].replace('_', ' ')} |")
P("")

# ---------------------------------------------------------------- Table S9: live check of 'elsewhere' targets
P("## Table S9. Live RefSNP check of 30 retired rsIDs whose current rsID is not at the same position in dbSNP156 (HG002, dbSNP146)\n")
live = open(os.path.join(WG, "downstream", "elsewhere_live_HG002.txt"), encoding="utf-8").read()
tally = eval(re.search(r"SUMMARY: (.*)$", live, re.M).group(1))
nret = int(re.search(r"^(\d+) 'elsewhere' examples", live, re.M).group(1))
summ = "; ".join(f"{k}: {v}" for k, v in sorted(tally.items(), key=lambda kv: -kv[1]))
P(f"30 cases drawn at random (seed 11) from the first {nret} 'elsewhere' cases in genome order "
  "(chromosomes 1-3; Supplementary Methods M7), listed in genome order. Classes: " + summ + ". "
  "Variants are given as position, then reference and alternate allele after normalization; an empty "
  "allele is shown as nothing (before '>') or '-' (after '>'). API error: the live query failed.\n")
P("| HG002 variant (normalized) | Retired rsID | Current rsID | Current placement (GRCh38) | Class |")
P("|---|---|---|---|---|")
ms = list(re.finditer(r"^  (\S+) (\S+)  (rs\d+) -> (rs\d+)  now at (\S+)  \[(.+)\]$", live, re.M))
for m in sorted(ms, key=lambda m: (int(m.group(1).split(":")[0][3:]), int(m.group(1).split(":")[1]))):
    P(f"| {m.group(1)} {m.group(2)} | {m.group(3)} | {m.group(4)} | {m.group(5)} | {m.group(6)} |")
P("")


# ---------------------------------------------------------------- Table S10: bounds for indels without an rsID match
P("## Table S10. Indels that received no rsID, and bounds on the variant rate\n")
P("Indels were not left-aligned, so an indel written at a shifted position by the file receives no rsID "
  "and leaves both the numerator and the denominator of the variant rate. Lower bound: all such indels "
  "would have received only current rsIDs. Upper bound: all would have received a retired rsID. Indels "
  "absent from the file because they were submitted to dbSNP later also fall in this group, so the "
  "bounds are conservative.\n")
P("| dbSNP file | Genome | Indels without an rsID | Variant rate | Lower bound | Upper bound |")
P("|---|---|---|---|---|---|")
for key, lab in B:
    for s_ in S:
        r = wg[s_][key]; t = txt[s_][key]
        nind = txt[s_]["n"] - txt[s_]["snv_total"]; un = nind - t["ind"][1]
        k, n = r["variants_retired"], r["variants_annotated"]
        P(f"| {lab} | {s_} | {un:,} of {nind:,} ({100*un/nind:.1f}%) | {100*k/n:.2f}% | {100*k/(n+un):.2f}% | {100*(k+un)/(n+un):.2f}% |")
P("")

# ---------------------------------------------------------------- Table S11: counts behind Table 2
P("## Table S11. Counts behind the percentages of Table 2\n")
P("Each cell: entries missed of reference entries (percentage). Reference entries as defined in the "
  "legend of Table 2.\n")
P("| Knowledge base and category | Genome | " + " | ".join(lab for _, lab in cols) + " |")
P("|---|---|" + "---|" * len(cols))


def crow(label, f):
    for i, s in enumerate(S):
        cells = []
        for key, _ in cols:
            k_, n_ = f(s, key); cells.append(f"{k_:,} of {n_:,} ({pc(k_, n_)})")
        P(f"| {label if i == 0 else ''} | {s} | " + " | ".join(cells) + " |")


crow("ClinVar B/LB (>=1 star), missed because of a retired rsID",
     lambda s, k: (cv(s, k, 'B/LB >=1*').get('missed, recovered by validated join (retired rsID)', 0),
                   cv(s, k, 'B/LB >=1*')['position-matched']))
crow("ClinVar B/LB (>=1 star), missed because ClinVar gives no rsID",
     lambda s, k: (cv(s, k, 'B/LB >=1*').get('missed, ClinVar entry has no rsID', 0),
                   cv(s, k, 'B/LB >=1*')['position-matched']))
crow("GWAS Catalog associations (p < 5x10^-8), missed",
     lambda s, k: (po[s][k]["other"]["GWAS | p<5e-8"]["missed by plain, recovered by validated"],
                   po[s][k]["other"]["GWAS | p<5e-8"]["validated"]))
crow("of which retired rsID on the pipeline side",
     lambda s, k: (ds[s][k]["sample"]["GWAS | p<5e-8"]["missed_pipeline_side"],
                   ds[s][k]["sample"]["GWAS | p<5e-8"]["reconciled"]))
P("")

open(os.path.join(HERE, "tables_generated.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")

# ---------------------------------------------------------------- main-text Tables 1 and 2
# The pipe tables of 01_main_text.md are rewritten from the same numbers, so they cannot drift.
SHORT = {"dbSNP138": "dbSNP138 (WARP)", "dbSNP144": "dbSNP144 (GDC)", "dbSNP146": "dbSNP146 (sarek)",
         "dbSNP156": "dbSNP156 (NCBI, Nov 2022)"}
t1 = ["| dbSNP file (default in) | Genome | Annotation rate | Variant rate | SNVs | Indels | Only retired |",
      "|---|---|---|---|---|---|---|"]
for i, (lab, s_, *c) in enumerate(T1):
    t1.append(f"| {SHORT[lab] if i % 3 == 0 else ''} | {s_} | " + " | ".join(c) + " |")
L2 = ["ClinVar P/LP (>=1 star) matching by position and allele, n",
      "of which missed because of a retired rsID, n",
      "ClinVar P/LP (>=1 star) attached to a different allele by the rsID join, n",
      "ClinVar B/LB (>=1 star) missed because of a retired rsID",
      "ClinVar B/LB (>=1 star) missed because ClinVar gives no rsID",
      "GWAS Catalog, p < 5x10^-8, missed",
      "of which retired rsID on the pipeline side",
      "PharmGKB clinical, levels 1A-2B, missed (n of N)"]
assert len(L2) == len(T2)
t2 = ["| Knowledge base and category | dbSNP138 (WARP) | dbSNP146 (sarek) | dbSNP156 (Nov 2022) |", "|---|---|---|---|"]
t2 += [f"| {l} | " + " | ".join(c) + " |" for l, c in zip(L2, T2)]
mp = os.path.join(HERE, "01_main_text.md")
if not os.path.exists(mp): sys.exit(0)   # the manuscript is not part of this repository
main = open(mp, encoding="utf-8").read()


def swap(text, caption, new_rows):
    a = text.index(caption); b = text.index("\n|", a) + 1; e = b
    while e < len(text) and text[e] == "|":
        e = text.index("\n", e) + 1
    return text[:b] + "\n".join(new_rows) + "\n" + text[e:]


new_main = swap(swap(main, "**Table 1.", t1), "**Table 2.", t2)
if new_main != main:
    open(mp, "w", encoding="utf-8").write(new_main)
    print("main-text Tables 1-2 updated", file=sys.stderr)
print("\n".join(out))
