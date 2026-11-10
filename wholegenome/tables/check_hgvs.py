"""Validates every HGVS description in the manuscript and Supplement with the VariantValidator
REST API (GRCh38). Output: hgvs_validation.tsv. Usage: python check_hgvs.py"""
import json, re, time, urllib.parse, urllib.request
import os
# tables_generated.md holds Table S6; the manuscript files (not in this repository) add the two
# examples of the text, NC_000013.11:g.60275658A>G and NC_000020.11:g.49283799G>C
src = ["tables_generated.md", "02_supplement_src.md", "01_main_text.md"]
txt = "".join(open(f, encoding="utf-8").read() for f in src if os.path.exists(f))
txt += " NC_000013.11:g.60275658A>G NC_000020.11:g.49283799G>C"
hgvs = sorted(set(re.findall(r"NC_0000\d\d\.\d+:g\.\d+[ACGT]>[ACGT]", txt)))
print(len(hgvs), "distinct HGVS descriptions")
rows = []
for h in hgvs:
    url = ("https://rest.variantvalidator.org/VariantValidator/variantvalidator/GRCh38/"
           + urllib.parse.quote(h) + "/mane_select?content-type=application%2Fjson")
    for k in range(5):
        try:
            d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "hgvs-check/1.0"}), timeout=60).read())
            break
        except Exception as e:
            err = str(e); d = None; time.sleep(5 * (k + 1))
    if d is None:
        rows.append((h, "API error", err)); continue
    warn = []; ok = False; gene = "-"
    for key, v in d.items():
        if key in ("flag", "metadata") or not isinstance(v, dict): continue
        warn += v.get("validation_warnings", [])
        loci = v.get("primary_assembly_loci", {}).get("grch38", {})
        if loci.get("hgvs_genomic_description") == h: ok = True
        gene = v.get("gene_symbol") or gene
    flag = d.get("flag")
    if flag == "intergenic":
        ok = ok or any("intergenic" in str(x) for x in d.values())
    bad = [w for w in warn if re.search(r"does not agree|ReferenceMismatch|not valid|Invalid", w)]
    rows.append((h, "VALID" if not bad else "PROBLEM", f"flag={flag}; gene={gene}; " + " | ".join(bad or warn[:1])))
    time.sleep(0.6)
with open("hgvs_validation.tsv", "w", encoding="utf-8") as o:
    o.write("hgvs\tresult\tdetails\n")
    for r in rows: o.write("\t".join(r) + "\n")
from collections import Counter
print(Counter(r[1] for r in rows))
for r in rows:
    if r[1] != "VALID": print(r)
