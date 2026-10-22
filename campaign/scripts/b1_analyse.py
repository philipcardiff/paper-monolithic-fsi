#!/usr/bin/env python3
"""B1: QoI differences, iterations, time and memory of the solid-PC windows.

Usage: b1_analyse.py <runs/b1> [--csv OUT]

Only the window counts: for cav and tube the steps after the spin-up's end
time t0 (b1_window.json), whether the run restarted there or ran from 0;
for the ring the whole run. For each case (ring, cav, tube) the iterative floor is the QoI difference
between S0 and S0tight at the same rank count. Every other configuration is
compared with S0tight at the same rank count (its QoI error) and with S0.

QoIs: the history of every column of the case's displacement monitors
(solidPointDisplacement*.dat), reduced to the largest difference over the
window relative to the largest |value| of that column in the reference run;
cav also the final total y force.
"""

import argparse
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_log import parse  # noqa: E402


def table(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        try:
            rows.append([float(v) for v in line.replace("(", " ")
                         .replace(")", " ").split()])
        except ValueError:
            pass
    return rows


def histories(run):
    """{name: {time: value}} for every displacement and force column."""
    out = {}
    for path in sorted(glob.glob(os.path.join(
            run, "postProcessing", "**", "solidPointDisplacement*.dat"),
            recursive=True)):
        name = os.path.basename(path)[len("solidPointDisplacement_"):-4]
        rows = table(path)
        for c in range(1, len(rows[0]) if rows else 1):
            col = {r[0]: r[c] for r in rows}
            if any(abs(v) > 0 for v in col.values()):
                out["%s[%d]" % (name, c)] = col
    for path in glob.glob(os.path.join(run, "postProcessing", "fluid",
                                       "forces", "*", "force.dat")):
        rows = table(path)
        out["Fy"] = {r[0]: r[2] for r in rows}
    return out


def window_stats(solved, t0):
    """Newton, Krylov and clock time over the steps after t0 (all steps if
    t0 is None)."""
    if t0 is None:
        before, win = [], solved
    else:
        before = [st for st in solved if float(st["time"]) <= t0 + 1e-12]
        win = [st for st in solved if float(st["time"]) > t0 + 1e-12]
    newton = [st["newton"] for st in win]
    ksp = sum(sum(st["ksp"]) for st in win)
    clocks = [st["clock_s"] for st in win if st["clock_s"] is not None]
    start = before[-1]["clock_s"] if before and before[-1]["clock_s"] \
        is not None else 0.0
    return {
        "n_steps": len(win),
        "iters_mean": round(sum(newton) / len(newton), 4) if newton else None,
        "ksp_per_newton_mean": round(ksp / sum(newton), 3)
        if newton and sum(newton) else None,
        "clock_s": round(clocks[-1] - start, 2) if clocks else None,
    }


def max_rel_diff(a, b):
    """Largest |a - b| over common times, relative to max |b|."""
    times = sorted(set(a) & set(b))
    if not times:
        return None
    scale = max(abs(b[t]) for t in times) or 1.0
    return max(abs(a[t] - b[t]) for t in times) / scale


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--csv")
    args = ap.parse_args()

    runs = {}
    for d in sorted(glob.glob(os.path.join(args.root, "b1-*-p*"))):
        name = os.path.basename(d)
        _, kind, config, p = name.split("-")
        meta = {}
        win = os.path.join(d, "b1_window.json")
        wmeta = json.load(open(win)) if os.path.isfile(win) else {}
        ddt_u = wmeta.get("ddt_U")
        t0 = wmeta.get("t0")
        if os.path.isfile(os.path.join(d, "run_meta.json")):
            meta = json.load(open(os.path.join(d, "run_meta.json")))
        log = os.path.join(d, "log.solids4Foam")
        s = window_stats(parse(log)[1], t0) if os.path.isfile(log) else {}
        meta["ddt_U"] = ddt_u
        h = histories(d)
        if t0 is not None:
            h = {k: {tt: v for tt, v in col.items() if tt > t0 + 1e-12}
                 for k, col in h.items()}
        runs[(kind, config, int(p[1:]))] = (name, d, s, meta, h)

    rows = []
    for (kind, config, ranks), (name, d, s, meta, h) in sorted(runs.items()):
        ref = runs.get((kind, "S0tight", ranks))
        s0 = runs.get((kind, "S0", ranks))
        diff_tight = diff_s0 = None
        if ref and ref[4] and h:
            diff_tight = max(filter(None, (max_rel_diff(h[k], ref[4][k])
                                           for k in h if k in ref[4])),
                             default=None)
        if s0 and s0[4] and h:
            diff_s0 = max(filter(None, (max_rel_diff(h[k], s0[4][k])
                                        for k in h if k in s0[4])),
                          default=None)
        n = s.get("n_steps") or 0
        clock = s.get("clock_s")
        rows.append({
            "run_id": name, "case": kind, "config": config, "ranks": ranks,
            "ddt_U": meta.get("ddt_U"),
            "n_steps": n, "newton_mean": s.get("iters_mean"),
            "ksp_per_newton": s.get("ksp_per_newton_mean"),
            "clock_s": clock,
            "clock_s_per_step": round(clock / n, 4) if clock and n else None,
            "peak_rss_sum_gb": meta.get("peak_rss_sum_gb"),
            "qoi_maxreldiff_vs_S0tight":
                "%.3e" % diff_tight if diff_tight is not None else "",
            "qoi_maxreldiff_vs_S0":
                "%.3e" % diff_s0 if diff_s0 is not None else "",
        })
    w = csv.DictWriter(open(args.csv, "w", newline="") if args.csv
                       else sys.stdout, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)


if __name__ == "__main__":
    main()
