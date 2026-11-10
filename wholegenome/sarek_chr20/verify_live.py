import json, time, urllib.request
s = json.load(open("sample50.json"))
def get(i):
    for k in range(6):
        try:
            return _get(i)
        except Exception:
            time.sleep(3 * (k + 1))
    return {}
def _get(i):
    req = urllib.request.Request(f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{i}", headers={"User-Agent": "rsid-check/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())
def chr20_pos(rec):
    out = set()
    for pl in rec.get("primary_snapshot_data", {}).get("placements_with_allele", []):
        if pl.get("seq_id") == "NC_000020.11":
            for a in pl["alleles"]: out.add(a["allele"]["spdi"]["position"])
    return out
ok_merged = ok_pos = 0
for old, (t, b, into) in s.items():
    r = get(old); time.sleep(0.35)
    mi = r.get("merged_snapshot_data", {}).get("merged_into", [])
    live = "primary_snapshot_data" in r
    tgt = mi[0] if mi else None
    same = False
    if tgt:
        ok_merged += 1
        t2 = get(tgt); time.sleep(0.35)
        same = bool(chr20_pos(t2))
        ok_pos += same
    print(old, "->", mi, "retired_build", b, "| old still live:", live, "| target on chr20:", same, flush=True)
print(f"\nmerged per live API: {ok_merged}/50; target placed on chr20 GRCh38: {ok_pos}/50")
