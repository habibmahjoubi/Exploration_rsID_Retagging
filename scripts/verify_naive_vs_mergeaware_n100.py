"""Extended naive-vs-merge-aware verification, n=100 (supersedes the n=30 pilot),
drawn from the allele-exact candidate panel (candidate_panel_allele_exact.csv)
rather than the earlier position-only panel, so it also benefits from the
allele-exact validation.
"""
import csv, json, random, time, urllib.request, sys

random.seed(42)

rows = list(csv.DictReader(open("candidate_panel_allele_exact.csv", encoding="utf-8")))
sample = random.sample(rows, 100)

def fetch_refsnp(rsid):
    url = f"https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/{rsid}"
    req = urllib.request.Request(url, headers={"User-Agent": "research-feasibility-check/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))

results = []
for i, row in enumerate(sample):
    current_rsid = row["current_rsid"]
    old_rsid = row["merged_from_rsids"].split(";")[0]
    try:
        rec = fetch_refsnp(old_rsid)
    except Exception as e:
        results.append({"old_rsid": old_rsid, "expected_current": current_rsid, "error": str(e)})
        time.sleep(0.4)
        continue

    merged_into = rec.get("merged_snapshot_data", {}).get("merged_into", [])
    naive_verdict = "UNKNOWN/RETIRED (no live data of its own)" if not rec.get("primary_snapshot_data") else "resolves directly (unexpected)"
    merge_aware_verdict = f"-> rs{merged_into[0]}" if merged_into else "NOT FLAGGED AS MERGED (unexpected)"
    match = (merged_into and str(merged_into[0]) == str(current_rsid))

    results.append({
        "old_rsid": old_rsid,
        "expected_current": current_rsid,
        "naive_verdict": naive_verdict,
        "merge_aware_verdict": merge_aware_verdict,
        "resolves_to_expected_current": bool(match),
    })
    if (i + 1) % 10 == 0:
        sys.stderr.write(f"[{i+1}/100] done\n")
    time.sleep(0.4)

n_ok = sum(1 for r in results if r.get("resolves_to_expected_current"))
n_no_primary = sum(1 for r in results if r.get("naive_verdict", "").startswith("UNKNOWN"))
n_err = sum(1 for r in results if "error" in r)

summary = {
    "n_sampled": 100,
    "n_no_primary_snapshot_data": n_no_primary,
    "n_confirmed_match_via_merge_ledger": n_ok,
    "n_errors": n_err,
}
print(json.dumps({"summary": summary, "details": results}, indent=2))
sys.stderr.write(json.dumps(summary, indent=2) + "\n")
