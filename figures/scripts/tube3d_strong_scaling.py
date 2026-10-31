"""3dTube strong scaling (timing row 6b): wall time per step, parallel
efficiency from one NUMA domain (16 processes) and Krylov iterations per
Newton iteration. Data: paper-data/tube3d_strong_scaling.csv."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(root / "paper-data/tube3d_strong_scaling.csv")))
steps = 50
series = {}
for r in rows:
    series.setdefault((r["coupling"], r["level"]), []).append(r)

style = {"mono": dict(marker="o", ls="-", label="quasi-monolithic"),
         "robin": dict(marker="s", ls="--", mfc="white", label="Robin–Neumann")}
colour = {"L2": "tab:blue", "L3": "tab:red"}

plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.4), constrained_layout=True)
for (c, l), rs in sorted(series.items()):
    n = [int(r["ranks"]) for r in rs]
    t = [float(r["median_exec_s"]) / steps for r in rs]
    kw = dict(style[c], color=colour[l], ms=4, lw=1)
    kw["label"] = f"{kw['label']}, level {l[1]}"
    ax[0].loglog(n, t, **kw)
    t16 = t[n.index(16)]
    ideal = [x for x in n if x >= 16]
    ax[0].loglog(ideal, [t16 * 16 / x for x in ideal], color=colour[l], lw=0.6, ls=":")
    m = [x for x in n if x >= 16]
    ax[1].semilogx(m, [t16 * 16 / (t[n.index(x)] * x) for x in m], **kw)
    if c == "mono":
        ax[2].semilogx(n, [float(r["ksp_per_newton"]) for r in rs], **kw)

ax[0].axvspan(0.8, 16, color="0.92", zorder=0)
ax[0].text(1.1, 0.85, "one NUMA\ndomain", transform=ax[0].get_xaxis_transform(), fontsize=7, va="top")
ax[0].set(xlabel="processes", ylabel="ExecutionTime per step (s)", title="(a)")
ax[1].axhline(1.0, color="0.5", lw=0.6)
ax[1].set(xlabel="processes", ylabel="efficiency relative to 16 processes", ylim=(0, 1.3), xlim=(12, 170), title="(b)")
ax[2].set(xlabel="processes", ylabel="Krylov iterations per Newton it.", ylim=(0, 32), title="(c)")
for a in ax:
    ticks = [16, 32, 64, 128] if a is ax[1] else [1, 2, 4, 8, 16, 32, 64, 128]
    a.set_xticks(ticks)
    a.set_xticklabels([str(x) for x in ticks])
    a.minorticks_off() if a is not ax[0] else None
h, lab = ax[0].get_legend_handles_labels()
ax[2].legend(h, lab, fontsize=6, frameon=False, loc="lower right")
fig.savefig(root / "figures/3dTube-strong-scaling.pdf")
