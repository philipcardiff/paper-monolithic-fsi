#!/usr/bin/env python3
"""R4/R5: post-process one finished run directory into qm_result.json.

Usage (Python >= 3.10):  qm_post.py RUN_DIR [--no-qoi]

Reads RUN_DIR/qm_run.json (qm_setup.py) and RUN_DIR/run_meta.json
(run_task.sh). Uses the cases' own verification drivers from the tree
($QM_S4F) for the QoIs, so that they are evaluated exactly as in the
verification READMEs, and campaign/scripts/parse_log.py ($QM_CAMPAIGN) for
per-step Newton and Krylov counts.

FSI3: driver extract() over the closing 1 s (u_x, u_y, drag, lift: mean,
  amplitude, frequency; periodicity), plus the lift amplitude of the signal
  smoothed with a centred moving average over 0.01 s (11/21/41 samples at
  1x/2x/4x; the VERIFICATION paper smooths the FSI2 lift over 21 steps of the
  2x mesh, 0.0105 s), evaluated over the same u_y periods.
  Iteration counts over coupled steps (t > couplingStartTime).
3dTube: driver extract() (u_r,max(A), t, u_z,min(A), t_arr(A), c_p, ...)
  for runs from t = 0 to 20 ms; iteration counts over all steps.
Timing: solver ClockTime per step from the log, over all counted steps and
  over the run's window (all steps of a restart run).
"""

import argparse
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path

S4F = Path(os.environ.get("QM_S4F",
                          "/project/home/p201287/philip/qm-final/solids4foam"))
CAMP = Path(os.environ.get("QM_CAMPAIGN",
                           "/project/home/p201287/philip/qm-final/runs/r4r5-scripts/campaign"))
TUT = S4F / "tutorials" / "fluidSolidInteraction"
RE_TIME_EXACT = re.compile(r"^Time = ([-+0-9.eE]+)$")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def coupled_window(steps, t_from):
    return [s for s in steps if float(s["time"]) > t_from + 1e-12]


def iteration_stats(steps):
    newton = [s["newton"] for s in steps]
    ksp = sum(sum(s["ksp"]) for s in steps)
    out = {"n_steps": len(steps)}
    if newton:
        out.update(iters_mean=sum(newton) / len(newton), iters_max=max(newton),
                   ksp_per_newton_mean=ksp / sum(newton) if sum(newton) else None,
                   ksp_total=ksp,
                   snes_not_converged=sum(1 for s in steps if not s["converged"]))
    return out


def clock_stats(steps, all_steps):
    """Solver clock over `steps`, a run of consecutive steps.

    all_steps: every time step of the log with its ClockTime (fluid-only and
    coupled), so that the clock before the window's first step is known."""
    if not steps:
        return {}
    times = [float(s["time"]) for s in all_steps]
    t_first = float(steps[0]["time"])
    k = min(range(len(times)), key=lambda i: abs(times[i] - t_first))
    prev = all_steps[k - 1]["clock_s"] if k > 0 else 0.0
    last = steps[-1]["clock_s"]
    if last is None or prev is None:
        return {}
    wall = last - prev
    out = {"window_clock_s": wall, "window_steps": len(steps),
           "clock_s_per_step": wall / len(steps)}
    # Excluding the first step of the window (start-up, first Jacobian and
    # preconditioner set-up after a restart); used for timing windows
    if len(steps) > 2 and steps[0]["clock_s"] is not None:
        w1 = last - steps[0]["clock_s"]
        out.update(window_clock_s_excl_first=w1,
                   clock_s_per_step_excl_first=w1 / (len(steps) - 1))
    return out


def all_steps_parse(log, system):
    """Every time step of the log (also those without a SNES `system`)."""
    pl = load("parse_log", CAMP / "scripts/parse_log.py")
    summary, solved = pl.parse(str(log), system)
    return pl, summary, solved


def iqn_iterations(case, t_from, ctol):
    path = case / "postProcessing/fsiResiduals.dat"
    if not path.is_file():
        return {}
    final = {}
    for line in path.read_text(errors="replace").splitlines():
        f = line.split()
        if not f or not re.fullmatch(r"[-+0-9.eE]+", f[0]):
            continue
        final[float(f[0])] = (float(f[1]), float(f[2]))
    rows = [(t, n, r) for t, (n, r) in sorted(final.items()) if t > t_from + 1e-12]
    if not rows:
        return {}
    its = [n for _, n, _ in rows]
    res = [r for _, _, r in rows]
    return {"n_steps": len(rows), "iters_mean": sum(its) / len(its),
            "iters_max": max(its), "iters_total": sum(its),
            "final_residual_max": max(res),
            "steps_above_tol": sum(1 for r in res if ctol and r > ctol)}


def smoothed_lift_amplitude(drv, case, spec, window, dt):
    td, ux, uy = drv.displacement_history(case)
    tf, drag, lift = drv.force_history(case, spec["thickness_m"])
    half = max(1, round(0.005 / dt))
    sm = []
    for k in range(len(lift)):
        a, b = max(0, k - half), min(len(lift), k + half + 1)
        sm.append(sum(lift[a:b]) / (b - a))
    # Drop the ends, where the average is one-sided
    tf, sm = tf[half:-half], sm[half:-half]
    fundamental = drv.periodic_statistics(td, uy, window)["crossings"]
    st = drv.periodic_statistics(tf, sm, window, fundamental)
    return {"lift_amplitude_smoothed": st["amplitude"],
            "lift_smoothing_samples": 2 * half + 1}


