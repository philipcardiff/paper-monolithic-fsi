"""Newton residual against Newton iteration for one time step of the
quasi-monolithic coupling: (a) 3dTube level 2 (16 processes, second step
from the t = 5 ms state) and (b) ringAddedMass, moderate level, mesh factor 2,
100 steps per period (first step), with the matrix-free Newton operator
(Krylov tolerance 1e-4, the default, and 1e-8) and with the assembled
approximate Jacobian as the operator. snes_rtol 1e-10 and snes_stol 0, so no
run stops on the step-norm test. Data: paper-data/newton_histories.csv
(MeluXina 5407757 and 5407768, solids4foam a421f063d)."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(root / "paper-data/newton_histories.csv")))
plt.rcParams.update({"font.size": 8, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(6.0, 3.0), constrained_layout=True)
series = [("mf", "matrix-free, Krylov tol. $10^{-4}$", dict(color="k", marker="o")),
          ("mf-ksp1e-8", "matrix-free, Krylov tol. $10^{-8}$", dict(color="tab:blue", marker="s", mfc="white")),
          ("assembled", "assembled approximate Jacobian", dict(color="tab:red", marker=".", ls="--"))]
for a, (case, step, title) in zip(ax, (("tube", "2", "(a) 3dTube, level 2"),
                                       ("ring", "1", "(b) ring, moderate, factor 2"))):
    for v, label, kw in series:
        h = [(int(r["iterate"]), float(r["fnorm"])) for r in rows
             if r["case"] == f"{case}-{v}" and r["step"] == step]
        f0 = h[0][1]
        a.semilogy([k for k, _ in h], [f / f0 for _, f in h], label=label,
                   **dict(dict(ms=3, lw=1), **kw))
    a.axhline(1e-6, color="0.5", lw=0.6, ls=":")
    a.text(a.get_xlim()[1], 1.4e-6, "default tolerance", ha="right", fontsize=6, color="0.4")
    a.set(xlabel="Newton iteration", ylabel=r"$\|F_k\| / \|F_0\|$", title=title, ylim=(1e-15, 3))
ax[0].legend(fontsize=6, frameon=False, loc="upper right")
fig.savefig(root / "figures/newton-convergence.pdf")
