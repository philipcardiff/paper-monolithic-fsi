#!/usr/bin/env python3
"""WP3 robustness maps: set up one ringAddedMass (3a) or collapsibleChannel
(3b) run directory from the solver-branch tutorial.

The cases are configured with the tutorials' own verification drivers
(imported read-only from the solids4foam tree, no bytecode written); this
script only edits case files in the copy: coupling, coupling test and caps,
schemes, densities and PETSc options. It writes wp3_case.json (the settings)
and wp3_cmd (the Allrun arguments) into the run directory.

  wp3_setup.py ring <run_dir> --coupling C --level L --steps N
  wp3_setup.py coll <run_dir> --coupling C --dt DT --rho-ratio R

C is one of aitken, iqn, rn, qm. Failure criterion and caps: see
paper-data/campaign/wp3/README.md (fixed before the runs).
"""

import os
import sys

# The drivers need Python >= 3.9; MeluXina's /usr/bin/python3 is 3.6
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
import shutil
from pathlib import Path

sys.dont_write_bytecode = True

QM_ROOT = Path(os.environ.get("QM_ROOT",
                              "/project/home/p201287/philip/qm-head"))
FSI = QM_ROOT / "solids4foam/tutorials/fluidSolidInteraction"
# #618 (merge 4ae081609) removed the viscousStressTranspose switch
POST_618 = os.environ.get("WP3_POST_618", "no") == "yes"

# Caps, identical for every coupling (README "Failure criterion")
N_OUTER_CORR = 200      # partitioned coupling iterations per step
SNES_MAX_IT = 20        # quasi-monolithic Newton iterations per step

# 3a: ring, standard solid, refinement-factor-2 mesh, two periods
RING_FACTOR = 2
RING_PERIODS = 2
# Extended level: ten times the strong fluid density (mu ~ 100); exact
# frequency from verification/scripts/ring_exact_frequencies.py compute()
RING_EXTENDED = {"rhoFluid": 14000.0, "omega": 0.2536156983296937,
                 "massRatio": 100.75506514014994}

# 3b: collapsibleChannel, fluid level 2, AMI 640 x 8 linear-reconstruction
# solid (B2), to the end of the first-trough window
COLL_LEVEL = 2
COLL_SOLID = (640, 8)
COLL_END = 0.75
RHO_FLUID = 1.0


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sub1(path, pattern, repl, flags=re.MULTILINE):
    text, n = re.subn(pattern, repl, path.read_text(), count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"wp3: no match for {pattern!r} in {path}")
    path.write_text(text)


def partitioned_coeffs(path, coupling):
    """Strict test, iteration cap, couplingReuse 0; Aitken from the IQN-ILS
    file (same predictor and initial relaxation)."""
    sub1(path, r"^(\s*nOuterCorr\s+)\d+;", rf"\g<1>{N_OUTER_CORR};")
    # outerCorrTolerance stays at the tutorial value (ring 1e-6,
    # collapsibleChannel 1e-4)
    extra = "    requireAllResidualMeasures yes;\n"
    if coupling == "iqn" and not re.search(r"^\s*couplingReuse\s",
                                           path.read_text(), re.MULTILINE):
        extra += "    couplingReuse 0;\n"
    sub1(path, r"(^\s*writeResidualsToFile\s+yes;\n)", rf"\g<1>{extra}")
    if coupling == "aitken":
        sub1(path, r"^fluidSolidInterface\s+IQNILS;",
             "fluidSolidInterface    Aitken;")
        sub1(path, r"^IQNILSCoeffs", "AitkenCoeffs")


def qm_options(case):
    """The Newton cap, and the transpose viscous term as the code provides
    it: before #618 (85b0c1de6) `viscousStressTranspose no` is set
    explicitly; from #618 (4ae081609) the switch is gone (the term is always
    on), so any entry is removed from the copy."""
    fp = case / "constant/fluid/fluidProperties.monolithic"
    text = re.sub(r"^\s*viscousStressTranspose\s+\w+;\n", "",
                  fp.read_text(), flags=re.MULTILINE)
    fp.write_text(text)
    if not POST_618:
        sub1(fp, r"(newtonIcoFluidCoeffs\s*\{\n)",
             r"\g<1>    viscousStressTranspose no;\n\n")
    sub1(case / "system/fvSolution.monolithic",
         r"(^\s*snes_stol\s+[^;]+;\n)",
         rf'\g<1>            snes_max_it "{SNES_MAX_IT}";\n')


