"""blobInTreacle temporal self-convergence at t = 1 s, factor-1 mesh: successive
change in u_x(A) and in the l2 norm of the interface position against the time
step, quasi-monolithic (snes_rtol = snes_stol = 1e-8, ksp_rtol 1e-6) and IQN-ILS
(strict test, 1e-6). Data: paper-data/blob_time_{qm,iqn}.csv, written by the
tutorial driver (verification/Allverify --study time) at solids4foam a421f063d."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 2.8), constrained_layout=True)
for cpl, name, kw in (("qm", "quasi-monolithic", dict(marker="o", ls="-", color="tab:blue")),
                      ("iqn", "IQN-ILS", dict(marker="s", ls="--", mfc="white", color="tab:red"))):
    rows = [r for r in csv.DictReader(open(root / f"paper-data/blob_time_{cpl}.csv"))
            if r["dx_change_m"] != "nan"]
    dt = [float(r["delta_t_s"]) for r in rows]
    for a, key in zip(ax, ("dx_change_m", "interface_change_m")):
        a.loglog(dt, [float(r[key]) for r in rows], ms=4, lw=1, label=name, **kw)
for a, lab in zip(ax, (r"change in $u_x$(A) (m)", r"change in interface position (m)")):
    x = [0.03125, 0.125]
    y0 = 3e-6 if lab.startswith("change in $u") else 1.5e-5
    a.loglog(x, [y0, y0 * 16], color="0.4", lw=0.8)
    a.text(0.05, y0 * 5, "2", fontsize=7, color="0.4")
    a.set_xlabel(r"$\Delta t$ (s)")
    a.set_xticks([0.015625, 0.03125, 0.0625, 0.125])
    a.set_xticklabels(["1/64", "1/32", "1/16", "1/8"])
    a.minorticks_off()
    a.set_ylabel(lab)
ax[0].legend(frameon=False)
ax[0].set_title("(a)", loc="left", fontsize=8)
ax[1].set_title("(b)", loc="left", fontsize=8)
fig.savefig(root / "figures/blobInTreacle-time.pdf")
