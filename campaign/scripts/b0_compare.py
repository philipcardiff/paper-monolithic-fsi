#!/usr/bin/env python3
"""B0: compare QoIs of the smoke runs (serial against 4 ranks, repeats).

Usage: b0_compare.py <runs/b0>

ringAddedMass: max |Dy(t)| difference over the whole history of
solidPointDisplacement_pointDispY, relative to max |Dy|.
cavityFlexibleBottom: final Dy of solidPointDisplacement_pointDisp and final
total y force on the plate, with relative differences to the serial run.
Prints one CSV row per run.
"""

import os
import sys


def table(path):
    rows = []
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        rows.append([float(v) for v in line.replace("(", " ")
                     .replace(")", " ").split()])
    return rows


def main():
    root = sys.argv[1]
    print("run_id,qoi,value,ref_run,rel_diff")
    ref = {}
    # Serial runs first, so they are the reference
    for run in sorted(os.listdir(root), key=lambda r: ("-s1" not in r, r)):
        d = os.path.join(root, run)
        pp = os.path.join(d, "postProcessing")
        if "-ram-" in run:
            dy = [r[2] for r in table(os.path.join(
                pp, "0", "solidPointDisplacement_pointDispY.dat"))]
            key = "ram"
            if key not in ref:
                ref[key] = (run, dy)
            rname, rdy = ref[key]
            scale = max(abs(v) for v in rdy)
            diff = max(abs(a - b) for a, b in zip(dy, rdy)) / scale
            print("%s,ram_Dy_history_maxdiff,%.9g,%s,%.3e"
                  % (run, dy[-1], rname, diff))
        elif "-cav-" in run:
            dy = table(os.path.join(
                pp, "0", "solidPointDisplacement_pointDisp.dat"))[-1][2]
            fy = table(os.path.join(
                pp, "fluid", "forces", "0", "force.dat"))[-1][2]
            key = "cav"
            if key not in ref:
                ref[key] = (run, dy, fy)
            rname, rdy, rfy = ref[key]
            print("%s,cav_Dy_final,%.9g,%s,%.3e"
                  % (run, dy, rname, (dy - rdy) / abs(rdy)))
            print("%s,cav_Fy_final,%.9g,%s,%.3e"
                  % (run, fy, rname, (fy - rfy) / abs(rfy)))


if __name__ == "__main__":
    main()
