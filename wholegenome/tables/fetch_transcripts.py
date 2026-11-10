"""MANE Select transcript (c.) and protein (p.) descriptions for every genomic HGVS description in
hgvs_validation.tsv, from the VariantValidator REST API (GRCh38). Variants without a MANE Select
transcript are queried against all RefSeq transcripts to name the overlapping gene, if any.
Output: hgvs_transcripts.tsv. Usage: python fetch_transcripts.py"""
import json, time, urllib.parse, urllib.request

def query(h, select):
    url = ("https://rest.variantvalidator.org/VariantValidator/variantvalidator/GRCh38/"
           + urllib.parse.quote(h) + f"/{select}?content-type=application%2Fjson")
    for k in range(5):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "hgvs-check/1.0"}), timeout=60).read())
        except Exception:
            time.sleep(5 * (k + 1))
    return None

hgvs = [l.split("\t")[0] for l in open("hgvs_validation.tsv", encoding="utf-8").read().splitlines()[1:]]
out = ["hgvs\tgene\ttranscript_c\tprotein_p\tnote"]
for h in hgvs:
    d = query(h, "mane_select")
    gene = c = p = ""; note = ""
    for key, v in (d or {}).items():
        if key in ("flag", "metadata") or not isinstance(v, dict) or not v.get("hgvs_transcript_variant"):
            continue
        gene = v.get("gene_symbol", ""); c = v["hgvs_transcript_variant"]
        p = (v.get("hgvs_predicted_protein_consequence") or {}).get("tlr", "")
        break
    if not c:
        a = query(h, "all")
        genes = sorted({v.get("gene_symbol") for k, v in (a or {}).items()
                        if isinstance(v, dict) and v.get("gene_symbol")})
        note = ("overlaps " + ", ".join(genes) + " (no MANE Select transcript)") if genes else "intergenic"
        gene = genes[0] if genes else ""
    out.append("\t".join([h, gene, c, p, note]))
    print(h, gene, c, p, note, flush=True)
    time.sleep(0.6)
open("hgvs_transcripts.tsv", "w", encoding="utf-8").write("\n".join(out) + "\n")
