"""Post-pipeline analyses (added 2026-11-10 after the spot-check of merge targets).

1. Locus check of merges. For every retired rsID that a bundle writes to a sample variant,
   resolve it through the b157 ledger and ask where the target rsID sits in dbSNP156:
     same allele      : the target is listed at the same normalized allele (a true duplicate merge)
     same position    : the target is at the same position, other allele
     elsewhere/absent : the target is not at this position in dbSNP156 (cross-locus merge, or a
                        target created after build 156)
   A sample of "elsewhere" targets is checked against the live RefSNP API (see check_elsewhere()).

2. Allele-aware ClinVar test. Reference = ClinVar entries matched to the sample variant by
   normalized position and allele (no rsID involved). For each bundle:
     plain join      : ClinVar entries whose rsID is among the pipeline rsIDs
     validated join  : pipeline rsIDs converted to current rsIDs, keeping a converted rsID only if
                       dbSNP156 lists it at the same allele (same-locus merges only)
     blind join      : every pipeline rsID converted through the ledger, no locus check
   Reported by ClinVar category:
     position-matched entries; found by plain join; missed by plain join; of which recovered by
     validated join (= loss caused by retired rsIDs); false entries brought in by the blind join
     (entries not matching the variant's position and allele), split into same-position-other-allele
     and other-locus.
   GWAS Catalog and PharmGKB (no alleles) are re-reported with validated conversion only.

Usage: python post_locus_allele.py <sample.vcf.gz> <bundle tsv prefix: wg_ | wg2_> <tag>
Run from G:/rsid_wg.
"""
import collections, gzip, json, math, os, pickle, sys
sys.path.insert(0, ".")
from normalize import normalize

SAMPLE, PFX, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
BUNDLES = [("dbSNP138 (GATK/WARP)", "d138"), ("dbSNP144 (GDC)", "d144"),
           ("dbSNP146 (sarek default)", "d146"), ("dbSNP156 (NCBI, Nov 2022)", "b156")]


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*max(0.0, c-h), 100*(c+h)


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{k:,}/{n:,} = {100*k/n if n else 0:.2f}% [{lo:.2f}-{hi:.2f}]"


print(f"== {SAMPLE} (bundle files {PFX}*.tsv)", flush=True)
D = pickle.load(open("downstream/prep.pkl", "rb"))
E, pos_keys, cur, led = D["E"], D["pos_keys"], D["cur"], D["led"]
E = [(e[0], f"{e[1]} {e[3]}" if e[0] == "ClinVar" else e[1], e[2], e[3]) for e in E]


def resolve(i):
    n = 0
    while i in led and n < 20: i = led[i]; n += 1
    return i


