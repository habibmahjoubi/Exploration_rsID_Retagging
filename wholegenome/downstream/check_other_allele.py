"""List ClinVar P/LP (>=1 star) entries that a plain rsID join attaches to a sample variant
although the ClinVar allele differs from the sample allele (same position, other allele).
Prints sample allele, ClinVar allele, gene and HGVS, to check these are genuinely different alleles
and not a normalization artifact.
Usage (from G:/rsid_wg): python downstream/check_other_allele.py <sample.vcf.gz> <bundle.tsv> <out.tsv>"""
import collections, gzip, pickle, sys
sys.path.insert(0, ".")
from normalize import normalize
SAMPLE, TSV, OUT = sys.argv[1:4]
D = pickle.load(open("downstream/prep.pkl", "rb"))
E, pos_keys = D["E"], D["pos_keys"]
key_of = {i: k for k, idxs in pos_keys.items() for i in idxs}
by_rs = collections.defaultdict(list)
for idx, e in enumerate(E):
    if e[0] == "ClinVar" and e[1] == "P/LP" and e[3] == ">=1*" and e[2] is not None: by_rs[e[2]].append(idx)
del D
calls = []
with gzip.open(SAMPLE, "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c, p, _, r, a, _, _, _, _, s = ln.rstrip("\n").split("\t")[:10]
        calls.append(((c, p, r, a, s.split(":")[0]), [(c,) + normalize(int(p), r, x) for x in a.split(",")]))
want = {k for _, ks in calls for k in ks}
km = collections.defaultdict(set)
with open(TSV) as f:
    for ln in f:
        c, p, r, a, i = ln.rstrip("\n").split("\t")
        for x in a.split(","):
            k = (c,) + normalize(int(p), r, x)
            if k in want: km[k] |= {int(z) for z in i.replace("rs", "").split(";") if z.isdigit()}
rows = []
for raw, keys in calls:
    ids = set().union(*(km.get(k, set()) for k in keys))
    for x in ids:
        for i in by_rs.get(x, ()):
            ck = key_of.get(i)
            if ck in keys: continue
            same_pos = ck is not None and (ck[0], ck[1]) in {(k[0], k[1]) for k in keys}
            rows.append((raw, keys[0], x, ck, "same position" if same_pos else "other locus"))
need = {(r[3][0], r[3][1]) for r in rows if r[3]}
info = {}
with gzip.open("downstream/clinvar_GRCh38.vcf.gz", "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c, p, vid, r, a, _, _, inf = ln.rstrip("\n").split("\t")[:8]
        k = ("chr" + c,) + normalize(int(p), r, a)
        if (k[0], k[1]) not in need: continue
        d = dict(x.split("=", 1) for x in inf.split(";") if "=" in x)
        info[k] = (vid, d.get("GENEINFO", "-").split(":")[0], d.get("CLNHGVS", "-"), d.get("CLNSIG", "-"))
with open(OUT, "w") as o:
    o.write("sample_variant\tGT\tsample_norm\trsID\tclinvar_norm\twhere\tclinvar_id\tgene\tclinvar_hgvs\tclnsig\n")
    for raw, sk, x, ck, where in rows:
        v = info.get(ck, ("-", "-", "-", "-"))
        o.write(f"{raw[0]}:{raw[1]} {raw[2]}>{raw[3]}\t{raw[4]}\t{sk[1]},{sk[2] or '-'},{sk[3] or '-'}\trs{x}\t"
                f"{ck[1] if ck else '-'},{(ck[2] or '-') if ck else '-'},{(ck[3] or '-') if ck else '-'}\t{where}\t"
                f"{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\n")
print(f"{len(rows)} P/LP>=1* entries attached by plain rsID join at a non-matching allele -> {OUT}")
print(collections.Counter(r[4] for r in rows))
