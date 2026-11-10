#!/usr/bin/env python3
"""FSI3 (fsi3g runs): benchmark statistics with the TurekHron2006 verification
driver's own periodic_statistics, over a closing window, from the merged
restart segments of each run. Writes qoi.csv."""
import csv
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VER = Path("/Volumes/OpenFOAM/philipc-v2512/solids4foam.development/tutorials/"
           "fluidSolidInteraction/TurekHron2006/verification")
spec_ = importlib.util.spec_from_file_location(
    "htv", VER / "scripts/hron_turek_verification.py")
htv = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(htv)

REF = json.load(open(VER / "reference/HronTurek_verification_references.json"))
THICK = REF["thickness_m"]


def merged(run, rel, cols):
    """time -> row, later restart segments overriding earlier ones."""
    data = {}
    base = HERE / "runs" / run / "postProcessing"
    dirs = sorted((p for p in (base / rel).parent.parent.glob("*")
                   if p.is_dir() and p.name[0].isdigit()),
                  key=lambda p: float(p.name))
    for d in dirs:
        f = d / Path(rel).name
        if not f.exists():
            continue
        for fields in htv.numeric_rows(f):
            v = [float(x) for x in fields]
            data[round(v[0], 9)] = [v[i] for i in cols]
    t = sorted(data)
    return t, [data[k] for k in t]


def stats(run, t0, t1):
    td, d = merged(run, "0/solidPointDisplacement_pointDisp.dat", (1, 2))
    tf, f = merged(run, "fluid/forces/0/force.dat", (1, 2))
    if td[-1] < t1 - 1e-6:
        raise RuntimeError(f"{run} ends at {td[-1]}")
    sel = lambda t, v: zip(*[(a, b) for a, b in zip(t, v) if a <= t1 + 1e-9])
    td_, d_ = sel(td, d)
    tf_, f_ = sel(tf, f)
    td_, tf_ = list(td_), list(tf_)
    w = t1 - t0
    hist = {"ux": (td_, [x[0] for x in d_]), "uy": (td_, [x[1] for x in d_]),
            "drag": (tf_, [x[0] / THICK for x in f_]),
            "lift": (tf_, [x[1] / THICK for x in f_])}
    fund = htv.periodic_statistics(*hist["uy"], w)["crossings"]
    row = {"run": run, "t0": t0, "t1": t1}
    for q, (t, v) in hist.items():
        s = htv.periodic_statistics(t, v, w, fund)
        for k in ("mean", "amplitude", "frequency", "periods",
                  "early_amplitude", "late_amplitude"):
            row[f"{q}_{k}"] = s[k]
    return row


def main():
    rows = []
    runs = ["qm_1", "iqn_1", "qm_2", "iqn_2", "qm_3", "iqn_3",
            "qm_2_dt1e-4", "qm_2_dt2e-4"]
    for r in runs:
        rows.append(stats(r, 5.0, 6.0))
    # the 2x solid check ends at 5.548 s: compare it with qm_2 on 4.5-5.5 s
    for r in ("qm_2", "qm_2_sf2"):
        rows.append(stats(r, 4.5, 5.5))
    ref = {k: v["value"] for k, v in REF["references"].items()}
    keys = list(rows[0])
    with open(HERE / "qoi.csv", "w", newline="") as h:
        w = csv.DictWriter(h, keys)
        w.writeheader()
        w.writerows(rows)
    q = ["ux_mean", "ux_amplitude", "uy_amplitude", "uy_frequency",
         "drag_mean", "drag_amplitude", "lift_amplitude"]
    print("run window " + " ".join(q))
    for r in rows:
        print(r["run"], f"{r['t0']}-{r['t1']}", " ".join(
            f"{r[k]:.5g}({100*(r[k]-ref[k])/abs(ref[k]):+.2f}%)" for k in q))
    print("ref", " ".join(f"{ref[k]:.5g}" for k in q))
    print("periodicity (late/early amplitude - 1, %):")
    for r in rows:
        print(r["run"], " ".join(
            f"{q_}:{100*(r[q_+'_late_amplitude']/r[q_+'_early_amplitude']-1):+.2f}"
            for q_ in ("ux", "uy", "drag", "lift")))


if __name__ == "__main__":
    sys.exit(main())
