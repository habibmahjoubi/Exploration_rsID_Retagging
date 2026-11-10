import gzip, sys, collections
sys.path.insert(0, ".")
from normalize import normalize
calls = []
with gzip.open("HG002_wg.vcf.gz", "rt") as f:
    for ln in f:
        if ln[0] == "#": continue
        c, p, _, r, a = ln.split("\t", 5)[:5]
        ks = [(c,) + normalize(int(p), r, x) for x in a.split(",")]
        if any(len(k[2]) != 1 or len(k[3]) != 1 for k in ks): calls.append(ks)
want = {k for ks in calls for k in ks}
def load(tsv):
    km = collections.defaultdict(set); mx = 0
    with open(tsv) as f:
        for ln in f:
            c, p, r, a, i = ln.rstrip("\n").split("\t")
            ids = {int(x) for x in i.replace("rs", "").split(";") if x.isdigit()}
            mx = max(mx, max(ids, default=0))
            for x in a.split(","):
                k = (c,) + normalize(int(p), r, x)
                if k in want: km[k] |= ids
    return km, mx
k146, mx146 = load("wg_d146.tsv"); k156, _ = load("wg_b156.tsv")
un = [ks for ks in calls if not any(k in k146 for k in ks)]
cls = collections.Counter()
for ks in un:
    ids = set().union(*(k156.get(k, set()) for k in ks))
    if not ids: cls["no rsID in dbSNP156 either"] += 1
    elif min(ids) > mx146: cls["all dbSNP156 rsIDs newer than dbSNP146 (rsID > max)"] += 1
    else: cls["has an rsID old enough to be in dbSNP146"] += 1
print(f"HG002 indels {len(calls):,}; without dbSNP146 rsID {len(un):,}; max rsID seen in dbSNP146 rs{mx146}")
for k, v in cls.most_common(): print(f"  {k}: {v:,} ({100*v/len(un):.1f}%)")
