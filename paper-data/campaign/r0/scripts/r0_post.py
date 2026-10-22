#!/usr/bin/env python3
"""R0 post-processing: status, iteration counts and primary QoIs of a run.

Usage:
    r0_post.py <run_dir> [...]              print one status line per run and
                                            write <run_dir>/r0_summary.json
    r0_post.py --completed <run_dir>        exit 0 only if the run completed
    r0_post.py --status <run_dir> [...]     status lines only, no QoIs/writes

<run_dir> is a directory made by r0_setup.py and run by jobs/r0_farm.sh. The
solver case is the run directory itself, or (3dTube, TurekHron2006) the
driver's copy under verification/work/. Newton and Krylov counts come from
campaign/scripts/parse_log.py (system Up); peak memory from the farm's
mem_samples.<jobid> file (sum of the solver ranks' VmRSS, sampled every 20 s).
The QoIs use the case's verification-script functions where they exist, so
they are measured as in the README.
"""

import csv
import glob
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from parse_log import classify, parse  # noqa: E402


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def jload(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return {}


def solver_case(run):
    meta = jload(run / "run_meta.json")
    if meta.get("solver_case") and Path(meta["solver_case"]).is_dir():
        return Path(meta["solver_case"])
    work = sorted((run / "verification/work").glob("*/"))
    return work[0] if work else run


def columns(path, skip_comment=True):
    rows = []
    for line in open(path, errors="replace"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            rows.append([float(x) for x in s.replace("(", " ").replace(")", " ").split()])
        except ValueError:
            continue
    return rows


def find_one(case, pattern):
    hits = sorted(glob.glob(str(case / pattern), recursive=True))
    return Path(hits[0]) if hits else None


# ---------------------------------------------------------------------------
# Case QoIs: list of (qoi, value, reference, reference_source, notes)
# ---------------------------------------------------------------------------

def qoi_ram(run, case):
    mod = load_module("ram_v", run / "verification/scripts/ring_added_mass_verification.py")
    ref = jload(run / "verification/reference/ringAddedMass_verification_references.json")
    tx, ux = mod.read_columns(case / mod.HISTORY_X, 1)
    ty, uy = mod.read_columns(case / mod.HISTORY_Y, 2)
    v = [0.5 * (a - b) for a, b in zip(ux, uy)]
    fd = mod.frequency_and_damping(tx, v, 4)
    w_ex = ref["exact"]["levels"]["moderate"]["omega"]
    return [
        ("omega", fd["omega"], w_ex,
         "exact, verification/reference (moderate, rhoFluid 140)",
         "standard 2nd-order velocity solid, too stiff in bending: README "
         "gives +20.7% for the standard solid on the tutorial mesh"),
        ("loss_per_period", fd["loss_per_period"], 0.00040,
         "README monolithic table: moderate, factor 2, 100 steps/period "
         "(0.040%); tutorial is factor 1", ""),
    ]


def qoi_wom(run, case):
    mod = load_module("wom_v", run / "verification/scripts/womersley_tube_verification.py")
    ref = jload(run / "verification/reference/womersleyTube_verification_references.json")
    # The tutorial runs 2 periods (factor-2 mesh, 100 steps per period) and
    # samples the last one; analyse that period
    ref["study"]["periods"] = 2
    ref["study"]["analysisPeriods"] = 1
    mod.WORK_ROOT = case.parent
    row = mod.analyse({"name": case.name, "factor": 2, "steps": 100}, ref)
    readme = {"profile": 4.70e-3, "flow_amp": 4.73e-4, "wallMid_amp": -9.96e-4,
              "wallMid_phase": -2.82e-3, "speed": -1.36e-4,
              "attenuation": -4.64e-3}
    out = []
    for k, r in readme.items():
        out.append((k + "_err", row[k], r,
                    "README monolithic table m2,n100 (6 periods, last 2 "
                    "analysed; this run: tutorial 2 periods, last 1)",
                    "relative error vs exact Womersley solution"))
    return out


def qoi_coll(run, case):
    rows = columns(find_one(case, "postProcessing/**/*wallMid*.dat"))
    ref = jload(run / "verification/reference/collapsibleChannel_verification_references.json")
    lo, hi = ref["troughWindow"]
    win = [r for r in rows if lo <= r[0] <= hi]
    t, y = min(((r[0], r[2]) for r in win), key=lambda p: p[1])
    oo = []
    for line in open(run / "verification/reference/collapsibleChannel_oomph_dt40.csv"):
        if line[0].isdigit():
            f = [float(x) for x in line.split(",")]
            if lo <= f[0] <= hi:
                oo.append((f[0], f[2]))
    to, yo = min(oo, key=lambda p: p[1])
    return [
        ("trough_wallMid", y, yo,
         "oomph-lib dt=0.025 (collapsibleChannel_oomph_dt40.csv)",
         f"t={t:.4f} s (oomph-lib t={to:.4f} s); README monolithic rows are "
         "at dt=0.00625 (L1: -0.19619, -9.1%)"),
        ("t_trough", t, to, "oomph-lib dt=0.025", ""),
    ]


def last_row(path):
    rows = columns(path)
    return rows[-1] if rows else None


def qoi_cav(run, case):
    d = last_row(find_one(case, "postProcessing/**/*pointDisp*.dat"))
    f = last_row(find_one(case, "postProcessing/**/force*.dat"))
    # The monitor point (4 -1 0.5) of this tutorial resolves to the mesh
    # point (4, -0.4): the plate underside (README)
    out = [("uy_underside", d[2], -0.201552,
            "README #597 rerun, level 1, Euler, at 200 s (300 s: -0.201546)",
            f"t={d[0]:g}; monitor point (4 -1 0.5) = underside")]
    if f:
        out.append(("Fy", f[2], -5.12258,
                    "README #597 rerun, level 1, Euler, 300 s",
                    "total force (col 3 of force.dat: total y)"))
    return out


def qoi_blob(run, case):
    d = last_row(find_one(case, "postProcessing/**/*pointDisp*.dat"))
    return [("ux_top", d[1], 0.116851,
             "README monolithic x1 (t=3 s, Euler, serial macOS)",
             f"t={d[0]:g}; partitioned x1 0.117301")]


def qoi_foil(run, case):
    rows = columns(find_one(case, "postProcessing/**/*displacement*.dat"))
    early = [r for r in rows if r[0] <= 0.01 + 1e-9]
    peak = max(early, key=lambda r: abs(r[1])) if early else None
    out = []
    if peak:
        out.append(("ux_TE_peak_first_0.01s", peak[1], 7.7e-8,
                    "README (b157ecaf3) quasi-monolithic dt=0.0025", ""))
    mx = max(rows, key=lambda r: math.hypot(r[1], r[2]))
    out.append(("uxy_TE_max_abs", math.hypot(mx[1], mx[2]), None, "",
                f"at t={mx[0]:g}; flapping beyond 0.2 s not in README"))
    out.append(("ux_TE_final", rows[-1][1], None, "", f"t={rows[-1][0]:g}"))
    out.append(("uy_TE_final", rows[-1][2], None, "", f"t={rows[-1][0]:g}"))
    f = last_row(find_one(case, "postProcessing/**/force*.dat"))
    if f:
        out.append(("Fx_final", f[1], None, "", f"t={f[0]:g}"))
    return out


# Primary QoIs of the driver runs and the README values they are compared
# with: (driver column, README value or None, source, Featflow column)
DRIVER_QOIS = {
    "tube": [("ur_max_A_m", 0.15949e-3), ("t_ur_max_A_s", 7.225e-3),
             ("uz_min_A_m", -0.08896e-3), ("t_arrival_A_s", 5.876e-3),
             ("wave_speed_pressure_m_s", 4.666)],
    "fsi1": [("ux", None), ("uy", None), ("drag", None), ("lift", None)],
    "fsi3": [("ux_mean", None), ("ux_amplitude", None), ("uy_amplitude", None),
             ("uy_frequency", None), ("drag_mean", None),
             ("drag_amplitude", None), ("lift_amplitude", None)],
}
TUBE_SRC = ("3dTube verification README, quasi-monolithic level 1 "
            "(backward, 8 ranks, PR #599 settings)")
# FSI1 conformal 1x errors vs Featflow in the README (#597 table)
FSI1_README = {"ux": 0.153, "uy": -0.350, "drag": -0.0044, "lift": 0.151}


def qoi_driver(run, case, key):
    out = []
    for p in sorted((run / "verification/postProcessing").glob("*.csv")):
        if "history" in p.name or "reference" in p.name:
            continue
        for row in csv.DictReader(open(p)):
            for col, readme in DRIVER_QOIS.get(key, []):
                if col not in row:
                    continue
                val = float(row[col])
                if key == "tube":
                    out.append((col, val, readme, TUBE_SRC, ""))
                    continue
                ref = row.get(f"{col}_reference")
                err = row.get(f"{col}_error")
                note = f"driver |error| vs Featflow {float(err):.4f}" \
                    if err else ""
                if key == "fsi1":
                    note += (f"; README conformal 1x error "
                             f"{FSI1_README[col]:+.4f}")
                else:
                    note += "; README has no conformal 1x FSI3 row"
                out.append((col, val, float(ref) if ref else None,
                            "Featflow (driver reference JSON)", note))
    return out


QOI = {"ram": qoi_ram, "wom": qoi_wom, "coll": qoi_coll, "cav": qoi_cav,
       "blob": qoi_blob, "foil": qoi_foil}


def cells(case):
    """Cell counts from the polyMesh owner headers (note "nCells:...")."""
    out = {}
    for region in ("fluid", "solid"):
        hits = sorted(glob.glob(str(case / "constant" / region / "polyMesh" / "owner*")))
        for h in hits:
            import gzip
            op = gzip.open if h.endswith(".gz") else open
            with op(h, "rt", errors="replace") as f:
                head = f.read(2000)
            m = __import__("re").search(r"nCells:\s*(\d+)", head)
            if m:
                out[region] = int(m.group(1))
                break
    return out


def peak_mem_gb(run, case, job):
    if (run / "mem.json").is_file():
        return jload(run / "mem.json").get("peak_mem_gb")
    best = None
    for f in glob.glob(str(run.parent / f"mem_samples.{job}")):
        for line in open(f):
            parts = line.split()
            if len(parts) >= 3 and os.path.realpath(parts[1]) == os.path.realpath(case):
                kb = int(parts[2])
                best = kb if best is None or kb > best else best
    return round(best / 2**20, 3) if best else None


def summarise(run, qois=True):
    run = Path(run).resolve()
    meta = jload(run / "run_meta.json")
    setup = jload(run / "r0_setup.json")
    case = solver_case(run)
    log = case / "log.solids4Foam"
    s = {"run_id": run.name, "case": setup.get("case"), "key": setup.get("key"),
         "solver_case": str(case)}
    if log.is_file():
        summ, _ = parse(str(log))
        state = "COMPLETED" if meta else "RUNNING"
        if meta.get("rc") == 124:
            state = "TIMEOUT"
        s.update(summ)
        s["status"] = classify(summ, state)
    else:
        s["status"] = "not started" if not meta else "diverged"
    s["meta"] = meta
    s["edits"] = setup.get("edits")
    if meta:
        s["peak_mem_gb"] = peak_mem_gb(run, case, meta.get("slurm_job_id"))
    if qois and s["status"] == "completed":
        try:
            key = setup.get("key")
            fn = QOI.get(key)
            s["qois"] = fn(run, case) if fn else qoi_driver(run, case, key)
        except Exception as e:  # report, do not hide, a QoI failure
            s["qoi_error"] = repr(e)
    return s


def main():
    args = sys.argv[1:]
    if args and args[0] == "--completed":
        s = summarise(args[1], qois=False)
        sys.exit(0 if s["status"] == "completed" else 1)
    if args and args[0] == "--records":
        # On the cluster: peak memory and cell counts next to each run, for
        # the post-processing elsewhere
        for run in args[1:]:
            run = Path(run).resolve()
            meta = jload(run / "run_meta.json")
            case = solver_case(run)
            json.dump({"peak_mem_gb": peak_mem_gb(run, case,
                                                   meta.get("slurm_job_id"))},
                      open(run / "mem.json", "w"))
            json.dump(cells(case), open(run / "cells.json", "w"))
        return
    quick = bool(args) and args[0] == "--status"
    if quick:
        args = args[1:]
    for run in args:
        s = summarise(run, qois=not quick)
        if s.get("meta") and not quick:
            json.dump(s, open(Path(run) / "r0_summary.json", "w"), indent=1,
                      default=str)
        print(f"{s['run_id']:28s} {s['status']:10s} t={s.get('t_last')} "
              f"steps={s.get('n_steps')} newton={s.get('iters_mean')}"
              f"/{s.get('iters_max')} ksp/N={s.get('ksp_per_newton_mean')} "
              f"clock={s.get('clock_s')} mem={s.get('peak_mem_gb')}"
              + (f" QOIERR {s['qoi_error']}" if s.get("qoi_error") else ""))


if __name__ == "__main__":
    main()
