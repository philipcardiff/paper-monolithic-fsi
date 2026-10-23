#!/usr/bin/env python3
"""Run agent A, batch 1: ringAddedMass (1a, 1d) and womersleyTube (1e).

Each run is a fresh copy of the tutorial at the solver head, set up with the
tutorials' own verification drivers (configure, analyse); only case files
are edited (viscousStressTranspose, coupling test, couplingReuse, PETSc
tolerances). All runs are serial; at most --cores run at once. Results go to
<runs>/<run_id>/ma_result.json.

    ma_run.py --s4f DIR --runs DIR [--cores N] [--only ID,ID] [--list]
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
TIGHT = {"snes_rtol": "1e-8", "snes_stol": "1e-8", "ksp_rtol": "1e-6"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


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


def set_partitioned(case, coupling):
    """Strict coupling test; IQN-ILS reuse pinned to the head default 0."""
    extra = "    requireAllResidualMeasures yes;\n"
    if coupling == "iqnils":
        extra += "    couplingReuse 0;\n"
    sub1(case / f"constant/fsiProperties.{coupling}",
         r"(^\s*writeResidualsToFile\s+yes;\n)", rf"\g<1>{extra}")


# ---------------------------------------------------------------------------
# Run definitions
# ---------------------------------------------------------------------------

def definitions():
    out = []
    # 1a: ring QM, 3 levels x mesh 1/2/4 x 25/50/100/200 steps per period,
    # with the dry (standard solid) ring for the wet/dry ratio
    for f in (1, 2, 4):
        for n in (25, 50, 100, 200):
            out.append(dict(id=f"ma-ram-dry-m{f}-n{n}", item="1a",
                            case="ram", kind="dry", solid="standard",
                            factor=f, steps=n))
            for lvl in ("weak", "moderate", "strong"):
                out.append(dict(id=f"ma-ram-qm-{lvl}-m{f}-n{n}", item="1a",
                                case="ram", kind="wet", level=lvl,
                                coupling="monolithic", solid="standard",
                                factor=f, steps=n, vst="no", petsc={}))
    # B1 iterative-error check: tight PETSc tolerances, m2 n100
    for lvl in ("weak", "moderate", "strong"):
        out.append(dict(id=f"ma-ram-qm-{lvl}-m2-n100-tight", item="1a",
                        case="ram", kind="wet", level=lvl,
                        coupling="monolithic", solid="standard", factor=2,
                        steps=100, vst="no", petsc=TIGHT))
    # 1d: partitioned, standard solid, strong, mesh 2 (QM is in 1a)
    for coupling, tag in (("iqnils", "iqn"), ("robin", "rn")):
        for n in (25, 50, 100):
            out.append(dict(id=f"ma-ram-{tag}-strong-m2-n{n}", item="1d",
                            case="ram", kind="wet", level="strong",
                            coupling=coupling, solid="standard", factor=2,
                            steps=n))
    # 1e: Womersley QM with the transpose term on and off; RN and IQN-ILS at
    # the head with the strict test (m2 n50 of all four is in WP0)
    cells = [(1, 200), (2, 200), (4, 200), (2, 100), (2, 400)]
    for f, n in cells:
        for vst in ("no", "yes"):
            out.append(dict(id=f"ma-wom-qm-vst{vst}-m{f}-n{n}", item="1e",
                            case="wom", coupling="monolithic", factor=f,
                            steps=n, vst=vst, petsc=TIGHT))
        for coupling, tag in (("robin", "rn"), ("iqnils", "iqn")):
            out.append(dict(id=f"ma-wom-{tag}-m{f}-n{n}", item="1e",
                            case="wom", coupling=coupling, factor=f,
                            steps=n))
    for r in out:
        r["ranks"] = 1
    return out


def cost(r):
    """Rough relative cost, to start the long runs first."""
    c = r["factor"] ** 2 * r["steps"]
    if r["case"] == "wom":
        c *= 6
    if r.get("coupling") in ("iqnils", "robin"):
        c *= 3
    return c


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_cmd(cmd, case, log_name):
    with (case / log_name).open("w") as log:
        t0 = time.time()
        res = subprocess.run(cmd, cwd=case, stdout=log,
                             stderr=subprocess.STDOUT)
        return res.returncode, time.time() - t0


def ksp_per_newton(case):
    text = (case / "log.solids4Foam").read_text(errors="replace")
    k = [int(n) for n in re.findall(
        r"Linear solve converged due to \w+ iterations (\d+)", text)]
    return sum(k) / len(k) if k else None


def run_ram(ctx, r):
    ram = ctx["ram"]
    ref = ctx["ram_ref"]
    exact = ref["exact"]
    omega = exact["dry"]["omega"] if r["kind"] == "dry" \
        else exact["levels"][r["level"]]["omega"]
    periods = ref["study"]["periods"]
    spec = {"kind": r["kind"], "level": r.get("level", ""),
            "coupling": r.get("coupling", ""), "solid": r["solid"],
            "factor": r["factor"], "steps": r["steps"], "periods": periods,
            "omega_exact": omega, "period": 2 * 3.141592653589793 / omega,
            "name": r["id"]}
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    ram.configure(case, spec, ref)
    cmd = ["./Allrun"]
    if r["kind"] == "wet":
        cmd += [r["coupling"], r["solid"]]
        if r["coupling"] == "monolithic":
            set_vst(case, r["vst"])
            set_petsc(case, r["petsc"])
        else:
            set_partitioned(case, r["coupling"])
    rc, wall = run_cmd(cmd, case, "log.Allrun")
    log = case / "log.solids4Foam"
    text = log.read_text(errors="replace") if log.is_file() else ""
    if re.search(r"FOAM FATAL|FOAM aborting", text) or \
            not re.search(r"^End\s*$", text, re.MULTILINE):
        raise RuntimeError(f"solver did not complete (rc {rc})")
    row = ram.analyse(spec)
    row.update(wall_s=wall, ksp_per_newton_mean=ksp_per_newton(case))
    return case, row


def run_wom(ctx, r):
    wom = ctx["wom"]
    ref = ctx["wom_ref"]
    spec = {"coupling": r["coupling"], "factor": r["factor"],
            "steps": r["steps"], "name": r["id"]}
    case = ctx["runs"] / r["id"]
    if case.exists():
        shutil.rmtree(case)
    wom.configure(case, spec, ref)
    if r["coupling"] == "monolithic":
        set_vst(case, r["vst"])
        set_petsc(case, r["petsc"])
    else:
        set_partitioned(case, r["coupling"])
    rc, wall = run_cmd(["./Allrun", r["coupling"]], case, "log.Allrun")
    problem = wom.solver_log_problem(case)
    if problem:
        raise RuntimeError(f"{problem} (rc {rc})")
    row = wom.analyse(spec, ref)
    row.pop("_profile", None)
    row.update(wall_s=wall, ksp_per_newton_mean=ksp_per_newton(case))
    return case, row


def execute(ctx, r):
    case = ctx["runs"] / r["id"]
    try:
        case, out = (run_ram if r["case"] == "ram" else run_wom)(ctx, r)
        out["status"] = "completed"
    except Exception as error:  # record and carry on
        out = {"status": "failed", "error": str(error),
               "traceback": traceback.format_exc()}
    out["run_id"] = r["id"]
    out["def"] = r
    if case.is_dir():
        subprocess.run([sys.executable, str(ctx["provenance"]), str(case),
                        "--ranks", "1", "--run-id", r["id"],
                        "--s4f", str(ctx["s4f"])],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (case / "ma_result.json").write_text(
            json.dumps(out, indent=2, default=str))
    print(f"{time.strftime('%H:%M:%S')} {r['id']}: {out['status']}",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s4f", required=True, type=Path)
    ap.add_argument("--runs", required=True, type=Path)
    ap.add_argument("--provenance", type=Path,
                    default=HERE / "provenance.py")
    ap.add_argument("--cores", type=int, default=8)
    ap.add_argument("--only")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    todo = definitions()
    if args.only:
        keep = set(args.only.split(","))
        todo = [r for r in todo if r["id"] in keep]
    if args.list:
        for r in todo:
            print(r["item"], r["id"])
        print(len(todo), "runs")
        return
    fsi = args.s4f / "tutorials" / "fluidSolidInteraction"
    ram = load("ramdrv", fsi / "ringAddedMass/verification/scripts/"
               "ring_added_mass_verification.py")
    wom = load("womdrv", fsi / "womersleyTube/verification/scripts/"
               "womersley_tube_verification.py")
    args.runs.mkdir(parents=True, exist_ok=True)
    ram.WORK_ROOT = args.runs
    wom.WORK_ROOT = args.runs
    ctx = dict(ram=ram, wom=wom, runs=args.runs, s4f=args.s4f,
               provenance=args.provenance,
               ram_ref=json.loads(ram.REFERENCE_FILE.read_text()),
               wom_ref=json.loads(wom.REFERENCE_FILE.read_text()))
    todo = sorted(todo, key=lambda r: -cost(r))
    sem = threading.Semaphore(args.cores)
    threads = []

    def worker(r):
        try:
            execute(ctx, r)
        finally:
            sem.release()

    for r in todo:
        sem.acquire()
        print(f"{time.strftime('%H:%M:%S')} start {r['id']}", flush=True)
        t = threading.Thread(target=worker, args=(r,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
