#!/usr/bin/env python3
"""Print one status line per campaign run.

Usage:
    status.py <runs_root> [<runs_root> ...] [--system Up]

A run is any directory below a root that contains provenance.json or
run_meta.json. The Slurm state comes from sacct, using the job id recorded
in provenance.json. Columns: run id, ranks, status, last time, steps, mean
and max Newton iterations per step, Krylov iterations per Newton iteration,
solver ExecutionTime and ClockTime, Allrun wall time.
"""

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_log import classify, parse  # noqa: E402


def load(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return {}


def slurm_states(job_ids):
    if not job_ids:
        return {}
    try:
        out = subprocess.run(
            ["sacct", "-n", "-X", "-P", "-o", "JobID,State",
             "-j", ",".join(sorted(job_ids))],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return {}
    states = {}
    for line in out.splitlines():
        jid, _, state = line.partition("|")
        states[jid.split("_")[0]] = state.split()[0] if state else None
    return states


def find_runs(root):
    for dirpath, dirnames, filenames in os.walk(root):
        if "provenance.json" in filenames or "run_meta.json" in filenames:
            dirnames[:] = []
            yield dirpath
        else:
            dirnames[:] = [d for d in dirnames
                           if not d.startswith(("processor", "postProcessing"))
                           and not d[0].isdigit()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--system", default="Up")
    args = ap.parse_args()

    runs = []
    for root in args.roots:
        for d in sorted(find_runs(root)):
            prov = load(os.path.join(d, "provenance.json"))
            meta = load(os.path.join(d, "run_meta.json"))
            runs.append((d, prov, meta))
    jobs = {p.get("slurm", {}).get("slurm_job_id") for _, p, _ in runs}
    states = slurm_states({j for j in jobs if j})

    fmt = "{:<26} {:>3} {:<9} {:>9} {:>6} {:>6} {:>4} {:>7} {:>9} {:>7} {:>8}"
    print(fmt.format("run_id", "np", "status", "t_last", "steps", "newt",
                     "max", "ksp/nw", "exec_s", "clock_s", "allrun_s"))
    for d, prov, meta in runs:
        log = os.path.join(d, "log.solids4Foam")
        state = states.get(prov.get("slurm", {}).get("slurm_job_id"))
        if meta and state in (None, "RUNNING"):
            state = "COMPLETED"  # Allrun returned, job may still be running
        if os.path.isfile(log):
            s, _ = parse(log, args.system)
            status = classify(s, state)
        else:
            s, status = {}, "pending" if not meta else "no-log"
        if meta.get("allrun_rc") not in (None, 0) and status == "completed":
            status = "allrun-rc%s" % meta["allrun_rc"]
        print(fmt.format(
            (prov.get("run_id") or os.path.basename(d))[:26],
            prov.get("ranks", meta.get("ranks", "")), status,
            str(s.get("t_last", "")), s.get("n_steps", ""),
            s.get("iters_mean", ""), s.get("iters_max", ""),
            s.get("ksp_per_newton_mean", ""), s.get("exec_s", ""),
            s.get("clock_s", ""), meta.get("allrun_wall_s", "")))


if __name__ == "__main__":
    main()
