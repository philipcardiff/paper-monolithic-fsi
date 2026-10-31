"""cavityFlexibleBottom: quasi-monolithic minus Aitken (relative) in u_y(A)
and F_y against the cell size, with the skewCorrected (default) and linear
continuity-flux interpolation. Open markers: negative difference.
Data: paper-data/cavity_interp_vs_aitken.csv."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(root / "paper-data/cavity_interp_vs_aitken.csv")))
dx = {1: 0.1, 2: 0.05, 3: 0.025, 4: 0.0125}
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 2.6), constrained_layout=True, sharey=True)
style = {"skewCorrected linear": dict(color="tab:blue", label="skewCorrected (default)"),
         "linear": dict(color="tab:red", label="linear")}
for a, col, name in ((ax[0], "uy_diff_pct", "$u_y$(A)"), (ax[1], "fy_diff_pct", "$F_y$")):
    for interp, st in style.items():
        rs = [r for r in rows if r["interp"] == interp]
        x = [dx[int(r["level"])] for r in rs]
        y = [float(r[col]) for r in rs]
        a.loglog(x, [abs(v) for v in y], color=st["color"], lw=1, label=st["label"])
        for xi, yi in zip(x, y):
            a.loglog(xi, abs(yi), marker="o", ms=4, color=st["color"], mfc=st["color"] if yi > 0 else "white")
    a.loglog([0.1, 0.0125], [0.3, 0.3 / 8], color="0.4", lw=0.6, ls=":")
    a.loglog([0.1, 0.0125], [0.03, 0.03 / 64], color="0.4", lw=0.6, ls="--")
    a.set(xlabel="$\\Delta x$ (m)", title=name)
    a.invert_xaxis()
    a.set_xticks(list(dx.values())); a.set_xticklabels(["0.1", "0.05", "0.025", "0.0125"]); a.minorticks_off()
ax[0].text(0.07, 0.25, "slope 1", fontsize=7, color="0.3")
ax[0].text(0.07, 0.008, "slope 2", fontsize=7, color="0.3")
ax[0].set(ylabel="|QM $-$ Aitken| (%)")
ax[1].legend(fontsize=6.5, frameon=False, loc="lower left", title="open: negative", title_fontsize=6)
fig.savefig(root / "figures/cavityFlexibleBottom-consistency.pdf")
