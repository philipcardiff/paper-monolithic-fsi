#!/usr/bin/env python3
"""Schematic of the collapsibleChannel geometry (not to scale vertically)."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams.update({"font.size": 8, "mathtext.fontset": "cm"})
INK = "#222222"
fig, ax = plt.subplots(figsize=(6.3, 1.9))
H, hw = 1.0, 0.25  # channel width; wall thickness drawn exaggerated (true 0.05)
ax.plot([0, 25], [0, 0], color=INK, lw=1.4)
ax.plot([0, 5], [H, H], color=INK, lw=1.4)
ax.plot([15, 25], [H, H], color=INK, lw=1.4)
ax.add_patch(Rectangle((5, H), 10, hw, facecolor="#c9dcf0", edgecolor=INK, lw=1.0))
ax.plot([0, 0], [0, H], color=INK, lw=0.8, ls="--")
ax.plot([25, 25], [0, H], color=INK, lw=0.8, ls="--")
for x in (6, 8, 10, 12, 14):
    ax.add_patch(FancyArrowPatch((x, H + hw + 0.45), (x, H + hw + 0.03),
                                 arrowstyle="-|>", mutation_scale=7, color=INK, lw=0.8))
ax.text(10, H + hw + 0.55, r"$p_{ext}(t)$", ha="center", va="bottom")
ax.plot(10, H, "o", color=INK, ms=3.5)
ax.text(10.25, H - 0.2, "wall midpoint", va="top", fontsize=7)
ax.text(-0.4, 0.5, r"$p_{in}$", ha="right", va="center")
ax.text(25.4, 0.5, r"$p = 0$", ha="left", va="center")
ax.text(19, 0.5, "fluid", ha="center", va="center")
ax.text(10, H + hw / 2, "elastic wall", ha="center", va="center", fontsize=7)
ax.text(2.5, -0.12, "rigid", ha="center", va="top", fontsize=7)
def dim(x0, x1, y, lab):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="<|-|>", mutation_scale=6, color=INK, lw=0.6))
    ax.text((x0 + x1) / 2, y - 0.08, lab, ha="center", va="top")
dim(0, 5, -0.45, r"$L_{up} = 5$")
dim(5, 15, -0.45, r"$L = 10$")
dim(15, 25, -0.45, r"$L_{down} = 10$")
ax.add_patch(FancyArrowPatch((27.6, 0), (27.6, H), arrowstyle="<|-|>", mutation_scale=6, color=INK, lw=0.6))
ax.text(27.9, 0.5, r"$a = 1$", va="center")
ax.set_xlim(-2.5, 30.5); ax.set_ylim(-1.0, 2.1); ax.axis("off")
fig.tight_layout()
fig.savefig(sys.argv[1])
