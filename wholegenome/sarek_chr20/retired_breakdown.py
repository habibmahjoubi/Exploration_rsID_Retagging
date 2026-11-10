"""For rsIDs assigned to the sarek calls by each bundle and retired in b157:
which build retired them, and collect a random sample for live-API validation."""
import bz2, gzip, re, random, collections, json
from normalize import normalize
exec(open("ledger_check.py").read().split("retired = set()")[0].split("per_bundle_ids, sarek_ann = {}, {}")[0])  # reuse sarek parsing
bundles = {"138": "d138.tsv", "146": "d146_chr20_idmap.tsv", "156": "b156_chr20_idmap.tsv"}
want = {}
for name, path in bundles.items():
    keymap = collections.defaultdict(set)
    with open(path) as f:
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) != 4: continue
            for a in p[2].split(","):
                keymap[normalize(int(p[0]), p[1], a)].update(int(r) for r in p[3].replace("rs", "").split(";") if r.isdigit())
    s = set()
    for keys in calls:
        for k in keys: s |= keymap.get(k, set())
    want[name] = s
allw = set().union(*want.values())
info = {}
rx = re.compile(rb'^\{"refsnp_id":"(\d+)".*"proxy_time":"([^"]+)","proxy_build_id":"(\d+)","merged_into":\[([^\]]*)\]')
with bz2.open("refsnp-merged.json.bz2", "rb") as f:
    for ln in f:
        m = rx.match(ln)
        if m and int(m.group(1)) in allw:
            info[int(m.group(1))] = (m.group(2).decode(), int(m.group(3)), m.group(4).decode().replace('"', ''))
for name, s in want.items():
    r = [info[i] for i in s if i in info]
    c = collections.Counter(b for _, b, _ in r)
    print(f"dbSNP{name}: retired={len(r):,}  by retiring build: {dict(sorted(c.items()))}")
random.seed(1)
sample = random.sample(sorted(i for i in want["146"] if i in info), 50)
json.dump({str(i): info[i] for i in sample}, open("sample50.json", "w"))
