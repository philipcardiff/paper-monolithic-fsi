#!/usr/bin/env python3
"""Per-step Newton histories of a quasi-monolithic solids4Foam log.

    ma_newton_hist.py LOG [--tmax T] > hist.csv

One row per Newton iterate of the monolithic momentum-continuity system:
time, iterate, SNES function norm, and the step's outcome.
"""
import argparse
import re

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--tmax", type=float, default=1e30)
a = ap.parse_args()
text = open(a.log, errors="replace").read()
print("time,iterate,fnorm,outcome")
for step in re.split(r"\nTime = ", text)[1:]:
    t = float(step.split("\n", 1)[0].split(",")[0])
    if t > a.tmax + 1e-12:
        break
    m = re.search(r"Solving the monolithic momentum-continuity system(.*?)"
                  r"Nonlinear solve ([^\n]*?) due to (\w+) iterations (\d+)",
                  step, re.S)
    if not m:
        continue
    for k, v in re.findall(r"^\s*(\d+) SNES Function norm ([0-9.eE+-]+)",
                           m.group(1), re.M):
        print(f"{t:g},{k},{v},{m.group(2).replace(' ', '_')}:{m.group(3)}")