def schemes_617(path):
    """With the #618 build (4ae081609), apply #617 (1252bd2e5, tutorials
    only) in the copy: ddt(dU) and ddt(p) backward, no
    interpolate(U) skewCorrected entry, as the partitioned fluid files."""
    text = path.read_text()
    text = re.sub(r"^(\s*ddt\((?:U|dU|p)\)\s+)Euler;", r"\g<1>backward;", text,
                  flags=re.MULTILINE)
    text = re.sub(r"^\s*interpolate\(U\)\s+skewCorrected linear;\n", "",
                  text, flags=re.MULTILINE)
    path.write_text(text)


def petsc_tolerances(case):
    text = (case / "system/fvSolution.monolithic").read_text()
    get = lambda k: re.search(rf'^\s*{k}\s+"?([^";]+)"?;', text,
                              re.MULTILINE).group(1)
    return {k: get(k) for k in ("snes_rtol", "snes_stol", "ksp_rtol",
                                "snes_max_it")}


def schemes_summary(path):
    text = path.read_text()
    out = {}
    for key in ("ddt(U)", "ddt(dU)", "ddt(p)", "div(phi,U)",
                "interpolate(U)"):
        m = re.search(rf"^\s*{re.escape(key)}\s+([^;]+);", text, re.MULTILINE)
        if m:
            out[key] = " ".join(m.group(1).split())
    for block in ("ddtSchemes", "gradSchemes"):
        m = re.search(rf"{block}\s*\{{[^}}]*?default\s+([^;]+);", text)
        if m:
            out[f"{block} default"] = " ".join(m.group(1).split())
    if re.search(r"[cC]ellLimited|faceLimited|cellMDLimited", text):
        raise SystemExit(f"wp3: limiter found in {path}")
    return out


# ---------------------------------------------------------------------------
# 3a ringAddedMass
# ---------------------------------------------------------------------------

def setup_ring(args):
    drv = load("ringdrv", FSI / "ringAddedMass/verification/scripts/"
               "ring_added_mass_verification.py")
    reference = json.loads(drv.REFERENCE_FILE.read_text())
    reference["levels"]["extended"] = {"rhoFluid": RING_EXTENDED["rhoFluid"]}
    exact = dict(reference["exact"]["levels"])
    exact["extended"] = RING_EXTENDED
    omega = exact[args.level]["omega"]
    allrun = {"aitken": "iqnils", "iqn": "iqnils", "rn": "robin",
              "qm": "monolithic"}[args.coupling]
    spec = {"kind": "wet", "level": args.level, "coupling": allrun,
            "solid": "standard", "factor": RING_FACTOR, "steps": args.steps,
            "periods": RING_PERIODS, "omega_exact": omega,
            "period": 2 * math.pi / omega}

    case = Path(args.run_dir).resolve()
    if case.exists():
        shutil.rmtree(case)
    drv.configure(case, spec, reference)

    if args.coupling == "qm":
        qm_options(case)
        schemes = case / "system/fluid/fvSchemes.monolithic"
        if POST_618:
            schemes_617(schemes)
    else:
        partitioned_coeffs(case / f"constant/fsiProperties.{allrun}",
                           args.coupling)
        schemes = case / "system/fluid/fvSchemes"
    meta = {
        "map": "3a", "case": "ringAddedMass", "coupling": args.coupling,
        "level": args.level, "rhoFluid": reference["levels"][args.level]
        ["rhoFluid"], "massRatio": exact[args.level]["massRatio"],
        "omega_exact": omega, "steps_per_period": args.steps,
        "periods": RING_PERIODS, "deltaT": spec["period"] / args.steps,
        "n_steps": args.steps * RING_PERIODS,
        "end_time": args.steps * RING_PERIODS * spec["period"] / args.steps,
        "mesh_factor": RING_FACTOR, "solid": "standard",
        "interface": "directMap", "fluid_schemes": schemes_summary(schemes),
        "solid_schemes": schemes_summary(case / "system/solid/fvSchemes"),
        "spec": spec,
    }
    finish(case, meta, ["./Allrun", allrun, "standard"])


