#!/usr/bin/env python3
"""Residual cost on 3dTube: a short quasi-monolithic run (default L2, 20
steps) set up exactly as the 3dTube verification driver's mesh study
(prepare_case: refinement, time step, backward, solid preconditioner,
monitors, parallel Allrun), run with a timing build (measurement-only patch
of foamPetscSnesSolver.C printing "SNES timing" after every SNESSolve), so
that the time of the residual evaluations and the total wall time can be
compared between builds.

    ma_cost.py RUN_DIR --s4f TREE [--level 2] [--steps 20] [--cores 8]

The solids4Foam on PATH (the sourced build) is used; TREE only supplies the
tutorial and the driver.
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("run_dir", type=Path)
ap.add_argument("--s4f", type=Path, required=True)
ap.add_argument("--level", type=int, default=2)
ap.add_argument("--steps", type=int, default=20)
ap.add_argument("--cores", type=int, default=8)
a = ap.parse_args()

drv_path = (a.s4f / "tutorials/fluidSolidInteraction/3dTube/verification/"
            "scripts/tube_3d_verification.py")
spec = importlib.util.spec_from_file_location("tubedrv", drv_path)
drv = importlib.util.module_from_spec(spec)
sys.modules["tubedrv"] = drv
spec.loader.exec_module(drv)

a.run_dir.parent.mkdir(parents=True, exist_ok=True)
drv.WORK_ROOT = a.run_dir.parent
reference = json.loads(drv.REFERENCE_FILE.read_text())
factor = 2 ** (a.level - 1)
delta_t = float(reference["mesh"]["base_delta_t_s"]) / factor
args = argparse.Namespace(time_scheme="backward", solid_preconditioner="hypre")
case = drv.prepare_case(a.run_dir.name, "monolithic", factor, delta_t,
                        a.steps * delta_t, args, reference, a.cores)

import os
env = dict(os.environ)

t0 = time.time()
with (case / "log.Allverify").open("w") as log:
    rc = subprocess.run([str(case / "Allrun"),
                         *drv.COUPLINGS["monolithic"]["allrun"]],
                        cwd=case, stdout=log, stderr=subprocess.STDOUT,
                        env=env).returncode
wall = time.time() - t0
solver = (case / "log.solids4Foam").read_text(errors="replace")


# Residual timing from the measurement-only "SNES timing" lines (printed by
# the timing build after every SNESSolve): the monolithic Up solves are the
# blocks that start with "Solving the monolithic momentum-continuity system"
up = re.findall(
    r"Solving the monolithic momentum-continuity system.*?"
    r"SNES timing: solve ([0-9.eE+-]+) s, residual evaluations (\d+) in "
    r"([0-9.eE+-]+) s", solver, re.DOTALL)
alls = re.findall(r"SNES timing: solve ([0-9.eE+-]+) s, residual evaluations "
                  r"(\d+) in ([0-9.eE+-]+) s", solver)
newton = [int(x) for x in re.findall(
    r"monolithic momentum-continuity system.*?Nonlinear solve \w+ due to "
    r"\w+ iterations (\d+)", solver, re.DOTALL)]
krylov = [int(x) for x in re.findall(
    r"Linear solve converged due to \w+ iterations (\d+)", solver)]
clock = re.findall(r"ClockTime\s*=\s*([0-9.eE+-]+)", solver)
exe = re.findall(r"ExecutionTime\s*=\s*([0-9.eE+-]+)", solver)
up_solve = sum(float(a) for a, _, _ in up)
up_evals = sum(int(b) for _, b, _ in up)
up_res = sum(float(c) for _, _, c in up)
res = dict(rc=rc, wall_s=wall, clock_s=float(clock[-1]) if clock else None,
           execution_s=float(exe[-1]) if exe else None,
           steps=len(newton), newton_total=sum(newton),
           krylov_total=sum(krylov),
           up_snes_solve_s=up_solve, up_residual_evals=up_evals,
           up_residual_s=up_res,
           up_residual_ms_per_eval=1e3 * up_res / up_evals if up_evals else None,
           all_snes_solve_s=sum(float(a) for a, _, _ in alls),
           all_residual_s=sum(float(c) for _, _, c in alls),
           completed=bool(re.search(r"^End\s*$", solver, re.MULTILINE)))
(case / "cost.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res))
