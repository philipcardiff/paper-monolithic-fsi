#!/usr/bin/env python3
"""WP0 runs (0b blobInTreacle, 0c womersleyTube) on the mac-studio.

Each run is a fresh copy of the tutorial at the solver head under runs/,
set up with the tutorial verification drivers' own functions; only case
files are edited (time scheme, viscousStressTranspose, coupling test,
PETSc tolerances). Runs are scheduled so that at most --cores ranks are in
use at once. Results go to runs/<run_id>/wp0_result.json.

    wp0_run.py [--cores 10] [--only ID,ID] [--list]
"""
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
S4F = ROOT / "s4f-qm-head"
RUNS = ROOT / "runs"
FSI = S4F / "tutorials" / "fluidSolidInteraction"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


blob = load("blobdrv", FSI / "blobInTreacle/verification/scripts/"
            "blob_in_treacle_verification.py")
wom = load("womdrv", FSI / "womersleyTube/verification/scripts/"
           "womersley_tube_verification.py")
wom.WORK_ROOT = RUNS


# ---------------------------------------------------------------------------
# Case-file edits
# ---------------------------------------------------------------------------

def sub1(path, pattern, repl, flags=re.MULTILINE):
    text, n = re.subn(pattern, repl, path.read_text(), count=1, flags=flags)
    if n != 1:
        raise RuntimeError(f"no match for {pattern!r} in {path}")
    path.write_text(text)


def set_vst(case, value):
    sub1(case / "constant/fluid/fluidProperties.monolithic",
         r"(newtonIcoFluidCoeffs\s*\{\n)",
         rf"\g<1>    viscousStressTranspose {value};\n\n")


def set_petsc(case, options):
    path = case / "system/fvSolution.monolithic"
    for key, value in options.items():
        sub1(path, rf"(^\s*{key}\s+)\"?[^;\"]*\"?;", rf'\g<1>"{value}";')


def set_strict(path, absolute=None):
    extra = "    requireAllResidualMeasures yes;\n"
    if absolute:
        extra += f"    outerCorrAbsoluteTolerance {absolute};\n"
    sub1(path, r"(^\s*writeResidualsToFile\s+yes;\n)", rf"\g<1>{extra}")


# ---------------------------------------------------------------------------
# Run definitions
# ---------------------------------------------------------------------------

TIGHT = {"snes_rtol": "1e-8", "snes_stol": "1e-8", "ksp_rtol": "1e-6"}
BLOB_DT = {1: 0.01, 2: 0.01, 4: 0.005}
BLOB_RANKS = {1: 1, 2: 2, 4: 4}

RUNS_DEF = []
for lvl in (1, 2, 4):
    for vst in ("no", "yes"):
        RUNS_DEF.append(dict(id=f"wp0-blob-qm-vst{vst}-x{lvl}", case="blob",
                             coupling="monolithic", level=lvl, vst=vst,
                             petsc={}, ranks=BLOB_RANKS[lvl]))
    RUNS_DEF.append(dict(id=f"wp0-blob-iqn-x{lvl}", case="blob",
                         coupling="partitioned", level=lvl,
                         ranks=BLOB_RANKS[lvl]))
# B1 iterative-error check at the tutorial level
RUNS_DEF.append(dict(id="wp0-blob-qm-vstno-x1-tight", case="blob",
                     coupling="monolithic", level=1, vst="no", petsc=TIGHT,
                     ranks=1))
for vst in ("no", "yes"):
    RUNS_DEF.append(dict(id=f"wp0-wom-qm-vst{vst}-m2n50", case="wom",
                         coupling="monolithic", vst=vst, petsc=TIGHT, ranks=1))
RUNS_DEF.append(dict(id="wp0-wom-qm-vstno-m2n50-tut", case="wom",
                     coupling="monolithic", vst="no", petsc={}, ranks=1))
RUNS_DEF.append(dict(id="wp0-wom-rn-m2n50", case="wom", coupling="robin",
                     ranks=1))
RUNS_DEF.append(dict(id="wp0-wom-iqn-m2n50", case="wom", coupling="iqnils",
                     ranks=1))


def run_cmd(cmd, case, log_name):
    with (case / log_name).open("w") as log:
        t0 = time.time()
        res = subprocess.run(cmd, cwd=case, stdout=log,
                             stderr=subprocess.STDOUT)
        return res.returncode, time.time() - t0


def newton_counts(log_text):
    counts = [int(n) for n in re.findall(
        r"^Solving the monolithic momentum-continuity system.*?"
        r"Nonlinear solve \w+ due to \w+ iterations (\d+)",
        log_text, re.MULTILINE | re.DOTALL)]
    ksp = [int(n) for n in re.findall(
        r"Linear solve converged due to \w+ iterations (\d+)", log_text)]
    return counts, ksp


def iqn_counts(case):
    path = case / "postProcessing/fsiResiduals.dat"
    per = {}
    if path.is_file():
        for line in path.read_text().splitlines()[1:]:
            f = line.split()
            if len(f) >= 2:
                per[f[0]] = max(per.get(f[0], 0), int(f[1]))
    return list(per.values())


