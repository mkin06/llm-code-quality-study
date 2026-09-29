#!/usr/bin/env python3
"""
07_figure1_annotated.py
Regenerates Fig. 1 (ACS by prompt level) with the annotations promised in
its caption: the median printed above each box and significance brackets
(*** = Bonferroni-corrected p < 0.001) for all six pairwise comparisons.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(ROOT, "results")
FIG_DIR = os.path.join(RESULTS_DIR, "figures")

df = pd.read_csv(os.path.join(RESULTS_DIR, "full_dataset.csv"))
pw = pd.read_csv(os.path.join(RESULTS_DIR, "rq1_pairwise.csv"))
order = ["P0", "P1", "P2", "P3"]
colors = ["#e74c3c", "#f39c12", "#3498db", "#2ecc71"]
data = [df.loc[df.prompt_level == l, "acs"].values for l in order]

fig, ax = plt.subplots(figsize=(8, 6.2))
bp = ax.boxplot(data, positions=range(4), widths=0.5, patch_artist=True,
                medianprops=dict(color="black", linewidth=1.6))
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c); patch.set_alpha(0.75)

# median labels above each box
for i, d in enumerate(data):
    ax.text(i, d.max() + 0.15, f"Mdn = {np.median(d):.1f}", ha="center", va="bottom",
            fontsize=10, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.6", alpha=0.9))

# significance brackets (all six pairs Bonferroni p < 0.001 -> ***)
def star(p):
    if isinstance(p, str) and p.startswith("<"): return "***"
    p = float(p)
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "n.s."

pairs = [("P0","P1"), ("P1","P2"), ("P2","P3"), ("P0","P2"), ("P1","P3"), ("P0","P3")]
ymax = max(d.max() for d in data)
h, gap = 0.28, 0.62
y = ymax + 0.95
for (a, b) in pairs:
    i, j = order.index(a), order.index(b)
    p = pw.loc[pw.pair == f"{a} vs {b}", "p_value_corrected"].iloc[0]
    ax.plot([i, i, j, j], [y, y + h, y + h, y], lw=1.1, color="black")
    ax.text((i + j) / 2, y + h + 0.03, star(p), ha="center", va="bottom", fontsize=10)
    y += gap

ax.set_ylim(-0.4, y + 0.3)
ax.set_xticks(range(4))
ax.set_xticklabels(["P0\n(Baseline)", "P1\n(Basic)", "P2\n(Patterns)", "P3\n(Clean+SOLID)"])
ax.set_ylabel("Architecture Conformance Score (0-10)")
ax.set_xlabel("Prompt Constraint Level")
ax.set_title("RQ1: ACS Distribution by Prompt Level")
ax.grid(True, axis="y", alpha=0.3)
plt.tight_layout()
out = os.path.join(FIG_DIR, "rq1_boxplot_acs.png")
plt.savefig(out, dpi=200)
print("saved", out)
