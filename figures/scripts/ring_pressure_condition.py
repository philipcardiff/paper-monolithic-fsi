"""ringAddedMass, quasi-monolithic: effect of the interface pressure condition.
(a) wet/dry frequency-ratio error and (b) amplitude loss per period against
mesh factor at 100 steps per period, moderate and strong levels, normal-momentum
gradient against zero gradient, with the dry ring in (b).
Data: paper-data/ring_pressure_condition.csv (evidence/m-runs-a-rfix, qois.csv,
runs 1a and 1b, solids4foam 1252bd2e5)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(root / "paper-data/ring_pressure_condition.csv")))
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 3.0), constrained_layout=True)
colour = {"moderate": "tab:blue", "strong": "tab:red"}
style = {"normalMomentum": dict(marker="o", ls="-", label="normal momentum"),
         "zeroGradient": dict(marker="s", ls="--", mfc="white", label="zero gradient")}


def series(level, bc, col):
    rs = sorted((int(r["factor"]), float(r[col]) * 100) for r in rows
                if r["level"] == level and r["pressure_bc"] == bc)
    return [f for f, _ in rs], [v for _, v in rs]


for lvl, c in colour.items():
    for bc, kw in style.items():
        kw = dict(kw, label=f"{kw['label']}, {lvl}")
        f, e = series(lvl, bc, "ratio_rel_error")
        ax[0].loglog(f, [abs(x) for x in e], color=c, ms=4, lw=1, **kw)
        f, l = series(lvl, bc, "loss_per_period")
        # A negative loss (amplitude growth) is drawn by its magnitude with an open marker
        ax[1].loglog(f, [abs(x) for x in l], color=c, ms=4, lw=1, **kw)
        for fi, li in zip(f, l):
            if li < 0:
                ax[1].plot(fi, -li, marker="o", ms=7, mfc="none", mec="k", mew=0.6)
f, l = series("dry", "", "loss_per_period")
ax[1].loglog(f, l, color="k", marker="x", lw=1, ms=5, label="dry ring")
for a, y0, s, txt, yt in ((ax[0], 5e-1, 1, "slope 1", 2.2e-1), (ax[0], 4e-2, 2, "slope 2", 4e-3)):
    a.loglog([1, 4], [y0, y0 / 4**s], color="0.4", lw=0.7, ls=":")
    a.text(2.3, yt, txt, fontsize=7, color="0.3")
ax[0].set(xlabel="mesh refinement factor", ylabel="|ratio error| (%)", title="(a)")
ax[1].set(xlabel="mesh refinement factor", ylabel="|amplitude loss per period| (%)", title="(b)")
for a in ax:
    a.set_xticks([1, 2, 4]); a.set_xticklabels(["1", "2", "4"]); a.minorticks_off()
ax[0].legend(fontsize=6, frameon=False, loc="lower left")
ax[1].legend(fontsize=6, frameon=False, loc="center")
fig.savefig(root / "figures/ringAddedMass-pressure-condition.pdf")
