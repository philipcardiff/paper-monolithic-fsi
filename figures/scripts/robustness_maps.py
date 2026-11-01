#!/usr/bin/env python3
# Paper variant of evidence/m-runs-b:paper-data/campaign/wp3/scripts/wp3_plot.py:
#   robustness_maps.py 3a/runs.csv,3a/qm618/runs.csv robustness-ring-map --map 3a
#   robustness_maps.py 3b/runs.csv,3b/qm618mm/runs.csv robustness-collapsible-map --map 3b
"""Draft robustness maps from runs.csv.

  wp3_plot.py runs.csv[,runs_qm618.csv] OUT_STEM --map 3a|3b

Each cell of the grid (3a: steps per period x added-mass level; 3b: time
step x density ratio) holds the four couplings side by side, in a fixed
order and shape: Aitken (square), IQN-ILS (triangle), Robin-Neumann
(diamond) open, quasi-monolithic (circle) filled. A run that passed is
drawn in ink and labelled with its mean iterations per step (coupling
iterations, or Newton iterations for QM); a failed run is drawn in red and
labelled with its failure class, so the status is never colour alone.
"""
import argparse
import csv
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#d9d8d4"
CRITICAL = "#d03b3b"
GRID_NA = "#a3a29c"  # not applicable (RN at a massless wall)
COUPLINGS = [("aitken", "Aitken", "s", False), ("iqn", "IQN-ILS", "^", False),
             ("rn", "Robin–Neumann", "D", False), ("qm", "Quasi-monolithic", "o",
                                                  True)]
CODE = {"cap": "cap", "newton": "Nwt", "mesh": "mesh", "nan": "NaN",
        "diverged": "div",
        "timeout": "t/o", "crash": "crash"}


def parse(run_id, which):
    if which == "3a":
        m = re.match(r"wp3-ram-(\w+?)-(\w+?)-n(\d+)(?:-r618(?:mm)?)?$", run_id)
        return m and (m.group(1), int(m.group(3)), m.group(2))
    m = re.match(r"wp3-coll-(\w+?)-dt([\d.e-]+?)-rho([\d.e-]+?)(?:-r618(?:mm)?)?$", run_id)
    return m and (m.group(1), float(m.group(2)), float(m.group(3)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs")
    ap.add_argument("out")
    ap.add_argument("--map", choices=("3a", "3b"), required=True)
    a = ap.parse_args()
    data = {}
    rows = []
    for f in a.runs.split(","):
        rows += list(csv.DictReader(open(f)))
    # Later files (e.g. the #618 QM reruns) replace earlier rows
    for r in rows:
        key = parse(r["run_id"], a.map)
        if key:
            data[key] = r
    if a.map == "3a":
        xs = [12, 25, 50, 100, 200]
        ys = ["weak", "moderate", "strong", "extended"]
        ylab = {"weak": "weak\n$\\mu = 0.1$", "moderate": "moderate\n$\\mu = 1$",
                "strong": "strong\n$\\mu = 10$", "extended": "extended\n$\\mu = 100$"}
        xlabel, ylabel = "Time steps per period", "Added-mass level"
        xtick = [str(x) for x in xs]
        title = "ringAddedMass, mesh 2, two periods"
    else:
        xs = [0.025, 0.0125, 0.00625, 0.003125]
        ys = [10.0, 1.0, 0.1, 0.01, 0.0]
        ylab = {y: f"{y:g}" for y in ys}
        xlabel, ylabel = r"$\Delta t$ (s)", r"$\rho_s/\rho_f$"
        xtick = [f"{x:g}" for x in xs]
        title = "collapsibleChannel, fluid L2, solid 640×8 (AMI), to t = 0.75 s"

    fig, ax = plt.subplots(figsize=(1.45 * len(xs) + 1.6,
                                    0.62 * len(ys) + 1.5))
    off = [-0.3, -0.1, 0.1, 0.3]
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            for k, (c, _, marker, filled) in enumerate(COUPLINGS):
                r = data.get((c, x, y))
                if r is None:
                    continue
                ok = r["status"] == "pass"
                na = r["status"] == "n/a"
                col = INK if ok else (GRID_NA if na else CRITICAL)
                ax.plot(i + off[k], j, marker=marker, ms=8, mew=1.4,
                        color=col, mfc=col if filled else "none",
                        linestyle="none", zorder=3)
                label = (f"{float(r['iters_mean']):.0f}" if ok and
                         r["iters_mean"] else CODE.get(r["status"],
                                                       r["status"]))
                if na:
                    label = "n/a"
                ax.text(i + off[k], j - 0.3, label, ha="center", va="top",
                        fontsize=6.5, color=MUTED if ok or na else CRITICAL)
    ax.set_xticks(range(len(xs)), xtick)
    ax.set_yticks(range(len(ys)), [ylab[y] for y in ys])
    ax.set_xlim(-0.55, len(xs) - 0.45)
    ax.set_ylim(-0.75, len(ys) - 0.4)
    for i in range(len(xs) - 1):
        ax.axvline(i + 0.5, color=GRID, lw=0.8, zorder=0)
    for j in range(len(ys) - 1):
        ax.axhline(j + 0.5, color=GRID, lw=0.8, zorder=0)
    ax.tick_params(length=0, labelsize=8, colors=INK)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel(xlabel, fontsize=9, color=INK)
    ax.set_ylabel(ylabel, fontsize=9, color=INK)
    handles = [Line2D([], [], marker=m, ms=7, mew=1.4, color=INK,
                      mfc=INK if f else "none", linestyle="none", label=n)
               for _, n, m, f in COUPLINGS]
    handles.append(Line2D([], [], marker="o", ms=7, color=CRITICAL,
                          mfc="none", linestyle="none",
                          label="failed"))
    if a.map == "3b":
        handles.append(Line2D([], [], marker="D", ms=7, color=GRID_NA,
                              mfc="none", linestyle="none",
                              label="not applicable"))
    ax.legend(handles=handles, loc="upper center", ncol=6, fontsize=7,
              frameon=False, bbox_to_anchor=(0.5, -0.16 - 0.02 * len(ys)),
              handletextpad=0.2, columnspacing=1.0)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{a.out}.{ext}", dpi=200)
    print(f"{a.out}.pdf/png")


if __name__ == "__main__":
    main()