# ---------------------------------------------------------------------------
# 3b collapsibleChannel
# ---------------------------------------------------------------------------

def setup_coll(args):
    drv = load("ccv", FSI / "collapsibleChannel/verification/scripts/"
               "collapsible_channel_verification.py")
    allrun = {"aitken": "iqnils", "iqn": "iqnils", "rn": "robin",
              "qm": "monolithic"}[args.coupling]
    case = Path(args.run_dir).resolve()
    if case.exists():
        shutil.rmtree(case)
    shutil.copytree(drv.CASE_DIR, case, ignore=drv.ignored, symlinks=True)
    solid = tuple(args.solid)
    spec = {"name": case.name, "fluid": args.level, "solid": solid,
            "dt": args.dt, "solidType": "linear", "coupling": allrun}
    # Block divisions, deltaT, endTime, AMI, and the IQN-ILS initial
    # relaxation scaled with deltaT^2 (also used as Aitken's initial factor)
    drv.configure_case(case, spec, args.end)
    if args.write_every_step:
        control = case / "system/controlDict"
        sub1(control, r"^(writeInterval\s+)[^;]+;", r"\g<1>1;")
        sub1(control, r"^(writeControl\s+)[^;]+;", r"\g<1>timeStep;")
        sub1(control, r"^(writeFormat\s+)[^;]+;", r"\g<1>ascii;")
    ami = re.search(r"^\s*interfaceTransferMethod\s+AMI;",
                    (case / f"constant/fsiProperties.{allrun}").read_text(),
                    re.MULTILINE) is not None

    rho_s = args.rho_ratio * RHO_FLUID
    sub1(case / "constant/solid/mechanicalProperties",
         r"^(\s*rho\s+rho \[1 -3 0 0 0 0 0\]\s+)[^;]+;", rf"\g<1>{rho_s:g};")

    if args.coupling == "qm":
        qm_options(case)
        # Conservative traction transfer through AMI, as B2 (AMI only)
        fsi = case / "constant/fsiProperties.monolithic"
        if ami:
          sub1(fsi, r"^(\s*interfaceTransferMethod\s+\w+;)",
             r"\g<1>\n\n    // B2: conservative force transfer through AMI\n"
             r"    conservativeTractionTransfer yes;")
          sub1(case / "0/solid/D",
               r"^(\s*interface\s*\n\s*\{\s*\n\s*type\s+solidTraction;)",
               r"\g<1>\n        useUndeformedArea yes;")
        # BDF2 fluid (the tutorial file says Euler); ddt(dU) stays Euler
        schemes = case / "system/fluid/fvSchemes.monolithic"
        if POST_618:
            schemes_617(schemes)
        else:
            sub1(schemes, r"^(\s*ddt\(U\)\s+)Euler;", r"\g<1>backward;")
        if args.mesh_motion == "diffusion":
            sub1(case / "constant/fluid/mechanicalProperties.monolithic",
                 r"(type\s+)neoHookeanElastic;", r"\g<1>diffusionHyperElastic;")
            sub1(case / "constant/fluid/dynamicMeshDict.monolithic",
                 r"^(regionName\s+fluid;\n)",
                 r"\g<1>\n// Stiffen the mesh motion near the moving wall\n"
                 r"diffusivity     quadratic inverseDistance (interface);\n")
        if args.monitor_mesh_ksp:
            sub1(case / "system/fluid/fvSolution.monolithic",
                 r"(^\s*ksp_converged_reason;\n)",
                 r"\g<1>            ksp_monitor_true_residual;\n")
        cmd = ["./Allrun", "monolithic"]
    else:
        partitioned_coeffs(case / f"constant/fsiProperties.{allrun}",
                           args.coupling)
        # Same gradient scheme in both arms (decision 23 Oct)
        schemes = case / "system/fluid/fvSchemes"
        sub1(schemes, r"(gradSchemes\s*\{\s*default\s+)Gauss linear;",
             r"\g<1>leastSquares;")
        cmd = ["./Allrun", "linear"] + (["robin"] if allrun == "robin"
                                        else [])
    fsi_text = (case / f"constant/fsiProperties.{allrun}").read_text()
    meta = {
        "map": "3b", "case": "collapsibleChannel", "coupling": args.coupling,
        "rho_ratio": args.rho_ratio, "rho_solid": rho_s,
        "rho_fluid": RHO_FLUID, "deltaT": args.dt, "end_time": args.end,
        "n_steps": round(args.end / args.dt), "fluid_level": args.level,
        "solid_mesh": f"{solid[0]}x{solid[1]}",
        "solid": "linear reconstruction (TL StVK)" if args.coupling != "qm"
        else "nonLinearGeometryTotalLagrangianVelocity (StVK)",
        "interface": re.search(r"^\s*interfaceTransferMethod\s+(\w+);",
                               fsi_text, re.MULTILINE).group(1),
        "fluid_schemes": schemes_summary(schemes),
        "solid_schemes": schemes_summary(
            case / ("system/solid/fvSchemes.monolithic"
                    if args.coupling == "qm" else "system/solid/fvSchemes")),
        "troughWindow": [0.3, 0.75],
        "mesh_motion": getattr(args, "mesh_motion", "tutorial"),
    }
    m = re.search(r"^\s*relaxationFactor\s+([^;]+);", fsi_text, re.MULTILINE)
    if m:
        meta["relaxationFactor"] = m.group(1)
    finish(case, meta, cmd)


