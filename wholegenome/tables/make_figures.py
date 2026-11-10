"""Figures for the Brief Communication (v3). Main Figure 1 = retirements per build (v2 Fig 3);
Supplementary Figure S1 = annotation rates (v2 Fig 2). v2 Figures 1 and 4 are not used.

Original header (v2):
Figures for manuscript v2 (static, print). Writes PDF + SVG (vector) and 600-dpi TIFF.

Fig 1  schematic: where a retired rsID matters (diagram, no data)
Fig 2  retired-rsID annotation rate by bundle: 3 GIAB genomes (whole genome) + real sarek run
Fig 3  retirements per dbSNP build (genome-wide ledger) and retirements after each default bundle
Fig 4  lookup loss of a plain rsID join, clinically relevant categories, by bundle and genome

Palette: reference categorical slots 1-3 (blue, orange, aqua), validated all-pairs, light
surface (validate_palette.js: all PASS; aqua < 3:1 contrast -> every series also has its own
marker shape and a direct label). Single-series charts use slot 1 only. Text in ink colours.
Figures 2 and 4 are drawn only from result files; missing inputs are reported, never invented.
"""
import json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
WG = os.environ.get("RSID_WG", os.path.join(HERE, ".."))
LEDGER_TABLE = os.path.join(WG, "merged_years.txt")

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
CRIT = "#c62828"   # status (critical), used only for the "lookup fails" path in Fig 1
SAMPLES = [("HG001", S1, "o"), ("HG002", S2, "s"), ("HG005", S3, "^")]
BUNDLES = ["dbSNP138 (GATK/WARP)", "dbSNP144 (GDC)", "dbSNP146 (sarek default)", "dbSNP156 (NCBI, Nov 2022)"]
BLAB = ["dbSNP138\nWARP default", "dbSNP144\nGDC", "dbSNP146\nsarek default", "dbSNP156\nNov 2022"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "xtick.color": INK2, "ytick.color": INK2, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "svg.fonttype": "none", "pdf.fonttype": 42,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
})
MM = 1 / 25.4
GRID_LW, RULE_LW, BAR = 0.5, 0.6, S1   # colour (screen) version
SUFFIX = ""


def save(fig, name):
    for ext, kw in (("pdf", {}), ("svg", {}), ("png", {"dpi": 300}), ("tiff",{"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}})):
        fig.savefig(os.path.join(HERE, f"{name}.{ext}"), bbox_inches="tight", **kw)
    plt.close(fig)
    print("wrote", name)


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n)) / d; h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return 100*p, 100*(c-h), 100*(c+h)


def style(ax, grid_axis="y"):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=GRID_LW); ax.set_axisbelow(True)
    ax.tick_params(length=2.5)


# ------------------------------------------------------------------ Figure 1
def fig1():
    fig, ax = plt.subplots(figsize=(174*MM, 66*MM)); ax.set_xlim(0, 100); ax.set_ylim(0, 42); ax.axis("off")
    def box(x, y, w, h, title, body, edge=MUTED, tcol=INK):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
                                    fc="white", ec=edge, lw=0.8))
        ax.text(x + w/2, y + h - 1.8, title, ha="center", va="top", fontsize=7.5, weight="bold", color=tcol)
        ax.text(x + w/2, y + h - 5.4, body, ha="center", va="top", fontsize=6.6, color=INK2, linespacing=1.3)
    def arrow(x0, y0, x1, y1, col=MUTED):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.9,
                    shrinkA=0, shrinkB=0, mutation_scale=7))
    box(1, 25, 20, 16, "dbSNP", "two rsIDs found to be\nthe same variant:\none is retired and\nkept only as a pointer")
    box(25, 25, 20, 16, "Frozen bundle", "copy of dbSNP taken\nat one build\n(WARP: 138,\nsarek: 146)")
    box(49, 25, 20, 16, "Variant calling", "GATK -D copies the\nbundle rsID into\nthe VCF ID column")
    box(74, 30.5, 25, 10.5, "By position", "chr-pos-ref-alt join:\nunaffected")
    box(74, 14.5, 25, 13.5, "rsID join", "ClinVar, GWAS Catalog,\nPharmGKB, by rsID:\na retired rsID finds nothing",
        edge=CRIT, tcol=CRIT)
    box(40, 0.5, 59, 11, "Fix", "reconcile rsIDs on both sides against the dbSNP merge ledger\nbefore any rsID join, and record the bundle build",
        edge=S1, tcol=S1)
    arrow(21.6, 33, 24.4, 33); arrow(45.6, 33, 48.4, 33)
    arrow(69.6, 35, 73.4, 35.5); arrow(69.6, 29, 73.4, 22, col=CRIT); arrow(86.5, 14.0, 86.5, 12.1, col=S1)
    ax.text(1, 22, "dbSNP keeps retiring rsIDs after a bundle is frozen,\nso the rsIDs a pipeline writes go out of date.",
            fontsize=6.5, color=INK2, va="top")
    ax.text(1, 15.5, "Base recalibration reads only the positions of known\nvariants: retired rsIDs do not affect it.",
            fontsize=6.5, color=MUTED, va="top")
    save(fig, "Figure_1" + SUFFIX)


