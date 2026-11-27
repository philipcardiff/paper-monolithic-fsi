"""Solid block of the preconditioning matrix on the collapsible-channel wall: (a) the smallest eigenvalues of
P0^{-1} J_ss, the compact block P0 against the Jacobian J_ss of the solid residual, for walls of thickness
h = 0.2-0.025 m (E h^3 fixed) and for h = 0.05 m with E x 8 and with dt x 4; (b) the eigenvector of the
smallest eigenvalue for the paper's wall (h = 0.05 m), drawn on the wall cells: vertical component along the
wall at mid-thickness and horizontal component across the thickness at the quarter point.
Data: paper-data/solid_block/spectrum.csv, slow_mode.csv (step-1 states of the coarse wall, 80 x 8 cells)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
root = Path(__file__).resolve().parents[2]
d = root / "paper-data/solid_block"
rows = [r for r in csv.DictReader(l for l in open(d / "spectrum.csv") if not l.startswith("#"))]
mode = [r for r in csv.DictReader(l for l in open(d / "slow_mode.csv") if not l.startswith("#"))]
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 3, figsize=(6.0, 2.5), constrained_layout=True, gridspec_kw={"width_ratios": [1.25, 1.25, 0.7]})
series = [("h0.2", "$L/h = 50$", dict(color="tab:green", marker="o")),
          ("h0.1", "$L/h = 100$", dict(color="tab:blue", marker="s")),
          ("h0.05", "$L/h = 200$ (paper)", dict(color="k", marker="^")),
          ("h0.025", "$L/h = 400$", dict(color="tab:red", marker="v")),
          ("h0.05_E8", "$L/h = 200$, $E\\times 8$", dict(color="0.45", marker="x", ls="--")),
          ("h0.05_dt4", "$L/h = 200$, $\\Delta t\\times 4$", dict(color="0.45", marker="+", ls=":"))]
for case, label, kw in series:
    ev = sorted(float(r["re"]) for r in rows if r["case"] == case)[:40]
    ax[0].semilogy(range(1, len(ev) + 1), ev, label=label, **dict(dict(ms=2.5, lw=0.8, mfc="none"), **kw))
ax[0].set(xlabel="eigenvalue index (ascending)", ylabel=r"$\lambda(\mathbf{P}_0^{-1}\mathbf{J}_{ss})$",
          title="(a) smallest eigenvalues", ylim=(5e-5, 2))
ax[0].legend(fontsize=6, frameon=False, loc="lower right")
j_mid = 3  # one of the two cell rows next to mid-thickness (8 cells across)
xs = [float(r["x"]) for r in mode if int(r["j"]) == j_mid]
uy = [float(r["uy"]) for r in mode if int(r["j"]) == j_mid]
ax[1].plot(xs, uy, color="k", lw=1.2, label="$u_y$, mid-thickness")
ax[1].set(xlabel="$x$ (m)", ylabel="mode component", title="(b) slowest mode, $L/h = 200$", ylim=(-1.15, 1.3))
i_q = 20  # quarter point x = 7.5 m
ys = [float(r["y"]) for r in mode if int(r["i"]) == i_q]
ux = [float(r["ux"]) for r in mode if int(r["i"]) == i_q]
uyq = [float(r["uy"]) for r in mode if int(r["i"]) == i_q]
eta = [(y - 1) / 0.05 for y in ys]
ax[2].plot([u / max(abs(v) for v in ux) for u in ux], eta, color="tab:red", lw=1, marker=".", ms=3, label="$u_x$")
ax[2].plot([u / max(abs(v) for v in uyq) for u in uyq], eta, color="tab:blue", lw=1, ls="--", label="$u_y$")
ax[2].axvline(0, color="0.7", lw=0.5)
ax[2].set(xlabel="normalised", ylabel="$(y - 1)/h$", title="(c) at $x = 7.5$ m", xlim=(-1.15, 1.15))
ax[2].legend(fontsize=6, frameon=False, loc="lower left")
ax[1].legend(fontsize=6, frameon=False, loc="lower left")
fig.savefig(root / "figures/solid-block-spectrum.pdf")
