#!/usr/bin/env python3
"""Hessenthaler Phase I on the rF meshes: (a) tip deflection history,
(b) mean deformed centreline (t = 40-45 s) against MRI, (c, d) v_z on the line
x = 0 of the MRI planes z = 10 and 30 mm. Quasi-monolithic: blue, solid;
partitioned IQN-ILS: red, dashed; mesh rF0-rF2 from light to dark.
Data: paper-data/hessenthaler/*.csv; MRI data: solids4foam tutorial
hessenthalerFsi/validation/reference (Hessenthaler et al. 2017, CC0)."""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

root = Path(__file__).resolve().parents[2]
D = root / "paper-data/hessenthaler"
REF = Path(sys.argv[1]) if len(sys.argv) > 1 else D


def rows(path):
    return list(csv.DictReader(l for l in open(path) if not l.startswith("#")))


plt.rcParams.update({"font.size": 8, "font.family": "serif", "mathtext.fontset": "cm"})
STY = {"QM": dict(color=("#6baed6", "#2171b5", "#08306b"), ls="-", name="quasi-monolithic"),
       "P": dict(color=("#fb6a4a", "#cb181d", "#67000d"), ls="--", name="IQN-ILS")}
fig = plt.figure(figsize=(6.3, 4.4), constrained_layout=True)
gs = fig.add_gridspec(2, 6)
ax_a = fig.add_subplot(gs[0, :4]); ax_b = fig.add_subplot(gs[0, 4:])
ax_c = fig.add_subplot(gs[1, :3]); ax_d = fig.add_subplot(gs[1, 3:], sharey=None)
# (a)
hist = rows(D / "tip_history.csv")
t = [float(r["t"]) for r in hist]
for c in ("QM", "P"):
    for L in range(3):
        run = f"{c}_rF{L}"
        pts = [(ti, float(r[run])) for ti, r in zip(t, hist) if r[run]]
        if pts:
            ax_a.plot(*zip(*pts), lw=0.8, ls=STY[c]["ls"], color=STY[c]["color"][L], label=f"{STY[c]['name']}, rF{L}")
ax_a.axhline(16.41, color="0.35", lw=0.8, ls=":", label="measured (MRI)")
ax_a.axvspan(40, 45, color="0.92", lw=0, zorder=0)
ax_a.set_xlim(0, 45); ax_a.set_ylim(14.5, 19.5)
ax_a.set_xlabel("$t$ (s)"); ax_a.set_ylabel("tip deflection $u_y$ (mm)")
ax_a.legend(frameon=False, fontsize=6, ncol=3, loc="upper right")
ax_a.set_title("(a)", fontsize=8, loc="left")
# (b)
line = rows(D / "centreline.csv")
meas = rows(REF / "phaseI_centreline.csv")
ax_b.plot([float(m["z_mm"]) for m in meas], [float(m["y_mm"]) for m in meas], "o", ms=2.5, mfc="white", mec="0.35", mew=0.7, label="MRI")
for run, c, L in (("QM_rF0", "QM", 0), ("P_rF0", "P", 0), ("P_rF1", "P", 1)):
    pts = [(float(r["z_mm"]), float(r["y_mm"])) for r in line if r["run"] == run]
    if pts:
        ax_b.plot(*zip(*pts), lw=0.9, ls=STY[c]["ls"], color=STY[c]["color"][L], label=f"{'QM' if c == 'QM' else 'IQN-ILS'} rF{L}")
ax_b.set_xlabel("$z$ (mm)"); ax_b.set_ylabel("$y$ (mm)"); ax_b.legend(frameon=False, fontsize=6, loc="upper left")
ax_b.set_title("(b)", fontsize=8, loc="left")
# (c, d)
prof = rows(D / "profiles.csv")
runs = [k for k in prof[0] if k.startswith(("QM_", "P_"))]
for ax, z, lab in ((ax_c, "10", "(c) $z = 10$ mm"), (ax_d, "30", "(d) $z = 30$ mm")):
    p = sorted((r for r in prof if r["z_mm"] == z), key=lambda r: float(r["y_mm"]))
    y = [float(r["y_mm"]) for r in p]
    ax.plot(y, [float(r["vz_mri"]) for r in p], "o", ms=2.5, mfc="white", mec="0.35", mew=0.7, label="MRI")
    for run in runs:
        c, m = run.split("_"); L = int(m[-1])
        q = [(yy, float(r[run])) for yy, r in zip(y, p) if r[run]]
        ax.plot(*zip(*q), lw=0.9, ls=STY[c]["ls"], color=STY[c]["color"][L], label=f"{'QM' if c == 'QM' else 'IQN-ILS'} rF{L}")
    ax.set_xlabel("$y$ (mm)"); ax.set_ylabel("$v_z$ (mm/s)"); ax.set_title(lab, fontsize=8, loc="left")
ax_c.legend(frameon=False, fontsize=6, loc="upper center", bbox_to_anchor=(0.5, 0.92))
for ax in (ax_a, ax_b, ax_c, ax_d):
    ax.grid(True, color="0.9", lw=0.5)
fig.savefig(root / "figures/hessenthaler-results.pdf")
