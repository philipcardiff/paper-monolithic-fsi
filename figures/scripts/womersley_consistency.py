"""womersleyTube: quasi-monolithic minus Robin-Neumann before (open) and after
(filled) the traction correction, against mesh factor (200 steps per period)
and steps per period (factor-2 mesh); grey band: |IQN-ILS minus Robin-Neumann|.
Data: paper-data/womersley_consistency.csv (from the qois.csv of
evidence/m-runs-a, m-runs-a-rfix and m-runs-wp0)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(root / "paper-data/womersley_consistency.csv")))
val = {(r["cell"], r["qoi"]): r for r in rows}
qoi = {"wallMid_amp": ("wall amplitude", "o", "tab:red"),
       "wallMid_phase": ("wall phase (rad)", "s", "tab:blue"),
       "flow_amp": ("flow-rate amplitude", "^", "tab:green"),
       "attenuation": ("attenuation", "D", "tab:purple")}
panels = [("mesh refinement factor", [(1, "m1-n200"), (2, "m2-n200"), (4, "m4-n200")]),
          ("steps per period", [(50, "m2-n50"), (100, "m2-n100"), (200, "m2-n200"), (400, "m2-n400")])]
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 3.0), constrained_layout=True, sharey=True)
for a, (xlabel, cells) in zip(ax, panels):
    x = [c[0] for c in cells]
    band = [max(abs(float(val[(c, q)]["iqn_minus_rn"])) for q in qoi) for _, c in cells]
    a.fill_between(x, 1e-7, band, color="0.88", lw=0, label="|IQN-ILS $-$ RN| (max.)")
    for q, (lab, m, col) in qoi.items():
        before = [abs(float(val[(c, q)]["qm_before_minus_rn"])) for _, c in cells]
        after = [abs(float(val[(c, q)]["qm_after_minus_rn"])) for _, c in cells]
        a.loglog(x, before, color=col, marker=m, mfc="white", ls="--", lw=0.8, ms=4)
        a.loglog(x, after, color=col, marker=m, ls="-", lw=1, ms=4, label=lab)
    a.set_xticks(x); a.set_xticklabels([str(v) for v in x]); a.minorticks_off()
    a.set(xlabel=xlabel, ylim=(1e-6, 2e-3))
ax[0].set(ylabel="|QM $-$ Robin–Neumann|", title="(a) 200 steps per period")
ax[1].set(title="(b) factor-2 mesh")
from matplotlib.lines import Line2D
h, lab = ax[1].get_legend_handles_labels()
h += [Line2D([], [], color="0.3", marker="o", mfc="white", ls="--", lw=0.8, ms=4),
      Line2D([], [], color="0.3", marker="o", ls="-", lw=1, ms=4)]
lab += ["before the correction", "after the correction"]
fig.legend(h, lab, fontsize=6, frameon=False, loc="outside lower center", ncol=4)
fig.savefig(root / "figures/womersleyTube-consistency.pdf")
