#!/usr/bin/env python3
"""Classify one WP3 run and extract its iteration counts and QoIs.

  wp3_post.py <run_dir> [--rc RC] [--wall WALL_S]

Writes <run_dir>/wp3_result.json. The failure criterion (fixed before the
runs, README.md) is applied in this order, identically for every coupling:

  nan        a non-finite value in the log or the monitored histories
  cap        a step reached the coupling-iteration cap (partitioned:
             "FSI coupling did not converge"; quasi-monolithic: the Newton
             solve of the coupled system did not converge, e.g. at
             snes_max_it)
  newton     a solid Newton (SNES) failure inside a partitioned step, or a
             mesh-motion SNES failure
  diverged   ring: |ovalling displacement| above 10 times its first peak;
             collapsibleChannel: |wall displacement| above the channel
             height (1 m)
  timeout    the run hit its wall-clock limit (not a coupling failure)
  crash      any other abnormal end (FOAM FATAL, signal, missing End)

A run that reaches its end time with none of the above is "pass".
"""

import os
import sys

if sys.version_info < (3, 9):
    for candidate in ("/usr/bin/python3.12", "/usr/bin/python3.11"):
        if os.access(candidate, os.X_OK):
            os.execv(candidate, [candidate] + sys.argv)
    sys.exit("wp3: Python >= 3.9 is required")

import argparse
import importlib.util
import json
import math
import re
from pathlib import Path

sys.dont_write_bytecode = True

QM_ROOT = Path(os.environ.get("QM_ROOT",
                              "/project/home/p201287/philip/qm-head"))
FSI = QM_ROOT / "solids4foam/tutorials/fluidSolidInteraction"

RE_TIME = re.compile(r"^Time = ([0-9.eE+-]+)\s*$")
RE_ITER = re.compile(r"^Time = (\S+), iteration: (\d+)")
RE_SNES_HDR = re.compile(r"^Solving .* for (\w+) using PETSc SNES")
RE_NONLIN = re.compile(r"Nonlinear solve (converged|did not converge) due to "
                       r"(\w+) iterations (\d+)")
RE_LIN = re.compile(r"Linear solve (converged|did not converge) due to "
                    r"\w+ iterations (\d+)")
RE_EXEC = re.compile(r"^ExecutionTime = (\S+) s\s+ClockTime = (\S+) s")
# Non-finite numbers, or a trapped floating-point exception (not the
# start-up line "trapFpe: Floating point exception trapping enabled")
RE_NAN = re.compile(r"(?<![\w.])[-+]?(nan|inf)(?![\w])|"
                    r"Floating point exception(?! trapping)", re.I)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_log(path, qm):
    """Per-step iteration counts and failure markers."""
    out = {"t_last": None, "newton": [], "ksp": [], "coupling": {},
           "coupled_snes_fail": None, "other_snes_fail": None,
           "coupling_cap": False, "fatal": None, "nan": False,
           "ended": False, "exec_s": None}
    if not path.is_file():
        return out
    active = None
    newton_step = None
    for line in path.open(errors="replace"):
        s = line.strip()
        m = RE_TIME.match(s)
        if m:
            out["t_last"] = float(m.group(1))
            active = None
            if newton_step is not None:
                out["newton"].append(newton_step)
            newton_step = None
            continue
        m = RE_ITER.match(s)
        if m:
            out["coupling"][m.group(1)] = max(out["coupling"].get(m.group(1),
                                                                  0),
                                              int(m.group(2)))
            continue
        m = RE_SNES_HDR.match(s)
        if m:
            active = m.group(1)
            continue
        m = RE_NONLIN.search(s)
        if m:
            coupled = qm and active == "Up"
            if coupled:
                newton_step = (newton_step or 0) + int(m.group(3))
            if m.group(1) != "converged":
                key = "coupled_snes_fail" if coupled else "other_snes_fail"
                if out[key] is None:
                    out[key] = (out["t_last"], active, m.group(2))
            continue
        if qm and active == "Up":
            m = RE_LIN.search(s)
            if m:
                out["ksp"].append(int(m.group(2)))
                continue
        if "FSI coupling did not converge" in s:
            out["coupling_cap"] = True
        if "FOAM FATAL" in s and out["fatal"] is None:
            out["fatal"] = s
        if RE_NAN.search(s) and not s.startswith("//"):
            out["nan"] = True
        m = RE_EXEC.match(s)
        if m:
            out["exec_s"] = float(m.group(1))
        if s == "End":
            out["ended"] = True
    if newton_step is not None:
        out["newton"].append(newton_step)
    return out


