#!/usr/bin/env python3
"""Post-process the B2 collapsibleChannel runs into runs.csv rows.

For each run directory (runs/b2/<run_id>):

- static runs (static_result.json): wall-midpoint deflection and its error
  against the static oomph-lib beam, -0.143628 m (negative = too stiff);
- monolithic FSI runs (b2_case.json): the first trough of the wall midpoint
  in t = [0.3, 0.75] s, parabola-refined (the tutorial driver's `trough`),
  and its error against oomph-lib at the same time step, as in the
  tutorial README: (|trough| - |trough_ref|)/|trough_ref|, with
  trough_ref = -0.215731 m at dt = 0.00625 s; wall time (solver ClockTime,
  and the Allrun wall time from run_meta.json); Newton iterations per step
  from the SNES "Nonlinear solve converged/diverged ... iterations N" lines;
  status completed / diverged / stalled / timeout.

The trough and reference readers are imported (read-only, no bytecode) from
the tutorial's verification driver, so the metric is the README's.

Usage: b2_post.py <runs_dir> [--tutorial DIR] [--csv OUT] [--commit SHA]
"""

import os
import sys

# The tutorial driver needs Python >= 3.7; MeluXina's /usr/bin/python3 is
# 3.6, so re-execute with a newer system interpreter when needed
if sys.version_info < (3, 8):
    for candidate in ("/usr/bin/python3.12", "/usr/bin/python3.11",
                      "/usr/bin/python3.8"):
        if os.access(candidate, os.X_OK):
            os.execv(candidate, [candidate] + sys.argv)
    sys.exit("b2: Python >= 3.8 is required")

import argparse
import csv
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_TUTORIAL = (
    "/project/home/p201287/philip/qm-paper/solids4foam/tutorials/"
    "fluidSolidInteraction/collapsibleChannel"
)
COLUMNS = [
    "run_id", "case", "study", "coupling", "level", "solid_mesh", "interface",
    "dt", "rho_ratio", "ranks", "exclusive", "code_commit", "status", "t_end",
    "n_steps", "iters_mean", "wall_s", "notes",
]
SNES = re.compile(
    r"Nonlinear solve (converged|diverged) due to (\S+) iterations (\d+)"
)


