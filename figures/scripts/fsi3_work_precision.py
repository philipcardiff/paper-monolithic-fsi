#!/usr/bin/env python3
"""Hron-Turek FSI3 work-precision: relative error against Featflow level 4
over the closing second (t = 5-6 s) against the cost in core-hours per
simulated second (average over the coupled phase, t = 2-6 s), mesh levels
1-3, quasi-monolithic (filled) and IQN-ILS (open). The grey band is the
3-5 % uncertainty of the reference amplitudes (companion paper).
Data: paper-data/fsi3_runs.csv."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

root = Path(__file__).resolve().parents[2]
rows = {r["run"]: r for r in csv.DictReader(
    line for line in open(root / "paper-data/fsi3_runs.csv")
    if not line.startswith("#"))}
plt.rcParams.update({"font.size": 8, "font.family": "serif",
                     "mathtext.fontset": "cm"})
panels = (("ux_mean", r"$u_x$(A) mean"), ("uy_amplitude", r"$u_y$(A) amplitude"),
          ("drag_amplitude", "drag amplitude"), ("lift_amplitude", "lift amplitude"))
fig, axes = plt.subplots(1, 4, figsize=(6.3, 2.2), sharey=True,
                         constrained_layout=True)
for ax, (q, title) in zip(axes, panels):
    ax.axhspan(3, 5, color="0.9", lw=0)
    for cpl, name, kw in (
            ("qm", "quasi-monolithic", dict(marker="o", ls="-", color="tab:blue")),
            ("iqn", "IQN-ILS", dict(marker="s", ls="--", mfc="white",
                                    color="tab:red"))):
        x = [float(rows[f"{cpl}_{L}"]["core_h_per_s_coupled"]) for L in (1, 2, 3)]
        y = [100 * abs(float(rows[f"{cpl}_{L}"][q + "_err"])) for L in (1, 2, 3)]
        ax.loglog(x, y, ms=4, lw=1, label=name, **kw)
        if cpl == "qm":
            for L, xi, yi in zip((1, 2, 3), x, y):
                ax.annotate(f"L{L}", (xi, yi), textcoords="offset points",
                            xytext=(3, -9), ha="left", fontsize=6.5,
                            color="tab:blue")
    ax.set_title(title, fontsize=8)
    ax.set_xlabel("core-hours per s")
    ax.set_ylim(0.1, 10)
    ax.grid(True, which="major", color="0.85", lw=0.5)
axes[0].set_ylabel("relative error (%)")
axes[0].legend(frameon=False, fontsize=6.5, loc="lower right")
fig.savefig(root / "figures/HronTurek3-work-precision.pdf")
