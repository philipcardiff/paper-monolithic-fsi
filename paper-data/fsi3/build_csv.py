#!/usr/bin/env python3
"""Write paper-data/fsi3_runs.csv: one row per fsi3g run with the benchmark
statistics (qoi.csv, window 5-6 s; the 2x solid check 4.5-5.5 s), their
errors against Featflow level 4, and cost and iteration counts over the
coupled phase 2-6 s and the window (cost.py)."""
import csv
import json
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1])
cost = runpy.run_path(str(HERE / "cost.py"), run_name="lib")
window = cost["window"]
REF = json.load(open(
    "/Volumes/OpenFOAM/philipc-v2512/solids4foam.development/tutorials/"
    "fluidSolidInteraction/TurekHron2006/verification/reference/"
    "HronTurek_verification_references.json"))["references"]
CELLS = {1: 96712, 2: 194183, 3: 387219}
SOLID = {1: (430, 24), 2: (608, 34), 3: (860, 48)}
Q = ["ux_mean", "ux_amplitude", "uy_mean", "uy_amplitude", "uy_frequency",
     "drag_mean", "drag_amplitude", "lift_mean", "lift_amplitude"]

rows = []
for r in csv.DictReader(open(HERE / "qoi.csv")):
    run = r["run"]
    if run == "qm_2" and r["t0"] == "4.5":
        run_label = "qm_2_w45"
    else:
        run_label = run
    env = dict(line.split("=", 1) for line in
               open(HERE / "runs" / run / "case.env").read().split("\n") if "=" in line)
    level = int(env["LEVEL"])
    t0, t1 = float(r["t0"]), float(r["t1"])
    out = {"run": run_label, "coupling": "QM" if run.startswith("qm") else "IQN-ILS",
           "level": level, "fluid_cells": CELLS[level],
           "solid_cells": SOLID[level][0] * SOLID[level][1] * (4 if "sf2" in run else 1),
           "dt_s": float(env["DT"]), "ranks": int(env["RANKS"]),
           "window_s": f"{t0:g}-{t1:g}"}
    for q in Q:
        v = float(r[q])
        out[q] = f"{v:.6g}"
        ref = REF[q]["value"]
        out[q + "_err"] = f"{(v - ref) / abs(ref):.5f}"
    w = window(run, t0, t1)
    c = window(run, 2.0, min(6.0, t1))
    out["core_h_per_s_window"] = f"{w['core_h_per_s']:.4g}"
    out["core_h_per_s_coupled"] = f"{c['core_h_per_s']:.4g}"
    out["wall_s_per_step_window"] = f"{w['wall_per_step']:.4g}"
    out["wall_s_per_step_coupled"] = f"{c['wall_per_step']:.4g}"
    out["newton_per_step"] = f"{w.get('newton', float('nan')):.3g}"
    out["krylov_per_newton"] = f"{w.get('krylov_per_newton', float('nan')):.3g}"
    out["coupling_its_per_step"] = f"{w.get('iqn', float('nan')):.3g}"
    rows.append(out)

with open(OUT, "w", newline="") as h:
    h.write("# Hron-Turek FSI3, fsi3g runs (MeluXina, solids4foam a421f063d, qm-a421 build).\n"
            "# Statistics over the window (driver periodic_statistics); errors relative to\n"
            "# Featflow level 4 (TurekHron2006/verification/reference). Cost: elapsed\n"
            "# core-hours per simulated second, side-by-side runs on one exclusive\n"
            "# 128-core node per level (indicative; start-up step of each job excluded).\n")
    w = csv.DictWriter(h, list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print(OUT, len(rows))