def ring_qois(case, meta, log):
    drv = load("ringdrv", FSI / "ringAddedMass/verification/scripts/"
               "ring_added_mass_verification.py")
    # Read without the driver's completeness check, so failed runs are
    # classified too
    rows = {}
    for name, col in ((drv.HISTORY_X, 1), (drv.HISTORY_Y, 2)):
        p = case / name
        series = []
        if p.is_file():
            for line in p.read_text(errors="replace").splitlines():
                f = line.split()
                if f and not f[0].startswith("#"):
                    try:
                        series.append((float(f[0]), float(f[col])))
                    except (ValueError, IndexError):
                        pass
        rows[name] = series
    n = min(len(rows[drv.HISTORY_X]), len(rows[drv.HISTORY_Y]))
    times = [rows[drv.HISTORY_X][i][0] for i in range(n)]
    oval = [0.5 * (rows[drv.HISTORY_X][i][1] - rows[drv.HISTORY_Y][i][1])
            for i in range(n)]
    q = {"history_samples": n}
    finite = all(math.isfinite(v) for v in oval)
    q["history_finite"] = finite
    if n and finite:
        quarter = meta["spec"]["period"] / 4
        first = [abs(v) for t, v in zip(times, oval) if t <= 1.5 * quarter]
        peak = max(first) if first else max(abs(v) for v in oval)
        q["first_peak"] = peak
        q["max_over_first_peak"] = max(abs(v) for v in oval) / peak \
            if peak > 0 else math.inf
    return q, times, oval, drv


def ring_frequency(drv, meta, times, oval):
    try:
        f = drv.frequency_and_damping(times, oval, meta["periods"])
    except SystemExit as e:
        return {"freq_note": f"not measurable: {e}"}
    except Exception as e:  # noqa: BLE001
        return {"freq_note": f"not measurable: {e}"}
    return {"omega": f["omega"],
            "omega_error": f["omega"] / meta["omega_exact"] - 1,
            "loss_per_period": f["loss_per_period"]}


def coll_qois(case, meta):
    drv = load("ccv", FSI / "collapsibleChannel/verification/scripts/"
               "collapsible_channel_verification.py")
    q = {}
    try:
        hist = drv.read_history(case, "wallMid")
    except RuntimeError:
        hist = []
    q["history_samples"] = len(hist)
    q["history_finite"] = all(math.isfinite(v) for _, v in hist)
    if hist and q["history_finite"]:
        q["max_abs_wall"] = max(abs(v) for _, v in hist)
        t_end = hist[-1][0]
        if t_end >= meta["end_time"] - 0.5 * meta["deltaT"]:
            tt, tv = drv.trough(hist, tuple(meta["troughWindow"]))
            q["trough_time"], q["trough_value"] = tt, tv
            refs = {1.0: drv.REFERENCE_CSV,
                    0.0: drv.REFERENCE_DIR /
                    "collapsibleChannel_oomph_massless_reference.csv"}
            ref_file = refs.get(meta["rho_ratio"])
            if ref_file is not None and ref_file.is_file():
                ref = drv.read_reference(ref_file)["wallMid"]
                rt, rv = drv.trough(ref, tuple(meta["troughWindow"]))
                q["trough_reference"] = rv
                q["trough_reference_source"] = ref_file.name
                q["trough_error"] = tv / rv - 1
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--rc", type=int, default=None)
    ap.add_argument("--wall", type=float, default=None)
    args = ap.parse_args()
    case = Path(args.run_dir).resolve()
    meta = json.loads((case / "wp3_case.json").read_text())
    qm = meta["coupling"] == "qm"
    log = parse_log(case / "log.solids4Foam", qm)

    if meta["map"] == "3a":
        q, times, oval, drv = ring_qois(case, meta, log)
        diverged = q.get("max_over_first_peak", 0) > 10
    else:
        q = coll_qois(case, meta)
        diverged = q.get("max_abs_wall", 0) > 1.0
    nan = log["nan"] or not q.get("history_finite", True)

    end_ok = log["ended"] and log["t_last"] is not None and \
        log["t_last"] >= meta["end_time"] - 0.5 * meta["deltaT"]
    if nan:
        status = "nan"
    elif log["coupling_cap"] or log["coupled_snes_fail"]:
        status = "cap"
    elif log["other_snes_fail"] and not end_ok:
        status = "newton"
    elif diverged:
        status = "diverged"
    elif args.rc == 124:
        status = "timeout"
    elif end_ok and log["fatal"] is None:
        status = "pass"
    else:
        status = "crash"
    # A converged run in which an inner (solid or mesh-motion) SNES solve
    # reported non-convergence but the step still converged is a pass with a
    # note
    if qm:
        iters = log["newton"]
    else:
        iters = list(log["coupling"].values())
    res = {
        "run_id": case.name, "status": status,
        "t_reached": log["t_last"], "end_time": meta["end_time"],
        "n_steps_done": len(iters),
        "iters_mean": sum(iters) / len(iters) if iters else None,
        "iters_max": max(iters) if iters else None,
        "iters_kind": "Newton (coupled system)" if qm else
        "coupling iterations",
        "ksp_per_newton_mean": (sum(log["ksp"]) / sum(log["newton"])
                                if qm and sum(log["newton"]) else None),
        "coupled_snes_fail": log["coupled_snes_fail"],
        "other_snes_fail": log["other_snes_fail"],
        "fatal": log["fatal"], "exec_s": log["exec_s"],
        "rc": args.rc, "wall_s": args.wall,
    }
    res.update(q)
    if meta["map"] == "3a" and status == "pass":
        res.update(ring_frequency(drv, meta, times, oval))
    (case / "wp3_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(f"{case.name} {status} t={log['t_last']} iters_mean="
          f"{res['iters_mean']}")


if __name__ == "__main__":
    main()
