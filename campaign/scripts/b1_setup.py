#!/usr/bin/env python3
"""B1: build the cases of the solid-block preconditioner check.

Usage (inside the run environment, Python >= 3.10):

    b1_setup.py spinup cav|tube DEST
    b1_setup.py window SPINUP DEST --config C --ranks N [--steps 50]
    b1_setup.py ring DEST --config C --ranks N

spinup  copies the tutorial and sets the level and time controls; the job
        then runs `./Allrun monolithic` in serial to the developed state:
        cav  cavityFlexibleBottom level 3 (factor 4), Δt 0.5 s, inlet ramp
             20 s (as the verification driver), to t = 100 s;
        tube 3dTube level 2 (factor 2), Δt 1.25e-5 s, with the driver's
             monitors, to t = 2 ms (160 steps), on 32 ranks
             (decomposeParMonolithic), reconstructed at the end.
Both set `restart yes` in the solid model's coefficients (a restart needs
the fields it writes) and the fluid ddt(U) of the monolithic variant (--ddt-u, default
backward).
window  copies a completed spin-up and runs it from t = 0 to the spin-up's
        end time plus --steps steps (the window), writing fields only at
        the end, with the solid-block configuration and rank count; with
        --restart it restarts from the spin-up's last time instead (not
        usable at 257b2e564: issue_mesh_motion_restart.md).
ring    builds ringAddedMass, moderate added mass, mesh factor 2, 50 steps
        per period, 2 periods, with the verification driver's configure();
        the job runs `./Allrun monolithic standard [parallel]`.

Configurations of the solid block of the UpU fieldsplit preconditioner:
    S0       redundant + LU (tutorial default)
    S1       BoomerAMG, settings of membraneRoof/system/solid/fvSolution
    S1n      S1 with nodal coarsening
    S2       bjacobi + LU per rank (parallel only)
    S0tight  S0 with snes_rtol and snes_stol 100 times smaller
"""

import argparse
import importlib.util
import json
import math
import os
import re
import shutil
import sys
from pathlib import Path

S4F = Path(os.environ.get("WM_PROJECT_USER_DIR", "")) / "solids4foam"
TUT = S4F / "tutorials" / "fluidSolidInteraction"

PREFIX = "fieldsplit_solid_"
BOOMERAMG = [
    ("pc_type", "hypre"),
    ("pc_hypre_type", "boomeramg"),
    ("pc_hypre_boomeramg_max_iter", '"1"'),
    ("pc_hypre_boomeramg_strong_threshold", '"0.7"'),
    ("pc_hypre_boomeramg_grid_sweeps_up", '"1"'),
    ("pc_hypre_boomeramg_grid_sweeps_down", '"1"'),
    ("pc_hypre_boomeramg_agg_nl", '"1"'),
    ("pc_hypre_boomeramg_agg_num_paths", '"1"'),
    ("pc_hypre_boomeramg_max_levels", '"25"'),
    ("pc_hypre_boomeramg_coarsen_type", "HMIS"),
    ("pc_hypre_boomeramg_interp_type", "ext+i"),
    ("pc_hypre_boomeramg_P_max", '"1"'),
    ("pc_hypre_boomeramg_truncfactor", '"0.3"'),
]
CONFIGS = {
    "S0": [("ksp_type", "preonly"), ("pc_type", "redundant"),
           ("redundant_pc_type", "lu")],
    "S1": [("ksp_type", "preonly")] + BOOMERAMG,
    "S1n": [("ksp_type", "preonly")] + BOOMERAMG
           + [("pc_hypre_boomeramg_nodal_coarsen", '"1"')],
    "S2": [("ksp_type", "preonly"), ("pc_type", "bjacobi"),
           ("sub_pc_type", "lu")],
}
CONFIGS["S0tight"] = CONFIGS["S0"]
TIGHTEN = 0.01
# Spin-up also writes the restart fields of the fluid mesh-motion solid
# (B1_FLUID_RESTART=1); otherwise the windows continue it with `restart no`
FLUID_RESTART = os.environ.get("B1_FLUID_RESTART", "1") == "1"
SPINUP_RANKS = int(os.environ.get("B1_SPINUP_RANKS", "32"))

