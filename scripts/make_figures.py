# -*- coding: utf-8 -*-
"""Two figures for the rsID-retagging manuscript, built as one homogeneous pair:
identical canvas size, typography, orientation (both vertical bar charts),
transparent background, and a shared muted color vocabulary (soft green =
current/good, soft red = stale). No in-image title (the Word "Figure N."
caption is the single title, added by add_figure() in the manuscript script)
and no in-image source note. 300 DPI, matplotlib only.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---- palette: muted/soft variants, not the vivid dataviz-skill status colors ----
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
GOOD = "#7fa876"       # soft sage green (current / up to date)
CRITICAL = "#c17b74"   # soft terracotta red (stale)
OTHER_GRAY = "#8f8d86"   # medium-dark gray (ambiguous: both IDs present) -- clearly
ABSENT_GRAY = "#dbd8d0"  # light gray (position absent) -- clearly distinct from OTHER_GRAY

# ---- shared canvas + typography, identical for both figures ----
FIGSIZE = (6.4, 4.2)
DPI = 300
AXIS_LABEL_FONTSIZE = 10
TICK_FONTSIZE = 9.5

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["axes.edgecolor"] = BASELINE
plt.rcParams["text.color"] = INK_PRIMARY


def new_figure():
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    return fig, ax


def strip_spines(ax, keep=()):
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(spine in keep)
    for s in keep:
        ax.spines[s].set_color(BASELINE)


def savefig_transparent(fig, path):
    fig.savefig(path, transparent=True)


# ============================================================
# Figure 1 -- headline: stale-identifier rate by bundle vintage
# (vertical bar chart, no in-image title, no source note)
# ============================================================
fig, ax = new_figure()

bundles = ["dbSNP138\n(GATK, 2014)", "dbSNP144\n(GDC/NCI, Jun 2015)"]
stale_pct = [12.75, 2.59]

bars = ax.bar(bundles, stale_pct, width=0.45, color=CRITICAL, zorder=3)

for bar, val in zip(bars, stale_pct):
    ax.annotate(
        f"{val:.2f}%",
        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 6), textcoords="offset points",
        ha="center", va="bottom", fontsize=12, color=INK_PRIMARY, fontweight="bold",
    )

ax.set_ylabel("Variants reporting a retired (pre-merge) rsID", color=INK_SECONDARY, fontsize=AXIS_LABEL_FONTSIZE)
ax.set_ylim(0, 14)
ax.tick_params(axis="x", colors=INK_SECONDARY, labelsize=TICK_FONTSIZE)
ax.tick_params(axis="y", colors=INK_MUTED, labelsize=TICK_FONTSIZE)
ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
strip_spines(ax, keep=("bottom",))
ax.yaxis.set_major_formatter(lambda x, pos: f"{x:.0f}%")

fig.tight_layout()
savefig_transparent(fig, "figure1_stale_rate_by_vintage.png")
plt.close(fig)

# ============================================================
# Figure 2 -- full composition breakdown per bundle
# (vertical stacked bar chart -- same orientation as Figure 1)
# ============================================================
fig, ax = new_figure()

labels = ["dbSNP138\n(2014)", "dbSNP144\n(Jun 2015)"]
current_pct = [2506 / 2894 * 100, 2725 / 2894 * 100]
stale_pct2 = [369 / 2894 * 100, 75 / 2894 * 100]
ambiguous_pct = [0 / 2894 * 100, 63 / 2894 * 100]
absent_pct = [19 / 2894 * 100, 31 / 2894 * 100]

x = range(len(labels))
bottom = [0, 0]
segments = [
    ("Current (up to date)", current_pct, GOOD),
    ("Stale (retired rsID)", stale_pct2, CRITICAL),
    ("Ambiguous (both IDs present)", ambiguous_pct, OTHER_GRAY),
    ("Position absent", absent_pct, ABSENT_GRAY),
]

for name, vals, color in segments:
    ax.bar(list(x), vals, bottom=bottom, width=0.45, color=color, label=name, zorder=3)
    bottom = [b + v for b, v in zip(bottom, vals)]

# Both stale-segment labels use the SAME style (outside, above the bar, dark
# ink) regardless of segment size, so the two bars read consistently rather
# than switching between an inside-white and an outside-dark label.
cum_top = [current_pct[i] + stale_pct2[i] for i in range(2)]
cum_top_ambig = [cum_top[i] + ambiguous_pct[i] for i in range(2)]

for i in range(2):
    if ambiguous_pct[i] >= 1:
        # both a stale and an ambiguous label apply to this bar (dbSNP144):
        # stack them explicitly, ambiguous label on top, with enough vertical
        # gap that they never collide regardless of segment thickness.
        ax.annotate(
            f"{stale_pct2[i]:.2f}%", xy=(i, cum_top_ambig[i]),
            xytext=(0, 24), textcoords="offset points",
            ha="center", va="bottom", fontsize=11, color=INK_PRIMARY, fontweight="bold",
        )
        ax.annotate(
            f"{ambiguous_pct[i]:.2f}%", xy=(i, cum_top_ambig[i]),
            xytext=(0, 6), textcoords="offset points",
            ha="center", va="bottom", fontsize=9.5, color=INK_SECONDARY, fontweight="bold",
        )
    else:
        ax.annotate(
            f"{stale_pct2[i]:.2f}%", xy=(i, cum_top[i]),
            xytext=(0, 6), textcoords="offset points",
            ha="center", va="bottom", fontsize=11, color=INK_PRIMARY, fontweight="bold",
        )

ax.set_xticks(list(x))
ax.set_xticklabels(labels, color=INK_SECONDARY, fontsize=TICK_FONTSIZE)
ax.set_ylim(0, 112)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.set_ylabel("% of the 2,894 tested variants", color=INK_SECONDARY, fontsize=AXIS_LABEL_FONTSIZE)
ax.tick_params(axis="x", colors=INK_SECONDARY, labelsize=TICK_FONTSIZE)
ax.tick_params(axis="y", colors=INK_MUTED, labelsize=TICK_FONTSIZE)
ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)
strip_spines(ax, keep=("bottom",))
ax.legend(
    loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4, frameon=False,
    fontsize=8.5, labelcolor=INK_SECONDARY,
)

fig.tight_layout()
savefig_transparent(fig, "figure2_composition_breakdown.png")
plt.close(fig)

print("Saved figure1_stale_rate_by_vintage.png and figure2_composition_breakdown.png")