def load_driver(tutorial: Path):
    path = tutorial / "verification/scripts/collapsible_channel_verification.py"
    spec = importlib.util.spec_from_file_location("ccv", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def commit_of(run_dir: Path, default: str) -> str:
    prov = load_json(run_dir / "provenance.json")
    for key in ("solids4foam_commit", "s4f_commit", "commit"):
        value = prov.get(key)
        if isinstance(value, dict):
            value = value.get("hash") or value.get("describe")
        if value:
            return str(value)[:9]
    s4f = prov.get("solids4foam")
    if isinstance(s4f, dict):
        value = s4f.get("describe") or s4f.get("hash")
        if value:
            return str(value)[:9]
    return default


def static_row(run_dir: Path, commit: str) -> dict:
    res = load_json(run_dir / "static_result.json")
    meta = load_json(run_dir / "run_meta.json")
    ok = res.get("status") == "completed"
    notes = ""
    if ok:
        notes = (f"wallMid {res['wallMid']:.6f} m vs -0.143628 m:"
                 f" rel. error {res['wallMid_relError']:+.3%}")
    else:
        notes = str(res.get("status", "no static_result.json"))
    return {
        "run_id": run_dir.name, "case": "collapsibleChannel static wall",
        "study": "static", "coupling": "solid only (partitioned linear solid)",
        "level": "", "solid_mesh": res.get("solid_mesh", ""), "interface": "",
        "dt": "", "rho_ratio": "", "ranks": meta.get("ranks", 1),
        "exclusive": "no", "code_commit": commit,
        "status": "completed" if ok else "failed", "t_end": "20 load steps",
        "n_steps": 20 if ok else "", "iters_mean": "",
        "wall_s": f"{res.get('clockTime', math.nan):.0f}" if ok else "",
        "notes": notes,
    }


def fsi_row(run_dir: Path, driver, refs: dict, commit: str) -> dict:
    case = load_json(run_dir / "b2_case.json")
    meta = load_json(run_dir / "run_meta.json")
    log = run_dir / "log.solids4Foam"
    text = log.read_text(errors="replace") if log.is_file() else ""
    end_time = float(case.get("end_time", 1.5))
    dt = float(case.get("dt", 0.00625))

    snes = SNES.findall(text)
    iters = [int(n) for kind, _, n in snes if kind == "converged"]
    diverged = [(reason, int(n)) for kind, reason, n in snes
                if kind == "diverged"]
    times = re.findall(r"^Time = ([0-9.eE+-]+)\s*$", text, re.MULTILINE)
    t_last = float(times[-1]) if times else 0.0
    clock = re.findall(r"ClockTime = ([0-9.eE+-]+) s", text)
    finished = bool(re.search(r"^End\s*$", text, re.MULTILINE))
    rc = meta.get("allrun_rc")

    if finished and abs(t_last - end_time) < 1e-6:
        status = "completed"
    elif rc == 124:
        status = "timeout"
    elif diverged or re.search(r"FOAM FATAL|nan", text[-20000:], re.I):
        status = "diverged"
    elif rc is None:
        status = "running"
    else:
        status = "stalled"

    notes = []
    trough_s = ""
    try:
        history = driver.read_history(run_dir, "wallMid")
        window = tuple(refs["troughWindow"])
        if history and history[-1][0] >= window[1]:
            t_tr, v_tr = driver.trough(history, window)
            ref_curve = driver.read_reference(
                driver.REFERENCE_DIR / f"collapsibleChannel_oomph_dt{1.0/dt:g}.csv"
            )["wallMid"]
            _, v_ref = driver.trough(ref_curve, window)
            err = (abs(v_tr) - abs(v_ref))/abs(v_ref)
            trough_s = f"{v_tr:.5f}"
            notes.append(
                f"trough {v_tr:.5f} m at t={t_tr:.4f} s; oomph-lib"
                f" {v_ref:.5f} m; error {err:+.2%}"
            )
    except (RuntimeError, ValueError, OSError) as error:
        notes.append(f"no trough: {error}")
    if diverged:
        notes.append(f"{len(diverged)} SNES diverged ({diverged[-1][0]})")
    if iters:
        notes.append(f"iters max {max(iters)}")
    if meta.get("allrun_wall_s") is not None:
        notes.append(f"Allrun wall {meta['allrun_wall_s']:.0f} s")
    if meta.get("node"):
        notes.append(f"node {meta['node']}")

    return {
        "run_id": run_dir.name, "case": "collapsibleChannel",
        "study": "mono", "coupling": "NewtonQuasiMonolithic",
        "level": case.get("level", ""), "solid_mesh": case.get("solid_mesh", ""),
        "interface": case.get("interfaceTransferMethod", "")
        + ("+conservative" if case.get("conservativeTractionTransfer") else ""),
        "dt": dt, "rho_ratio": 1, "ranks": meta.get("ranks", 1),
        "exclusive": "yes" if meta.get("exclusive") else "no",
        "code_commit": commit, "status": status, "t_end": t_last,
        "n_steps": len(iters) + len(diverged),
        "iters_mean": f"{sum(iters)/len(iters):.2f}" if iters else "",
        "wall_s": f"{float(clock[-1]):.0f}" if clock else "",
        "notes": "; ".join(notes),
        "_trough": trough_s,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs_dir")
    parser.add_argument("--tutorial", default=DEFAULT_TUTORIAL)
    parser.add_argument("--csv", default="runs.csv")
    parser.add_argument("--commit", default="257b2e564")
    args = parser.parse_args()
    driver = load_driver(Path(args.tutorial))
    refs = driver.load_references()
    rows = []
    for run_dir in sorted(Path(args.runs_dir).iterdir()):
        if not run_dir.is_dir():
            continue
        commit = commit_of(run_dir, args.commit)
        if (run_dir / "static_result.json").is_file():
            rows.append(static_row(run_dir, commit))
        elif (run_dir / "b2_case.json").is_file():
            rows.append(fsi_row(run_dir, driver, refs, commit))
    with open(args.csv, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(f"{row['run_id']}: {row['status']}, {row['notes']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
