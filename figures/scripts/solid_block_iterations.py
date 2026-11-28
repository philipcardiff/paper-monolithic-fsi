"""Krylov iterations per Newton iteration of the quasi-monolithic coupling on the collapsible channel (fluid level 1,
dt = 0.00625 s, t <= 0.15 s, paper solver settings) with the compact solid block and with the coloured
finite-difference solid block: (a) against the wall slenderness L/h, with E h^3 fixed (series A: fixed cell aspect
ratio; series B: 80 x 8 wall cells); (b) against a factor on Young's modulus at L/h = 200.
Data: paper-data/solid_block/slenderness.csv."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mt
root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(l for l in open(root / "paper-data/solid_block/slenderness.csv") if not l.startswith("#")))
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 2.6), constrained_layout=True)
style = {"compact": dict(color="tab:red", label="compact block"),
         "colouredFD": dict(color="tab:blue", label="finite-difference block")}
for blk, kw in style.items():
    for series, ls, mk in (("A", "-", "o"), ("B", "--", "s")):
        pts = sorted((float(r["L_over_h"]), float(r["krylov_per_newton"])) for r in rows
                     if r["study"] == "slenderness" and r["series"] == series and r["solid_block"] == blk)
        ax[0].loglog(*zip(*pts), ls=ls, marker=mk, ms=3, lw=1, mfc="white" if series == "B" else None,
                     color=kw["color"], label=f"{kw['label']}, series {series}")
    pts = sorted((float(r["E_factor"]), float(r["krylov_per_newton"])) for r in rows
                 if r["study"] == "stiffness" and r["solid_block"] == blk)
    ax[1].semilogx(*zip(*pts), marker="o", ms=3, lw=1, color=kw["color"], label=kw["label"])
ax[0].set(xlabel="$L/h$", ylabel="Krylov iterations per Newton iteration", title="(a) wall slenderness")
ax[0].xaxis.set_major_formatter(mt.ScalarFormatter()); ax[0].xaxis.set_minor_formatter(mt.NullFormatter())
ax[0].set_xticks([50, 100, 200, 400])
ax[0].legend(fontsize=6, frameon=False, loc="center right")
ax[1].set(xlabel="factor on $E$ ($L/h = 200$)", title="(b) wall stiffness", yscale="log")
ax[1].set_xticks([0.125, 1, 8]); ax[1].set_xticklabels(["1/8", "1", "8"]); ax[1].xaxis.set_minor_formatter(mt.NullFormatter())
for a in ax:
    a.set_ylim(15, 700)
    a.set_yticks([20, 50, 100, 200, 500]); a.yaxis.set_major_formatter(mt.ScalarFormatter()); a.yaxis.set_minor_formatter(mt.NullFormatter())
ax[1].legend(fontsize=6, frameon=False, loc="center right")
fig.savefig(root / "figures/solid-block-iterations.pdf")
