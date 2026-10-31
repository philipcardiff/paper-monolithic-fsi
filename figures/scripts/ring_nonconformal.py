"""ringAddedMass, quasi-monolithic, 100 steps per period, strong level:
(a) largest relative imbalance of the total interface force over the run and
(b) relative error of the wet/dry frequency ratio, against mesh factor, for a
conformal interface (direct map) and for solid interfaces coarser and finer
than the fluid interface with interpolated and conservative traction transfer.
Data: paper-data/ring_nonconformal.csv (MeluXina 5407040, solids4foam
a421f063d, interfaceFluxDiagnostics yes)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
rows = [r for r in csv.DictReader(open(root / "paper-data/ring_nonconformal.csv"))
        if r["level"] == "strong"]
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 3.0), constrained_layout=True)
series = [("conformal", "directMap", "conformal", dict(color="k", marker="x", ms=5)),
          ("coarser", "interp", "coarser solid, interpolated", dict(color="tab:blue", marker="s", mfc="white")),
          ("coarser", "cons", "coarser solid, conservative", dict(color="tab:blue", marker="s", ls="--")),
          ("finer", "interp", "finer solid, interpolated", dict(color="tab:red", marker="o", mfc="white")),
          ("finer", "cons", "finer solid, conservative", dict(color="tab:red", marker="o", ls="--"))]
for si, tr, label, kw in series:
    rs = sorted((int(r["factor"]), r) for r in rows
                if r["solid_interface"] == si and r["transfer"] == tr)
    f = [x for x, _ in rs]
    kw = dict(dict(ms=4, lw=1), **kw)
    ax[0].semilogy(f, [float(r["rel_imbalance_max"]) for _, r in rs], label=label, **kw)
    ax[1].semilogy(f, [abs(float(r["ratio_rel_error"])) * 100 for _, r in rs], label=label, **kw)
ax[0].set(xscale="log", xlabel="mesh refinement factor", ylabel="max relative force imbalance", title="(a)")
ax[1].set(xscale="log", xlabel="mesh refinement factor", ylabel="|ratio error| (%)", title="(b)")
for a in ax:
    a.set_xticks([1, 2, 4]); a.set_xticklabels(["1", "2", "4"]); a.minorticks_off()
ax[0].legend(fontsize=6, frameon=False, loc="center right")
fig.savefig(root / "figures/ringAddedMass-nonconformal.pdf")