calls = []
with gzip.open(SAMPLE, "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c, p, _, r, a = ln.split("\t", 5)[:5]
        calls.append([(c,) + normalize(int(p), r, x) for x in a.split(",")])
want = {k for ks in calls for k in ks}
wantpos = {(k[0], k[1]) for k in want}
print(f"   {len(calls):,} variants", flush=True)


def load(tsv):
    km = collections.defaultdict(set)
    with open(tsv) as f:
        for ln in f:
            c, p, r, a, i = ln.rstrip("\n").split("\t")
            ids = {int(x) for x in i.replace("rs", "").split(";") if x.isdigit()}
            for x in a.split(","):
                k = (c,) + normalize(int(p), r, x)
                if k in want or (k[0], k[1]) in wantpos: km[k] |= ids
    return km


k156 = load("wg3_b156.tsv")
at_pos156 = collections.defaultdict(set)
for k, ids in k156.items(): at_pos156[(k[0], k[1])] |= ids

# ClinVar: entry index -> its normalized key; resource indexes
key_of = {}
for k, idxs in pos_keys.items():
    for i in idxs: key_of[i] = k
by_dist = collections.defaultdict(list); by_cur = collections.defaultdict(list)
for idx, e in enumerate(E):
    if e[2] is None: continue
    by_dist[e[2]].append(idx); by_cur[cur[e[2]]].append(idx)

out = {}
elsewhere_examples = []
for name, short in BUNDLES:
    km = k156 if short == "b156" else load(f"{PFX}{short}.tsv")
    loc = collections.Counter(); loc_ids = collections.defaultdict(set)
    cv = collections.defaultdict(collections.Counter)    # ClinVar category -> counters
    oth = collections.defaultdict(collections.Counter)   # GWAS / PharmGKB category -> counters
    for keys in calls:
        ids = set().union(*(km.get(k, set()) for k in keys))
        if not ids: continue
        # --- 1. locus check
        validated = set()
        for i in ids:
            t = resolve(i)
            if t == i:
                validated.add(i); continue
            if any(t in k156.get(k, ()) for k in keys): cls = "same allele"; validated.add(t)
            elif any(t in at_pos156.get((k[0], k[1]), ()) for k in keys): cls = "same position, other allele"
            else:
                cls = "elsewhere or absent in dbSNP156"
                if len(elsewhere_examples) < 400 and short == "d146": elsewhere_examples.append((keys[0], i, t))
            loc[cls] += 1; loc_ids[cls].add(i)
        blind = {resolve(i) for i in ids}
        # --- 2. allele-aware ClinVar
        P = {i for k in keys for i in pos_keys.get(k, ())}
        plain = {i for x in ids for i in by_dist.get(x, ())}
        valid = {i for x in validated for i in by_cur.get(x, ())}
        blindj = {i for x in blind for i in by_cur.get(x, ())}
        for i in P:
            cat = E[i][1]; c = cv[cat]
            c["position-matched"] += 1
            c["found by plain join"] += i in plain
            c["missed by plain join"] += i not in plain
            c["missed, recovered by validated join (retired rsID)"] += (i not in plain) and (i in valid)
            c["missed, ClinVar entry has no rsID"] += (i not in plain) and E[i][2] is None
        for i in blindj - P:
            if E[i][0] != "ClinVar": continue
            same_pos = key_of.get(i, (None, None))[:2] in {(k[0], k[1]) for k in keys}
            cv[E[i][1]]["false via blind join: " + ("same position, other allele" if same_pos else "other locus")] += 1
        for i in plain - P:
            if E[i][0] != "ClinVar": continue
            same_pos = key_of.get(i, (None, None))[:2] in {(k[0], k[1]) for k in keys}
            cv[E[i][1]]["plain-join entry not matching allele: " + ("same position, other allele" if same_pos else "other locus")] += 1
        # --- GWAS / PharmGKB with validated conversion
        for i in valid | plain:
            if E[i][0] == "ClinVar": continue
            o = oth[(E[i][0], E[i][1])]
            o["validated"] += i in valid; o["plain"] += i in plain
            o["missed by plain, recovered by validated"] += (i in valid) and (i not in plain)
    tot = sum(loc.values())
    print(f"\n-- {name}")
    print(f"   retired rsIDs written: {tot:,} annotations ({sum(len(s) for s in loc_ids.values()):,} distinct)")
    for cls in ("same allele", "same position, other allele", "elsewhere or absent in dbSNP156"):
        print(f"     target {cls:<34} {pct(loc[cls], tot)}")
    print("   ClinVar, allele-aware (reference = entries matched by position and allele):")
    for cat in sorted(cv):
        c = cv[cat]
        if not c["position-matched"] and not any(v for k, v in c.items() if k.startswith(("false", "plain-join"))): continue
        print(f"     {cat:<22} matched {c['position-matched']:>6,} | missed by plain rsID join "
              f"{pct(c['missed by plain join'], c['position-matched'])} | of which retired rsID "
              f"{c['missed, recovered by validated join (retired rsID)']:,}, entry without rsID "
              f"{c['missed, ClinVar entry has no rsID']:,}"
              f" | blind-join false: same-pos {c['false via blind join: same position, other allele']:,},"
              f" other-locus {c['false via blind join: other locus']:,}"
              f" | plain-join other-allele {c['plain-join entry not matching allele: same position, other allele']:,}")
    print("   GWAS / PharmGKB (rsID-level), validated conversion:")
    for k in sorted(oth):
        o = oth[k]
        print(f"     {k[0]:<18} {k[1]:<20} validated {o['validated']:>8,} | plain {o['plain']:>8,} | "
              f"missed by plain {pct(o['missed by plain, recovered by validated'], o['validated'])}")
    out[name] = dict(locus={k: v for k, v in loc.items()},
                     locus_distinct={k: len(v) for k, v in loc_ids.items()},
                     clinvar={k: dict(v) for k, v in cv.items()},
                     other={" | ".join(k): dict(v) for k, v in oth.items()})
json.dump(out, open(f"downstream/post_locus_allele{TAG}.json", "w"), indent=1)
with open(f"downstream/elsewhere_examples{TAG}.tsv", "w") as o:
    for k, i, t in elsewhere_examples: o.write(f"{k[0]}\t{k[1]+1}\t{k[2] or '-'}\t{k[3] or '-'}\trs{i}\trs{t}\n")
print("\ndone", flush=True)
