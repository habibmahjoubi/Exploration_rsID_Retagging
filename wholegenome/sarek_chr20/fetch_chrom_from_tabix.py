"""Extract one contig from a remote BGZF+tabix VCF using only HTTP range requests.

Usage: python fetch_chrom_from_tabix.py <vcf_url> <local_tbi> <contig> <out_idmap.tsv>
Writes pos<TAB>ref<TAB>alt<TAB>rsID (same layout as data/*_idmap.tsv.gz).
"""
import gzip, struct, sys, zlib, urllib.request

url, tbi_path, contig, out_path = sys.argv[1:5]

raw = gzip.open(tbi_path, "rb").read()
assert raw[:4] == b"TBI\x01"
n_ref, = struct.unpack_from("<i", raw, 4)
l_nm, = struct.unpack_from("<i", raw, 32)
names = raw[36:36 + l_nm].split(b"\x00")[:n_ref]
off = 36 + l_nm
target = names.index(contig.encode())
beg_v, end_v = None, None
for i in range(n_ref):
    n_bin, = struct.unpack_from("<i", raw, off); off += 4
    for _ in range(n_bin):
        _bin, n_chunk = struct.unpack_from("<Ii", raw, off); off += 8
        for _ in range(n_chunk):
            cb, ce = struct.unpack_from("<QQ", raw, off); off += 16
            if i == target:
                beg_v = cb if beg_v is None else min(beg_v, cb)
                end_v = ce if end_v is None else max(end_v, ce)
    n_intv, = struct.unpack_from("<i", raw, off); off += 4 + 8 * n_intv

c_beg, u_beg = beg_v >> 16, beg_v & 0xFFFF
c_end = (end_v >> 16) + 70000  # include the last block
print(f"{contig}: bytes {c_beg}-{c_end} ({(c_end - c_beg) / 1e6:.0f} MB compressed)", flush=True)

req = urllib.request.Request(url, headers={"Range": f"bytes={c_beg}-{c_end}"})
resp = urllib.request.urlopen(req, timeout=600)

prefix = contig.encode() + b"\t"
n_out = 0
first = True
buf = b""
pending = b""
done = False
d = zlib.decompressobj(31)
with open(out_path, "w", encoding="utf-8") as out:
    while not done:
        chunk = resp.read(1 << 20)
        if not chunk:
            break
        data = pending + chunk
        pending = b""
        while data and not done:
            try:
                txt = d.decompress(data)
            except zlib.error:
                done = True  # trailing partial block past the contig
                break
            if first:
                txt = txt[u_beg:]
                first = False
            buf += txt
            if d.eof:
                data = d.unused_data
                d = zlib.decompressobj(31)
            else:
                data = b""
            lines = buf.split(b"\n")
            buf = lines.pop()
            for ln in lines:
                if not ln.startswith(prefix):
                    if n_out:
                        done = True
                        break
                    continue
                f = ln.split(b"\t", 5)
                out.write(f"{f[1].decode()}\t{f[3].decode()}\t{f[4].decode()}\t{f[2].decode()}\n")
                n_out += 1
                if n_out % 2_000_000 == 0:
                    print(f"  {n_out:,} records", flush=True)
print(f"done: {n_out:,} records written to {out_path}")
