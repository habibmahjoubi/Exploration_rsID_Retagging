"""Check ClinVar for the 369 dbSNP138-stale (current, old) rsID pairs: does
the CURRENT id have a real ClinVar clinical-significance record, and does the
OLD (bundle-reported, retired) id ALSO resolve in ClinVar, or fail silently?
This is the concrete test of whether the stale-identifier problem has
clinical consequence, not just an administrative one.
"""
import json, time, sys, urllib.request, urllib.parse

def esearch_count(db, rsid):
    params = urllib.parse.urlencode({"db": db, "term": f"rs{rsid}", "retmode": "json"})
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "rsid-clinvar-check/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return int(data.get("esearchresult", {}).get("count", 0))

rows = []
with open("stale_pairs_138.tsv", encoding="utf-8") as f:
    for line in f:
        current, old, pos, ref, alt = line.rstrip("\n").split("\t")
        rows.append((current, old, pos, ref, alt))

results = []
for i, (current, old, pos, ref, alt) in enumerate(rows):
    try:
        n_current = esearch_count("clinvar", current)
    except Exception as e:
        n_current = -1
    time.sleep(0.35)
    try:
        n_old = esearch_count("clinvar", old)
    except Exception as e:
        n_old = -1
    time.sleep(0.35)
    results.append((current, old, pos, ref, alt, n_current, n_old))
    if (i + 1) % 25 == 0:
        sys.stderr.write(f"[{i+1}/{len(rows)}]\n")

both_zero = sum(1 for r in results if r[5] == 0 and r[6] == 0)
current_has_old_missing = [r for r in results if r[5] > 0 and r[6] == 0]
both_have = [r for r in results if r[5] > 0 and r[6] > 0]
current_zero = sum(1 for r in results if r[5] == 0)

print(f"Total pairs checked: {len(results)}")
print(f"Current id has >=1 ClinVar record: {sum(1 for r in results if r[5] > 0)}")
print(f"  ...of which the OLD (bundle-reported) id has ZERO ClinVar records: {len(current_has_old_missing)}")
print(f"  ...of which the OLD id ALSO has >=1 ClinVar record: {len(both_have)}")
print(f"Neither id has any ClinVar record: {both_zero}")
print()
print("Examples where current has ClinVar data but the bundle-reported OLD id does not:")
for r in current_has_old_missing[:15]:
    print(" ", r)

with open("clinvar_check_results.tsv", "w") as f:
    f.write("current\told\tpos\tref\talt\tn_clinvar_current\tn_clinvar_old\n")
    for r in results:
        f.write("\t".join(str(x) for x in r) + "\n")