SPINUP = {
    "cav": {"tutorial": "cavityFlexibleBottom", "factor": 4,
            "deltaT": 0.5, "endTime": 100.0},
    "tube": {"tutorial": "3dTube", "factor": 2,
             "deltaT": 1.25e-5, "endTime": 2e-3},
}


def load(name, path):
    """Import a verification driver of the tutorial tree as a module."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def ignore_outputs(directory, names):
    return {n for n in names if n.startswith(("processor", "log.",
                                              "postProcessing"))
            or n.startswith("mem.")
            or n in ("work", "verification", "run_meta.json",
                     "provenance.json")}


def set_entry(path, key, value):
    """Set a top-level entry of an OpenFOAM dictionary."""
    text = Path(path).read_text()
    text, count = re.subn(rf"^({re.escape(key)}\s+)[^;]+;",
                          rf"\g<1>{value};", text, flags=re.MULTILINE)
    if count != 1:
        sys.exit(f"Expected one top-level '{key}' in {path}, found {count}")
    Path(path).write_text(text)


def set_ranks(case, ranks):
    for path in [case / "system/decomposeParDict"] \
            + list(case.glob("system/*/decomposeParDict")):
        if path.is_file():
            set_entry(path, "numberOfSubdomains", str(ranks))


def apply_config(case, config):
    """Replace the solid-block options of solvers/UpU/options."""
    path = case / "system/fvSolution.monolithic"
    text = path.read_text()
    m = re.search(r"^\s*UpU\s*\{", text, flags=re.MULTILINE)
    if not m:
        sys.exit(f"No UpU solver in {path}")
    o = re.compile(r"\boptions\s*\{").search(text, m.end())
    depth, i = 1, o.end()
    while depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    body = text[o.end():i - 1]
    lines = [ln for ln in body.split("\n")
             if not re.match(rf"\s*{PREFIX}\w+", ln)]
    if config == "S0tight":
        for key in ("snes_rtol", "snes_stol"):
            for k, ln in enumerate(lines):
                mm = re.match(rf'(\s*{key}\s+)"?([^";\s]+)"?\s*;', ln)
                if mm:
                    value = float(mm.group(2)) * TIGHTEN
                    lines[k] = f'{mm.group(1)}"{value:g}";'
                    break
            else:
                sys.exit(f"No {key} in {path}")
    indent = "            "
    added = [f"{indent}// B1 configuration {config}"] + [
        f"{indent}{PREFIX}{k} {v};" for k, v in CONFIGS[config]]
    body = "\n".join(lines).rstrip() + "\n\n" + "\n".join(added) + "\n        "
    path.write_text(text[:o.end()] + body + text[i - 1:])


def set_restart(case, region="solid", value="yes"):
    """Set `restart` in the coefficients of a region's solid model.

    solid, yes: the spin-up writes the fields a consistent restart needs.
    fluid, no:  the fluid mesh motion is a total-displacement solid with no
                history (cav: neo-Hookean total Lagrangian; tube: linear
                elastic), which the solver lets continue without them."""
    path = case / f"constant/{region}/solidProperties.monolithic"
    text = path.read_text()
    model = re.search(r"^solidModel\s+(\w+);", text, flags=re.MULTILINE)
    if not model:
        sys.exit(f"No solidModel in {path}")
    # The coefficients block may be keyed by a regular expression, e.g.
    # "linearGeometryTotalDisplacementCoeffs|...Coeffs" (3dTube fluid)
    coeffs = re.search(rf'^"?[^\n{{]*\b{model.group(1)}Coeffs\b[^\n{{]*\s*\{{',
                       text, flags=re.MULTILINE)
    if not coeffs:
        sys.exit(f"No {model.group(1)}Coeffs in {path}")
    if re.search(r"^\s*restart\s", text, flags=re.MULTILINE):
        sys.exit(f"{path} already sets restart")
    path.write_text(text[:coeffs.end()] + f"\n    restart {value};"
                    + text[coeffs.end():])


MONOLITHIC_DECOMPOSITION = """
monolithicCoeffs
{
    regions (fluid solid);

    // DOF-based, as decomposeParMonolithic's README: fluid 4, solid 3
    regionWeights
    {
        fluid   4;
        solid   3;
    }

    interfaces
    (
        {
            regionA     fluid;
            patchA      wall;
            regionB     solid;
            patchB      inner-wall;
        }
    );
}
"""


def set_ddt_u(case, scheme):
    """Set the fluid ddt(U) scheme of the monolithic variant (decision of
    20 October: backward wherever possible)."""
    path = case / "system/fluid/fvSchemes.monolithic"
    text, count = re.subn(r"(ddt\(U\)\s+)\w+;", rf"\g<1>{scheme};",
                          path.read_text())
    if count != 1:
        sys.exit(f"Expected one ddt(U) in {path}, found {count}")
    path.write_text(text)


def spinup(kind, dest, ddt_u):
    s = SPINUP[kind]
    src = TUT / s["tutorial"]
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, symlinks=True, ignore=ignore_outputs)
    if kind == "cav":
        drv = load("cav_drv", next((src / "verification/scripts").glob(
            "*verification*.py")))
        ref = json.loads(drv.REFERENCE_FILE.read_text())
        drv.refine_mesh(dest / "system/fluid/blockMeshDict", s["factor"])
        drv.refine_mesh(dest / "system/solid/blockMeshDict", s["factor"])
        drv.set_control(dest, "endTime", s["endTime"])
        drv.set_control(dest, "deltaT", s["deltaT"])
        mono = ref["variants"]["monolithic"] if "variants" in ref else {}
        drv.ramp_inlet(dest, float(mono.get("inlet_ramp_s", 20.0)))
    else:
        drv = load("tube_drv", src / "verification/scripts/"
                   "tube_3d_verification.py")
        ref = json.loads(drv.REFERENCE_FILE.read_text())
        drv.refine_mesh(drv.block_mesh_dict(dest, "fluid"), s["factor"])
        drv.refine_mesh(drv.block_mesh_dict(dest, "solid"), s["factor"])
        drv.add_monitors(dest, ref)
        # The tutorial Allrun is serial; a whole node is billed anyway, so
        # the spin-up runs on SPINUP_RANKS ranks and is reconstructed
        set_ranks(dest, SPINUP_RANKS)
        # decomposeParMonolithic reads one graph over both regions,
        # joined across the FSI interface (3dTube: fluid wall/solid inner-wall)
        dpd = dest / "system/decomposeParDict"
        dpd.write_text(dpd.read_text().rstrip() + "\n"
                       + MONOLITHIC_DECOMPOSITION)
        allrun = dest / "Allrun"
        serial = "solids4Foam::runApplication solids4Foam\n"
        text = allrun.read_text()
        if text.count(serial) != 1:
            sys.exit(f"Expected one serial solver call in {allrun}")
        allrun.write_text(text.replace(
            serial,
            "solids4Foam::runApplication decomposeParMonolithic -force\n"
            "solids4Foam::runParallel solids4Foam || exit 1\n"
            "solids4Foam::runApplication -s fluid reconstructPar "
            "-region fluid -latestTime\n"
            "solids4Foam::runApplication -s solid reconstructPar "
            "-region solid -latestTime\n"))
    control = dest / "system/controlDict"
    set_entry(control, "deltaT", f"{s['deltaT']:.10g}")
    set_entry(control, "endTime", f"{s['endTime']:.10g}")
    # Both tutorials use writeControl runTime
    set_entry(control, "writeInterval", f"{s['endTime']:.10g}")
    set_ddt_u(dest, ddt_u)
    set_restart(dest)
    if FLUID_RESTART:
        set_restart(dest, "fluid", "yes")
    (dest / "b1_spinup.json").write_text(json.dumps(
        dict(s, kind=kind, ddt_U=ddt_u, fluid_restart=FLUID_RESTART),
        indent=1))


def latest_time(case):
    times = []
    for d in case.iterdir():
        try:
            times.append((float(d.name), d.name))
        except ValueError:
            pass
    return max(times)


def window(src, dest, config, ranks, steps, ddt_u, from_start):
    """A window of `steps` steps after the spin-up's end time t0.

    from_start: run from t = 0 through the spin-up to t0 + steps*dt (the
    window is the last `steps` steps; b1_analyse.py reads only those).
    Otherwise restart from the spin-up's t0: not usable at 257b2e564, as the
    fluid mesh-motion solid does not continue consistently from a restart
    (issue_mesh_motion_restart.md)."""
    if dest.exists():
        shutil.rmtree(dest)
    t0, name = latest_time(src)
    if t0 <= 0:
        sys.exit(f"Spin-up {src} has no time directory after 0")

    def ignore(directory, names):
        skip = ignore_outputs(directory, names)
        if Path(directory) == src:
            for n in names:
                try:
                    if float(n) not in ((0.0,) if from_start else (0.0, t0)):
                        skip.add(n)
                except ValueError:
                    pass
        return skip

    shutil.copytree(src, dest, symlinks=True, ignore=ignore)
    meta = json.loads((src / "b1_spinup.json").read_text())
    dt = meta["deltaT"]
    t1 = t0 + steps * dt
    control = dest / "system/controlDict"
    if from_start:
        set_entry(control, "startFrom", "startTime")
        set_entry(control, "writeInterval", f"{t1:.10g}")
    else:
        set_entry(control, "startFrom", "latestTime")
        set_entry(control, "writeInterval", f"{t1 - t0:.10g}")
    set_entry(control, "endTime", f"{t1:.10g}")
    apply_config(dest, config)
    if not from_start and not meta.get("fluid_restart"):
        set_restart(dest, "fluid", "no")
    set_ranks(dest, ranks)
    set_ddt_u(dest, ddt_u)
    (dest / "b1_window.json").write_text(json.dumps(dict(
        spinup=str(src), kind=meta["kind"], config=config, ranks=ranks,
        steps=steps, t0=t0, t1=t1, deltaT=dt, ddt_U=ddt_u,
        from_start=from_start,
        spinup_ddt_U=meta.get("ddt_U", "Euler")), indent=1))


def ring(dest, config, ranks):
    src = TUT / "ringAddedMass"
    drv = load("ring_drv", src / "verification/scripts/"
               "ring_added_mass_verification.py")
    ref = json.loads(drv.REFERENCE_FILE.read_text()) \
        if hasattr(drv, "REFERENCE_FILE") else None
    if ref is None:
        ref = json.loads(next((src / "verification/reference").glob(
            "*.json")).read_text())
    omega = ref["exact"]["levels"]["moderate"]["omega"]
    spec = {"kind": "wet", "level": "moderate", "factor": 2, "steps": 50,
            "periods": 2, "period": 2 * math.pi / omega, "solid": "standard",
            "coupling": "monolithic", "omega_exact": omega}
    if dest.exists():
        shutil.rmtree(dest)
    drv.configure(dest, spec, ref)
    apply_config(dest, config)
    set_ranks(dest, ranks)
    (dest / "b1_window.json").write_text(json.dumps(dict(
        kind="ring", config=config, ranks=ranks, spec=spec,
        ddt_U="backward (tutorial)"), indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("spinup")
    p.add_argument("kind", choices=sorted(SPINUP))
    p.add_argument("dest", type=Path)
    p.add_argument("--ddt-u", default="backward")
    p = sub.add_parser("window")
    p.add_argument("spinup", type=Path)
    p.add_argument("dest", type=Path)
    p.add_argument("--config", choices=sorted(CONFIGS), required=True)
    p.add_argument("--ranks", type=int, required=True)
    p.add_argument("--steps", type=int, default=50)
    p.add_argument("--ddt-u", default="backward")
    p.add_argument("--restart", action="store_true",
                   help="restart from the spin-up instead of running from 0")
    p = sub.add_parser("ring")
    p.add_argument("dest", type=Path)
    p.add_argument("--config", choices=sorted(CONFIGS), required=True)
    p.add_argument("--ranks", type=int, required=True)
    args = ap.parse_args()
    if args.cmd == "spinup":
        spinup(args.kind, args.dest.resolve(), args.ddt_u)
    elif args.cmd == "window":
        window(args.spinup.resolve(), args.dest.resolve(), args.config,
               args.ranks, args.steps, args.ddt_u, not args.restart)
    else:
        ring(args.dest.resolve(), args.config, args.ranks)


if __name__ == "__main__":
    main()
