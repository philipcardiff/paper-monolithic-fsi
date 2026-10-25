#!/usr/bin/env python3
"""One line per R4/R5 run: state, simulated time reached, steps, clock.

Usage (MeluXina):  qm_status.py RUN_DIR [RUN_DIR ...]
Reads qm_result.json when the run is finished, otherwise the tail of
log.solids4Foam (last 'Time =' and ClockTime lines only).
"""
import json
import re
import sys
from pathlib import Path


def tail(path, n=200000):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - n))
            return f.read().decode(errors="replace")
    except OSError:
        return ""


for d in map(Path, sys.argv[1:]):
    if not (d / "qm_run.json").is_file():
        continue
    run = json.loads((d / "qm_run.json").read_text())
    res = d / "qm_result.json"
    if res.is_file():
        r = json.loads(res.read_text())
        it, tm = r.get("iterations", {}), r.get("timing", {})
        print(f"{d.name:28s} {str(r.get('status')):10s} steps={it.get('n_steps')} "
              f"it={it.get('iters_mean') and round(it['iters_mean'], 2)} "
              f"s/step={tm.get('clock_s_per_step') and round(tm['clock_s_per_step'], 3)}"
              f"{' ERR ' + r['post_error'][:60] if r.get('post_error') else ''}")
        continue
    t = tail(d / "log.solids4Foam")
    times = re.findall(r"^Time = ([-+0-9.eE]+)$", t, re.M)
    clock = re.findall(r"ClockTime = (\S+) s", t)
    fatal = "FATAL" in t
    state = "fatal" if fatal else ("running" if times else "pending/prep")
    print(f"{d.name:28s} {state:10s} t={times[-1] if times else '-'}/"
          f"{run['t_end']} clock={clock[-1] if clock else '-'} s")