# ------------------------------------------------------------------ Figure 2
SAREK = {  # Table 3 (HG002 chr20 30x, real sarek run): retired, written
    "dbSNP138 (GATK/WARP)": (4423, 95397), "dbSNP144 (GDC)": (10925, 102630),
    "dbSNP146 (sarek default)": (11461, 104069), "dbSNP156 (NCBI, Nov 2022)": (647, 122609)}
SAREK_NATIVE = (4342, 94467)


def fig2():
    data = {}
    for s, _, _ in SAMPLES:
        p = os.path.join(WG, "wg_results.json" if s == "HG002" else f"wg_results_{s}.json")
        if os.path.exists(p): data[s] = json.load(open(p))
        else: print(f"  Fig 2: {p} missing -> {s} not drawn")
    fig, ax = plt.subplots(figsize=(120*MM, 70*MM)); style(ax)
    off = {"HG001": -0.22, "HG002": -0.07, "HG005": 0.08}
    for s, col, mk in SAMPLES:
        if s not in data: continue
        for i, b in enumerate(BUNDLES):
            r = data[s].get(b)
            if not r: continue
            v, lo, hi = wilson(r["retired_annotations"], r["annotations"])
            ax.errorbar(i + off[s], v, yerr=[[v-lo], [hi-v]], fmt=mk, ms=4.2, color=col, mec="white",
                        mew=0.6, elinewidth=0.8, capsize=0, zorder=3, label=f"{s} whole genome" if i == 0 else None)
    for i, b in enumerate(BUNDLES):
        v, lo, hi = wilson(*SAREK[b])
        ax.errorbar(i + 0.23, v, yerr=[[v-lo], [hi-v]], fmt="D", ms=4, mfc="white", mec=INK2, color=INK2,
                    mew=0.9, elinewidth=0.8, zorder=3, label="real sarek run, HG002 chr20" if i == 0 else None)
    v, lo, hi = wilson(*SAREK_NATIVE)
    ax.annotate(f"native GATK -D: {v:.2f}%\n(re-annotation: 4.64%)", xy=(0.23, v), xytext=(0.5, 1.6), fontsize=6.4, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.set_xticks(range(4)); ax.set_xticklabels(BLAB); ax.set_xlim(-0.5, 3.6)
    ax.set_ylabel("Retired rsIDs among rsIDs written (%)"); ax.set_ylim(0, 12.5)
    from matplotlib.lines import Line2D
    hd = [Line2D([], [], ls="none", marker=mk, ms=4.2, color=col, mec="white", mew=0.6) for _, col, mk in SAMPLES]
    hd.append(Line2D([], [], ls="none", marker="D", ms=4, mfc="white", mec=INK2, mew=0.9))
    lb = [f"{s} whole genome" for s, _, _ in SAMPLES] + ["real sarek run, HG002 chr20"]
    ax.legend(hd, lb, frameon=False, fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2,
              handletextpad=0.3, columnspacing=1.2)
    ax.set_title("Annotation rate, with 95% Wilson intervals", loc="left", color=INK, pad=6)
    save(fig, "Figure_S1")


# ------------------------------------------------------------------ Figure 3
def fig3():
    rows = open(LEDGER_TABLE).read().split("build\tretired_rsids\n")[1].split()
    per = {int(rows[i]): int(rows[i+1]) for i in range(0, len(rows), 2)}
    fig, (a, b) = plt.subplots(1, 2, figsize=(174*MM, 62*MM), gridspec_kw={"width_ratios": [2.3, 1]})
    style(a); style(b, "x")
    xs = sorted(per); a.bar(xs, [per[x]/1e6 for x in xs], width=0.8, color=BAR, linewidth=0)
    for x, ha, dx in ((130, "center", 0), (152, "center", 0), (157, "left", 0.7)):
        lab = f"{per[x]/1e6:.2f}M" + (f"\nb{x}" if x in (130, 152) else "")
        a.text(x + dx, per[x]/1e6 + 0.15, lab, ha=ha, va="bottom", fontsize=6.3, color=INK2, linespacing=1.1)
    for bb, nm in ((138, "WARP"), (146, "sarek"), (156, "NCBI")):
        a.axvline(bb + 0.5, color=MUTED, lw=RULE_LW, ls=(0, (3, 2)), zorder=0)
        a.text(bb + 0.2, 2.3, f"{nm} file, b{bb}", fontsize=6.0, color=MUTED, va="bottom", ha="right", rotation=90)
    a.set_xlabel("dbSNP build that retired the rsID"); a.set_ylabel("Retired rsIDs (millions)")
    a.set_ylim(0, 10.5); a.set_xlim(84, 163)
    a.set_title("a  Retirements per build, genome-wide (b157 ledger)", loc="left", color=INK, pad=6)
    # in-file counts: distinct chr1-22 rsIDs of each file that are retired (G:/rsid_wg/bundle_rate.txt)
    INFILE = {138: 1021831, 144: 2145350, 146: 2294215, 156: 508061}
    names = {138: "dbSNP138 (WARP)", 144: "dbSNP144 (GDC)", 146: "dbSNP146 (sarek)", 156: "dbSNP156 (NCBI)"}
    order = (156, 146, 144, 138)
    after = [sum(v for k, v in per.items() if k > bb)/1e6 for bb in order]
    infile = [INFILE[bb]/1e6 for bb in order]
    h = 0.36
    b.barh([i + h/2 for i in range(4)], after, height=h, color=BAR, linewidth=0, label="genome-wide (ledger)")
    b.barh([i - h/2 for i in range(4)], infile, height=h, color="white", edgecolor=BAR, linewidth=RULE_LW,
           hatch="////", label="in the file, chr1-22")
    for i, (v, w) in enumerate(zip(after, infile)):
        b.text(v + 0.15, i + h/2, f"{v:.2f}M", va="center", fontsize=6.2, color=INK2)
        b.text(w + 0.15, i - h/2, f"{w:.2f}M", va="center", fontsize=6.2, color=INK2)
    b.set_yticks(range(4)); b.set_yticklabels([names[bb] for bb in order]); b.set_xlim(0, 13)
    b.set_xlabel("Retired rsIDs (millions)")
    b.legend(frameon=False, fontsize=6.2, loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=2,
             handlelength=1.4, columnspacing=1.0, handletextpad=0.4)
    b.set_title("b  Retired rsIDs, by dbSNP file", loc="left", color=INK, pad=6)
    b.tick_params(axis="y", length=0)
    fig.tight_layout(w_pad=2)
    save(fig, "Figure_1" + SUFFIX)


# ------------------------------------------------------------------ Figure 4
CATS = [("ClinVar | P/LP >=1*", "ClinVar pathogenic /\nlikely pathogenic (>=1 star)"),
        ("GWAS | p<5e-8", "GWAS Catalog\np < 5x10^-8"),
        ("PharmGKB-clinical | level 1A", "PharmGKB clinical\nlevel 1A")]


def fig4():
    data = {}
    for s, _, _ in SAMPLES:
        p = os.path.join(WG, "downstream", "downstream_results.json" if s == "HG002" else f"downstream_results_{s}.json")
        if os.path.exists(p): data[s] = json.load(open(p))
        else: print(f"  Fig 4: {p} missing -> {s} not drawn")
    if not data:
        print("  Fig 4: no downstream results yet; skipped"); return
    fig, axes = plt.subplots(1, len(CATS), figsize=(174*MM, 60*MM), sharey=False)
    off = {"HG001": -0.15, "HG002": 0.0, "HG005": 0.15}
    for ax, (key, title) in zip(axes, CATS):
        style(ax)
        for s, col, mk in SAMPLES:
            if s not in data: continue
            for i, bnd in enumerate(BUNDLES):
                r = data[s].get(bnd, {}).get("sample", {}).get(key)
                if not r or not r["reconciled"]: continue
                v, lo, hi = wilson(r["missed"], r["reconciled"])
                ax.errorbar(i + off[s], v, yerr=[[v-lo], [hi-v]], fmt=mk, ms=4, color=col, mec="white",
                            mew=0.6, elinewidth=0.8, zorder=3, label=s if i == 0 else None)
        ax.set_xticks(range(4)); ax.set_xticklabels(["138", "144", "146", "156"]); ax.set_xlim(-0.5, 3.5)
        ax.set_xlabel("dbSNP bundle"); ax.set_ylim(0, None); ax.set_title(title, loc="left", color=INK, pad=5)
    axes[0].set_ylabel("Entries missed by a plain rsID join (%)")
    axes[-1].legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.tight_layout(w_pad=1.5)
    save(fig, "Figure_4")


if __name__ == "__main__":
    fig3()   # -> Figure_1 (colour)
    fig2()   # -> Figure_S1 (colour; supplement)
    # EJHG submission version: greyscale, every rule >= 1 pt
    GRID_LW, RULE_LW, BAR, SUFFIX = 1.0, 1.0, "#4d4d4d", "_greyscale"
    plt.rcParams.update({"axes.linewidth": 1.0, "xtick.major.width": 1.0, "ytick.major.width": 1.0,
                         "axes.edgecolor": "#808080"})
    fig3()   # -> Figure_1_greyscale