def finish(case, meta, cmd):
    meta["caps"] = {"nOuterCorr": N_OUTER_CORR, "snes_max_it": SNES_MAX_IT}
    if meta["coupling"] == "qm":
        meta["petsc"] = petsc_tolerances(case)
        meta["viscousStressTranspose"] = ("removed (#618, transpose term "
                                          "always on)" if POST_618 else "no")
    else:
        fsi = (case / "constant").glob("fsiProperties.*")
        text = next(f for f in fsi if "requireAllResidualMeasures"
                    in f.read_text()).read_text()
        meta["coupling_tol"] = "outerCorrTolerance " + re.search(
            r"^\s*outerCorrTolerance\s+([^;]+);", text, re.MULTILINE).group(1)
        for key in ("robinPressureTolerance", "robinFluxTolerance"):
            m = re.search(rf"^\s*{key}\s+([^;]+);", text, re.MULTILINE)
            if m:
                meta["coupling_tol"] += f"; {key} {m.group(1)}"
        meta["convergence_test"] = "strict (requireAllResidualMeasures yes)"
        if meta["coupling"] == "iqn":
            meta["couplingReuse"] = 0
    meta["allrun"] = cmd
    (case / "wp3_case.json").write_text(json.dumps(meta, indent=1) + "\n")
    (case / "wp3_cmd").write_text(" ".join(cmd) + "\n")
    print(json.dumps({k: meta[k] for k in ("map", "coupling", "deltaT",
                                           "n_steps")}))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ring")
    p.add_argument("run_dir")
    p.add_argument("--coupling", choices=("aitken", "iqn", "rn", "qm"),
                   required=True)
    p.add_argument("--level", choices=("weak", "moderate", "strong",
                                       "extended"), required=True)
    p.add_argument("--steps", type=int, required=True)
    p = sub.add_parser("coll")
    p.add_argument("run_dir")
    p.add_argument("--coupling", choices=("aitken", "iqn", "rn", "qm"),
                   required=True)
    p.add_argument("--dt", type=float, required=True)
    p.add_argument("--rho-ratio", type=float, required=True)
    # B2 reruns: other fluid level, solid mesh and end time
    p.add_argument("--level", type=int, default=COLL_LEVEL)
    p.add_argument("--solid", nargs=2, type=int, default=list(COLL_SOLID),
                   metavar=("NX", "NY"))
    p.add_argument("--end", type=float, default=COLL_END)
    # Diagnostics: write every time step, in ASCII
    p.add_argument("--write-every-step", action="store_true")
    # QM fluid mesh motion: the tutorial's neoHookeanElastic law, or the
    # diffusionHyperElastic law with a quadratic inverse-distance
    # diffusivity from the interface (as TurekHron2006)
    p.add_argument("--mesh-motion", choices=("tutorial", "diffusion"),
                   default="tutorial")
    # Diagnostics: Krylov residual monitor on the mesh-motion (D) solve
    p.add_argument("--monitor-mesh-ksp", action="store_true")
    args = ap.parse_args()
    (setup_ring if args.cmd == "ring" else setup_coll)(args)


if __name__ == "__main__":
    main()
