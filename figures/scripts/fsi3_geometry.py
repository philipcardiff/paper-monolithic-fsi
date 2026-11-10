#!/usr/bin/env python3
"""Hron-Turek FSI3: geometry and the level-1 fluid mesh of Section 7.

(a) the whole channel with the boundary conditions and dimensions (m), the
fluid mesh drawn under it; (b) the cylinder and flag, where the gmsh mesh
family is refined towards the flag tip. The flag is drawn as the solid
region (its own uniform mesh, 430 x 24 cells at level 1, is not drawn).

Usage: fsi3_geometry.py OUT.pdf PATH/TO/fluid/polyMesh
(the level-1 gmsh fluid mesh, ASCII; see paper-data/fsi3_runs.csv)."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mesh_layer import plane_faces  # noqa: E402

plt.rcParams.update({"font.size": 8, "font.family": "serif",
                     "mathtext.fontset": "cm"})
INK = "#222222"
SOLID = "#c9dcf0"
out, mesh = sys.argv[1], sys.argv[2]
polys = plane_faces(mesh, ("x", "y"))

fig = plt.figure(figsize=(6.3, 3.6))
ax = fig.add_axes([0.02, 0.50, 0.96, 0.48])
bx = fig.add_axes([0.10, 0.02, 0.80, 0.44])

for a, lw in ((ax, 0.08), (bx, 0.15)):
    a.add_collection(PolyCollection(polys, facecolors="none", edgecolors="0.62",
                                    linewidths=lw, rasterized=True))
    a.add_patch(Circle((0.2, 0.2), 0.05, facecolor="0.80", edgecolor=INK, lw=0.7, zorder=3))
    x0 = 0.2 + (0.05 ** 2 - 0.01 ** 2) ** 0.5
    a.add_patch(Rectangle((x0, 0.19), 0.6 - x0, 0.02, facecolor=SOLID,
                          edgecolor=INK, lw=0.7, zorder=4))
    a.plot(0.6, 0.2, "o", color=INK, ms=2.5, zorder=5)
    a.set_aspect("equal")
    a.axis("off")


def dim(a, p0, p1, lab, off, **kw):
    a.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<|-|>", mutation_scale=6,
                                color=INK, lw=0.6, shrinkA=0, shrinkB=0))
    a.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], lab,
           ha="center", va="center", **kw)


ax.plot([0, 2.5, 2.5, 0, 0], [0, 0, 0.41, 0.41, 0], color=INK, lw=0.9)
ax.set_xlim(-0.16, 2.62)
ax.set_ylim(-0.2, 0.52)
dim(ax, (0, -0.1), (2.5, -0.1), "2.5", (0, -0.045))
dim(ax, (-0.06, 0), (-0.06, 0.41), "0.41", (-0.055, 0))
ax.text(1.25, 0.44, "no slip", ha="center", va="bottom")
ax.text(1.25, -0.015, "no slip", ha="center", va="top")
ax.set_xlim(-0.16, 2.62)
ax.text(0.03, 0.36, "parabolic\ninflow", ha="left", va="top", fontsize=7)
ax.text(2.47, 0.36, "outlet\n$p = 0$", ha="right", va="top", fontsize=7)
ax.set_title("(a)", loc="left", fontsize=8)

bx.set_xlim(0.08, 0.72)
bx.set_ylim(0.11, 0.29)
bx.text(0.2, 0.2, "$r = 0.05$\n$(0.2, 0.2)$", ha="center", va="center",
        fontsize=6.5, zorder=6)
bx.text(0.42, 0.2, "flag $0.35 \\times 0.02$", ha="center", va="center",
        fontsize=7, zorder=6)
bx.text(0.607, 0.207, "A $(0.6, 0.2)$", ha="left", va="bottom", fontsize=7,
        zorder=6)
bx.set_title("(b)", loc="left", fontsize=8)
fig.savefig(out, dpi=600)
