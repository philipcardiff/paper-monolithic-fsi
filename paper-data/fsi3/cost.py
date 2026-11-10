#!/usr/bin/env python3
"""FSI3 fsi3g cost and iteration statistics from steps.txt over a window.

steps.txt columns: run log time dclock newton krylov iqn. A later log
overrides an earlier one at the same time (restarts repeat steps); the first
step of every log carries the start-up and is dropped."""
import collections
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RANKS = {"qm_1": 16, "iqn_1": 16, "qm_2": 24, "iqn_2": 24, "qm_3": 64,
         "iqn_3": 64, "qm_2_dt1e-4": 24, "qm_2_dt2e-4": 24, "qm_2_sf2": 24}

steps = collections.defaultdict(dict)
first = set()
seen = set()
for line in open(HERE / "steps.txt"):
    run, log, t, dc, nit, kry, iqn = line.split()
    key = (run, log)
    t = round(float(t), 9)
    if key not in seen:
        seen.add(key)
        first.add((run, log, t))
        steps[run][t] = None  # start-up step: dropped, but still overrides
        continue
    steps[run][t] = (float(dc), int(nit), int(kry), int(iqn))


def window(run, t0, t1):
    rows = [v for t, v in steps[run].items() if t0 < t <= t1 + 1e-9]
    n_all = len(rows)
    rows = [r for r in rows if r is not None]
    wall = sum(r[0] for r in rows) * n_all / len(rows)  # fill dropped steps
    out = {"steps": n_all, "wall_s": wall,
           "core_h_per_s": wall * RANKS[run] / 3600 / (t1 - t0),
           "wall_per_step": wall / n_all}
    if run.startswith("qm"):
        out["newton"] = sum(r[1] for r in rows) / len(rows)
        out["krylov_per_newton"] = sum(r[2] for r in rows) / max(1, sum(r[1] for r in rows))
    else:
        out["iqn"] = sum(r[3] for r in rows) / len(rows)
    return out


if __name__ == "__main__":
  for run in RANKS:
        for t0, t1 in ((5.0, 6.0), (4.0, 5.0), (2.0, 6.0)):
          if run == "qm_2_sf2" and t1 > 5.5:
              t0, t1 = 4.5, 5.5
          try:
              w = window(run, t0, t1)
          except ZeroDivisionError:
              continue
          print(run, f"{t0}-{t1}", " ".join(
              f"{k}={v:.4g}" for k, v in w.items()))