def post_fsi3(case, run, meta, out, want_qoi):
    drv = load("hron_drv", TUT / "TurekHron2006/verification/scripts/"
               "hron_turek_verification.py")
    spec = json.loads(drv.REFERENCE_FILE.read_text())
    t_start = float(run.get("t_start", 0.0))
    t_end = float(run["t_end"])
    coupling_start = 2.0
    t_from = max(t_start, coupling_start)
    log = case / "log.solids4Foam"
    pl, summary, solved = all_steps_parse(log, "Up")
    out["log_summary"] = {k: summary[k] for k in
                          ("n_steps", "t_last", "snes_not_converged",
                           "snes_fail_reasons", "exec_s", "clock_s", "ended",
                           "fatal")}
    if run["coupling"] == "NewtonQuasiMonolithic":
        win = coupled_window(solved, t_from)
        out["iterations"] = iteration_stats(win)
        _, _, steps = all_steps_parse_any(pl, log)
        out["timing"] = clock_stats(
            [s for s in steps if float(s["time"]) > t_from + 1e-12], steps)
    else:
        ctol = float(run["tol"].get("ctol", spec["outer_corr_tolerance"]))
        out["iterations"] = iqn_iterations(case, t_from, ctol)
        # every step's clock: parse with a system name that never matches
        _, _, steps = all_steps_parse_any(pl, log)
        win = [s for s in steps if float(s["time"]) > t_from + 1e-12]
        out["timing"] = clock_stats(win, steps)
    out["status"] = pl.classify(summary, "COMPLETED")
    if run["coupling"] != "NewtonQuasiMonolithic":
        it = out["iterations"]
        if summary["fatal"]:
            text = log.read_text(errors="replace")
            out["status"] = "stalled" if "FSI coupling did not converge after" \
                in text else "diverged"
        elif it.get("steps_above_tol"):
            out["status"] = "stalled"
        elif summary["ended"]:
            out["status"] = "completed"
    if want_qoi and out["status"] == "completed" and t_end - t_start >= 1.5:
        row = drv.extract(case, spec, 1.0, t_end)
        row.update(smoothed_lift_amplitude(drv, case, spec, 1.0, run["dt"]))
        out["qoi"] = {k: v for k, v in row.items()
                      if isinstance(v, (int, float))}
        out["reference"] = {k: v["value"] for k, v in spec["references"].items()}


def all_steps_parse_any(pl, log):
    """Steps with their clock times regardless of SNES solves (partitioned)."""
    steps = []
    cur = None
    for line in open(log, errors="replace"):
        s = line.strip()
        m = RE_TIME_EXACT.match(s)
        if m:
            cur = {"time": m.group(1), "clock_s": None}
            steps.append(cur)
            continue
        m = pl.RE_EXEC.match(s)
        if m and cur is not None:
            cur["clock_s"] = float(m.group(2))
    steps = [s for s in steps if s["clock_s"] is not None]
    return None, None, steps


def post_tube(case, run, meta, out, want_qoi):
    drv = load("tube_drv", TUT / "3dTube/verification/scripts/tube_3d_verification.py")
    ref = json.loads(drv.REFERENCE_FILE.read_text())
    t_start = float(run.get("t_start", 0.0))
    t_end = float(run["t_end"])
    log = case / "log.solids4Foam"
    pl, summary, solved = all_steps_parse(log, "Up")
    out["log_summary"] = {k: summary[k] for k in
                          ("n_steps", "t_last", "snes_not_converged",
                           "snes_fail_reasons", "exec_s", "clock_s", "ended",
                           "fatal")}
    out["status"] = pl.classify(summary, "COMPLETED")
    if run["coupling"] == "NewtonQuasiMonolithic":
        out["iterations"] = iteration_stats(solved)
        _, _, steps = all_steps_parse_any(pl, log)
        out["timing"] = clock_stats(steps, steps)
    else:
        _, _, steps = all_steps_parse_any(pl, log)
        out["timing"] = clock_stats(steps, steps)
        try:
            s = drv.iteration_summary(case, t_end)
            out["iterations"] = {"n_steps": s["time_steps"],
                                 "iters_mean": s["mean_fsi_iterations"],
                                 "iters_max": s["maximum_fsi_iterations"],
                                 "iters_total": s["total_fsi_iterations"]}
            if t_start == 0.0:
                out["coupling_checks"] = drv.coupling_summary(case, "robin", t_end)
        except RuntimeError as e:
            out["iterations_error"] = str(e)
            if t_start == 0.0 and summary["ended"]:
                out["status"] = "stalled"
    if want_qoi and out["status"] == "completed" and t_start == 0.0 \
            and t_end >= 0.02 - 1e-12:
        row = drv.extract(case, ref, t_end)
        row.pop("_histories", None)
        out["qoi"] = {k: v for k, v in row.items()
                      if isinstance(v, (int, float)) and math.isfinite(v)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir")
    ap.add_argument("--no-qoi", action="store_true")
    args = ap.parse_args()
    case = Path(args.run_dir).resolve()
    run = json.loads((case / "qm_run.json").read_text())
    meta_path = case / "run_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.is_file() else {}
    out = {"run_dir": str(case)}
    try:
        if run["case"] == "TurekHron2006":
            post_fsi3(case, run, meta, out, not args.no_qoi)
        else:
            post_tube(case, run, meta, out, not args.no_qoi)
    except (RuntimeError, OSError, ValueError, KeyError, IndexError) as e:
        out["post_error"] = f"{type(e).__name__}: {e}"
    (case / "qm_result.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out.get(k) for k in ("status", "iterations", "timing",
                                                "post_error")}))


if __name__ == "__main__":
    main()
