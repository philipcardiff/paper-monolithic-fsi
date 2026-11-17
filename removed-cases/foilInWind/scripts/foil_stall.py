#!/usr/bin/env python3
"""foilInWind at dt = 0.01 s: QM Newton and IQN-ILS coupling residuals per step.

    foil_stall.py newton_rf_qm_dt0.01.csv fsiResiduals_iqn_dt0.01.dat out.pdf
Data: evidence/m-runs-a-rfix 7a (QM) and evidence/m-runs-a 7a (IQN-ILS).
"""
import csv
import sys
from collections import OrderedDict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 8, "mathtext.fontset": "cm"})
qm = OrderedDict()
for r in csv.DictReader(open(sys.argv[1])):
    qm.setdefault(r["time"], []).append(float(r["fnorm"]))
iqn = OrderedDict()
for line in open(sys.argv[2]):
    p = line.split()
    if len(p) == 3 and p[0][0].isdigit():
        iqn.setdefault(p[0], []).append(float(p[2]))
fig, ax = plt.subplots(1, 2, figsize=(6.3, 2.5))
cmap = plt.get_cmap("viridis")
for i, (t, f) in enumerate(qm.items()):
    ax[0].semilogy(range(len(f)), [x / f[0] for x in f], "-o", ms=2, lw=1,
                   color=cmap(i / max(1, len(qm) - 1)), label=f"$t = {float(t):.2f}$ s")
ax[0].axhline(1e-4, color="0.5", ls=":", lw=0.8)
ax[0].set_xlabel("Newton iteration"); ax[0].set_ylabel("relative residual")
ax[0].set_title("(a) quasi-monolithic", loc="left", fontsize=8)
ax[0].legend(fontsize=6, frameon=False)
for i, (t, r) in enumerate(iqn.items()):
    ax[1].semilogy(range(1, len(r) + 1), r, "-o", ms=2, lw=1,
                   color=cmap(i / max(1, len(iqn) - 1)), label=f"$t = {float(t):.2f}$ s")
ax[1].axhline(1e-5, color="0.5", ls=":", lw=0.8)
ax[1].set_xlabel("coupling iteration"); ax[1].set_ylabel("interface residual")
ax[1].set_title("(b) IQN-ILS", loc="left", fontsize=8)
ax[1].legend(fontsize=6, frameon=False, ncol=2)
fig.tight_layout()
fig.savefig(sys.argv[3])
