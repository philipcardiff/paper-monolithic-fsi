#!/usr/bin/env python3
"""Parse a solids4Foam log into per-step Newton and Krylov counts.

Usage:
    parse_log.py <log.solids4Foam> [--system Up] [--steps-csv FILE] [--json]

Each time step of a quasi-monolithic run contains several PETSc SNES solves,
each introduced by a line "Solving ... for <X> using PETSc SNES" (the fluid
mesh motion `D`, the monolithic system `Up`). The counts of the solve named
by --system are attributed to the step; the others are ignored.

Summary fields: n_steps, iters_mean/max (Newton iterations per step),
ksp_per_newton_mean (Krylov iterations per Newton iteration),
the number of steps whose SNES did not converge and their reasons, the last
ExecutionTime/ClockTime, and whether the solver reached "End".
"""

import argparse
import csv
import json
import re
import sys

RE_TIME = re.compile(r"^Time = (\S+)")
RE_SNES_HDR = re.compile(r"^Solving .* for (\w+) using PETSc SNES")
RE_LIN = re.compile(r"Linear solve (converged|did not converge) due to "
                    r"(\w+) iterations (\d+)")
RE_NONLIN = re.compile(r"Nonlinear solve (converged|did not converge) due to "
                       r"(\w+) iterations (\d+)")
RE_EXEC = re.compile(r"^ExecutionTime = (\S+) s\s+ClockTime = (\S+) s")
RE_FATAL = re.compile(r"FOAM FATAL|Floating point exception|"
                      r"\bnan\b|negative (cell )?volume|segmentation", re.I)


def parse(path, system="Up"):
    steps = []
    cur = None
    active = None
    fatal = None
    ended = False
    last_exec = last_clock = None
    with open(path, errors="replace") as f:
        for line in f:
            s = line.strip()
            m = RE_TIME.match(s)
            if m:
                cur = {"time": m.group(1), "newton": None, "ksp": [],
                       "reason": None, "converged": None,
                       "exec_s": None, "clock_s": None}
                steps.append(cur)
                active = None
                continue
            m = RE_SNES_HDR.match(s)
            if m:
                active = m.group(1)
                continue
            if cur is not None and active == system:
                m = RE_LIN.search(s)
                if m:
                    cur["ksp"].append(int(m.group(3)))
                    continue
                m = RE_NONLIN.search(s)
                if m:
                    # A step may contain retries; keep the last solve
                    cur["newton"] = int(m.group(3))
                    cur["reason"] = m.group(2)
                    cur["converged"] = m.group(1) == "converged"
                    continue
            m = RE_EXEC.match(s)
            if m:
                last_exec, last_clock = float(m.group(1)), float(m.group(2))
                if cur is not None:
                    cur["exec_s"], cur["clock_s"] = last_exec, last_clock
                continue
            if s == "End":
                ended = True
            elif fatal is None and RE_FATAL.search(s) \
                    and not s.startswith("trapFpe") \
                    and "SNES Function norm" not in s:
                fatal = s[:200]

    solved = [st for st in steps if st["newton"] is not None]
    newton = [st["newton"] for st in solved]
    ksp_total = sum(sum(st["ksp"]) for st in solved)
    failed = [st for st in solved if not st["converged"]]
    summary = {
        "log": path,
        "system": system,
        "n_steps": len(solved),
        "t_last": solved[-1]["time"] if solved else None,
        "iters_mean": round(sum(newton) / len(newton), 4) if newton else None,
        "iters_max": max(newton) if newton else None,
        "ksp_per_newton_mean":
            round(ksp_total / sum(newton), 3) if newton and sum(newton)
            else None,
        "ksp_total": ksp_total,
        "snes_not_converged": len(failed),
        "snes_fail_reasons": sorted({st["reason"] for st in failed}),
        "exec_s": last_exec,
        "clock_s": last_clock,
        "ended": ended,
        "fatal": fatal,
    }
    return summary, solved


def classify(summary, slurm_state=None):
    """Campaign status: completed, diverged, stalled, timeout or running."""
    if slurm_state and slurm_state.startswith("TIMEOUT"):
        return "timeout"
    if summary["fatal"]:
        return "diverged"
    if summary["snes_not_converged"]:
        reasons = summary["snes_fail_reasons"]
        if reasons and all(r == "DIVERGED_MAX_IT" for r in reasons):
            return "stalled"
        return "diverged"
    if summary["ended"]:
        return "completed"
    if slurm_state in (None, "RUNNING", "PENDING"):
        return "running"
    return "diverged"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("log")
    ap.add_argument("--system", default="Up")
    ap.add_argument("--steps-csv")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    summary, steps = parse(args.log, args.system)
    summary["status"] = classify(summary, "COMPLETED")
    if args.steps_csv:
        with open(args.steps_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time", "newton", "ksp_total", "reason",
                        "exec_s", "clock_s"])
            for st in steps:
                w.writerow([st["time"], st["newton"], sum(st["ksp"]),
                            st["reason"], st["exec_s"], st["clock_s"]])
    json.dump(summary, sys.stdout, indent=None if not args.json else 1)
    print()


if __name__ == "__main__":
    main()
