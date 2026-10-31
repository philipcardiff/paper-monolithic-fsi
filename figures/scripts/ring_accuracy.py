"""ringAddedMass, quasi-monolithic: (a) wet/dry frequency-ratio error against
mesh factor at 100 steps per period; (b) amplitude loss per period against
steps per period on the factor-2 mesh, strong level, with the dry ring.
Data: paper-data/ring_monolithic_{mesh,runs}.csv (paper-fsi-verification,
branch ring-monolithic); Robin-Neumann from Table tab:ring_cost."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
mesh = list(csv.DictReader(open(root / "paper-data/ring_monolithic_mesh.csv")))
runs = list(csv.DictReader(open(root / "paper-data/ring_monolithic_runs.csv")))
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 3.0), constrained_layout=True)
colour = {"weak": "tab:green", "moderate": "tab:blue", "strong": "tab:red"}
for lvl, c in colour.items():
    for cpl, kw in (("monolithic", dict(marker="o", ls="-")),
                    ("iqnils", dict(marker="s", ls="--", mfc="white"))):
        rs = [r for r in mesh if f"_{lvl}_{cpl}_" in r["name"]]
        f = [int(r["factor"]) for r in rs]
        e = [abs(float(r["ratio_error"])) * 100 for r in rs]
        name = "quasi-monolithic" if cpl == "monolithic" else "IQN-ILS"
        ax[0].loglog(f, e, color=c, ms=4, lw=1, label=f"{name}, {lvl}", **kw)
ax[0].loglog([1, 4], [2e-3, 2e-3 / 16], color="0.4", lw=0.7, ls=":")
ax[0].text(2.2, 6e-4, "slope 2", fontsize=7, color="0.3")
ax[0].set(xlabel="mesh refinement factor", ylabel="|ratio error| (%)", title="(a)")
ax[0].set_xticks([1, 2, 4]); ax[0].set_xticklabels(["1", "2", "4"]); ax[0].minorticks_off()
ax[0].legend(fontsize=5.5, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.22))

def loss(pred):
    rs = sorted((int(r["steps"]), float(r["loss_per_period"]) * 100)
                for r in runs if r["factor"] == "2" and r["periods"] == "4" and pred(r))
    return [s for s, _ in rs], [l for _, l in rs]

s, l = loss(lambda r: r["kind"] == "dry")
ax[1].loglog(s, l, color="k", marker="x", lw=1, ms=5, label="dry ring")
s, l = loss(lambda r: r["level"] == "strong" and r["coupling"] == "monolithic")
ax[1].loglog(s, l, color="tab:red", marker="o", lw=1, ms=4, mfc="none", label="quasi-monolithic")
s, l = loss(lambda r: r["level"] == "strong" and r["coupling"] == "iqnils")
ax[1].loglog(s, l, color="tab:red", marker="s", ls="--", lw=1, ms=4, mfc="white", label="IQN-ILS")
ax[1].loglog([25, 50, 100], [2.59, 0.38, 0.062], color="tab:purple", marker="^", ls="-.", lw=1, ms=4,
             mfc="white", label="Robin–Neumann")
ax[1].set(xlabel="steps per period", ylabel="amplitude loss per period (%)", title="(b) strong level")
ax[1].set_xticks([25, 50, 100]); ax[1].set_xticklabels(["25", "50", "100"]); ax[1].minorticks_off()
ax[1].legend(fontsize=6, frameon=False, loc="lower left")
fig.savefig(root / "figures/ringAddedMass-accuracy.pdf")
