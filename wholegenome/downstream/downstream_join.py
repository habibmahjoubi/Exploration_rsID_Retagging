"""Downstream test for reviewer point 4: does a retired rsID in pipeline output change what an
rsID-keyed knowledge base returns, and is a chr-pos-ref-alt join immune?

Resources (exact versions + md5 in MD5SUMS.txt / SOURCES.txt):
  ClinVar GRCh38 VCF 2026-11-08 (INFO RS=, CLNSIG, CLNREVSTAT) -- also has positions/alleles,
    so it gives the chr-pos-ref-alt baseline the reviewer asks about.
  GWAS Catalog associations v1.0 full, release 2026-11-02 (SNPS, SNP_ID_CURRENT, CHR_POS).
  PharmGKB/ClinPGx clinical annotations (CREATED 2025-07-05) + variant annotations
    (CREATED 2026-11-05), rs-keyed rows only.
Merge ledger: dbSNP b157 refsnp-merged.json.bz2 (retired rsID -> merged_into).

Two analyses, per bundle (dbSNP138 / 144 / 146 / b156):
 A. Sample-level, HG002 v4.2.1 chr1-22: the bundle's allele-exact rsIDs at each benchmark
    variant (as GATK -D assigns them) are joined to each resource
      naive      = resource entries whose distributed rsID is among the pipeline IDs
      reconciled = both sides resolved to current rsIDs through the ledger
    missed = reconciled - naive (naive is a subset by construction), split by which side
    carries the retired ID. ClinVar is also joined by normalized chr-pos-ref-alt.
 B. Resource-centric, genome-wide, sample-independent: for every resource entry, does the
    bundle contain its current rsID, only a retired predecessor, or neither? An entry whose
    locus the bundle labels with a retired ID only is unreachable by rsID join for any sample
    carrying that variant. ID-level (allele match not checked), so an upper bound per entry;
    analysis A is the allele-exact check.

Stages (cached, rerunnable):  python downstream_join.py prep
                              python downstream_join.py scan <bundle.vcf.gz> <out.ids>
                              python downstream_join.py report
"""
import bz2, csv, gzip, json, math, os, pickle, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from normalize import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
WG = os.path.join(HERE, "..")
P = lambda *a: os.path.join(HERE, *a)
BUNDLES = [("dbSNP138 (GATK/WARP)", "wg_d138.tsv", "d138.ids"),
           ("dbSNP144 (GDC)", "wg_d144.tsv", "d144.ids"),
           ("dbSNP146 (sarek default)", "wg_d146.tsv", "d146.ids"),
           ("dbSNP156 (NCBI, Nov 2022)", "wg_b156.tsv", "b156.ids")]
RS = re.compile(r"rs(\d+)")


def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*(c-h), 100*(c+h)


# ---------------------------------------------------------------- prep
def load_ledger():
    rx_id = re.compile(rb'^\{"refsnp_id":"(\d+)"')
    rx_into = re.compile(rb'"merged_into":\[([^\]]*)\]')
    led = {}
    with bz2.open(os.path.join(WG, "refsnp-merged.json.bz2"), "rb") as f:
        for ln in f:
            m = rx_id.match(ln); t = rx_into.search(ln)
            if m and t:
                into = [int(x) for x in re.findall(rb"\d+", t.group(1))]
                if into: led[int(m.group(1))] = into[0]
    return led


def resolver(led):
    def resolve(i):
        seen = 0
        while i in led and seen < 20:
            i = led[i]; seen += 1
        return i
    return resolve


def clinvar_class(sig):
    s = sig.lower()
    if "conflicting" in s: return "conflicting"
    if "pathogenic" in s and "benign" not in s: return "P/LP"
    if "benign" in s and "pathogenic" not in s: return "B/LB"
    if "uncertain" in s: return "VUS"
    if "drug_response" in s: return "drug_response"
    if "risk_factor" in s: return "risk_factor"
    return "other"