def provenance(case, r):
    subprocess.run([sys.executable, str(ROOT / "scripts/provenance.py"),
                    str(case), "--ranks", str(r["ranks"]),
                    "--run-id", r["id"], "--s4f", str(S4F)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_blob(r):
    case = RUNS / r["id"]
    if case.exists():
        shutil.rmtree(case)
    shutil.copytree(blob.CASE_DIR, case, ignore=blob.ignored, symlinks=True)
    lvl = r["level"]
    if lvl != 1:
        for region in ("fluid", "solid"):
            blob.refine_mesh(case / "system" / region / "blockMeshDict", lvl)
    end_time, dt = 3.0, BLOB_DT[lvl]
    control = case / "system/controlDict"
    blob.set_entry(control, "endTime", f"{end_time:.10g}")
    blob.set_entry(control, "deltaT", f"{dt:.10g}")
    cmd = ["./Allrun"]
    if r["coupling"] == "monolithic":
        cmd.append("monolithic")
        # BDF2 for the fluid momentum (the solid is already backward);
        # ddt(dU) only enters the approximate Jacobian, kept as in the
        # womersleyTube and ringAddedMass tutorials
        sub1(case / "system/fluid/fvSchemes.monolithic",
             r"(ddt\(U\)\s+)Euler;", r"\g<1>backward;")
        set_vst(case, r["vst"])
        set_petsc(case, r["petsc"])
    else:
        # strict test; the absolute test stops the near-steady steps from
        # all running to nOuterCorr (fluidSolidInterfaces README)
        set_strict(case / "constant/fsiProperties", absolute="1e-9")
    if r["ranks"] > 1:
        blob.set_cores(case, r["ranks"])
        cmd.append("parallel")
    rc, wall = run_cmd(cmd, case, "log.Allrun")
    blob.check_solver_log(case / "log.solids4Foam", end_time, r["id"])
    hist = blob.displacement_history(case)
    text = (case / "log.solids4Foam").read_text(errors="replace")
    out = dict(run_id=r["id"], wall_s=wall, ux=hist[-1][1], uy=hist[-1][2],
               t_end=hist[-1][0], dt=dt, n_steps=round(end_time / dt),
               steady_spread_0p5=blob.steady_spread(hist, 0.5),
               fluid_cells=blob.count_cells(case, "fluid"),
               solid_cells=blob.count_cells(case, "solid"))
    clock = re.findall(r"ClockTime\s*=\s*([0-9.eE+-]+)", text)
    out["clock_s"] = float(clock[-1]) if clock else None
    if r["coupling"] == "monolithic":
        n, k = newton_counts(text)
    else:
        n, k = iqn_counts(case), []
    out.update(iters_mean=sum(n) / len(n) if n else None,
               iters_max=max(n) if n else None, iters_n=len(n),
               ksp_per_newton_mean=sum(k) / len(k) if k else None)
    return case, out


def run_wom(r):
    spec = {"coupling": r["coupling"], "factor": 2, "steps": 50,
            "name": r["id"]}
    reference = json.loads(wom.REFERENCE_FILE.read_text())
    case = RUNS / r["id"]
    if case.exists():
        shutil.rmtree(case)
    wom.configure(case, spec, reference)
    if r["coupling"] == "monolithic":
        set_vst(case, r["vst"])
        set_petsc(case, r["petsc"])
    else:
        set_strict(case / f"constant/fsiProperties.{r['coupling']}")
    rc, wall = run_cmd(["./Allrun", r["coupling"]], case, "log.Allrun")
    problem = wom.solver_log_problem(case)
    if problem:
        raise RuntimeError(f"{r['id']} {problem}")
    row = wom.analyse(spec, reference)
    row.pop("_profile", None)
    text = (case / "log.solids4Foam").read_text(errors="replace")
    _, k = newton_counts(text)
    row.update(run_id=r["id"], wall_s=wall,
               ksp_per_newton_mean=sum(k) / len(k) if k else None)
    return case, row


def execute(r):
    case = RUNS / r["id"]
    try:
        case, out = (run_blob if r["case"] == "blob" else run_wom)(r)
        out["status"] = "completed"
    except Exception as error:  # record and carry on
        out = {"run_id": r["id"], "status": "failed", "error": str(error)}
    out["def"] = r
    if case.is_dir():
        provenance(case, r)
        (case / "wp0_result.json").write_text(json.dumps(out, indent=2))
    print(f"{time.strftime('%H:%M:%S')} {r['id']}: {out['status']}",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cores", type=int, default=10)
    ap.add_argument("--only")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    todo = RUNS_DEF
    if args.only:
        keep = args.only.split(",")
        todo = [r for r in RUNS_DEF if r["id"] in keep]
    if args.list:
        for r in todo:
            print(r["id"], r["ranks"])
        return
    RUNS.mkdir(exist_ok=True)
    # largest first, so the long x4 runs start early
    todo = sorted(todo, key=lambda r: -r.get("level", 0) * r["ranks"])
    free = [args.cores]
    cond = threading.Condition()
    threads = []

    def worker(r):
        try:
            execute(r)
        finally:
            with cond:
                free[0] += r["ranks"]
                cond.notify_all()

    for r in todo:
        with cond:
            cond.wait_for(lambda: free[0] >= r["ranks"])
            free[0] -= r["ranks"]
        print(f"{time.strftime('%H:%M:%S')} start {r['id']} "
              f"({r['ranks']} ranks)", flush=True)
        t = threading.Thread(target=worker, args=(r,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