def load_resources():
    E = []  # entries: (resource, category, distributed_rsid, extra)
    pos_keys = {}  # ClinVar normalized (chrN,pos0,del,ins) -> entry index list
    with gzip.open(P("clinvar_GRCh38.vcf.gz"), "rt") as f:
        for ln in f:
            if ln[0] == "#": continue
            c, p, _, r, a, _, _, info = ln.rstrip("\n").split("\t")[:8]
            if not (c.isdigit() and 1 <= int(c) <= 22): continue
            d = dict(x.split("=", 1) for x in info.split(";") if "=" in x)
            rev = d.get("CLNREVSTAT", "")
            stars = "0*" if ("no_assertion" in rev or "no_classification" in rev or "no_interpretation" in rev) else ">=1*"
            cat = clinvar_class(d.get("CLNSIG", ""))
            idx = len(E)
            E.append(("ClinVar", cat, int(d["RS"].split("|")[0]) if "RS" in d else None, stars))
            if a not in (".", "*") and r != a:
                pos_keys.setdefault(("chr" + c,) + normalize(int(p), r, a), []).append(idx)
    with open(P("gwas-catalog-associations-full", "gwas-catalog-download-associations-v1.0-full.tsv"), encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            try: pv = float(row["P-VALUE"])
            except ValueError: pv = 1.0
            cat = "p<5e-8" if pv < 5e-8 else "p>=5e-8"
            for m in RS.findall(row["SNPS"]):
                E.append(("GWAS", cat, int(m), row["SNP_ID_CURRENT"]))
    for fn, res in [(("clinicalAnnotations", "clinical_annotations.tsv"), "PharmGKB-clinical"),
                    (("variantAnnotations", "var_drug_ann.tsv"), "PharmGKB-variant"),
                    (("variantAnnotations", "var_pheno_ann.tsv"), "PharmGKB-variant"),
                    (("variantAnnotations", "var_fa_ann.tsv"), "PharmGKB-variant")]:
        with open(P(*fn), encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter="\t"):
                lvl = row.get("Level of Evidence", "")
                cat = ("level " + lvl) if lvl else "variant annotation"
                for m in RS.findall(row["Variant/Haplotypes"]):
                    E.append((res, cat, int(m), ""))
    return E, pos_keys


def prep():
    print("loading ledger ...", flush=True)
    led = load_ledger(); resolve = resolver(led)
    print(f"  {len(led):,} retired rsIDs", flush=True)
    E, pos_keys = load_resources()
    print(f"  {len(E):,} resource entries; ClinVar chr-pos-ref-alt keys {len(pos_keys):,}", flush=True)
    cur = {e[2]: resolve(e[2]) for e in E if e[2] is not None}
    want = set(cur) | set(cur.values())
    preds = collections.defaultdict(set)  # current id -> retired ids resolving to it
    for x in led:
        r = resolve(x)
        if r in want: preds[r].add(x)
    targets = want | {x for s in preds.values() for x in s}
    with open(P("targets.txt"), "w") as o:
        o.write("\n".join(map(str, sorted(targets))))
    pickle.dump(dict(E=E, pos_keys=pos_keys, cur=cur, preds=dict(preds), led=led),
                open(P("prep.pkl"), "wb"), protocol=4)
    print(f"  targets for bundle scan: {len(targets):,}; prep.pkl written", flush=True)


# ---------------------------------------------------------------- scan
def scan(src, out):
    T = {int(x) for x in open(P("targets.txt")).read().split()}
    found = set(); n = 0
    with gzip.open(src, "rb") as g:
        for ln in g:
            if ln[:1] == b"#": continue
            n += 1
            idf = ln.split(b"\t", 3)[2]
            for x in idf.split(b";"):
                if x[:2] == b"rs":
                    i = int(x[2:])
                    if i in T: found.add(i)
    with open(out + ".part", "w") as o:
        o.write("\n".join(map(str, sorted(found))))
    os.replace(out + ".part", out)
    print(f"{src}: {n:,} records, {len(found):,} target IDs present", flush=True)


# ---------------------------------------------------------------- report
def report(sample="HG002_wg.vcf.gz", pfx="wg_", tag=""):
    D = pickle.load(open(P("prep.pkl"), "rb"))
    E, pos_keys, cur, preds, led = D["E"], D["pos_keys"], D["cur"], D["preds"], D["led"]
    # ClinVar categories carry the review-star split (">=1*" / "0*") so P/LP >=1* is reportable
    E = [(e[0], f"{e[1]} {e[3]}" if e[0] == "ClinVar" else e[1], e[2], e[3]) for e in E]
    resolve = resolver(led)
    by_dist = collections.defaultdict(list); by_cur = collections.defaultdict(list)
    for k, e in enumerate(E):
        if e[2] is None: continue
        by_dist[e[2]].append(k); by_cur[cur[e[2]]].append(k)
    lab = lambda k: (E[k][0], E[k][1])
    out = {}

    print("=" * 78)
    print("Resource-side staleness: entries distributed under a retired rsID (b157 ledger)")
    rs_tot = collections.Counter(); rs_ret = collections.Counter()
    for e in E:
        if e[2] is None: continue
        rs_tot[(e[0], e[1])] += 1; rs_ret[(e[0], e[1])] += e[2] in led
    for k in sorted(rs_tot):
        print(f"  {k[0]:<18} {k[1]:<20} {rs_ret[k]:>7,}/{rs_tot[k]:>9,} = {100*rs_ret[k]/rs_tot[k]:.2f}%")
    g = [e for e in E if e[0] == "GWAS" and e[2] in led and e[3]]
    agree = sum(1 for e in g if e[3].isdigit() and int(e[3]) == cur[e[2]])
    print(f"  GWAS SNP_ID_CURRENT agrees with ledger resolution for {agree:,}/{len(g):,} retired SNPS")

    # ---------- A: sample-level (HG002)
    calls = []
    with gzip.open(os.path.join(WG, sample), "rt") as f:
        for ln in f:
            if ln[0] == "#": continue
            c, p, _, r, a = ln.split("\t", 5)[:5]
            calls.append([(c,) + normalize(int(p), r, x) for x in a.split(",")])
    pos_hit = [set(k for key in keys for k in pos_keys.get(key, ())) for keys in calls]
    print("\n" + "=" * 78)
    print(f"A. {sample} (GIAB v4.2.1 chr1-22), {len(calls):,} benchmark variants")
    print(f"   ClinVar chr-pos-ref-alt join (no rsID involved): {sum(len(s) for s in pos_hit):,} entries "
          f"at {sum(1 for s in pos_hit if s):,} variants")
    for name, tsv, _ in BUNDLES:
        path = os.path.join(WG, tsv.replace("wg_", pfx, 1))
        if not os.path.exists(path):
            print(f"\n-- {name}: {tsv} not ready, skipped"); continue
        km = collections.defaultdict(set)
        with open(path) as f:
            for ln in f:
                c, p, r, a, i = ln.rstrip("\n").split("\t")
                ids = {int(x) for x in i.replace("rs", "").split(";") if x.isdigit()}
                for x in a.split(","):
                    km[(c,) + normalize(int(p), r, x)] |= ids
        naive_n = collections.Counter(); recon_n = collections.Counter()
        miss_pipe = collections.Counter(); miss_res = collections.Counter()
        var_lost = collections.Counter(); clin_pos_vs_rs = collections.Counter()
        examples = []
        for vi, keys in enumerate(calls):
            ids = set().union(*(km.get(k, set()) for k in keys))
            naive = {k for i in ids for k in by_dist.get(i, ())}
            curids = {resolve(i) for i in ids}
            recon = {k for i in curids for k in by_cur.get(i, ())}
            for k in naive: naive_n[lab(k)] += 1
            for k in recon: recon_n[lab(k)] += 1
            missed = recon - naive
            lost_cats = set()
            for k in missed:
                pipe_retired = cur[E[k][2]] not in ids  # pipeline lacks the current ID
                (miss_pipe if pipe_retired else miss_res)[lab(k)] += 1
                lost_cats.add(lab(k))
                if pipe_retired and len(examples) < 15 and E[k][1] in ("P/LP >=1*", "level 1A", "level 1B", "level 2A", "level 2B", "p<5e-8"):
                    examples.append((keys[0][0], keys[0][1] + 1, sorted(ids), E[k][2], E[k][0], E[k][1]))
            for c in lost_cats: var_lost[c] += 1
            # ClinVar: rsID joins vs position join
            cp = pos_hit[vi]
            if cp or any(E[k][0] == "ClinVar" for k in recon):
                nv = {k for k in naive if E[k][0] == "ClinVar"}; rc = {k for k in recon if E[k][0] == "ClinVar"}
                clin_pos_vs_rs["pos"] += len(cp); clin_pos_vs_rs["pos&naive"] += len(cp & nv)
                clin_pos_vs_rs["pos&recon"] += len(cp & rc)
        print(f"\n-- {name}")
        print(f"   {'resource':<18} {'category':<20} {'reconciled':>10} {'naive':>9} {'missed':>8} "
              f"{'%':>6} {'95% CI':>13}  pipeline-side / resource-side  sample variants losing >=1")
        rows = {}
        for k in sorted(recon_n):
            m = recon_n[k] - naive_n[k]; lo, hi = wilson(m, recon_n[k])
            print(f"   {k[0]:<18} {k[1]:<20} {recon_n[k]:>10,} {naive_n[k]:>9,} {m:>8,} "
                  f"{100*m/recon_n[k]:>5.2f}% {lo:>5.2f}-{hi:<6.2f}  {miss_pipe[k]:>7,} / {miss_res[k]:<7,}  {var_lost[k]:>7,}")
            rows[" | ".join(k)] = dict(reconciled=recon_n[k], naive=naive_n[k], missed=m,
                                       missed_pipeline_side=miss_pipe[k], missed_resource_side=miss_res[k],
                                       hg002_variants_losing=var_lost[k])
        cp = clin_pos_vs_rs
        if cp["pos"]:
            print(f"   ClinVar position-matched entries also found by naive rsID join: {cp['pos&naive']:,}/{cp['pos']:,} "
                  f"({100*cp['pos&naive']/cp['pos']:.2f}%); by reconciled join: {cp['pos&recon']:,} ({100*cp['pos&recon']/cp['pos']:.2f}%)")
        for ex in examples:
            print(f"     e.g. {ex[0]}:{ex[1]} pipeline IDs {ex[2]} -> {ex[4]} {ex[5]} entry filed under rs{ex[3]}")
        out[name] = dict(sample=rows, clinvar_pos=dict(cp))

    # ---------- B: resource-centric
    print("\n" + "=" * 78)
    print("B. Resource-centric, genome-wide (ID-level): entries unreachable by naive rsID join")
    for name, _, ids_file in BUNDLES:
        path = P(ids_file)
        if not os.path.exists(path):
            print(f"\n-- {name}: {ids_file} not ready, skipped"); continue
        B = {int(x) for x in open(path).read().split()}
        tot = collections.Counter(); ret_only = collections.Counter(); res_stale = collections.Counter()
        for e in E:
            if e[2] is None: continue
            r = cur[e[2]]
            has_cur = r in B; has_pred = any(x in B for x in preds.get(r, ()))
            if not (has_cur or has_pred): continue
            tot[(e[0], e[1])] += 1
            if e[2] in B: continue
            if has_cur: res_stale[(e[0], e[1])] += 1
            else: ret_only[(e[0], e[1])] += 1
        print(f"\n-- {name}")
        print(f"   {'resource':<18} {'category':<20} {'locus in bundle':>15} {'retired-only':>13} {'%':>6}  {'resource-stale':>14} {'%':>6}")
        rows = {}
        for k in sorted(tot):
            print(f"   {k[0]:<18} {k[1]:<20} {tot[k]:>15,} {ret_only[k]:>13,} {100*ret_only[k]/tot[k]:>5.2f}%  "
                  f"{res_stale[k]:>14,} {100*res_stale[k]/tot[k]:>5.2f}%")
            rows[" | ".join(k)] = dict(in_bundle=tot[k], retired_only=ret_only[k], resource_stale=res_stale[k])
        out.setdefault(name, {})["resource_centric"] = rows
    json.dump(out, open(P(f"downstream_results{tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "prep": prep()
    elif sys.argv[1] == "report": report(*sys.argv[2:5])  # optional: <sample.vcf.gz> <tsv prefix> <tag>
    else: scan(sys.argv[2], sys.argv[3])
